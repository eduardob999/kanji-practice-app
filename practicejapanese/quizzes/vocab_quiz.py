from practicejapanese.core.vocab import load_vocab
from practicejapanese.core.utils import quiz_loop
import random
import os

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "N5Vocab.csv"))

def ask_question(vocab_list):
    item = random.choice(vocab_list)
    print()  # Add empty line before the question
    correct = False
    if random.choice([True, False]):
        print(f"Reading: {item[1]}")
        print(f"Meaning: {item[2]}")
        answer = input("What is the Kanji? ")
        correct = (answer == item[0])
        if correct:
            print("Correct!")
        else:
            print(f"Incorrect. The correct Kanji is: {item[0]}")
    else:
        print(f"Kanji: {item[0]}")
        print(f"Meaning: {item[2]}")
        answer = input("What is the Reading? ")
        correct = (answer == item[1])
        if correct:
            print("Correct!")
        else:
            print(f"Incorrect. The correct Reading is: {item[1]}")
    update_score(CSV_PATH, item[0], correct)
    print()  # Add empty line after the question

def run():
    vocab_list = load_vocab(CSV_PATH)
    # Load vocab quiz scores (column 4)
    import csv
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.reader(f)
        scores = [(row[0], int(row[3]) if len(row) > 3 and row[3].isdigit() else 0) for row in reader if row and row[0]]
    if not scores:
        print("No vocab found.")
        return
    min_score = min(score for _, score in scores)
    lowest_vocab = [item for item in vocab_list if item[0] in [k for k, s in scores if s == min_score]]
    quiz_loop(ask_question, lowest_vocab)

# --- Score update helper ---
import csv
def update_score(csv_path, key, correct):
    temp_path = csv_path + '.temp'
    updated_rows = []
    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row in reader:
            if row and row[0] == key:
                # Update vocab quiz score (column 4, index 3)
                if correct:
                    try:
                        row[3] = str(int(row[3]) + 1)
                    except ValueError:
                        row[3] = '1'
                else:
                    row[3] = '0'
            updated_rows.append(row)
    with open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(updated_rows)
    os.replace(temp_path, csv_path)