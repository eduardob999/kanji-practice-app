"""Command-line entry point for the PracticeJapanese application."""

from __future__ import annotations

import sys

from source.core.menu import run_application


def main() -> None:
    """Delegate to the core menu module."""

    run_application(sys.argv[1:])


if __name__ == "__main__":
    main()