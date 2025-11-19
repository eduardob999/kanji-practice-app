from __future__ import annotations

import random
from typing import MutableMapping, Optional, Sequence

from practicejapanese.module.kanji import KanjiRow, load_kanji
from practicejapanese.core.utils import (
    is_undo_command,
    lowest_score_items,
    run_quiz_with_undo,
    update_score,
)
from practicejapanese.module.quiz.common import display_level_info, kanji_csv_path

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
    print("Correct!" if correct else f"Incorrect. The correct Kanji is: {kanji}")
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
    def fetch_items() -> Sequence[KanjiRow]:
        kanji_list = load_kanji(CSV_PATH)
        return lowest_score_items(CSV_PATH, kanji_list, score_col=3)

    run_quiz_with_undo(fetch_items, ask_question, "No kanji found.")