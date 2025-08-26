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

    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if not fieldnames:
            return  # nothing to do
        score_field = fieldnames[score_col] if score_col >= 0 else fieldnames[-1]
        has_id = 'ID' in fieldnames

        for row in reader:
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
                    if correct:
                        try:
                            row[score_field] = str(int(row.get(score_field, '0')) + 1)
                        except ValueError:
                            row[score_field] = '1'
                    else:
                        row[score_field] = '0'
                    if not update_all:
                        updated_once = True
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
