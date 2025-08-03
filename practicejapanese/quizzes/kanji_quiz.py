from practicejapanese.core.kanji import load_kanji
from practicejapanese.core.utils import quiz_loop
import random
import os

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "N5Kanji.csv"))

def ask_question():
    kanji_list = load_kanji(CSV_PATH)
    item = random.choice(kanji_list)
    print()  # Add empty line before the question
    print(f"Readings: {item[1]}")
    print(f"Meaning: {item[2]}")
    answer = input("What is the Kanji? ")
    if answer == item[0]:
        print("Correct!")
    else:
        print(f"Incorrect. The correct Kanji is: {item[0]}")
    print()  # Add empty line after the question

def quiz(kanji_list):
    ask_question()

def run():
    kanji_list = load_kanji(CSV_PATH)
    quiz_loop(quiz, kanji_list)