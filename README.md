# App for practicing Japanese

## Setup

### Linux

1. Install Python 3 and pip.
2. Install mpv for audio playback:

```bash
sudo apt-get install mpv
```
   or in Termux
```bash
pkg install mpv
```


3. Install the app via pip

4. For PDF quiz functionality:
   - Install PyPDF2:
     ```bash
     pip install PyPDF2
     ```
   - For opening PDFs:
     - On Linux, install a PDF viewer (e.g., xpdf, evince) and desktop-file-utils:
       ```bash
       sudo apt-get install xpdf desktop-file-utils
       ```
     - On Termux, install a PDF viewer app and use termux-open.

## Features

- Practice Japanese quizzes: vocab, kanji, audio, fill-in, and PDF-based quizzes.
- PDF Quiz: Extracts text from a selected page range of a PDF and uses it as quiz content. Accessible from the main menu.


## Known issues:

N/A

## Testing solution:

N/A