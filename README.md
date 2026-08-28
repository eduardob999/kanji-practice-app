> ## This project has moved
>
> Kanjiba is now a web app: **<https://eduardob999.github.io/kanji-app/>**
> Source: **<https://github.com/eduardob999/kanji-app>**
>
> It does everything this CLI did — the same four quiz types, built from the
> same `Kanji.csv` and `Vocab.csv` — and the things a terminal could not:
>
> - **An adaptive schedule** instead of a score that counts right answers.
>   FSRS, with its weights fitted to how you actually forget, so an item comes
>   back just before you would have lost it rather than on a fixed rotation.
> - **Handwriting**, on a phone screen, for every one of the 2,211 kanji in
>   the corpus — which is what this CLI always assumed you had an IME for.
> - **Progress that syncs**, so a phone on a train and a laptop at a desk are
>   the same study history, and it works with no connection either way.
>
> Your scores come with you. `scripts/migrate-scores.mjs` over there reads this
> app's `scores.txt` and seeds the new schedule from it, spread over a fortnight
> so day one is not a wall.
>
> This repository stays up for anyone still running it, and `pip install pjapp`
> still works. It is no longer being developed.

---

# Kanjiba

Kanjiba is a lightweight, keyboard-driven CLI that helps you drill JLPT vocabulary, kanji, audio comprehension, and fill-in-the-blank exercises. Keep the app running in a terminal, answer questions in rapid fire, and let it track your progress locally. It is intended to be used along a handwritting japanese input system.

## Highlights
- **Focused study sessions** – switch between vocab, kanji, fill-in, audio, or a fully random mix.
- **Smart progress tracking** – CSV data files automatically store per-level progress, and a dashboard shows completion bars when the app starts.
- **Undo + score resets** – mis-key an answer? undo it, or reset entire datasets when you want a clean slate.
- **Offline friendly** – everything ships with the package; no network access required after installation.

## Requirements
- Python 3.9 or newer
- `mpv` (for audio quizzes)
- A terminal that supports ANSI colours for the best experience (falls back gracefully otherwise)

### Install `mpv`

```bash
sudo apt-get install mpv
# Termux
pkg install mpv
```

## Installation

Install the published PyPI package (recommended for everyday learners):

```bash
pip install --upgrade pjapp
```

## Quick Start

```bash
pjapp        # launches the interactive menu
pjapp -h     # prints all flags
```

When launched without flags, the app shows your current kanji/vocab progress and prompts you to pick a quiz type.

### Available Quizzes
- `Random Quiz` – each question pulls from a different category to simulate the unpredictability of JLPT exams.
- `Vocab Quiz` – word meaning + reading questions sourced from `practicejapanese/data/Vocab.csv`.
- `Kanji Quiz` – kanji meaning drills powered by `practicejapanese/data/Kanji.csv`.
- `Kanji Fill-in Quiz` – fill-in-the-blank prompts for on-yomi / kun-yomi practice.
- `Audio Quiz` – listen via `mpv` and type the matching prompt.
- `Reset all scores` – recalculates scores by JLPT level (5→0 … 1→4) for both CSV files.

### Helpful Flags
- `-h`, `--help` – usage info.
- `-v`, `--version` – print package version.
- `-verbose` – show extra metadata (level + score) while quizzing.
- `-dev` – launch the built-in developer playground (handy for experimenting with quiz logic).

## Where Data Lives
- Scores and logs default to `~/public/practicejapanese/` (see `core/utils.py:get_score_output_dir`).
- Configure alternate directories, sentence-cache behaviour, or storage locations by editing `config.json` at the project root. Example:

```json
{
   "storage_root": "~/Documents/pjapp",
   "sentence_cache_settings": {
      "enabled": true,
      "prefetch_interval_seconds": 20,
      "batch_fetch_size": 5
   }
}
```

Delete the file or remove keys to fall back to defaults.

## Developing Locally

```bash
git clone https://github.com/eduardob999/PracticeJapanese.git
cd PracticeJapanese
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m practicejapanese.main   # run the CLI
pytest                            # run the test suite
```

Useful scripts live in `scripts/` (e.g., CSV maintenance helpers) and `backup/` contains historical tooling that might inspire experiments.

## Troubleshooting
- **Audio doesn’t play** – confirm `mpv` is installed and in `PATH`. Run `mpv --version` to verify.
- **Colours missing** – ensure your terminal supports ANSI escape codes, or unset `NO_COLOR`.
- **Scores look wrong** – choose “Reset all scores” from the main menu, or delete the generated CSV copies under your storage root to regenerate them.
- **Sentence cache stalls** – tweak `sentence_cache_settings` in `config.json`, or delete `sentence_cache.json` to force a refresh.

## Contributing
Pull requests and feedback are welcome! If you plan a larger change, open an issue describing the desired quiz mode or UX tweak so we can align early. Remember to include tests (see `tests/`) whenever you touch quiz logic or scoring utilities.

Enjoy your study session! がんばって！
