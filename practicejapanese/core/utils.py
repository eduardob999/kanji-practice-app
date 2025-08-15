import random
import os
import csv

# --- Global config flags ---
VERBOSE = False

def set_verbose(flag: bool):
    global VERBOSE
    VERBOSE = bool(flag)

def is_verbose() -> bool:
    return VERBOSE


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


# --- DRY helpers for quizzes ---


def update_score(csv_path, key, correct, score_col=-1, reading=None, level=None):
    """Update the score for a given row.

    Parameters:
        csv_path (str): Path to CSV.
        key (str): Kanji (primary key).
        correct (bool): If True increment, else reset to 0.
        score_col (int): Index of score column to mutate.
        reading (str|None): Optional reading to disambiguate duplicates.
        level (str|int|None): Optional level to disambiguate duplicates.

    Behavior:
        If reading/level supplied, only the row whose Kanji matches AND whose
        reading (matches either 'Reading' or 'Readings' column) AND/OR level
        (if provided) matches will be updated. Other duplicate variants keep
        their scores, preventing unintended resets.
    """
    temp_path = csv_path + '.temp'
    updated_rows = []
    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        for row in reader:
            if row and row.get("Kanji") == key:
                do_update = True
                # Reading disambiguation
                if reading is not None:
                    r_match = False
                    for rf in ("Reading", "Readings"):
                        if rf in row and (row.get(rf) or '').strip() == str(reading).strip():
                            r_match = True
                            break
                    if not r_match:
                        do_update = False
                # Level disambiguation
                if level is not None:
                    lvl_val = (row.get('Level') or '').strip()
                    if lvl_val != str(level).strip():
                        do_update = False
                if do_update:
                    score_field = fieldnames[score_col] if score_col >= 0 else fieldnames[-1]
                    if correct:
                        try:
                            row[score_field] = str(int(row[score_field]) + 1)
                        except (ValueError, IndexError):
                            row[score_field] = '1'
                    else:
                        row[score_field] = '0'
            updated_rows.append(row)
    with open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    os.replace(temp_path, csv_path)


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
