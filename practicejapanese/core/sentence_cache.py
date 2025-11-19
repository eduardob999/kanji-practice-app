import json
import os
import random
import threading
import time
from datetime import datetime
from typing import List

import requests

from practicejapanese.core.vocab import load_vocab
from practicejapanese.core.utils import (
    get_sentence_cache_file,
    get_sentence_cache_settings,
    lowest_score_items,
)

_CACHE = None
_CACHE_LOCK = threading.Lock()
_PREFETCH_THREAD = None


def _ensure_cache_loaded():
    global _CACHE
    if _CACHE is not None:
        return
    cache_path = get_sentence_cache_file()
    dir_path = os.path.dirname(cache_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    try:
        with open(cache_path, "r", encoding="utf-8") as fh:
            _CACHE = json.load(fh)
    except (OSError, json.JSONDecodeError):
        _CACHE = {}


def _persist_cache():
    cache_path = get_sentence_cache_file()
    dir_path = os.path.dirname(cache_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    temp_path = cache_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as fh:
        json.dump(_CACHE, fh, ensure_ascii=False, indent=2)
    os.replace(temp_path, cache_path)


def get_cached_sentences(kanji: str) -> List[str]:
    _ensure_cache_loaded()
    with _CACHE_LOCK:
        entry = _CACHE.get(kanji)
        if not entry:
            return []
        return list(entry.get("sentences", []))


def _store_sentences(kanji: str, reading: str, sentences: List[str]):
    if not sentences:
        return
    _ensure_cache_loaded()
    with _CACHE_LOCK:
        _CACHE[kanji] = {
            "reading": reading,
            "sentences": sentences,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        _persist_cache()


def _fetch_sentences_from_api(reading: str, kanji: str, limit: int) -> List[str]:
    url = f"https://tatoeba.org/en/api_v0/search?from=jpn&query={reading}&limit={limit}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []
    sentences = []
    for item in data.get("results", []):
        text = item.get("text", "")
        if kanji in text or reading in text:
            sentences.append(text)
    return sentences


def get_or_fetch_sentences(reading: str, kanji: str, limit: int = 5) -> List[str]:
    sentences = get_cached_sentences(kanji)
    if sentences:
        return sentences[:limit]
    api_sentences = _fetch_sentences_from_api(reading, kanji, limit)
    if api_sentences:
        _store_sentences(kanji, reading, api_sentences)
    return api_sentences


def start_sentence_prefetcher():
    settings = get_sentence_cache_settings()
    if not settings.get("enabled", True):
        return
    global _PREFETCH_THREAD
    if _PREFETCH_THREAD and _PREFETCH_THREAD.is_alive():
        return
    _PREFETCH_THREAD = threading.Thread(
        target=_prefetch_loop, args=(settings,), daemon=True, name="SentencePrefetcher"
    )
    _PREFETCH_THREAD.start()


def _prefetch_loop(settings):
    vocab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Vocab.csv"))
    interval = max(5, int(settings.get("prefetch_interval_seconds", 30)))
    batch_size = max(1, int(settings.get("batch_fetch_size", 3)))
    api_limit = max(1, int(settings.get("api_limit", 5)))
    min_sentences = max(1, int(settings.get("min_sentences", 1)))

    while True:
        try:
            vocab_list = load_vocab(vocab_path)
            if not vocab_list:
                time.sleep(interval)
                continue
            lowest = lowest_score_items(vocab_path, vocab_list, score_col=4)
            candidates = lowest if lowest else vocab_list
            random.shuffle(candidates)
            fetched = 0
            for word in candidates:
                kanji = word[0]
                reading = word[1]
                if len(get_cached_sentences(kanji)) >= min_sentences:
                    continue
                sentences = _fetch_sentences_from_api(reading, kanji, api_limit)
                if sentences:
                    _store_sentences(kanji, reading, sentences)
                    fetched += 1
                if fetched >= batch_size:
                    break
        except Exception as exc:
            print(f"[SentencePrefetcher] {exc}")
        time.sleep(interval)