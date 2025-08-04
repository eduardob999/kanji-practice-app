from practicejapanese.core.kanji import load_kanji
from practicejapanese.core.utils import quiz_loop, update_score, lowest_score_items
import random
import os


CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "N5Kanji.csv"))

def ask_question(kanji_list):
    item = random.choice(kanji_list)
    print()  # Add empty line before the question
    print(f"Readings: {item[1]}")
    print(f"Meaning: {item[2]}")
    answer = input("What is the Kanji? ")
    correct = (answer == item[0])
    if correct:
        print("Correct!")
    else:
        print(f"Incorrect. The correct Kanji is: {item[0]}")
    update_score(CSV_PATH, item[0], correct, score_col=3)
    print()  # Add empty line after the question

def run():
    kanji_list = load_kanji(CSV_PATH)
    lowest_kanji = lowest_score_items(CSV_PATH, kanji_list, score_col=3)
    if not lowest_kanji:
        print("No kanji found.")
        return
    quiz_loop(ask_question, lowest_kanji)

# --- Score update helper removed, now using core.utils ---