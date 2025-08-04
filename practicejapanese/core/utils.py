import random
import os
import csv


def reset_scores():
    print("[reset_scores] Starting score reset for all CSV files...")
    csv_files = [
        os.path.abspath(os.path.join(os.path.dirname(
            __file__), "..", "data", "N5Kanji.csv")),
        os.path.abspath(os.path.join(os.path.dirname(
            __file__), "..", "data", "N5Vocab.csv")),
    ]
    for csv_path in csv_files:
        print(f"[reset_scores] Processing file: {csv_path}")
        temp_path = csv_path + '.temp'
        updated_rows = []
        with open(csv_path, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            for row_num, row in enumerate(reader):
                print(f"[reset_scores] Row {row_num}: {row}")
                if row:
                    if os.path.basename(csv_path) == "N5Vocab.csv":
                        # Last two columns are scores
                        if len(row) >= 2:
                            print(
                                f"[reset_scores] Resetting last two columns for vocab row: {row[-2:]}")
                            row[-1] = '0'
                            row[-2] = '0'
                    else:
                        # Only last column is score
                        print(
                            f"[reset_scores] Resetting last column for kanji row: {row[-1] if row else None}")
                        row[-1] = '0'
                updated_rows.append(row)
        print(f"[reset_scores] Writing updated rows to temp file: {temp_path}")
        with open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(updated_rows)
        print(f"[reset_scores] Replacing original file with temp file.")
        os.replace(temp_path, csv_path)
    print("[reset_scores] All scores reset to zero.")


def quiz_loop(quiz_func, data):
    print("[quiz_loop] Starting quiz loop...")
    try:
        while True:
            print("[quiz_loop] Calling quiz function...")
            quiz_func(data)
    except KeyboardInterrupt:
        print("[quiz_loop] KeyboardInterrupt detected. Exiting quiz. Goodbye!")


# --- DRY helpers for quizzes ---


def update_score(csv_path, key, correct, score_col=-1):
    """
    Update the score for a given key in the specified column (score_col).
    If correct, increment; else, set to zero.
    Verbose: prints every step and error encountered.
    """
    print(
        f"[update_score] Updating score for key: {key} in file: {csv_path}, column: {score_col}, correct: {correct}")
    temp_path = csv_path + '.temp'
    updated_rows = []
    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row_num, row in enumerate(reader):
            print(f"[update_score] Row {row_num}: {row}")
            if row and row[0] == key:
                print(f"[update_score] Found matching key at row {row_num}")
                if correct:
                    try:
                        old_score = row[score_col]
                        row[score_col] = str(int(row[score_col]) + 1)
                        print(
                            f"[update_score] Incremented score from {old_score} to {row[score_col]}")
                    except (ValueError, IndexError) as e:
                        print(
                            f"[update_score] Error incrementing score: {e}. Setting score to 1.")
                        row[score_col] = '1'
                else:
                    print(f"[update_score] Answer incorrect. Resetting score to 0.")
                    row[score_col] = '0'
            updated_rows.append(row)
    print(f"[update_score] Writing updated rows to temp file: {temp_path}")
    with open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(updated_rows)
    print(f"[update_score] Replacing original file with temp file.")
    os.replace(temp_path, csv_path)


def lowest_score_items(csv_path, vocab_list, score_col):
    """
    Returns items from vocab_list whose key (row[0]) has the lowest score in score_col.
    Verbose: prints all scores and selection process.
    """
    print(
        f"[lowest_score_items] Reading scores from: {csv_path}, score column: {score_col}")
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        scores = []
        for row_num, row in enumerate(reader):
            if row and row[0]:
                try:
                    score = int(row[score_col]) if len(
                        row) > score_col and row[score_col].isdigit() else 0
                except Exception as e:
                    print(
                        f"[lowest_score_items] Error parsing score at row {row_num}: {e}")
                    score = 0
                print(
                    f"[lowest_score_items] Row {row_num}: key={row[0]}, score={score}")
                scores.append((row[0], score))
    if not scores:
        print("[lowest_score_items] No scores found. Returning empty list.")
        return []
    min_score = min(score for _, score in scores)
    print(f"[lowest_score_items] Minimum score found: {min_score}")
    lowest_keys = [k for k, s in scores if s == min_score]
    print(f"[lowest_score_items] Keys with lowest score: {lowest_keys}")
    selected_items = [item for item in vocab_list if item[0] in lowest_keys]
    print(
        f"[lowest_score_items] Returning {len(selected_items)} items with lowest score.")
    return selected_items
