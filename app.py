import random
import requests
import json

# Load JMdict data (assumed to be a dict: {reading: kanji})
def load_jmdict(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# Fetch sentences from Tatoeba containing the target reading
def fetch_sentences(reading, kanji, limit=5):
    url = f"https://tatoeba.org/en/api_v0/search?from=jpn&query={reading}&limit={limit}"
    resp = requests.get(url)
    data = resp.json()
    sentences = []
    for item in data.get("results", []):
        text = item.get("text", "")
        # Accept sentences containing either the reading or the kanji
        if reading in text or kanji in text:
            sentences.append(text)
    return sentences

# Generate quiz questions
def generate_questions(jmdict, readings):
    questions = []
    for reading in readings:
        kanji = jmdict.get(reading)
        if not kanji:
            continue
        sentences = fetch_sentences(reading, kanji)
        for sentence in sentences:
            # Highlight the reading or kanji in the sentence
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
    # Example readings to quiz
    readings = ["みず", "がっこう", "やま", "えいが"]
    # Load JMdict (provide path to your processed JMdict JSON)
    jmdict = load_jmdict("jmdict.json")
    questions = generate_questions(jmdict, readings)
    if questions:
        quiz(questions)
    else:
        print("No questions generated. Check JMdict and Tatoeba API.")