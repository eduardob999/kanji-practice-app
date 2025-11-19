"""Audio-based quiz that uses TTS to drill vocabulary recall."""

from __future__ import annotations

import random
import subprocess
import tempfile
from pathlib import Path
from typing import List, MutableMapping, Optional, Sequence, Tuple

from gtts import gTTS

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
TTS_LANG = "ja"
_PLAYER_CMD = ("mpv", "--really-quiet")
Question = Tuple[str, str]


def _save_tts_audio(sentence: str) -> Optional[Path]:
    """Generate a temporary MP3 file for the provided sentence."""

    tmp_path: Optional[Path] = None
    try:
        tts = gTTS(text=sentence, lang=TTS_LANG)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_path = Path(tmp.name)
        tts.save(tmp_path.as_posix())
    except Exception as exc:  # pragma: no cover - gTTS/network dependent
        print(f"[TTS Error] {exc}")
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()
        return None
    return tmp_path


def play_tts(sentence: str) -> None:
    """Speak the sentence via gTTS and a command-line audio player."""

    audio_path = _save_tts_audio(sentence)
    if audio_path is None:
        return
    try:
        subprocess.run((*_PLAYER_CMD, audio_path.as_posix()), check=True)
    except subprocess.CalledProcessError as exc:
        print(f"[TTS Error] {exc}")
    finally:
        if audio_path.exists():
            audio_path.unlink()


def ask_question(
    vocab_list: Sequence[VocabRow],
    *,
    item_override: Optional[VocabRow] = None,
) -> Optional[MutableMapping[str, object]]:
    """Run a single audio-based vocab question."""

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
        play_tts(f"問題の言葉は{kanji}です")
        print(f"{blue_text('Meaning:', bold=True)} {meaning}")
        play_tts(f"読み方は{reading}")
        play_tts(f"問題の言葉は{kanji}です")
        user_input = input(
            "Your answer (kanji and/or okurigana): "
        ).strip()
        if is_undo_command(user_input):
            return {"undo_requested": True, "item": word}
        correct = user_input == kanji
        if correct:
            print(green_text("Correct!"))
        else:
            print(f'{blue_text("Incorrect")}. The correct Kanji is: {kanji}')
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
    print("Replace with kanji (+ okurigana):")
    print("(The sentences will be played as audio)")
    play_tts(f"問題の言葉は{kanji}です")
    for sentence, _ in selected:
        play_tts(sentence)
    play_tts(f"問題の言葉は{kanji}です")
    user_input = input(
        "Your answer (kanji and/or okurigana): "
    ).strip()
    if is_undo_command(user_input):
        return {"undo_requested": True, "item": word}
    correct = user_input == kanji
    if correct:
        print(green_text("Correct!"))
    else:
        print(f'{blue_text("Incorrect")}. The correct Kanji is: {kanji}')
    print(f"Meaning: {meaning}")
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
    """Launch the audio quiz loop, prefetching sentences when allowed."""

    start_sentence_prefetcher()

    def fetch_items() -> Sequence[VocabRow]:
        vocab_list = load_vocab(CSV_PATH)
        return lowest_score_items(CSV_PATH, vocab_list, score_col=4)

    run_quiz_with_undo(fetch_items, ask_question, "No vocab found.")


def generate_questions(vocab_item: VocabRow) -> List[Question]:
    """Return example sentences that include the kanji in context."""

    reading, kanji = vocab_item[1], vocab_item[0]
    sentences = get_or_fetch_sentences(reading, kanji, 5)
    return [(sentence, kanji) for sentence in sentences if kanji in sentence]


if __name__ == "__main__":
    print("Running Kanji Fill-in Quiz in DEV mode...")
    run()
