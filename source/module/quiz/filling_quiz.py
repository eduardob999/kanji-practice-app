"""Kanji fill-in quiz that replaces readings with blanks in sentences."""

from __future__ import annotations

import random
from typing import List, MutableMapping, Optional, Sequence, Tuple

from source.core.sentence_cache import (
    get_or_fetch_sentences,
    start_sentence_prefetcher,
)
from source.core.utils import (
    blue_text,
    green_text,
    is_undo_command,
    lowest_score_items,
    run_quiz_with_undo,
    update_score,
)
from source.module.vocab import VocabRow, load_vocab
from source.module.quiz.common import display_level_info, vocab_csv_path

CSV_PATH = vocab_csv_path()
Question = Tuple[str, str]


def ask_question(
    vocab_list: Sequence[VocabRow],
    *,
    item_override: Optional[VocabRow] = None,
) -> Optional[MutableMapping[str, object]]:
    """Ask the user to replace hiragana with the correct kanji."""

    if not vocab_list:
        return None
    word = item_override or random.choice(vocab_list)
    kanji, reading, meaning = word[0], word[1], word[2]
    filling_score = word[4] if len(word) > 4 else ""
    level = word[5] if len(word) > 5 else ""
    questions = generate_questions(word)

    print()
    display_level_info(level, filling_score)

    if not questions:
        print(f"{blue_text('Reading:', bold=True)} {reading}")
        print(f"{blue_text('Meaning:', bold=True)} {meaning}")
        user_input = input(
            green_text("Your answer (kanji and/or okurigana): ", bold=True)
        ).strip()
        if is_undo_command(user_input):
            return {"undo_requested": True, "item": word}
        correct = user_input == kanji
        if correct:
            print(green_text("Correct!"))
        else:
            print(blue_text(f"Wrong. Correct kanji: {kanji}"))
        change = update_score(
            CSV_PATH,
            kanji,
            correct,
            score_col=4,
            reading=reading,
            meaning=meaning,
            level=level,
            return_change=True,
        )
        print()
        return {"item": word, "change": change}

    sample_size = 2 if len(questions) >= 2 else 1
    selected = random.sample(questions, sample_size)
    print(blue_text("Replace with kanji (+ okurigana):", bold=True))
    for sentence, _ in selected:
        print(sentence)
    user_input = input(
        green_text("Your answer (kanji and/or okurigana): ", bold=True)
    ).strip()
    if is_undo_command(user_input):
        return {"undo_requested": True, "item": word}
    correct = user_input == kanji
    if correct:
        print(green_text("Correct!"))
    else:
        print(blue_text(f"Wrong. Correct kanji: {kanji}"))
    print(f"{blue_text('Meaning:', bold=True)} {meaning}")
    change = update_score(
        CSV_PATH,
        kanji,
        correct,
        score_col=4,
        reading=reading,
        meaning=meaning,
        level=level,
        return_change=True,
    )
    print()
    return {"item": word, "change": change}


def run() -> None:
    """Start the fill-in quiz loop using the undo-enabled runner."""

    start_sentence_prefetcher()

    def fetch_items() -> Sequence[VocabRow]:
        vocab_list = load_vocab(CSV_PATH)
        return lowest_score_items(CSV_PATH, vocab_list, score_col=4)

    run_quiz_with_undo(fetch_items, ask_question, "No vocab found.")


def generate_questions(vocab_item: VocabRow) -> List[Question]:
    """Produce sentences with highlighted reading placeholders."""

    reading, kanji = vocab_item[1], vocab_item[0]
    sentences = get_or_fetch_sentences(reading, kanji, 5)
    questions: List[Question] = []
    for sentence in sentences:
        if kanji not in sentence:
            continue
        formatted = sentence.replace(kanji, f"[{reading}]")
        questions.append((formatted, kanji))
    return questions


if __name__ == "__main__":
    print("Running Kanji Fill-in Quiz in DEV mode...")
    run()