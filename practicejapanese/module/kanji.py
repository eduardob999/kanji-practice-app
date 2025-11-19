"""Load kanji data structures from the packaged CSV files."""

from __future__ import annotations

import csv
import os
from typing import List, Tuple

KanjiRow = Tuple[str, str, str, str, str]


def load_kanji(path: os.PathLike[str] | str) -> List[KanjiRow]:
    """Load kanji entries from the provided CSV file."""

    kanji_list: List[KanjiRow] = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kanji = (row.get("Kanji") or "").strip()
            if not kanji:
                continue
            readings = (row.get("Readings") or "").strip()
            meaning = (row.get("Meaning") or "").strip()
            score = (row.get("Score") or "").strip()
            level = (row.get("Level") or "").strip()
            kanji_list.append((kanji, readings, meaning, score, level))
    return kanji_list