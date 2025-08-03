import sys
from practicejapanese import __version__ as VERSION
from practicejapanese.quizzes import vocab_quiz, kanji_quiz, filling_quiz
import random
import os

def random_quiz():
    from practicejapanese.core.vocab import load_vocab
    from practicejapanese.core.kanji import load_kanji

    vocab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "N5Vocab.csv"))
    kanji_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "N5Kanji.csv"))

    vocab_list = load_vocab(vocab_path)
    kanji_list = load_kanji(kanji_path)

    quizzes = [
        ("Vocab Quiz", lambda: vocab_quiz.ask_question(vocab_list)),
        ("Kanji Quiz", lambda: kanji_quiz.ask_question(kanji_list)),
        ("Kanji Fill-in Quiz", lambda: filling_quiz.ask_question(vocab_list))
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

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        print(f"PracticeJapanese version {VERSION}")
        return

    print("Select quiz type:")
    print("1. Random Quiz (random category each time)")
    print("2. Vocab Quiz")
    print("3. Kanji Quiz")
    print("4. Kanji Fill-in Quiz")
    print("5. Reset all scores to zero")
    choice = input("Enter number: ").strip()
    try:
        if choice == "1":
            random_quiz()
        elif choice == "2":
            vocab_quiz.run()
            print()  # Add empty line after each question
        elif choice == "3":
            kanji_quiz.run()
            print()  # Add empty line after each question
        elif choice == "4":
            filling_quiz.run()
            print()  # Add empty line after each question
        elif choice == "5":
            from practicejapanese.core.utils import reset_scores
            reset_scores()
        else:
            print("Invalid choice.")
    except KeyboardInterrupt:
        print("\nQuiz interrupted. Goodbye!")

if __name__ == "__main__":
    main()