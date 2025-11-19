from __future__ import annotations

import csv
import os
from typing import List, Tuple

VocabRow = Tuple[str, str, str, str, str, str]


def load_vocab(path: os.PathLike[str] | str) -> List[VocabRow]:
    """Load vocabulary entries while preserving legacy tuple ordering."""

    vocab_list: List[VocabRow] = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kanji = (row.get("Kanji") or "").strip()
            if not kanji:
                continue
            reading = (row.get("Reading") or "").strip()
            meaning = (row.get("Meaning") or "").strip()
            vocab_score = (row.get("VocabScore") or "").strip()
            filling_score = (row.get("FillingScore") or "").strip()
            level = (row.get("Level") or "").strip()
            vocab_list.append(
                (kanji, reading, meaning, vocab_score, filling_score, level)
            )
    return vocab_list