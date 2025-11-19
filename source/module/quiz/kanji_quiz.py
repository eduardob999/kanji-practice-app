"""Kanji reading quiz with undo-aware scoring updates."""

from __future__ import annotations

import random
from typing import MutableMapping, Optional, Sequence

from source.module.kanji import KanjiRow, load_kanji
from source.core.utils import (
    blue_text,
    green_text,
    is_undo_command,
    lowest_score_items,
    run_quiz_with_undo,
    update_score,
)
from source.module.quiz.common import display_level_info, kanji_csv_path

CSV_PATH = kanji_csv_path()


def ask_question(
    kanji_list: Sequence[KanjiRow],
    *,
    item_override: Optional[KanjiRow] = None,
) -> Optional[MutableMapping[str, object]]:
    """Quiz the user on a kanji entry."""

    if not kanji_list:
        return None
    item = item_override or random.choice(kanji_list)
    kanji, readings, meaning = item[0], item[1], item[2]
    score = item[3] if len(item) > 3 else ""
    level = item[4] if len(item) > 4 else ""

    print()
    display_level_info(level, score)
    print(f"Readings: {readings}")
    print(f"Meaning: {meaning}")
    answer = input("What is the Kanji? ").strip()
    if is_undo_command(answer):
        return {"undo_requested": True, "item": item}
    correct = answer == kanji
    if correct:
        print(green_text("Correct!"))
    else:
        print(f'{blue_text("Incorrect")}. The correct Kanji is: {kanji}')
    change = update_score(
        CSV_PATH,
        kanji,
        correct,
        score_col=3,
        reading=readings,
        meaning=meaning,
        level=level,
        return_change=True,
    )
    print()
    return {"item": item, "change": change}


def run() -> None:
    """Run the interactive kanji quiz until the user exits."""

    def fetch_items() -> Sequence[KanjiRow]:
        kanji_list = load_kanji(CSV_PATH)
        return lowest_score_items(CSV_PATH, kanji_list, score_col=3)

    run_quiz_with_undo(fetch_items, ask_question, "No kanji found.")