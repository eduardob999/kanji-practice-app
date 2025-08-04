# Move ask_question above run
def ask_question(vocab_list):
    sample = random.sample(vocab_list, min(10, len(vocab_list)))
    questions = generate_questions(sample)
    if questions:
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
    else:
        print("No fill-in questions generated. Check API or vocab data.")
# Restore run() function above __main__ block
def run():
    vocab_list = load_vocab(CSV_PATH)
    lowest_vocab = lowest_score_items(CSV_PATH, vocab_list, score_col=4)
    if not lowest_vocab:
        print("No vocab found.")
        return
    quiz_loop(ask_question, lowest_vocab)
from practicejapanese.core.vocab import load_vocab
import random
import requests
import os
from practicejapanese.core.utils import quiz_loop, update_score, lowest_score_items
from functools import lru_cache

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "N5Vocab.csv"))

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
    import concurrent.futures
    questions = []
    # Prepare args for parallel fetch
    args = [(item[1], item[0], 5) for item in vocab_list]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda arg: cached_fetch_sentences(*arg), args))
    for item, sentences in zip(vocab_list, results):
        kanji = item[0]
        reading = item[1]
        for sentence in sentences:
            if kanji in sentence:
                formatted = sentence.replace(kanji, f"[{reading}]")
                questions.append((formatted, kanji))
    return questions

    sample = random.sample(vocab_list, min(10, len(vocab_list)))
    questions = generate_questions(sample)
    if questions:
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
    else:
        print("No fill-in questions generated. Check API or vocab data.")

    vocab_list = load_vocab(CSV_PATH)
    lowest_vocab = lowest_score_items(CSV_PATH, vocab_list, score_col=4)
    if not lowest_vocab:
        print("No vocab found.")
        return
    quiz_loop(ask_question, lowest_vocab)

# --- Score update helper removed, now using core.utils ---

# Place __main__ block at the end of the file

if __name__ == "__main__":
    print("Running Kanji Fill-in Quiz in DEV mode...")
    run()