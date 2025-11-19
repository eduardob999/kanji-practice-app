"""Developer tooling for exporting and importing quiz scores."""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from source import __version__ as VERSION
from source.core.utils import get_score_output_dir, resolve_data_path


KANJI_FILE = resolve_data_path("Kanji.csv")
VOCAB_FILE = resolve_data_path("Vocab.csv")


def _prompt_choice() -> str:
    """Solicit a developer-mode action from the user."""

    print("Developer mode activated!")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {Path.cwd()}")
    print("Available quizzes: vocab_quiz, kanji_quiz, filling_quiz")
    print("Dev options:")
    print("1. Save all scores")
    print("2. Load all scores (overwrite current)")
    print("3. Exit dev mode")
    return input("Enter dev option: ").strip()


def _score_header_lines() -> List[str]:
    """Build the static header that prefixes exported score files."""

    return [
        f"PracticeJapanese Scores (version {VERSION})",
        "",
    ]


def _collect_kanji_score_lines(path: Path) -> List[str]:
    """Read kanji scores from ``path`` and return printable lines."""

    lines = ["Kanji Scores:"]
    try:
        with path.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                kanji = (row.get("Kanji") or "").strip()
                if not kanji:
                    continue
                score = (row.get("Score") or "").strip()
                lines.append(f"{kanji}: {score}")
    except OSError as exc:
        lines.append(f"[Error reading {path.name}: {exc}]")
    return lines + [""]


def _collect_vocab_score_lines(path: Path) -> List[str]:
    """Read vocab and filling quiz scores from ``path`` for export."""

    lines = ["Vocab Scores:"]
    try:
        with path.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                word = (row.get("Kanji") or "").strip()
                if not word:
                    continue
                vocab_score = (row.get("VocabScore") or "").strip()
                filling_score = (row.get("FillingScore") or "").strip()
                lines.append(
                    f"{word}: Vocab Quiz Score = {vocab_score}, Filling Quiz Score = {filling_score}"
                )
    except OSError as exc:
        lines.append(f"[Error reading {path.name}: {exc}]")
    return lines


def _save_all_scores() -> None:
    """Persist the current kanji and vocab scores into ``scores.txt``."""

    out_dir = get_score_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "scores.txt"
    lines: List[str] = []
    lines.extend(_score_header_lines())
    lines.extend(_collect_kanji_score_lines(KANJI_FILE))
    lines.extend(_collect_vocab_score_lines(VOCAB_FILE))
    try:
        out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"All scores saved to: {out_file}")
    except OSError as exc:
        print(f"Failed to save scores to {out_file}: {exc}")


def _parse_score_file(lines: Iterable[str]) -> Tuple[Dict[str, List[int]], Dict[str, List[Tuple[int, int]]]]:
    """Split score export contents into per-kanji and per-vocab updates."""

    kanji_scores: Dict[str, List[int]] = {}
    vocab_scores: Dict[str, List[Tuple[int, int]]] = {}
    section = None
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("Kanji Scores:"):
            section = "kanji"
            continue
        if line.startswith("Vocab Scores:"):
            section = "vocab"
            continue
        if section == "kanji" and ":" in line:
            key, _, value = line.partition(":")
            try:
                score = int(value.strip())
            except ValueError:
                continue
            kanji_scores.setdefault(key.strip(), []).append(score)
        elif section == "vocab" and ":" in line:
            word, _, rest = line.partition(":")
            vocab_score = None
            filling_score = None
            for piece in rest.split(","):
                piece = piece.strip()
                if piece.startswith("Vocab Quiz Score ="):
                    try:
                        vocab_score = int(piece.split("=", 1)[1].strip())
                    except ValueError:
                        vocab_score = None
                elif piece.startswith("Filling Quiz Score ="):
                    try:
                        filling_score = int(piece.split("=", 1)[1].strip())
                    except ValueError:
                        filling_score = None
            if vocab_score is not None or filling_score is not None:
                vocab_scores.setdefault(word.strip(), []).append(
                    (vocab_score or 0, filling_score or 0)
                )
    return kanji_scores, vocab_scores


def _apply_kanji_scores(updates: Dict[str, List[int]]) -> None:
    """Write kanji score updates back to the packaged CSV."""

    if not updates:
        return
    temp_path = KANJI_FILE.with_suffix(KANJI_FILE.suffix + ".temp")
    try:
        with KANJI_FILE.open("r", encoding="utf-8") as infile, temp_path.open(
            "w", encoding="utf-8", newline=""
        ) as outfile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames or []
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                kanji = (row.get("Kanji") or "").strip()
                if kanji in updates and updates[kanji]:
                    if "Score" in fieldnames:
                        row["Score"] = str(updates[kanji].pop(0))
                writer.writerow(row)
        temp_path.replace(KANJI_FILE)
        print(f"Updated Kanji scores in {KANJI_FILE}")
    except OSError as exc:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        print(f"Failed updating {KANJI_FILE.name}: {exc}")


def _apply_vocab_scores(updates: Dict[str, List[Tuple[int, int]]]) -> None:
    """Write vocab and filling quiz score updates back to the CSV."""

    if not updates:
        return
    temp_path = VOCAB_FILE.with_suffix(VOCAB_FILE.suffix + ".temp")
    try:
        with VOCAB_FILE.open("r", encoding="utf-8") as infile, temp_path.open(
            "w", encoding="utf-8", newline=""
        ) as outfile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames or []
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                word = (row.get("Kanji") or "").strip()
                if word in updates and updates[word]:
                    vocab_score, filling_score = updates[word].pop(0)
                    if "VocabScore" in fieldnames:
                        row["VocabScore"] = str(vocab_score)
                    if "FillingScore" in fieldnames:
                        row["FillingScore"] = str(filling_score)
                writer.writerow(row)
        temp_path.replace(VOCAB_FILE)
        print(f"Updated Vocab scores in {VOCAB_FILE}")
    except OSError as exc:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        print(f"Failed updating {VOCAB_FILE.name}: {exc}")


def _load_all_scores() -> None:
    """Import scores from a prior ``scores.txt`` export and apply them."""

    in_file = get_score_output_dir() / "scores.txt"
    if not in_file.exists():
        print(f"Scores file not found: {in_file}")
        return
    try:
        lines = in_file.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(f"Failed to read {in_file}: {exc}")
        return

    kanji_updates, vocab_updates = _parse_score_file(lines)
    _apply_kanji_scores(kanji_updates)
    _apply_vocab_scores(vocab_updates)


def run_dev_mode() -> None:
    """Prompt for a developer action and execute it immediately."""

    handlers = {
        "1": _save_all_scores,
        "2": _load_all_scores,
    }
    choice = _prompt_choice()
    handler = handlers.get(choice)
    if handler is None:
        print("Exiting dev mode.")
        return
    handler()
