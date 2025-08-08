import random
import os
import csv


def reset_scores():
    print("Resetting all scores to zero...")
    for csv_path in [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "N5Kanji.csv")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "N5Vocab.csv")),
    ]:
        temp_path = csv_path + '.temp'
        updated_rows = []
        with open(csv_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            for row in reader:
                if row:
                    if os.path.basename(csv_path) == "N5Vocab.csv":
                        # Reset both score columns
                        row['VocabScore'] = '0'
                        row['FillingScore'] = '0'
                    else:
                        # Only last column is score
                        row['Score'] = '0'
                updated_rows.append(row)
        with open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        os.replace(temp_path, csv_path)
    print("All scores reset to zero.")


def quiz_loop(quiz_func, data):
    try:
        while True:
            quiz_func(data)
    except KeyboardInterrupt:
        print("\nExiting quiz. Goodbye!")


# --- DRY helpers for quizzes ---


def update_score(csv_path, key, correct, score_col=-1):
    """
    Update the score for a given key in the specified column (score_col).
    If correct, increment; else, set to zero.
    """
    temp_path = csv_path + '.temp'
    updated_rows = []
    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        for row in reader:
            if row and row.get("Kanji") == key:
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
    Returns items from vocab_list whose key (row[0]) has the lowest score in score_col.
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
    lowest_keys = [k for k, s in scores if s == min_score]
    return [item for item in vocab_list if item[0] in lowest_keys]
