# CDVEA install instructions for AI coding agents

These steps are for an AI agent (Claude Code, Codex, Cursor or similar) that a user has asked to install CDVEA on **Windows 10/11 x64**. Run the commands in PowerShell. Tell the user what each step does. If a step fails, show the error and stop; don't improvise workarounds.

**Ask the user before installing any system software (steps 1 and 6) and before editing any app configuration (steps 3, 4 and 6).**

## 0. Look for an earlier CDVEA install

An older CDVEA registered from another folder keeps loading after you install a new one, and two enabled copies give the app duplicate tools. Check before you start:

```powershell
Select-String "$env:USERPROFILE\.claude\plugins\known_marketplaces.json" -Pattern 'chandan-digital' -Context 0,4
Select-String "$env:USERPROFILE\.codex\config.toml" -Pattern '^\[plugins\."cdvea@' -Context 0,1
```

Report what you find (folder, version from its `.claude-plugin\plugin.json`, enabled or not). Don't remove or disable anything yet; step 4 handles it with the user's permission.

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

If `Downloads\CDVEA.zip` already exists, tell the user the first line replaces it with the latest release. For Claude Code, Codex CLI and Cursor the zip can go anywhere (for example a temporary folder); only the Codex app needs it in Downloads.

## 3. Run CDVEA setup

Choose `-Hosts` for the app you are running in:

| Agent | `-Hosts` value |
| --- | --- |
| Claude Code, with `claude` on PATH | `claude` |
| Claude Code desktop app without the `claude` CLI on PATH | `none` (step 4 registers it) |
| Codex CLI | `codex` |
| Codex app, Cursor or any other agent | `none` |

Check with `Get-Command claude` and `Get-Command codex`. The Claude desktop app doesn't put `claude` on PATH. With `-Hosts claude` and no CLI, setup downloads everything and then fails at the last step with `claude CLI is not on PATH`.

`-Hosts claude` and `-Hosts codex` change the app's plugin configuration, so ask the user first.

```powershell
powershell -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\CDVEA-Plugin\CDVEA\setup.ps1" -Hosts <value>
```

Setup downloads CDVEA's own Python 3.12, its pinned packages (about 200 MB) and the Bengali/Hindi/English speech model (about 484 MB, SHA-256 checked) into `%LOCALAPPDATA%\CDVEA`. It can take 5–15 minutes, so use a long command timeout (at least 20 minutes) or run it in the background. Success ends with `"status": "ready"`. If the download is interrupted, run the same command again: it resumes.

## 4. Connect the plugin to the app

- **Claude Code / Codex CLI:** step 3 already registered the plugin. Tell the user to restart the app once and open a new chat.
- **Claude Code desktop without the CLI:** give the user these commands to run in a terminal where `claude` works (installing the CLI is in the [Claude Code setup docs](https://code.claude.com/docs/en/setup)). The first two only apply if step 0 found an older `chandan-digital` marketplace:

  ```powershell
  claude plugin uninstall cdvea@chandan-digital
  claude plugin marketplace remove chandan-digital
  claude plugin marketplace add "$env:LOCALAPPDATA\CDVEA-Plugin\CDVEA"
  claude plugin install cdvea@chandan-digital --scope user
  ```

  Then restart the Claude app and open a new chat.
- **Older copy in Codex:** if step 0 found two `cdvea@…` entries with `enabled = true`, ask the user, back up `config.toml`, and set the older one's `enabled` to `false`. Don't delete its folder or cache. Restart Codex.
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

It must print JSON with `"ready": true`. Report the result to the user, plus anything optional that doctor lists as missing (Node.js for HyperFrames/Remotion, Blender). Don't install those unless the user asks; step 6 covers them.

## 6. Optional: motion graphics and 3D

Only when the user wants these features. Ask before each install.

| Feature | Software | Install | Check |
| --- | --- | --- | --- |
| HTML motion (HyperFrames) and React motion (Remotion) | Node.js LTS | `winget install --id OpenJS.NodeJS.LTS -e` | `node --version` |
| Animated titles, logos, HTML compositions | HyperFrames CLI | `npm install -g hyperframes` | `hyperframes doctor` |
| React motion graphics, alpha overlays | Remotion (per project) | see below | `npm run still` |
| 3D logos, product animation, camera moves | Blender | `winget install --id BlenderFoundation.Blender -e` | `& $env:BLENDER_PATH --version` |

**Remotion** isn't installed globally. Copy CDVEA's bundled starter to a work folder and install its pinned packages there:

```powershell
$r = "$env:USERPROFILE\Documents\CDVEA-Remotion"
Copy-Item "$env:LOCALAPPDATA\CDVEA-Plugin\CDVEA\vendor\video-editing\skills\video-editing\assets\remotion-edit-template" $r -Recurse
Set-Location $r
npm ci
npx remotion browser ensure
npm run still
```

`npx remotion browser ensure` downloads Remotion's headless Chrome (about 100 MB) once; tell the user before running it. `npm run still` writes `output\still.png`.

**Blender** from winget isn't added to PATH. CDVEA's doctor reads `BLENDER_PATH`, so ask the user, then set it for their account:

```powershell
$b = Get-ChildItem 'C:\Program Files\Blender Foundation' -Recurse -Filter blender.exe -Depth 2 | Sort-Object FullName -Descending | Select-Object -First 1
[Environment]::SetEnvironmentVariable('BLENDER_PATH', $b.FullName, 'User')
```

A new environment variable only reaches apps started afterwards. Tell the user to restart the AI app, then run doctor again: `optional.blender.available` must be `true`.

## Notes

- Nothing in setup uploads the user's media or needs an account. Setup downloads only from GitHub, PyPI, Astral (uv/Python) and Hugging Face.
- An agent that started before an install can't see new PATH entries or environment variables. Read them fresh (`[Environment]::GetEnvironmentVariable('Path','User')`) or ask the user to restart the agent before reporting something as missing.
- Cloning the repo with Git (instead of the zip) needs `git config core.longpaths true`: some vendor paths pass Windows' 260-character limit.
- Uninstall: remove the plugin from the app, then delete `%LOCALAPPDATA%\CDVEA` and `%LOCALAPPDATA%\CDVEA-Plugin`.
- Full human guide (English and Bengali): [SETUP-GUIDE.md](SETUP-GUIDE.md).
