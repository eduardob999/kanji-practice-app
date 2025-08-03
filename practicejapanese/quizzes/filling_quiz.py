from practicejapanese.core.vocab import load_vocab
import random
import requests
import os

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "N5Vocab.csv"))

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
    for kanji, reading, _ in vocab_list:
        sentences = fetch_sentences(reading, kanji)
        for sentence in sentences:
            if kanji in sentence:
                # Replace kanji with hiragana reading, highlighted
                formatted = sentence.replace(kanji, f"[{reading}]")
                questions.append((formatted, kanji))
    return questions

def ask_question():
    vocab_list = load_vocab(CSV_PATH)
    # Try up to 100 times to get a question
    for _ in range(100):
        sample = random.sample(vocab_list, min(10, len(vocab_list)))
        questions = generate_questions(sample)
        if questions:
            sentence, answer = random.choice(questions)
            print("\n=== Kanji Fill-in Quiz ===")
            print("Replace the highlighted hiragana with the correct kanji:")
            print(sentence)
            user_input = input("Your answer (kanji): ").strip()
            if user_input == answer:
                print("Correct!")
            else:
                print(f"Wrong. Correct kanji: {answer}")
            print()
            return
    print("No fill-in questions generated. Skipping this round.\n")

def quiz(questions):
    ask_question()

def run():
    vocab_list = load_vocab(CSV_PATH)
    vocab_list = random.sample(vocab_list, min(10, len(vocab_list)))
    questions = generate_questions(vocab_list)
    if questions:
        quiz(questions)
    else:
        print("No questions generated. Check API or vocab data.")

if __name__ == "__main__":
    print("Running Kanji Fill-in Quiz in DEV mode...")
    run()