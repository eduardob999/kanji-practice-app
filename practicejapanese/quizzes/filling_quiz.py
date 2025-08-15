import os
import random
import requests
from functools import lru_cache
from practicejapanese.core.vocab import load_vocab
from practicejapanese.core.utils import quiz_loop, update_score, lowest_score_items, is_verbose

CSV_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "data", "Vocab.csv"))


def ask_question(vocab_list):
    """Ask the user to replace hiragana with the correct kanji."""
    word = random.choice(vocab_list)
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
        user_input = input("Your answer (kanji): ").strip()
        correct = (user_input == kanji)
        if correct:
            print("Correct!")
        else:
            print(f"Wrong. Correct kanji: {kanji}")
        update_score(CSV_PATH, kanji, correct, score_col=4, reading=reading, level=level)
        print()
        return
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
    user_input = input("Your answer (kanji): ").strip()
    correct = (user_input == answer)
    if correct:
        print("Correct!")
    else:
        print(f"Wrong. Correct kanji: {answer}")
    # Score column is 'FillingScore' (index 4)
    update_score(CSV_PATH, answer, correct, score_col=4, reading=word[1], level=level)
    print()


def run():
    def dynamic_quiz_loop():
        try:
            while True:
                vocab_list = load_vocab(CSV_PATH)
                lowest_vocab = lowest_score_items(
                    CSV_PATH, vocab_list, score_col=4)
                if not lowest_vocab:
                    print("No vocab found.")
                    return
                ask_question(lowest_vocab)
        except KeyboardInterrupt:
            print("\nExiting quiz. Goodbye!")
    dynamic_quiz_loop()


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