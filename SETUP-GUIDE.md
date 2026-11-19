# Set up CDVEA on Windows

Run setup once. Afterwards, use Claude Code or Codex normally and describe the video edit you want. You do not need to open a launcher, activate Python or switch a model on and off.

The automatic installer supports Windows 10/11 on x64. Core FFmpeg tools also support other systems, but this release does not provide their automatic installer.

## 1. Install the prerequisites

You need Git, Python 3.10 or newer, and FFmpeg 6.1 or newer with FFprobe. If they are missing, open PowerShell and run:

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
winget install --id Gyan.FFmpeg -e
```

Close and reopen PowerShell, then check:

```powershell
git --version
python --version
ffmpeg -version
ffprobe -version
```

If your Python command is `py`, the PowerShell setup wrapper can use it. Fix the Python installation if neither command works.

Install your chosen host and complete its normal account sign-in:

- [Claude Code installation](https://code.claude.com/docs/en/setup)
- [Codex installation](https://developers.openai.com/codex/quickstart)

Use a current native CLI where possible. Check `claude --version` or `codex --version` in PowerShell. The CDVEA setup does not install these host apps or change their permission policy.

## 2. Clone the private repository

Sign in to GitHub using an account with access to this repository. Use Git Credential Manager or `gh auth login`. Keep tokens out of URLs and scripts.

```powershell
git clone https://github.com/chandandigital-cms/CDVEA.git
cd CDVEA
```

A Claude or OpenAI login does not provide GitHub repository access. Give another person access through GitHub if they need to clone this private code.

## 3. Run setup once

To configure every supported host CLI that setup can find:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

Or select a host:

```powershell
python setup.py --hosts claude
python setup.py --hosts codex
python setup.py --hosts both
```

Setup checks FFmpeg, finds or installs uv, downloads an isolated Python 3.12.15, creates a virtual environment and installs the pinned dependencies. It then downloads the multilingual small model from a fixed official Hugging Face revision, checks its SHA-256 fingerprint and verifies Bengali, Hindi and English support. Finally, it registers CDVEA in the selected host profiles.

The default runtime location is `%LOCALAPPDATA%\CDVEA`. Model weights are about 484 MB; Python and packages need extra space. The first download can take several minutes. After an interruption, rerun setup and keep its cache so the downloader can resume.

Use `--hosts none` for runtime setup without host registration. Use `--runtime-dir "D:\CDVEA-Runtime"` for another location. Setup records the custom location in the standard per-user runtime configuration. Restart the host apps after changing it.

Setup does not download a model during ordinary plugin activation. The one-time setup command performs downloads; the transcription tool subsequently uses local files.

## 4. Restart the host once

Close and reopen Claude Code or Codex and start a new chat. Look for **CDVEA by Chandan Digital** in the installed plugins.

Give a normal instruction with your media file path:

```text
Create Bengali subtitles for D:\Videos\interview.mp4 using CDVEA.
```

```text
Reduce the fan noise and make the voice clearer. Keep the original video.
```

```text
Make a 30-second vertical Short from this footage, with our supplied logo.
```

The host selects a relevant skill and calls its tools. The speech model loads only for a transcription job. Its process exits after the job. The host may still ask for file access or tool permission under its existing settings.

## 5. Verify the setup

Read-only configuration check:

```powershell
python setup.py --check
```

Check tools through the configured runtime:

```powershell
python cdvea/run.py doctor
```

Run local integration tests:

```powershell
python cdvea/test_cdvea.py
```

The tests generate short synthetic media. They need FFmpeg and FFprobe, but do not download a model or call a hosted AI service.

For direct transcription during troubleshooting:

```powershell
python cdvea/run.py transcribe "D:\Videos\interview.mp4" --language bn
```

Use `hi` for Hindi, `en` for English, or omit language for automatic detection. A new folder beside the input receives `transcript.srt` and `transcript.json`. The source stays intact. Check names, prices, phone numbers and unclear speech before using captions in a finished video.

## 6. Fix common problems

| Problem | Action |
| --- | --- |
| Host CLI missing | Install Claude Code or Codex, reopen PowerShell and rerun setup. |
| Python missing | Install Python and check its PATH setting. |
| FFmpeg or FFprobe missing | Install FFmpeg, reopen PowerShell and rerun setup. |
| Plugin absent from an old chat | Fully restart the host and start a new chat. |
| Download interrupted | Rerun setup; retain the runtime cache. |
| Runtime or model missing | Rerun setup. Keep the runtime folder in place during use. |
| File or tool permission request | Review it in the host’s normal permission controls. |

Keep `requirements-local.lock.txt` unless you deliberately test an upgrade. NumPy 2.2.6 and PyAV 16.0.1 are pinned because newer versions caused errors on the development device.

## 7. Understand local and online work

Initial setup needs internet for Python, packages and the model. After setup, the configured speech tool uses local files in offline mode and does not upload your audio. Claude Code and Codex still use their own online AI services.

HyperFrames, Remotion, Blender, scene detection and hosted media generation have separate optional dependencies. This installer sets up the core and local speech runtime. [CAPABILITIES.md](CAPABILITIES.md) describes the other routes.

## 8. Update the plugin

From the source checkout:

```powershell
git pull --ff-only
python setup.py
```

Restart the host after a plugin version update. Runtime files and models remain outside the Git checkout. Setup reuses the environment and checks the existing model before downloading it again.
