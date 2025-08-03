import csv
import random
import requests

CSV_PATH = "data/N5Vocab.csv"

def load_vocab_kanji(path):
    vocab_list = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            kanji = row[0].strip()
            reading = row[1].strip()
            # Only include entries with a Kanji word and a reading
            if kanji and reading:
                vocab_list.append((kanji, reading))
    return vocab_list

def fetch_sentences(reading, kanji, limit=5):
    url = f"https://tatoeba.org/en/api_v0/search?from=jpn&query={reading}&limit={limit}"
    try:
        resp = requests.get(url)
        data = resp.json()
    except Exception:
        return []
    sentences = []
    for item in data.get("results", []):
        text = item.get("text", "")
        if reading in text or kanji in text:
            sentences.append(text)
    return sentences

def generate_questions(vocab_list):
    questions = []
    for kanji, reading in vocab_list:
        sentences = fetch_sentences(reading, kanji)
        for sentence in sentences:
            # Highlight the reading in the sentence
            if reading in sentence:
                formatted = sentence.replace(reading, f"[{reading}]")
            elif kanji in sentence:
                formatted = sentence.replace(kanji, f"[{reading}]")
            else:
                formatted = sentence
            questions.append((formatted, kanji))
    return questions

def quiz(questions):
    print("=== Kanji Fill-in Quiz ===")
    score = 0
    random.shuffle(questions)

    for sentence, answer in questions:
        print("\nReplace the highlighted hiragana with the correct kanji:")
        print(sentence)
        user_input = input("Your answer (kanji): ").strip()
        if user_input == answer:
            print("Correct!")
            score += 1
        else:
            print(f"Wrong. Correct kanji: {answer}")

    print(f"\nYour score: {score}/{len(questions)}")

if __name__ == "__main__":
    vocab_list = load_vocab_kanji(CSV_PATH)
    # Limit to a few questions for speed
    vocab_list = random.sample(vocab_list, min(10, len(vocab_list)))
    questions = generate_questions(vocab_list)
    if questions:
        quiz(questions)
    else:
        print("No questions generated. Check API or vocab data.")