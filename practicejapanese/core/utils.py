import random
import os
import csv
import json

UNDO_KEYWORD = "undo"
_CONFIG_CACHE = None

# --- Global config flags ---
VERBOSE = False

def set_verbose(flag: bool):
    global VERBOSE
    VERBOSE = bool(flag)

def is_verbose() -> bool:
    return VERBOSE


def _config_path():
    # config.json lives at repo root (two levels up from this file)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config.json"))


def load_config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    config_file = _config_path()
    try:
        with open(config_file, "r", encoding="utf-8") as fh:
            _CONFIG_CACHE = json.load(fh)
    except (OSError, json.JSONDecodeError):
        _CONFIG_CACHE = {}
    return _CONFIG_CACHE


def get_score_output_dir():
    config = load_config()
    configured = config.get("score_output_dir") if isinstance(config, dict) else None
    if configured:
        return os.path.expanduser(configured)
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, "public", "practicejapanese")


def reset_scores():
    print("Resetting scores based on Level (5→0, 4→1, 3→2, 2→3, 1→4)...")
    for csv_path in [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Kanji.csv")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Vocab.csv")),
    ]:
        temp_path = csv_path + '.temp'
        updated_rows = []
        with open(csv_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            for row in reader:
                if row:
                    # Determine reset value from Level column: 5->0, 4->1, 3->2, 2->3, 1->4
                    level_raw = (row.get('Level') or '').strip()
                    try:
                        level = int(level_raw)
                        # Map so higher level number -> lower starting score
                        # For typical JLPT levels (1..5), this yields: 5→0, 4→1, 3→2, 2→3, 1→4
                        reset_value = max(0, 5 - level)
                    except ValueError:
                        # Fallback if Level is missing/invalid
                        reset_value = 0

                    if os.path.basename(csv_path) == "Vocab.csv":
                        # Reset both score columns if present
                        if 'VocabScore' in fieldnames:
                            row['VocabScore'] = str(reset_value)
                        if 'FillingScore' in fieldnames:
                            row['FillingScore'] = str(reset_value)
                    else:
                        # Only last column is score or explicit Score column
                        if 'Score' in fieldnames:
                            row['Score'] = str(reset_value)
                updated_rows.append(row)
        with open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        os.replace(temp_path, csv_path)
    print("All scores reset based on Level.")


def quiz_loop(quiz_func, data):
    try:
        while True:
            quiz_func(data)
    except KeyboardInterrupt:
        print("\nExiting quiz. Goodbye!")


def is_undo_command(value: str) -> bool:
    return (value or "").strip().lower() == UNDO_KEYWORD


def undo_score_change(change_record):
    if not change_record:
        return False
    csv_path = change_record.get("csv_path")
    score_field = change_record.get("score_field")
    target_index = change_record.get("row_index")
    if not csv_path or score_field is None or target_index is None:
        return False
    temp_path = csv_path + '.temp'
    updated_rows = []
    changed = False

    try:
        with open(csv_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
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

    with open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    os.replace(temp_path, csv_path)
    return True


def run_quiz_with_undo(fetch_items, ask_question, empty_message="No items found."):
    history = []
    pending_stack = []
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

            result = ask_question(question_pool, item_override=item_override)
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
                pending_stack.append(undone_entry["item"])
                continue

            if current_item is None:
                continue
            history.append({
                "item": current_item,
                "change": result.get("change"),
            })
    except KeyboardInterrupt:
        print("\nExiting quiz. Goodbye!")


# --- DRY helpers for quizzes ---


def update_score(
    csv_path,
    key,
    correct,
    score_col=-1,
    reading=None,
    level=None,
    meaning=None,
    unique_id=None,
    update_all=False,
    return_change=False,
):
    """Update the score for a (single) vocab / kanji row.

    Disambiguation hierarchy (first match wins unless update_all=True):
      1. If unique_id provided and CSV has column 'ID', update rows whose ID matches only.
      2. Else filter by Kanji == key.
         a. If reading provided, require exact match against 'Reading' or 'Readings'.
         b. If level provided, require Level match.
         c. If meaning provided, require Meaning match.

    By default only the *first* matching row is updated, preventing accidental
    increments on duplicate homographs. Set update_all=True to opt-in to the
    legacy behaviour of modifying every matching duplicate.
    """
    temp_path = csv_path + '.temp'
    updated_rows = []
    updated_once = False

    change_record = None

    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if not fieldnames:
            return change_record if return_change else None
        score_field = fieldnames[score_col] if score_col >= 0 else fieldnames[-1]
        has_id = 'ID' in fieldnames
        row_index = -1

        for row in reader:
            row_index += 1
            if not row:
                updated_rows.append(row)
                continue

            should_attempt = False
            # Unique ID match has highest priority if provided
            if unique_id is not None and has_id:
                if str(row.get('ID','')).strip() == str(unique_id).strip():
                    should_attempt = True
                else:
                    should_attempt = False
            else:
                # Base Kanji match required
                if row.get('Kanji') == key:
                    should_attempt = True
                else:
                    should_attempt = False

            if should_attempt and (not updated_once or update_all):
                disamb_ok = True
                # Reading check
                if reading is not None:
                    r_val = str(reading).strip()
                    r_match = False
                    for rf in ('Reading', 'Readings'):
                        if rf in row and (row.get(rf) or '').strip() == r_val:
                            r_match = True
                            break
                    if not r_match:
                        disamb_ok = False
                # Level check
                if disamb_ok and level is not None:
                    if (row.get('Level') or '').strip() != str(level).strip():
                        disamb_ok = False
                # Meaning check
                if disamb_ok and meaning is not None:
                    if (row.get('Meaning') or '').strip() != str(meaning).strip():
                        disamb_ok = False

                if disamb_ok:
                    prev_value = row.get(score_field, '0')
                    if correct:
                        try:
                            new_value = str(int(row.get(score_field, '0')) + 1)
                        except ValueError:
                            new_value = '1'
                    else:
                        new_value = '0'
                    row[score_field] = new_value
                    if return_change and change_record is None:
                        change_record = {
                            "csv_path": csv_path,
                            "row_index": row_index,
                            "score_field": score_field,
                            "prev_value": prev_value,
                            "new_value": new_value,
                        }
                    if not update_all:
                        updated_once = True
            updated_rows.append(row)

    with open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    os.replace(temp_path, csv_path)

    if return_change:
        return change_record


def lowest_score_items(csv_path, vocab_list, score_col):
    """
    Returns only those items whose Kanji has the global minimum score AND whose
    own tuple score equals that minimum (prevents higher-score duplicates of the
    same Kanji from being selected randomly).
    """
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        score_field = fieldnames[score_col] if score_col >= 0 else fieldnames[-1]
        scores = [(row["Kanji"], int(row[score_field]) if row.get(score_field) and row[score_field].isdigit() else 0)
                  for row in reader if row and row.get("Kanji")]
    if not scores:
        return []
    min_score = min(score for _, score in scores)
    # For quick lookup of min score per key
    key_min_scores = {}
    for k, s in scores:
        if k not in key_min_scores or s < key_min_scores[k]:
            key_min_scores[k] = s
    score_index = score_col  # tuple index aligns with csv order in loaders
    filtered = []
    for item in vocab_list:
        try:
            item_score = int(item[score_index])
        except (ValueError, IndexError):
            item_score = 0
        if item_score == min_score and key_min_scores.get(item[0], None) == min_score:
            filtered.append(item)
    return filtered
