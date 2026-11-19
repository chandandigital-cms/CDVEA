# Install CDVEA

**Windows 10/11 x64:** follow [the setup guide](SETUP-GUIDE.md). Step 1 lists the software to install (Python and FFmpeg) with download links. Step 2 runs `setup.ps1`, which downloads the CDVEA runtime, its Python packages and the speech model.

**macOS and Linux (manual):** the core FFmpeg tools work, but there is no automatic installer.

1. Install Python 3.10+ and FFmpeg 6.1+ (for example `brew install python ffmpeg` or `sudo apt install python3 python3-venv ffmpeg`).
2. Create an environment and install the pinned packages:

   ```bash
   python3 -m venv ~/.local/share/cdvea/.venv
   ~/.local/share/cdvea/.venv/bin/pip install -r requirements-local.lock.txt
   ```

3. Download the model from [Systran/faster-whisper-small](https://huggingface.co/Systran/faster-whisper-small) into `~/.local/share/cdvea/models/faster-whisper-small`.
4. Write `~/.local/share/cdvea/runtime.json` with the paths:

   ```json
   {
     "python": "/home/you/.local/share/cdvea/.venv/bin/python",
     "model": "/home/you/.local/share/cdvea/models/faster-whisper-small",
     "FFMPEG_PATH": "/usr/bin/ffmpeg",
     "FFPROBE_PATH": "/usr/bin/ffprobe"
   }
   ```

5. Check with `python3 cdvea/run.py doctor`.
