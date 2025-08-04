import os
import random
import requests
from functools import lru_cache
from practicejapanese.core.vocab import load_vocab
from practicejapanese.core.utils import quiz_loop, update_score, lowest_score_items

CSV_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "data", "N5Vocab.csv"))


def ask_question(vocab_list):
    """Ask the user to replace hiragana with the correct kanji."""
    word = random.choice(vocab_list)
    questions = generate_questions(word)
    if not questions:
        print("No fill-in questions generated. Check API or vocab data.")
        return
    sentence, answer = random.choice(questions)
    print("Replace the highlighted hiragana with the correct kanji:")
    print(sentence)
    user_input = input("Your answer (kanji): ").strip()
    correct = (user_input == answer)
    if correct:
        print("Correct!")
    else:
        print(f"Wrong. Correct kanji: {answer}")
    update_score(CSV_PATH, answer, correct, score_col=4)
    print()


def run():
    vocab_list = load_vocab(CSV_PATH)
    lowest_vocab = lowest_score_items(CSV_PATH, vocab_list, score_col=4)
    if not lowest_vocab:
        print("No vocab found.")
        return
    quiz_loop(ask_question, lowest_vocab)


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
