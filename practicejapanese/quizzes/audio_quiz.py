import os
import random
import requests
from functools import lru_cache
from gtts import gTTS
import subprocess
import tempfile
import time
from practicejapanese.core.vocab import load_vocab
from practicejapanese.core.utils import quiz_loop, update_score, lowest_score_items, is_verbose

CSV_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "data", "Vocab.csv"))


def play_tts(sentence):
    try:
        tts = gTTS(text=sentence, lang='ja')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            # Only use mpv for audio playback
            try:
                subprocess.run(['mpv', '--really-quiet', fp.name], check=True)
            except Exception as e:
                print(f"[TTS Error] {e}")
            os.remove(fp.name)
    except Exception as e:
        print(f"[TTS Error] {e}")

def ask_question(vocab_list):
    """Audio quiz: print instructions and cues, only play sentences as audio."""
    word = random.choice(vocab_list)
    questions = generate_questions(word)
    if not questions:
        print()
        # Define variables before using them
        kanji = word[0]
        reading = word[1]
        meaning = word[2]
        level = word[-1] if len(word) > 5 else ""
        filling_score = word[4] if len(word) > 4 else ""
        if level:
            if is_verbose():
                print(f"[Level {level} | Score {filling_score}]")
            else:
                print(f"[Level {level}]")
        play_tts(f"問題の漢字は{kanji}")
        print(f"Meaning: {meaning}")
        play_tts(f"読み方は{reading}")
        play_tts(f"問題の漢字は{kanji}")
        user_input = input("Your answer (kanji): ").strip()
        correct = (user_input == kanji)
        if correct:
            print("Correct!")
        else:
            print(f"Wrong. Correct kanji: {kanji}")
        update_score(CSV_PATH, kanji, correct, score_col=4)
        print()
        return
    # Select two distinct questions for context
    if len(questions) >= 2:
        selected = random.sample(questions, 2)
    else:
        selected = [questions[0]]
    kanji = selected[0][1]
    print()  # Add empty line before the question
    level = word[-1] if len(word) > 5 else ""
    filling_score = word[4] if len(word) > 4 else ""
    if level:
        if is_verbose():
            print(f"[Level {level} | Score {filling_score}]")
        else:
            print(f"[Level {level}]")
    print("Replace the highlighted hiragana with the correct kanji:")
    print("(The sentences will be played as audio)")
    play_tts(f"問題の漢字は{kanji}")
    for idx, (sentence, answer) in enumerate(selected):
        play_tts(sentence)
    play_tts(f"問題の漢字は{kanji}")
    # Use the first question's answer for checking
    answer = selected[0][1]
    user_input = input("Your answer (kanji): ").strip()
    correct = (user_input == answer)
    if correct:
        print("Correct!")
    else:
        print(f"Wrong. Correct kanji: {answer}")
    # Score column is 'FillingScore' (index 4)
    update_score(CSV_PATH, answer, correct, score_col=4)
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
            questions.append((sentence, kanji))
    return questions


if __name__ == "__main__":
    print("Running Kanji Fill-in Quiz in DEV mode...")
    run()
