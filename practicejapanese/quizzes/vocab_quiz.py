from practicejapanese.core.vocab import load_vocab
from practicejapanese.core.utils import quiz_loop, update_score, lowest_score_items
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
    update_score(CSV_PATH, item[0], correct, score_col=3)
    print()  # Add empty line after the question

def run():
    vocab_list = load_vocab(CSV_PATH)
    lowest_vocab = lowest_score_items(CSV_PATH, vocab_list, score_col=3)
    if not lowest_vocab:
        print("No vocab found.")
        return
    quiz_loop(ask_question, lowest_vocab)