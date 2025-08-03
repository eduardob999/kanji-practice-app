import sys
from practicejapanese import __version__ as VERSION
from practicejapanese.quizzes import vocab_quiz, kanji_quiz, filling_quiz
import random

def random_quiz():
    quizzes = [
        ("Vocab Quiz", vocab_quiz.ask_question),
        ("Kanji Quiz", kanji_quiz.ask_question),
        ("Kanji Fill-in Quiz", filling_quiz.ask_question)
    ]
    try:
        while True:
            selected_name, selected_quiz = random.choice(quizzes)
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
        else:
            print("Invalid choice.")
    except KeyboardInterrupt:
        print("\nQuiz interrupted. Goodbye!")

if __name__ == "__main__":
    main()