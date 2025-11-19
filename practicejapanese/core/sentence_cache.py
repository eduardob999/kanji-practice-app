"""Maintain a cache of example sentences and prefetch them in the background."""

from __future__ import annotations

import json
import random
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, MutableMapping, Optional

import requests

from practicejapanese.module.vocab import load_vocab
from practicejapanese.core.utils import (
    get_sentence_cache_file,
    get_sentence_cache_settings,
    lowest_score_items,
    resolve_data_path,
)

CacheData = Dict[str, Any]

_CACHE: Optional[MutableMapping[str, CacheData]] = None
_CACHE_LOCK = threading.Lock()
_PREFETCH_THREAD: Optional[threading.Thread] = None


def _ensure_cache_loaded() -> None:
    """Initialise the in-memory cache by reading the persisted JSON file."""

    global _CACHE
    if _CACHE is not None:
        return
    cache_path = get_sentence_cache_file()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with cache_path.open("r", encoding="utf-8") as fh:
            _CACHE = json.load(fh)
    except (OSError, json.JSONDecodeError):
        _CACHE = {}


def _persist_cache() -> None:
    """Durably store the in-memory cache contents to disk."""

    cache_path = get_sentence_cache_file()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = cache_path.with_suffix(cache_path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as fh:
        json.dump(_CACHE, fh, ensure_ascii=False, indent=2)
    temp_path.replace(cache_path)


def get_cached_sentences(kanji: str) -> List[str]:
    """Return cached example sentences for ``kanji`` if available."""

    _ensure_cache_loaded()
    with _CACHE_LOCK:
        if _CACHE is None:
            return []
        entry = _CACHE.get(kanji)
        if not entry:
            return []
        return list(entry.get("sentences", []))


def _store_sentences(kanji: str, reading: str, sentences: List[str]) -> None:
    """Save new sentences for ``kanji`` with metadata and persist them."""

    if not sentences:
        return
    _ensure_cache_loaded()
    with _CACHE_LOCK:
        if _CACHE is None:
            return
        _CACHE[kanji] = {
            "reading": reading,
            "sentences": sentences,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        _persist_cache()


def _fetch_sentences_from_api(reading: str, kanji: str, limit: int) -> List[str]:
    """Retrieve example sentences from Tatoeba for the given reading/kanji."""

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
    """Return cached sentences when present, otherwise fetch from the API."""

    sentences = get_cached_sentences(kanji)
    if sentences:
        return sentences[:limit]
    api_sentences = _fetch_sentences_from_api(reading, kanji, limit)
    if api_sentences:
        _store_sentences(kanji, reading, api_sentences)
    return api_sentences


def start_sentence_prefetcher() -> None:
    """Start the background thread that prefetches sentences when enabled."""

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


def _prefetch_loop(settings: MutableMapping[str, Any]) -> None:
    """Background worker that periodically fetches low-score vocabulary sentences."""

    vocab_path = resolve_data_path("Vocab.csv")
    interval = max(5, int(settings.get("prefetch_interval_seconds", 30)))
    batch_size = max(1, int(settings.get("batch_fetch_size", 3)))
    api_limit = max(1, int(settings.get("api_limit", 5)))
    min_sentences = max(1, int(settings.get("min_sentences", 1)))

    while True:
        try:
            vocab_list = load_vocab(str(vocab_path))
            if not vocab_list:
                time.sleep(interval)
                continue
            lowest = lowest_score_items(vocab_path, vocab_list, score_col=4)
            candidates = list(lowest) if lowest else list(vocab_list)
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