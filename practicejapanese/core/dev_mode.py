import sys
import os
from practicejapanese import __version__ as VERSION

def run_dev_mode():
    print("Developer mode activated!")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Available quizzes: vocab_quiz, kanji_quiz, filling_quiz")
    print("Dev options:")
    print("1. Show all scores")
    print("2. Exit dev mode")
    dev_choice = input("Enter dev option: ").strip()
    if dev_choice == "1":
        from practicejapanese.core.vocab import load_vocab
        from practicejapanese.core.kanji import load_kanji
        vocab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/N5Vocab.csv"))
        kanji_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/N5Kanji.csv"))
        vocab_list = load_vocab(vocab_path)
        kanji_list = load_kanji(kanji_path)
        print("\nKanji Scores:")
        for entry in kanji_list:
            if isinstance(entry, tuple) and len(entry) >= 4:
                kanji = entry[0]
                score = entry[-1]
                print(f"{kanji}: {score}")
        print("\nAll scores displayed.")
        print("\nVocab Scores:")
        for entry in vocab_list:
            if isinstance(entry, tuple) and len(entry) >= 5:
                word = entry[0]
                vocab_score = entry[3]
                filling_score = entry[4]
                print(f"{word}: Vocab Quiz Score = {vocab_score}, Filling Quiz Score = {filling_score}")
    else:
        print("Exiting dev mode.")
