"""Co-ordinate quiz selection and execution with undo support."""

from __future__ import annotations

import random
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from practicejapanese.core.utils import lowest_score_items, resolve_data_path, undo_score_change
from practicejapanese.module.quiz import audio_quiz, filling_quiz, kanji_quiz
from practicejapanese.module.quiz import vocab_quiz

QuizItem = Sequence[Any]
QuizPool = Sequence[QuizItem]
QuizFetch = Callable[[], QuizPool]
QuizAsk = Callable[..., Optional[Dict[str, Any]]]
UndoEntry = Dict[str, Any]

VOCAB_FILE = resolve_data_path("Vocab.csv")
KANJI_FILE = resolve_data_path("Kanji.csv")

def _make_lowest_score_fetcher(
    loader: Callable[[str], QuizPool], csv_path: str, score_col: int
) -> QuizFetch:
    """Return a callable that loads items and filters by lowest score."""

    def fetch() -> QuizPool:
        items = loader(csv_path)
        return lowest_score_items(csv_path, items, score_col=score_col)

    return fetch


def _build_quizzes(
    load_vocab: Callable[[str], QuizPool], load_kanji: Callable[[str], QuizPool]
) -> List[Tuple[str, QuizFetch, QuizAsk]]:
    """Return the configured quiz roster pairing loaders to ask functions."""

    fill_fetcher = _make_lowest_score_fetcher(load_vocab, str(VOCAB_FILE), 4)
    return [
        ("Vocab Quiz", _make_lowest_score_fetcher(load_vocab, str(VOCAB_FILE), 3), vocab_quiz.ask_question),
        ("Kanji Quiz", _make_lowest_score_fetcher(load_kanji, str(KANJI_FILE), 3), kanji_quiz.ask_question),
        ("Kanji Fill-in Quiz", fill_fetcher, filling_quiz.ask_question),
        ("Audio Quiz", fill_fetcher, audio_quiz.ask_question),
    ]


def random_quiz() -> None:
    """Run randomised quizzes until the user exits."""

    from practicejapanese.module.vocab import load_vocab
    from practicejapanese.module.kanji import load_kanji

    quizzes = _build_quizzes(load_vocab, load_kanji)
    history: List[UndoEntry] = []
    pending_stack: List[Tuple[QuizAsk, str, Any]] = []

    try:
        while True:
            if pending_stack:
                ask_fn, name, item_override = pending_stack.pop()
                question_pool: QuizPool = [item_override]
                print(f"Re-asking: {name}")
            else:
                name, fetch_fn, ask_fn = random.choice(quizzes)
                question_pool = fetch_fn()
                item_override = None
                if not question_pool:
                    print(f"No questions available for {name}.")
                    continue
                print(f"Selected: {name}")

            result = ask_fn(question_pool, item_override=item_override)
            if not result:
                continue
            current_item = result.get("item") or item_override

            if result.get("undo_requested"):
                if current_item is not None:
                    pending_stack.append((ask_fn, name, current_item))
                if not history:
                    print("Nothing to undo.")
                    continue
                undone_entry = history.pop()
                undo_score_change(undone_entry.get("change"))
                print(f"Previous answer from {undone_entry['name']} undone. Re-asking it now.")
                pending_stack.append(
                    (
                        undone_entry["ask_fn"],
                        undone_entry["name"],
                        undone_entry["item"],
                    )
                )
                continue

            if current_item is None:
                continue

            history.append(
                {
                    "ask_fn": ask_fn,
                    "name": name,
                    "item": current_item,
                    "change": result.get("change"),
                }
            )
            print()
    except KeyboardInterrupt:
        print("\nQuiz interrupted. Goodbye!")
