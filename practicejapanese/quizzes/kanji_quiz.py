from practicejapanese.core.kanji import load_kanji
from practicejapanese.core.utils import quiz_loop, update_score, lowest_score_items, is_verbose
import random
import os


CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Kanji.csv"))

def ask_question(kanji_list):
    item = random.choice(kanji_list)
    print()  # Add empty line before the question
    level = item[-1] if len(item) > 4 else ""
    score = item[3] if len(item) > 3 else ""
    if level:
        if is_verbose():
            print(f"[Level {level} | Score {score}]")
        else:
            print(f"[Level {level}]")
    print(f"Readings: {item[1]}")
    print(f"Meaning: {item[2]}")
    answer = input("What is the Kanji? ")
    correct = (answer == item[0])
    if correct:
        print("Correct!")
    else:
        print(f"Incorrect. The correct Kanji is: {item[0]}")
    # Score column is 'Score' (index 3)
    update_score(CSV_PATH, item[0], correct, score_col=3, reading=item[1], level=level)
    print()  # Add empty line after the question

def run():
    def dynamic_quiz_loop():
        try:
            while True:
                kanji_list = load_kanji(CSV_PATH)
                lowest_kanji = lowest_score_items(CSV_PATH, kanji_list, score_col=3)
                if not lowest_kanji:
                    print("No kanji found.")
                    return
                ask_question(lowest_kanji)
        except KeyboardInterrupt:
            print("\nExiting quiz. Goodbye!")
    dynamic_quiz_loop()

# --- Score update helper removed, now using core.utils ---