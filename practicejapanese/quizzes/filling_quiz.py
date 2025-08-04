from practicejapanese.core.vocab import load_vocab
import random
import requests
import os
from practicejapanese.core.utils import quiz_loop
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

def ask_question(vocab_list):
    sample = random.sample(vocab_list, min(10, len(vocab_list)))
    questions = generate_questions(sample)
    if questions:
        sentence, answer = random.choice(questions)
        print("\n=== Kanji Fill-in Quiz ===")
        print("Replace the highlighted hiragana with the correct kanji:")
        print(sentence)
        user_input = input("Your answer (kanji): ").strip()
        correct = (user_input == answer)
        if correct:
            print("Correct!")
        else:
            print(f"Wrong. Correct kanji: {answer}")
        update_score(CSV_PATH, answer, correct)
        print()
    else:
        print("No fill-in questions generated. Check API or vocab data.")

def run():
    vocab_list = load_vocab(CSV_PATH)
    # Load filling quiz scores (column 5)
    import csv
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.reader(f)
        scores = [(row[0], int(row[4]) if len(row) > 4 and row[4].isdigit() else 0) for row in reader if row and row[0]]
    if not scores:
        print("No vocab found.")
        return
    min_score = min(score for _, score in scores)
    lowest_vocab = [item for item in vocab_list if item[0] in [k for k, s in scores if s == min_score]]
    quiz_loop(ask_question, lowest_vocab)

import csv
def update_score(csv_path, key, correct):
    temp_path = csv_path + '.temp'
    updated_rows = []
    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row in reader:
            if row and row[0] == key:
                # Update filling quiz score (column 5, index 4)
                if correct:
                    try:
                        row[4] = str(int(row[4]) + 1)
                    except ValueError:
                        row[4] = '1'
                else:
                    row[4] = '0'
            updated_rows.append(row)
    with open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(updated_rows)
    os.replace(temp_path, csv_path)

if __name__ == "__main__":
    print("Running Kanji Fill-in Quiz in DEV mode...")
    run()