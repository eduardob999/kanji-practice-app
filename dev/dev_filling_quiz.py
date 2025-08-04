import os
import random
import requests
from functools import lru_cache
from practicejapanese.core.vocab import load_vocab
from practicejapanese.core.utils import quiz_loop, update_score, lowest_score_items

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "N5Vocab.csv"))


def ask_question(vocab_list):
    """
    Verbose: Ask the user to replace hiragana with the correct kanji.
    This function samples 10 vocab items, generates fill-in questions, and prompts the user for input.
    It prints detailed information about each step and the internal state.
    """
    print("[ask_question] Starting question round...")
    print(f"[ask_question] Received vocab_list with {len(vocab_list)} items.")
    sample = random.sample(vocab_list, 1)
    print(f"[ask_question] Sampled item: {sample}")
    questions = generate_questions(sample)
    print(f"[ask_question] Generated {len(questions)} questions.")
    if not questions:
        print("[ask_question] No fill-in questions generated. Check API or vocab data.")
        return
    sentence, answer = random.choice(questions)
    print(f"[ask_question] Selected question: {sentence} | Answer: {answer}")
    print("Replace the highlighted hiragana with the correct kanji:")
    print(sentence)
    user_input = input("Your answer (kanji): ").strip()
    print(f"[ask_question] User input: {user_input}")
    correct = (user_input == answer)
    print(f"[ask_question] Correct? {correct}")
    if correct:
        print("Correct!")
    else:
        print(f"Wrong. Correct kanji: {answer}")
    print(f"[ask_question] Updating score for answer '{answer}' with correct={correct}.")
    update_score(CSV_PATH, answer, correct, score_col=4)
    print("[ask_question] Score updated.")
    print()


def run():
    """
    Verbose: Run the Kanji Fill-in Quiz.
    Loads vocab, finds lowest scoring items, and starts the quiz loop.
    Prints detailed information about each step.
    """
    print("[run] Loading vocabulary from CSV_PATH:", CSV_PATH)
    vocab_list = load_vocab(CSV_PATH)
    print(f"[run] Loaded {len(vocab_list)} vocab items.")
    print("[run] Finding lowest score items...")
    lowest_vocab = lowest_score_items(CSV_PATH, vocab_list, score_col=4)
    print(f"[run] Found {len(lowest_vocab)} lowest score items.")
    if not lowest_vocab:
        print("[run] No vocab found.")
        return
    print("[run] Starting quiz loop...")
    quiz_loop(ask_question, lowest_vocab)
    print("[run] Quiz loop finished.")


@lru_cache(maxsize=128)
def cached_fetch_sentences(reading, kanji, limit=5):
    """
    Verbose: Fetch example sentences containing the reading or kanji from Tatoeba.
    Prints the API URL, response status, and results.
    """
    url = f"https://tatoeba.org/en/api_v0/search?from=jpn&query={reading}&limit={limit}"
    print(f"[cached_fetch_sentences] Fetching sentences for reading='{reading}', kanji='{kanji}', limit={limit}")
    print(f"[cached_fetch_sentences] API URL: {url}")
    try:
        resp = requests.get(url)
        print(f"[cached_fetch_sentences] Response status code: {resp.status_code}")
        data = resp.json()
        print(f"[cached_fetch_sentences] Response JSON: {data}")
    except Exception as e:
        print(f"[cached_fetch_sentences] Exception occurred: {e}")
        return tuple()
    sentences = []
    for item in data.get("results", []):
        text = item.get("text", "")
        print(f"[cached_fetch_sentences] Checking sentence: {text}")
        if reading in text or kanji in text:
            print(f"[cached_fetch_sentences] Sentence contains reading or kanji. Adding: {text}")
            sentences.append(text)
    print(f"[cached_fetch_sentences] Returning {len(sentences)} sentences.")
    return tuple(sentences)


def generate_questions(vocab_list):
    """
    Verbose: Generate fill-in-the-blank questions from vocab list using example sentences.
    Prints details about parallel fetching and question formatting.
    """
    print(f"[generate_questions] Generating questions for vocab_list of length {len(vocab_list)}.")
    questions = []
    for item in vocab_list:
        reading, kanji = item[1], item[0]
        print(f"[generate_questions] Fetching sentences for reading='{reading}', kanji='{kanji}'")
        sentences = cached_fetch_sentences(reading, kanji, 5)
        print(f"[generate_questions] Fetched {len(sentences)} sentences.")
        for sentence in sentences:
            print(f"[generate_questions] Checking sentence: {sentence}")
            if kanji in sentence:
                formatted = sentence.replace(kanji, f"[{reading}]")
                print(f"[generate_questions] Formatted question: {formatted}")
                questions.append((formatted, kanji))
    print(f"[generate_questions] Returning {len(questions)} questions.")
    return questions


if __name__ == "__main__":
    print("[main] Running Kanji Fill-in Quiz in DEV mode...")
    run()
