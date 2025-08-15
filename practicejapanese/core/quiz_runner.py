import os
import random
from practicejapanese.quizzes import audio_quiz, vocab_quiz, kanji_quiz

def random_quiz():
    from practicejapanese.core.vocab import load_vocab
    from practicejapanese.core.kanji import load_kanji

    vocab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/Vocab.csv"))
    kanji_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/Kanji.csv"))

    from practicejapanese.core.utils import lowest_score_items
    from practicejapanese.quizzes import filling_quiz

    # Always reload latest scores before each question so displayed score is accurate.
    def next_vocab_question():
        vocab_list = load_vocab(vocab_path)
        lowest = lowest_score_items(vocab_path, vocab_list, score_col=3)
        if lowest:
            vocab_quiz.ask_question(lowest)

    def next_kanji_question():
        kanji_list = load_kanji(kanji_path)
        lowest = lowest_score_items(kanji_path, kanji_list, score_col=3)
        if lowest:
            kanji_quiz.ask_question(lowest)

    def next_fill_question():
        vocab_list = load_vocab(vocab_path)
        lowest = lowest_score_items(vocab_path, vocab_list, score_col=4)
        if lowest:
            filling_quiz.ask_question(lowest)

    def next_audio_question():
        vocab_list = load_vocab(vocab_path)
        lowest = lowest_score_items(vocab_path, vocab_list, score_col=4)
        if lowest:
            audio_quiz.ask_question(lowest)

    quizzes = [
        ("Vocab Quiz", next_vocab_question),
        ("Kanji Quiz", next_kanji_question),
        ("Kanji Fill-in Quiz", next_fill_question),
        ("Audio Quiz", next_audio_question),
    ]

    try:
        while True:
            name, func = random.choice(quizzes)
            print(f"Selected: {name}")
            func()
            print()
    except KeyboardInterrupt:
        print("\nQuiz interrupted. Goodbye!")
