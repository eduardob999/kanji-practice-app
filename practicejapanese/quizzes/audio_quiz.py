import os
import random
import subprocess
import tempfile
from gtts import gTTS

from practicejapanese.core.vocab import load_vocab
from practicejapanese.core.utils import (
    is_verbose,
    is_undo_command,
    lowest_score_items,
    run_quiz_with_undo,
    update_score,
)
from practicejapanese.core.sentence_cache import (
    get_or_fetch_sentences,
    start_sentence_prefetcher,
)

CSV_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "data", "Vocab.csv"))


def play_tts(sentence):
    try:
        tts = gTTS(text=sentence, lang='ja')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            try:
                subprocess.run(['mpv', '--really-quiet', fp.name], check=True)
            except Exception as e:
                print(f"[TTS Error] {e}")
            os.remove(fp.name)
    except Exception as e:
        print(f"[TTS Error] {e}")


def ask_question(vocab_list, *, item_override=None):
    """Audio quiz: print instructions and cues, only play sentences as audio."""
    word = item_override or random.choice(vocab_list)
    questions = generate_questions(word)
    if not questions:
        print()
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
        play_tts(f"問題の言葉は{kanji}")
        print(f"Meaning: {meaning}")
        play_tts(f"読み方は{reading}")
        play_tts(f"問題の言葉は{kanji}")
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

    if len(questions) >= 2:
        selected = random.sample(questions, 2)
    else:
        selected = [questions[0]]
    kanji = selected[0][1]
    print()
    level = word[-1] if len(word) > 5 else ""
    filling_score = word[4] if len(word) > 4 else ""
    if level:
        if is_verbose():
            print(f"[Level {level} | Score {filling_score}]")
        else:
            print(f"[Level {level}]")
    print("Replace the highlighted hiragana with the correct kanji:")
    print("(The sentences will be played as audio)")
    play_tts(f"問題の言葉は{kanji}")
    for sentence, answer in selected:
        play_tts(sentence)
    play_tts(f"問題の言葉は{kanji}")
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
    start_sentence_prefetcher()

    def fetch_items():
        vocab_list = load_vocab(CSV_PATH)
        return lowest_score_items(
            CSV_PATH, vocab_list, score_col=4)

    run_quiz_with_undo(fetch_items, ask_question, "No vocab found.")


def generate_questions(vocab_list):
    questions = []
    reading, kanji = vocab_list[1], vocab_list[0]
    sentences = get_or_fetch_sentences(reading, kanji, 5)
    for sentence in sentences:
        if kanji in sentence:
            questions.append((sentence, kanji))
    return questions


if __name__ == "__main__":
    print("Running Kanji Fill-in Quiz in DEV mode...")
    run()
