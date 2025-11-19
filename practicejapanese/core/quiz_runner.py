import os
import random
from practicejapanese.quizzes import audio_quiz, vocab_quiz, kanji_quiz, filling_quiz
from practicejapanese.core.utils import lowest_score_items, undo_score_change

def random_quiz():
    from practicejapanese.core.vocab import load_vocab
    from practicejapanese.core.kanji import load_kanji

    vocab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/Vocab.csv"))
    kanji_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/Kanji.csv"))
    def fetch_vocab_items():
        vocab_list = load_vocab(vocab_path)
        return lowest_score_items(vocab_path, vocab_list, score_col=3)

    def fetch_kanji_items():
        kanji_list = load_kanji(kanji_path)
        return lowest_score_items(kanji_path, kanji_list, score_col=3)

    def fetch_filling_items():
        vocab_list = load_vocab(vocab_path)
        return lowest_score_items(vocab_path, vocab_list, score_col=4)

    quizzes = [
        ("Vocab Quiz", fetch_vocab_items, vocab_quiz.ask_question),
        ("Kanji Quiz", fetch_kanji_items, kanji_quiz.ask_question),
        ("Kanji Fill-in Quiz", fetch_filling_items, filling_quiz.ask_question),
        ("Audio Quiz", fetch_filling_items, audio_quiz.ask_question),
    ]

    history = []
    pending_stack = []

    try:
        while True:
            if pending_stack:
                ask_fn, name, item_override = pending_stack.pop()
                question_pool = [item_override]
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
                pending_stack.append((undone_entry["ask_fn"], undone_entry["name"], undone_entry["item"]))
                continue

            if current_item is None:
                continue

            history.append({
                "ask_fn": ask_fn,
                "name": name,
                "item": current_item,
                "change": result.get("change"),
            })
            print()
    except KeyboardInterrupt:
        print("\nQuiz interrupted. Goodbye!")
