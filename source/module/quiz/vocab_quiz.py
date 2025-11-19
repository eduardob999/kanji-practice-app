from __future__ import annotations

import random
import re
from typing import List, MutableMapping, Optional, Sequence

from source.core.utils import (
    blue_text,
    green_text,
    is_undo_command,
    lowest_score_items,
    run_quiz_with_undo,
    update_score,
)
from source.module.vocab import VocabRow, load_vocab
from source.module.quiz.common import display_level_info, vocab_csv_path

CSV_PATH = vocab_csv_path()


def _normalize_reading(raw: str) -> str:
    """Normalise spacing for reading strings."""

    return (raw or "").replace("\u3000", " ").strip()


def _expand_readings(reading_field: str) -> List[str]:
    """Expand a combined reading field into distinct normalised readings."""

    parts = re.split(r"[;/、・,]", reading_field or "")
    cleaned: List[str] = []
    for part in parts:
        token = _normalize_reading(part)
        if not token:
            continue
        token = re.sub(r"^[\(（]\s*(.+?)\s*[\)）]$", r"\1", token)
        cleaned.append(token)
    seen: set[str] = set()
    unique: List[str] = []
    for value in cleaned:
        if value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def ask_question(
    vocab_list: Sequence[VocabRow],
    *,
    item_override: Optional[VocabRow] = None,
) -> Optional[MutableMapping[str, object]]:
    """Quiz the user on a vocabulary reading."""

    if not vocab_list:
        return None
    item = item_override or random.choice(vocab_list)
    kanji, reading, meaning = item[0], item[1], item[2]
    vocab_score = item[3] if len(item) > 3 else ""
    level = item[5] if len(item) > 5 else ""

    print()
    display_level_info(level, vocab_score)
    print(f"Kanji: {kanji}")
    print(f"Meaning: {meaning}")
    answer = _normalize_reading(
        input("What is the Reading? ")
    )
    if is_undo_command(answer):
        return {"undo_requested": True, "item": item}
    valid_readings = _expand_readings(reading)
    correct = answer in valid_readings
    if correct:
        print(green_text("Correct!"))
    else:
        print(f'{blue_text("Incorrect")}. The correct Reading is: {reading}')
    change = update_score(
        CSV_PATH,
        kanji,
        correct,
        score_col=3,
        reading=reading,
        meaning=meaning,
        level=level,
        return_change=True,
    )
    print()
    return {"item": item, "change": change}


def run() -> None:
    def fetch_items() -> Sequence[VocabRow]:
        vocab_list = load_vocab(CSV_PATH)
        return lowest_score_items(CSV_PATH, vocab_list, score_col=3)

    run_quiz_with_undo(fetch_items, ask_question, "No vocab found.")