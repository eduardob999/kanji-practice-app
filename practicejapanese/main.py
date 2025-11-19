"""Command-line entry point for the PracticeJapanese application."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Optional

from practicejapanese import __version__ as VERSION
from practicejapanese.core.dev_mode import run_dev_mode
from practicejapanese.core.quiz_runner import random_quiz
from practicejapanese.core.sentence_cache import start_sentence_prefetcher
from practicejapanese.core.utils import reset_scores, set_verbose
from practicejapanese.module.quiz import audio_quiz, kanji_quiz
from practicejapanese.module.quiz import vocab_quiz

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


@dataclass(frozen=True)
class MenuAction:
    label: str
    handler: Callable[[], None]
    post_hook: Optional[Callable[[], None]] = None


def _display_menu(actions: Dict[str, MenuAction]) -> None:
    print("Select quiz type:")
    for key, action in actions.items():
        print(f"{key}. {action.label}")
    print("(Run 'pjapp -h' for command-line options)")


def _handle_choice(choice: str, actions: Dict[str, MenuAction]) -> None:
    action = actions.get(choice)
    if not action:
        print("Invalid choice.")
        return
    action.handler()
    if action.post_hook:
        action.post_hook()


def _post_quiz_hook() -> None:
    print()


def _parse_flags(args: Iterable[str]) -> Optional[str]:
    flags = set(args)
    if any(flag in {"-h", "--help"} for flag in flags):
        print(HELP_TEXT)
        return "handled"
    if any(flag in {"-v", "--version"} for flag in flags):
        print(f"PracticeJapanese version {VERSION}")
        return "handled"
    if "-dev" in flags:
        run_dev_mode()
        return "handled"
    if "-verbose" in flags:
        set_verbose(True)
    return None


def main() -> None:
    start_sentence_prefetcher()

    args = sys.argv[1:]
    if args:
        handled = _parse_flags(args)
        if handled:
            return

    actions: Dict[str, MenuAction] = {
        "1": MenuAction("Random Quiz (random category each time)", random_quiz, _post_quiz_hook),
        "2": MenuAction("Vocab Quiz", vocab_quiz.run, _post_quiz_hook),
        "3": MenuAction("Kanji Quiz", kanji_quiz.run, _post_quiz_hook),
        "4": MenuAction("Kanji Fill-in Quiz", _run_filling_quiz, _post_quiz_hook),
        "5": MenuAction("Audio Quiz", audio_quiz.run, _post_quiz_hook),
        "6": MenuAction("Reset all scores", reset_scores),
    }

    _display_menu(actions)
    try:
        choice = input("Enter number: ").strip()
        _handle_choice(choice, actions)
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
    except EOFError:
        print("\nNo input received. Goodbye!")


def _run_filling_quiz() -> None:
    from practicejapanese.module.quiz import filling_quiz

    filling_quiz.run()


if __name__ == "__main__":
    main()