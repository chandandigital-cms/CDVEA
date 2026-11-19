# CDVEA install instructions for AI coding agents

These steps are for an AI agent (Claude Code, Codex, Cursor or similar) that a user has asked to install CDVEA on **Windows 10/11 x64**. Run the commands in PowerShell. Tell the user what each step does. If a step fails, show the error and stop; don't improvise workarounds.

**Ask the user before installing any system software (step 1) and before editing any app configuration (step 4).**

## 1. Check and install the required software

```powershell
python --version
ffmpeg -version
ffprobe -version
```

- Python must be 3.10 or newer. If it's missing or older, ask the user, then run `winget install --id Python.Python.3.12 -e`.
- FFmpeg must be 6.1 or newer, with FFprobe. If it's missing, ask the user, then run `winget install --id Gyan.FFmpeg -e`.
- If `winget` is unavailable, give the user the links instead: [python.org](https://www.python.org/downloads/windows/) (tick "Add python.exe to PATH") and [gyan.dev FFmpeg builds](https://www.gyan.dev/ffmpeg/builds/).

New installs don't reach the current shell's PATH. Start a new PowerShell process (or ask the user to restart the agent), then repeat the checks until all three commands work.

## 2. Download the plugin

```powershell
Invoke-WebRequest https://github.com/chandandigital-cms/CDVEA/releases/latest/download/CDVEA.zip -OutFile "$env:USERPROFILE\Downloads\CDVEA.zip"
Expand-Archive "$env:USERPROFILE\Downloads\CDVEA.zip" "$env:LOCALAPPDATA\CDVEA-Plugin" -Force
```

The plugin is now in `%LOCALAPPDATA%\CDVEA-Plugin\CDVEA`. Keep `Downloads\CDVEA.zip`: the Codex app needs it in step 4.

## 3. Run CDVEA setup

Choose `-Hosts` for the app you are running in:

| Agent | `-Hosts` value |
| --- | --- |
| Claude Code (CLI or desktop) | `claude` |
| Codex CLI | `codex` |
| Codex app, Cursor or any other agent | `none` |

```powershell
powershell -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\CDVEA-Plugin\CDVEA\setup.ps1" -Hosts <value>
```

Setup downloads CDVEA's own Python 3.12, its pinned packages (about 200 MB) and the Bengali/Hindi/English speech model (about 484 MB, SHA-256 checked) into `%LOCALAPPDATA%\CDVEA`. It can take 5–15 minutes, so use a long command timeout (at least 20 minutes) or run it in the background. Success ends with `"status": "ready"`. If the download is interrupted, run the same command again: it resumes.

## 4. Connect the plugin to the app

- **Claude Code / Codex CLI:** step 3 already registered the plugin. Tell the user to restart the app once and open a new chat.
- **Codex app:** tell the user to open **New Plugin**, choose `Downloads\CDVEA.zip` (not extracted) and click **Add plugin**, then restart Codex.
- **Cursor:** ask the user first, then add this server to `%USERPROFILE%\.cursor\mcp.json`. Merge it into the existing `mcpServers` object and don't remove other servers. Replace `<LOCALAPPDATA>` with the real value of `$env:LOCALAPPDATA`, using `\\` in JSON:

  ```json
  {
    "mcpServers": {
      "cdvea": {
        "command": "python",
        "args": ["<LOCALAPPDATA>\\CDVEA-Plugin\\CDVEA\\mcp\\launch.py"]
      }
    }
  }
  ```

  Then tell the user to restart Cursor. Cursor gets the 49 MCP tools; the skill files stay readable in `%LOCALAPPDATA%\CDVEA-Plugin\CDVEA\skills`.

## 5. Verify

```powershell
python "$env:LOCALAPPDATA\CDVEA-Plugin\CDVEA\cdvea\run.py" doctor
```

It must print JSON with `"ready": true`. Report the result to the user, plus anything optional that doctor lists as missing (Node.js for HyperFrames/Remotion, Blender). Don't install those unless the user asks.

## Notes

- Nothing in setup uploads the user's media or needs an account. Setup downloads only from GitHub, PyPI, Astral (uv/Python) and Hugging Face.
- Uninstall: remove the plugin from the app, then delete `%LOCALAPPDATA%\CDVEA` and `%LOCALAPPDATA%\CDVEA-Plugin`.
- Full human guide (English and Bengali): [SETUP-GUIDE.md](SETUP-GUIDE.md).
