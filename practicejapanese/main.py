from practicejapanese.quizzes import vocab_quiz, kanji_quiz, filling_quiz
import random

def random_quiz():
    quizzes = [vocab_quiz.run, kanji_quiz.run, filling_quiz.run]
    selected_quiz = random.choice(quizzes)
    selected_quiz()

def main():
    print("Select quiz type:")
    print("1. Vocab Quiz")
    print("2. Kanji Quiz")
    print("3. Random Quiz (random category each time)")
    print("4. Kanji Fill-in Quiz")
    choice = input("Enter number: ").strip()
    try:
        if choice == "1":
            vocab_quiz.run()
            print()  # Add empty line after each question
        elif choice == "2":
            kanji_quiz.run()
            print()  # Add empty line after each question
        elif choice == "3":
            random_quiz()
        elif choice == "4":
            filling_quiz.run()
            print()  # Add empty line after each question
        else:
            print("Invalid choice.")
    except KeyboardInterrupt:
        print("\nQuiz interrupted. Goodbye!")

if __name__ == "__main__":
    main()