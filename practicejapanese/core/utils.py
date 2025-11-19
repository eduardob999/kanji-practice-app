from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, MutableMapping, Optional, Sequence

UNDO_KEYWORD = "undo"

_CONFIG_CACHE: Optional[MutableMapping[str, Any]] = None

_MODULE_DIR = Path(__file__).resolve().parent
_PACKAGE_ROOT = _MODULE_DIR.parent
_PROJECT_ROOT = _MODULE_DIR.parents[2]
_DATA_DIR = _PACKAGE_ROOT / "data"

# --- Global config flags ---
VERBOSE = False


def resolve_project_path(*parts: str) -> Path:
    """Return a project-root-relative path as an absolute Path."""

    return _PROJECT_ROOT.joinpath(*parts)


def resolve_data_path(*parts: str) -> Path:
    """Return a path inside the packaged data directory."""

    return _DATA_DIR.joinpath(*parts)


def set_verbose(flag: bool) -> None:
    """Enable or disable verbose console output for the package."""

    global VERBOSE
    VERBOSE = bool(flag)


def is_verbose() -> bool:
    """Return the current verbosity flag."""

    return VERBOSE


def _config_path() -> Path:
    """Return the absolute path to the shared configuration file."""

    return resolve_project_path("config.json")


def load_config() -> MutableMapping[str, Any]:
    """Load the shared configuration file once and memoise the result."""

    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    config_file = _config_path()
    try:
        with config_file.open("r", encoding="utf-8") as fh:
            _CONFIG_CACHE = json.load(fh)
    except (OSError, json.JSONDecodeError):
        _CONFIG_CACHE = {}
    return _CONFIG_CACHE


def get_score_output_dir() -> Path:
    """Return the directory where score exports should be written."""

    config = load_config()
    configured = config.get("score_output_dir") if isinstance(config, dict) else None
    if configured:
        return Path(os.path.expanduser(str(configured)))
    home_dir = Path(os.path.expanduser("~"))
    return home_dir / "public" / "practicejapanese"


def get_sentence_cache_file() -> Path:
    """Return the path to the JSON file storing cached example sentences."""

    config = load_config()
    configured = config.get("sentence_cache_file") if isinstance(config, dict) else None
    if configured:
        return Path(os.path.expanduser(str(configured)))
    return get_score_output_dir() / "sentence_cache.json"


def get_sentence_cache_settings() -> Dict[str, Any]:
    """Return the merged default + user-defined sentence cache settings."""

    defaults: Dict[str, Any] = {
        "enabled": True,
        "prefetch_interval_seconds": 30,
        "batch_fetch_size": 3,
        "api_limit": 5,
        "min_sentences": 1,
    }
    config = load_config()
    settings = config.get("sentence_cache_settings") if isinstance(config, dict) else None
    if isinstance(settings, dict):
        merged = defaults.copy()
        merged.update(settings)
        return merged
    return defaults


