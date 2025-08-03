from practicejapanese.core.vocab import load_vocab
from practicejapanese.core.utils import quiz_loop
import random
import os

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "N5Vocab.csv"))

def ask_question(vocab_list):
    item = random.choice(vocab_list)
    print()  # Add empty line before the question
    if random.choice([True, False]):
        print(f"Reading: {item[1]}")
        print(f"Meaning: {item[2]}")
        answer = input("What is the Kanji? ")
        if answer == item[0]:
            print("Correct!")
        else:
            print(f"Incorrect. The correct Kanji is: {item[0]}")
    else:
        print(f"Kanji: {item[0]}")
        print(f"Meaning: {item[2]}")
        answer = input("What is the Reading? ")
        if answer == item[1]:
            print("Correct!")
        else:
            print(f"Incorrect. The correct Reading is: {item[1]}")
    print()  # Add empty line after the question

def run():
    vocab_list = load_vocab(CSV_PATH)
    quiz_loop(ask_question, vocab_list)