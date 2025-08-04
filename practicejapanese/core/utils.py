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
            reader = csv.reader(infile)
            for row in reader:
                if row:
                    if os.path.basename(csv_path) == "N5Vocab.csv":
                        # Last two columns are scores
                        if len(row) >= 2:
                            row[-1] = '0'
                            row[-2] = '0'
                    else:
                        # Only last column is score
                        row[-1] = '0'
                updated_rows.append(row)
        with open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(updated_rows)
        os.replace(temp_path, csv_path)
    print("All scores reset to zero.")
import random

def quiz_loop(quiz_func, data):
    try:
        while True:
            quiz_func(data)
    except KeyboardInterrupt:
        print("\nExiting quiz. Goodbye!")

# --- DRY helpers for quizzes ---
import csv
def update_score(csv_path, key, correct, score_col=-1):
    """
    Update the score for a given key in the specified column (score_col).
    If correct, increment; else, set to zero.
    """
    temp_path = csv_path + '.temp'
    updated_rows = []
    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row in reader:
            if row and row[0] == key:
                if correct:
                    try:
                        row[score_col] = str(int(row[score_col]) + 1)
                    except (ValueError, IndexError):
                        row[score_col] = '1'
                else:
                    row[score_col] = '0'
            updated_rows.append(row)
    with open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(updated_rows)
    os.replace(temp_path, csv_path)

def lowest_score_items(csv_path, vocab_list, score_col):
    """
    Returns items from vocab_list whose key (row[0]) has the lowest score in score_col.
    """
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        scores = [(row[0], int(row[score_col]) if len(row) > score_col and row[score_col].isdigit() else 0)
                  for row in reader if row and row[0]]
    if not scores:
        return []
    min_score = min(score for _, score in scores)
    lowest_keys = [k for k, s in scores if s == min_score]
    return [item for item in vocab_list if item[0] in lowest_keys]