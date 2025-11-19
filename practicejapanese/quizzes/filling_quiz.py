import os
import random
import requests
from functools import lru_cache
from practicejapanese.core.vocab import load_vocab
from practicejapanese.core.utils import (
    is_verbose,
    is_undo_command,
    lowest_score_items,
    run_quiz_with_undo,
    update_score,
)

CSV_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "data", "Vocab.csv"))


def ask_question(vocab_list, *, item_override=None):
    """Ask the user to replace hiragana with the correct kanji."""
    word = item_override or random.choice(vocab_list)
    questions = generate_questions(word)
    if not questions:
        # Show hiragana and meaning if no fill-in questions can be generated
        reading = word[1]
        meaning = word[2]
        kanji = word[0]
        level = word[-1] if len(word) > 5 else ""
        filling_score = word[4] if len(word) > 4 else ""
        if level:
            if is_verbose():
                print(f"[Level {level} | Score {filling_score}]")
            else:
                print(f"[Level {level}]")
        print(f"Reading: {reading}")
        print(f"Meaning: {meaning}")
        user_input = input("Your answer (kanji and/or okurigana): ").strip()
        if is_undo_command(user_input):
            return {"undo_requested": True, "item": word}
        correct = (user_input == kanji)
        if correct:
            print("Correct!")
        else:
            print(f"Wrong. Correct kanji: {kanji}")
        change = update_score(
            CSV_PATH,
            kanji,
            correct,
            score_col=4,
            reading=reading,
            meaning=meaning,
            level=level,
            return_change=True,
        )
        print()
        return {"item": word, "change": change}
    # Select two distinct questions for context
    if len(questions) >= 2:
        selected = random.sample(questions, 2)
    else:
        selected = [questions[0]]
    level = word[-1] if len(word) > 5 else ""
    filling_score = word[4] if len(word) > 4 else ""
    if level:
        if is_verbose():
            print(f"[Level {level} | Score {filling_score}]")
        else:
            print(f"[Level {level}]")
    print("Replace the highlighted hiragana with the correct kanji:")
    for idx, (sentence, answer) in enumerate(selected):
        print(f"{sentence}")
    # Use the first question's answer for checking
    answer = selected[0][1]
    user_input = input("Your answer (kanji and/or okurigana): ").strip()
    if is_undo_command(user_input):
        return {"undo_requested": True, "item": word}
    correct = (user_input == answer)
    if correct:
        print("Correct!")
    else:
        print(f"Wrong. Correct kanji: {answer}")
    print(f"Meaning: {word[2]}")
    # Score column is 'FillingScore' (index 4)
    change = update_score(
        CSV_PATH,
        answer,
        correct,
        score_col=4,
        reading=word[1],
        meaning=word[2],
        level=level,
        return_change=True,
    )
    print()
    return {"item": word, "change": change}


def run():
    def fetch_items():
        vocab_list = load_vocab(CSV_PATH)
        return lowest_score_items(CSV_PATH, vocab_list, score_col=4)

    run_quiz_with_undo(fetch_items, ask_question, "No vocab found.")


@lru_cache(maxsize=128)
def cached_fetch_sentences(reading, kanji, limit=5):
    url = f"https://tatoeba.org/en/api_v0/search?from=jpn&query={reading}&limit={limit}"
    try:
        resp = requests.get(url)
        data = resp.json()
    except Exception:
        return tuple()
    sentences = []
    for item in data.get("results", []):
        text = item.get("text", "")
        if reading in text or kanji in text:
            sentences.append(text)
    return tuple(sentences)


def generate_questions(vocab_list):
    questions = []
    reading, kanji = vocab_list[1], vocab_list[0]
    sentences = cached_fetch_sentences(reading, kanji, 5)
    for sentence in sentences:
        if kanji in sentence:
            formatted = sentence.replace(kanji, f"[{reading}]")
            questions.append((formatted, kanji))
    return questions


if __name__ == "__main__":
    print("Running Kanji Fill-in Quiz in DEV mode...")
    run()