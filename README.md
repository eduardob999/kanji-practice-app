# App for practicing Japanese

## Setup

### Linux

1. Install Python 3 and pip.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install mpv for audio playback:
   ```bash
   sudo apt-get install mpv
   ```

### Termux (Android)

1. Install Python in Termux:
   ```bash
   pkg install python
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install termux-media-player:
   ```bash
   pkg install termux-api
   ```
   (You may need to install the Termux:API app from F-Droid for full functionality.)

The app will automatically use the correct audio playback method for your environment.

## Known issues:

N/A

## Testing solution:

N/A