def reset_scores() -> None:
    """Normalise quiz scores based on JLPT level metadata."""

    print("Resetting scores based on Level (5→0, 4→1, 3→2, 2→3, 1→4)...")
    for csv_path in (resolve_data_path("Kanji.csv"), resolve_data_path("Vocab.csv")):
        temp_path = csv_path.with_suffix(csv_path.suffix + ".temp")
        updated_rows: List[Dict[str, Any]] = []
        with csv_path.open("r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames or []
            for row in reader:
                if row:
                    level_raw = (row.get("Level") or "").strip()
                    try:
                        level = int(level_raw)
                        reset_value = max(0, 5 - level)
                    except ValueError:
                        reset_value = 0

                    if csv_path.name == "Vocab.csv":
                        if "VocabScore" in fieldnames:
                            row["VocabScore"] = str(reset_value)
                        if "FillingScore" in fieldnames:
                            row["FillingScore"] = str(reset_value)
                    elif "Score" in fieldnames:
                        row["Score"] = str(reset_value)
                updated_rows.append(row)

        with temp_path.open("w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        temp_path.replace(csv_path)
    print("All scores reset based on Level.")


def quiz_loop(quiz_func: Callable[[Any], None], data: Any) -> None:
    """Call the supplied quiz function until the user interrupts."""

    try:
        while True:
            quiz_func(data)
    except KeyboardInterrupt:
        print("\nExiting quiz. Goodbye!")


def is_undo_command(value: str) -> bool:
    """Return True when the user typed the undo sentinel."""

    return (value or "").strip().lower() == UNDO_KEYWORD


def undo_score_change(change_record: Optional[MutableMapping[str, Any]]) -> bool:
    """Revert a previously recorded score modification."""

    if not change_record:
        return False
    csv_path = Path(change_record.get("csv_path", ""))
    score_field = change_record.get("score_field")
    target_index = change_record.get("row_index")
    if not csv_path or score_field is None or target_index is None:
        return False
    temp_path = csv_path.with_suffix(csv_path.suffix + ".temp")
    updated_rows: List[Dict[str, Any]] = []
    changed = False

    try:
        with csv_path.open("r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames or []
            if not fieldnames or score_field not in fieldnames:
                return False
            row_index = -1
            for row in reader:
                row_index += 1
                if not row:
                    updated_rows.append(row)
                    continue
                if row_index == target_index:
                    row[score_field] = change_record.get("prev_value", "0")
                    changed = True
                updated_rows.append(row)
    except OSError:
        return False

    if not changed:
        return False

    with temp_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    temp_path.replace(csv_path)
    return True


def run_quiz_with_undo(
    fetch_items: Callable[[], Sequence[Any]],
    ask_question: Callable[[Sequence[Any]], Optional[MutableMapping[str, Any]]],
    empty_message: str = "No items found.",
) -> None:
    """Launch a quiz loop that supports undoing the previous answer."""

    history: List[MutableMapping[str, Any]] = []
    pending_stack: List[Any] = []
    try:
        while True:
            if pending_stack:
                item_override = pending_stack.pop()
                question_pool = [item_override]
            else:
                question_pool = fetch_items()
                item_override = None
                if not question_pool:
                    print(empty_message)
                    return

            result = ask_question(question_pool, item_override=item_override)  # type: ignore[arg-type]
            if not result:
                continue
            current_item = result.get("item") or item_override

            if result.get("undo_requested"):
                if current_item is not None:
                    pending_stack.append(current_item)
                if not history:
                    print("Nothing to undo.")
                    continue
                undone_entry = history.pop()
                undo_score_change(undone_entry.get("change"))
                print("Previous answer undone. Re-asking it now.")
                pending_stack.append(undone_entry["item"])  # type: ignore[index]
                continue

            if current_item is None:
                continue
            history.append(
                {
                    "item": current_item,
                    "change": result.get("change"),
                }
            )
    except KeyboardInterrupt:
        print("\nExiting quiz. Goodbye!")


def update_score(
    csv_path: os.PathLike[str] | str,
    key: str,
    correct: bool,
    score_col: int = -1,
    reading: Optional[str] = None,
    level: Optional[str] = None,
    meaning: Optional[str] = None,
    unique_id: Optional[str] = None,
    update_all: bool = False,
    return_change: bool = False,
) -> Optional[MutableMapping[str, Any]]:
    """Update the score column for the row matching the provided key."""

    csv_path = Path(csv_path)
    temp_path = csv_path.with_suffix(csv_path.suffix + ".temp")
    updated_rows: List[Dict[str, Any]] = []
    updated_once = False
    change_record: Optional[MutableMapping[str, Any]] = None

    with csv_path.open("r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames or []
        if not fieldnames:
            return change_record if return_change else None
        score_field = fieldnames[score_col] if score_col >= 0 else fieldnames[-1]
        has_id = "ID" in fieldnames
        row_index = -1

        for row in reader:
            row_index += 1
            if not row:
                updated_rows.append(row)
                continue

            should_attempt = False
            if unique_id is not None and has_id:
                if str(row.get("ID", "")).strip() == str(unique_id).strip():
                    should_attempt = True
            elif row.get("Kanji") == key:
                should_attempt = True

            if should_attempt and (not updated_once or update_all):
                if reading is not None:
                    r_val = reading.strip()
                    r_match = any(
                        (row.get(rf) or "").strip() == r_val for rf in ("Reading", "Readings") if rf in row
                    )
                    if not r_match:
                        updated_rows.append(row)
                        continue
                if level is not None and (row.get("Level") or "").strip() != str(level).strip():
                    updated_rows.append(row)
                    continue
                if meaning is not None and (row.get("Meaning") or "").strip() != str(meaning).strip():
                    updated_rows.append(row)
                    continue

                prev_value = row.get(score_field, "0")
                if correct:
                    try:
                        new_value = str(int(row.get(score_field, "0")) + 1)
                    except ValueError:
                        new_value = "1"
                else:
                    new_value = "0"
                row[score_field] = new_value
                if return_change and change_record is None:
                    change_record = {
                        "csv_path": str(csv_path),
                        "row_index": row_index,
                        "score_field": score_field,
                        "prev_value": prev_value,
                        "new_value": new_value,
                    }
                if not update_all:
                    updated_once = True
            updated_rows.append(row)

    with temp_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    temp_path.replace(csv_path)

    if return_change:
        return change_record
    return None


def lowest_score_items(
    csv_path: os.PathLike[str] | str,
    vocab_list: Sequence[Sequence[Any]],
    score_col: int,
) -> List[Sequence[Any]]:
    """Return the tuples whose score matches the minimum value found in the CSV."""

    csv_path = Path(csv_path)
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        score_field = fieldnames[score_col] if score_col >= 0 else fieldnames[-1]
        scores = [
            (
                row.get("Kanji"),
                int(row.get(score_field, "0")) if (row.get(score_field) or "").isdigit() else 0,
            )
            for row in reader
            if row and row.get("Kanji")
        ]
    if not scores:
        return []
    min_score = min(score for _, score in scores)
    key_min_scores: Dict[str, int] = {}
    for kanji, score in scores:
        if kanji is None:
            continue
        if kanji not in key_min_scores or score < key_min_scores[kanji]:
            key_min_scores[kanji] = score

    filtered: List[Sequence[Any]] = []
    for item in vocab_list:
        if not item:
            continue
        try:
            item_score = int(item[score_col])
        except (ValueError, IndexError, TypeError):
            item_score = 0
        if item[0] in key_min_scores and key_min_scores[item[0]] == min_score and item_score == min_score:
            filtered.append(item)
    return filtered
