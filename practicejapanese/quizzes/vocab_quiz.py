from practicejapanese.core.vocab import load_vocab
from practicejapanese.core.utils import quiz_loop, update_score, lowest_score_items, is_verbose
import random
import os
import re

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Vocab.csv"))

def _normalize_reading(s: str) -> str:
    # Normalize spaces (including full-width), trim
    return (s or "").replace("\u3000", " ").strip()


def _expand_readings(reading_field: str):
    # Split multiple possible readings on common delimiters
    parts = re.split(r"[;/、・,]", reading_field or "")
    # Remove bracketed hints like (する) if they appear; keep base
    cleaned = []
    for p in parts:
        p = _normalize_reading(p)
        if not p:
            continue
        # Drop surrounding parentheses if the entire token is parenthesized
        p = re.sub(r"^[\(（]\s*(.+?)\s*[\)）]$", r"\1", p)
        cleaned.append(p)
    # Ensure unique values, preserve order
    seen = set()
    uniq = []
    for c in cleaned:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq


def ask_question(vocab_list):
    item = random.choice(vocab_list)
    print()  # Add empty line before the question
    # Always ask for the reading
    level = item[-1] if len(item) > 5 else ""
    # Vocab score index 3
    vocab_score = item[3] if len(item) > 3 else ""
    if level:
        if is_verbose():
            print(f"[Level {level} | Score {vocab_score}]")
        else:
            print(f"[Level {level}]")
    print(f"Kanji: {item[0]}")
    print(f"Meaning: {item[2]}")
    answer = _normalize_reading(input("What is the Reading? "))
    valid_readings = _expand_readings(item[1])
    correct = answer in valid_readings
    if correct:
        print("Correct!")
    else:
        # Show canonical reading(s)
        show = item[1]
        print(f"Incorrect. The correct Reading is: {show}")
    # Score column is 'VocabScore' (index 3)
    update_score(CSV_PATH, item[0], correct, score_col=3, reading=item[1], level=level)
    print()  # Add empty line after the question

def run():
    def dynamic_quiz_loop():
        try:
            while True:
                vocab_list = load_vocab(CSV_PATH)
                lowest_vocab = lowest_score_items(CSV_PATH, vocab_list, score_col=3)
                if not lowest_vocab:
                    print("No vocab found.")
                    return
                ask_question(lowest_vocab)
        except KeyboardInterrupt:
            print("\nExiting quiz. Goodbye!")
    dynamic_quiz_loop()