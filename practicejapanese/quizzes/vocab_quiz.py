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
    quiz_loop(ask_question, vocab_list)

# --- Score update helper ---
import csv
def update_score(csv_path, key, correct):
    temp_path = csv_path + '.temp'
    updated_rows = []
    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row in reader:
            if row and row[0] == key:
                if correct:
                    try:
                        row[-1] = str(int(row[-1]) + 1)
                    except ValueError:
                        row[-1] = '1'
                else:
                    row[-1] = '0'
            updated_rows.append(row)
    with open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(updated_rows)
    os.replace(temp_path, csv_path)