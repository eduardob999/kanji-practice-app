import os
import random
from practicejapanese.quizzes import vocab_quiz, kanji_quiz, filling_quiz

def random_quiz():
    from practicejapanese.core.vocab import load_vocab
    from practicejapanese.core.kanji import load_kanji

    vocab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/N5Vocab.csv"))
    kanji_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/N5Kanji.csv"))

    vocab_list = load_vocab(vocab_path)
    kanji_list = load_kanji(kanji_path)

    from practicejapanese.core.utils import lowest_score_items
    quizzes = [
        ("Vocab Quiz", lambda: vocab_quiz.ask_question(vocab_list)),
        ("Kanji Quiz", lambda: kanji_quiz.ask_question(kanji_list)),
        ("Kanji Fill-in Quiz", lambda: filling_quiz.ask_question(lowest_score_items(vocab_path, vocab_list, score_col=4)))
    ]
    import threading
    import queue
    def preload_question(q):
        while True:
            selected_name, selected_quiz = random.choice(quizzes)
            q.put((selected_name, selected_quiz))

    q = queue.Queue(maxsize=1)
    loader_thread = threading.Thread(target=preload_question, args=(q,), daemon=True)
    loader_thread.start()
    try:
        while True:
            selected_name, selected_quiz = q.get()  # Wait for next question to be ready
            print(f"Selected: {selected_name}")
            selected_quiz()
            print()  # Add empty line after each question
    except KeyboardInterrupt:
        print("\nQuiz interrupted. Goodbye!")
