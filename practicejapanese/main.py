import sys
from practicejapanese import __version__ as VERSION
from practicejapanese.quizzes import audio_quiz, vocab_quiz, kanji_quiz
from practicejapanese.core.quiz_runner import random_quiz
from practicejapanese.core.dev_mode import run_dev_mode
from practicejapanese.core.utils import set_verbose

HELP_TEXT = f"""PracticeJapanese {VERSION}
Usage: pjapp [options]

Options:
    -v, --version        Show version and exit
    -h, --help           Show this help message and exit
    -dev                 Enter developer mode
    -verbose             Show extra info (Level and Score) in questions

If no options are given, an interactive menu is shown.
You can also combine -verbose with the menu (e.g. pjapp -verbose).
"""

def main():
    # Parse simple flags (order-insensitive, no args needed)
    args = sys.argv[1:]
    if args:
        # Handle help first
        if any(a in ("-h", "--help") for a in args):
            print(HELP_TEXT)
            return
        if any(a in ("-v", "--version") for a in args):
            print(f"PracticeJapanese version {VERSION}")
            return
        if "-dev" in args:
            run_dev_mode()
            return
        if "-verbose" in args:
            set_verbose(True)

    print("Select quiz type:")
    print("1. Random Quiz (random category each time)")
    print("2. Vocab Quiz")
    print("3. Kanji Quiz")
    print("4. Kanji Fill-in Quiz")
    print("5. Audio Quiz")
    print("6. Reset all scores")
    print("(Run 'pjapp -h' for command-line options)")
    try:
        choice = input("Enter number: ").strip()
        if choice == "1":
            random_quiz()
        elif choice == "2":
            vocab_quiz.run()
            print()  # Add empty line after each question
        elif choice == "3":
            kanji_quiz.run()
            print()  # Add empty line after each question
        elif choice == "4":
            from practicejapanese.quizzes import filling_quiz
            filling_quiz.run()
            print()  # Add empty line after each question
        elif choice == "5":
            audio_quiz.run()
            print()  # Add empty line after each question
        elif choice == "6":
            from practicejapanese.core.utils import reset_scores
            reset_scores()
        else:
            print("Invalid choice.")
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
    except EOFError:
        # Handle Ctrl+D (EOF) gracefully
        print("\nNo input received. Goodbye!")

if __name__ == "__main__":
    main()