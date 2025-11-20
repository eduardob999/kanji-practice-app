"""Shared utilities for quiz modules, including CSV path helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from source.core.utils import blue_text, green_text, is_verbose

# Resolve data directory relative to package root so packaged CSVs are always found.
_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
_DATA_DIR = _PACKAGE_ROOT / "data"


def vocab_csv_path() -> Path:
    """Return the absolute path to the packaged vocabulary CSV file."""

    return _DATA_DIR / "Vocab.csv"


def kanji_csv_path() -> Path:
    """Return the absolute path to the packaged kanji CSV file."""

    return _DATA_DIR / "Kanji.csv"


def display_level_info(level: str, score: Optional[str], score_label: str = "Score") -> None:
    """Print the JLPT level (and optional score) respecting verbosity settings."""

    level = (level or "").strip()
    score = (score or "").strip()
    if not level:
        return
    level_text = f"Level {level}"
    if is_verbose() and score:
        score_text = f"{score_label} {score}"
        print(f"[{level_text} | {score_text}]")
    else:
        print(f"[{level_text}]")
