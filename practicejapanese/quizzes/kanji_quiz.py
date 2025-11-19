from practicejapanese.core.kanji import load_kanji
from practicejapanese.core.utils import (
    is_verbose,
    is_undo_command,
    lowest_score_items,
    run_quiz_with_undo,
    update_score,
)
import random
import os


CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Kanji.csv"))

def ask_question(kanji_list, *, item_override=None):
    item = item_override or random.choice(kanji_list)
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
    if is_undo_command(answer):
        return {"undo_requested": True, "item": item}
    correct = (answer == item[0])
    if correct:
        print("Correct!")
    else:
        print(f"Incorrect. The correct Kanji is: {item[0]}")
    # Score column is 'Score' (index 3)
    change = update_score(
        CSV_PATH,
        item[0],
        correct,
        score_col=3,
        reading=item[1],
        meaning=item[2],
        level=level,
        return_change=True,
    )
    print()  # Add empty line after the question
    return {"item": item, "change": change}

def run():
    def fetch_items():
        kanji_list = load_kanji(CSV_PATH)
        return lowest_score_items(CSV_PATH, kanji_list, score_col=3)

    run_quiz_with_undo(fetch_items, ask_question, "No kanji found.")

# --- Score update helper removed, now using core.utils ---