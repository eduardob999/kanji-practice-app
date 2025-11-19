"""CLI menu orchestration for the PracticeJapanese application."""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional, Tuple

from source import __version__ as VERSION
from source.core.dev_mode import run_dev_mode
from source.core.quiz_runner import random_quiz
from source.core.sentence_cache import start_sentence_prefetcher
from source.core.utils import (
    blue_text,
    get_score_output_dir,
    green_text,
    resolve_data_path,
    reset_scores,
    set_verbose,
)
from source.module.quiz import audio_quiz, kanji_quiz, vocab_quiz

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


LOG_FILE: Optional[Path] = None
_LOGGING_CONFIGURED = False
logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    """Ensure errors are persisted to ``error.log`` for troubleshooting."""

    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    log_dir = get_score_output_dir()
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / "error.log"
    log_path.touch(exist_ok=True)

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(logging.ERROR)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    if root_logger.level > logging.WARNING:
        root_logger.setLevel(logging.WARNING)

    global LOG_FILE
    LOG_FILE = log_path

    _LOGGING_CONFIGURED = True


def _safe_int(value: object, default: int = 0) -> int:
    """Convert ``value`` to ``int`` when possible, otherwise return ``default``."""

    try:
        text = str(value).strip()
    except Exception:
        return default
    if not text:
        return default
    try:
        return int(text)
    except (TypeError, ValueError):
        return default


def _compute_level_progress(
    csv_path: Path, score_getter: Callable[[Dict[str, str]], int]
) -> Dict[int, Tuple[int, int]]:
    """Return completed/total counts per JLPT level for ``csv_path``."""

    totals: Dict[int, int] = {level: 0 for level in range(1, 6)}
    completed: Dict[int, int] = {level: 0 for level in range(1, 6)}

    try:
        with csv_path.open("r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if not row:
                    continue
                level = _safe_int(row.get("Level"), default=0)
                if level not in totals:
                    continue
                totals[level] += 1
                score_value = score_getter(row)
                threshold = 6 - level
                if score_value >= threshold:
                    completed[level] += 1
    except (OSError, csv.Error):
        return {level: (0, 0) for level in range(1, 6)}

    return {level: (completed[level], totals[level]) for level in totals}


def _progress_bar(fraction: float, width: int = 24) -> str:
    """Render a simple ASCII progress bar for ``fraction`` in ``[0, 1]``."""

    fraction = max(0.0, min(1.0, fraction))
    filled = min(width, max(0, int(round(fraction * width))))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def _render_progress_section(title: str, progress: Dict[int, Tuple[int, int]]) -> None:
    """Print a labelled block of JLPT progress bars."""

    print(blue_text(title, bold=True))
    for level in range(5, 0, -1):
        done, total = progress.get(level, (0, 0))
        fraction = (done / total) if total else 0.0
        raw_label = f"N{level}"
        label = blue_text(f"{raw_label:<3}", bold=True)
        bar = green_text(_progress_bar(fraction))
        percentage = fraction * 100.0
        pct = green_text(f"{percentage:6.2f}%")
        print(f"  {label} {bar} {pct} ({done}/{total})")
    print()


def _show_title_screen() -> None:
    """Display the application banner and current kanji/vocabulary progress."""

    width = 50
    separator = blue_text("=" * width)
    print(separator)
    print(blue_text("PracticeJapanese".center(width), bold=True))
    print(green_text(f"Version {VERSION}".center(width)))
    print(green_text("A command-line Japanese learning application".center(width)))
    print("by eduardob999 (github) ©2025".center(width))
    print("Press Ctrl+C at any time to exit safely.".center(width))
    print(separator)

    kanji_progress = _compute_level_progress(
        resolve_data_path("Kanji.csv"),
        lambda row: _safe_int(row.get("Score")),
    )

    def _vocab_score(row: Dict[str, str]) -> int:
        scores = [_safe_int(row.get(field)) for field in ("VocabScore", "FillingScore")]
        return max(scores) if scores else 0

    vocab_progress = _compute_level_progress(resolve_data_path("Vocab.csv"), _vocab_score)

    _render_progress_section("Kanji Progress", kanji_progress)
    _render_progress_section("Vocabulary Progress", vocab_progress)


def _display_menu(actions: Dict[str, MenuAction]) -> None:
    print(blue_text("Select quiz type:", bold=True))
    for key, action in actions.items():
        key_display = green_text(key, bold=True)
        print(f"{key_display}. {action.label}")
    print(green_text("(Run 'pjapp -h' for command-line options)"))


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


def _run_filling_quiz() -> None:
    from source.module.quiz import filling_quiz

    filling_quiz.run()


def run_application(args: Iterable[str]) -> None:
    """Entrypoint for the CLI menu flow."""

    _configure_logging()

    try:
        start_sentence_prefetcher()

        args = list(args)
        if args:
            handled = _parse_flags(args)
            if handled:
                return

        _show_title_screen()

        actions: Dict[str, MenuAction] = {
            "1": MenuAction(
                "Random Quiz (random category each time)", random_quiz, _post_quiz_hook
            ),
            "2": MenuAction("Vocab Quiz", vocab_quiz.run, _post_quiz_hook),
            "3": MenuAction("Kanji Quiz", kanji_quiz.run, _post_quiz_hook),
            "4": MenuAction("Kanji Fill-in Quiz", _run_filling_quiz, _post_quiz_hook),
            "5": MenuAction("Audio Quiz", audio_quiz.run, _post_quiz_hook),
            "6": MenuAction("Reset all scores", reset_scores),
        }

        _display_menu(actions)
        choice = input(green_text("Enter number: ", bold=True)).strip()
        _handle_choice(choice, actions)
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
    except EOFError:
        print("\nNo input received. Goodbye!")
    except Exception:
        logger.exception("Unhandled error during PracticeJapanese execution")
        destination = str(LOG_FILE) if LOG_FILE else "error.log"
        print(f"\nAn unexpected error occurred. See {destination} for details.")


__all__ = ["run_application", "HELP_TEXT"]
