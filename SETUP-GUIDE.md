# CDVEA setup guide (Windows 10/11 x64)

CDVEA is an AI plugin. It does the editing with software that runs on your own computer, so you install that software once, run CDVEA setup, and then add the plugin to Codex or Claude Code.

**[বাংলা নির্দেশিকা নিচে আছে ↓](#বাংলা-নির্দেশিকা)**

> **Shortcut:** let Claude Code, Codex or Cursor do all of this for you. Paste the prompt from [the README](README.md#-install-with-your-ai-agent) and the agent follows [AI-INSTALL.md](AI-INSTALL.md).

## 1. Install the required software

| Software | Why CDVEA needs it | Download | Or install with winget |
| --- | --- | --- | --- |
| **Python 3.10+** (3.12 recommended) | Starts the CDVEA tools and runs setup | [python.org/downloads/windows](https://www.python.org/downloads/windows/) | `winget install --id Python.Python.3.12 -e` |
| **FFmpeg 6.1+** (with FFprobe) | Cuts, mixes, captions and exports video | [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) ("release full") · [ffmpeg.org](https://ffmpeg.org/download.html) | `winget install --id Gyan.FFmpeg -e` |
| **Codex** or **Claude Code** | The AI app that uses the plugin | [Codex](https://developers.openai.com/codex/quickstart) · [Claude Code](https://code.claude.com/docs/en/setup) | — |

When you install Python from python.org, tick **"Add python.exe to PATH"** on the first screen.

If you download FFmpeg from gyan.dev instead of winget, extract it (for example to `C:\ffmpeg`) and add its `bin` folder to PATH: open **Start → "Edit environment variables for your account" → Path → Edit → New**, enter `C:\ffmpeg\bin`, then click OK.

**Close and reopen PowerShell**, then check that both work:

```powershell
python --version
ffmpeg -version
```

## 2. Download the plugin and run setup

Open **PowerShell** and paste these three lines:

```powershell
Invoke-WebRequest https://github.com/chandandigital-cms/CDVEA/releases/latest/download/CDVEA.zip -OutFile "$env:USERPROFILE\Downloads\CDVEA.zip"
Expand-Archive "$env:USERPROFILE\Downloads\CDVEA.zip" "$env:LOCALAPPDATA\CDVEA-Plugin" -Force
powershell -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\CDVEA-Plugin\CDVEA\setup.ps1" -Hosts none
```

The first line saves `CDVEA.zip` in your **Downloads** folder. Setup then downloads these automatically into `%LOCALAPPDATA%\CDVEA`:

| Downloaded by setup | Size | Source |
| --- | --- | --- |
| Python 3.12 runtime for CDVEA (separate from your own Python) | about 30 MB | [astral-sh/python-build-standalone](https://github.com/astral-sh/python-build-standalone) via [uv](https://docs.astral.sh/uv/) |
| Python packages (faster-whisper, PyAV, NumPy…) | about 200 MB | [PyPI](https://pypi.org/), exact versions in `requirements-local.lock.txt` |
| Multilingual speech model (Bengali, Hindi, English) | about 484 MB | [Systran/faster-whisper-small](https://huggingface.co/Systran/faster-whisper-small) (SHA-256 checked) |

Wait until you see `"status": "ready"`. An interrupted download resumes when you run the last line again.

## 3. Add the plugin

**Codex app:** open **New Plugin**, click **Choose file**, select `Downloads\CDVEA.zip` (don't extract it) and click **Add plugin**. Restart Codex and open a new chat.

**Claude Code or Codex CLI:** instead of uploading, run:

```powershell
powershell -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\CDVEA-Plugin\CDVEA\setup.ps1" -Hosts claude
```

Use `-Hosts codex` for the Codex CLI. Restart the app once.

**Claude desktop app:** the desktop app doesn't put the `claude` command on PATH, so `-Hosts claude` stops with `claude CLI is not on PATH`. Keep `-Hosts none` from step 2, then run these in a terminal where `claude` works (the first two only if an older CDVEA is registered):

```powershell
claude plugin uninstall cdvea@chandan-digital
claude plugin marketplace remove chandan-digital
claude plugin marketplace add "$env:LOCALAPPDATA\CDVEA-Plugin\CDVEA"
claude plugin install cdvea@chandan-digital-local --scope user
```

**Older CDVEA already installed?** Keep only one copy enabled. In Codex, open `%USERPROFILE%\.codex\config.toml` and set `enabled = false` under the older `[plugins."cdvea@…"]` entry, then restart Codex.

Try: *"Use CDVEA doctor to check my setup."*

## 4. Use the tools without an AI app (optional)

```powershell
python "$env:LOCALAPPDATA\CDVEA-Plugin\CDVEA\cdvea\run.py" doctor
python "$env:LOCALAPPDATA\CDVEA-Plugin\CDVEA\cdvea\run.py" transcribe "D:\Videos\interview.mp4" --language bn
```

Use `--language hi` for Hindi or `en` for English, or leave it out for automatic detection.

## Optional software

Only needed for some features. See [CAPABILITIES.md](CAPABILITIES.md).

| Software | Used for | Download | Or install with | Check |
| --- | --- | --- | --- | --- |
| Node.js LTS | Needed by HyperFrames and Remotion, some social helpers | [nodejs.org](https://nodejs.org/) | `winget install --id OpenJS.NodeJS.LTS -e` | `node --version` |
| HyperFrames CLI | Animated titles, logos, HTML motion graphics | [hyperframes](https://github.com/heygen-com/hyperframes) | `npm install -g hyperframes` | `hyperframes doctor` |
| Remotion | React motion graphics and transparent overlays | [remotion.dev](https://www.remotion.dev/) | per project, see below | `npm run still` |
| Blender | 3D logos, product animation, camera moves | [blender.org/download](https://www.blender.org/download/) | `winget install --id BlenderFoundation.Blender -e` | `& $env:BLENDER_PATH --version` |
| Git | Cloning the source instead of downloading CDVEA.zip | [git-scm.com](https://git-scm.com/download/win) | `winget install --id Git.Git -e` | `git --version` |

**Remotion** lives inside a project folder. Copy CDVEA's starter and install it there:

```powershell
$r = "$env:USERPROFILE\Documents\CDVEA-Remotion"
Copy-Item "$env:LOCALAPPDATA\CDVEA-Plugin\CDVEA\vendor\video-editing\skills\video-editing\assets\remotion-edit-template" $r -Recurse
Set-Location $r
npm ci
npx remotion browser ensure
npm run still
```

The browser step downloads Remotion's headless Chrome (about 100 MB) once. `npm run still` saves a test frame to `output\still.png`.

**Blender** isn't added to PATH by its installer. Tell CDVEA where it is, then restart your AI app:

```powershell
$b = Get-ChildItem 'C:\Program Files\Blender Foundation' -Recurse -Filter blender.exe -Depth 2 | Sort-Object FullName -Descending | Select-Object -First 1
[Environment]::SetEnvironmentVariable('BLENDER_PATH', $b.FullName, 'User')
```

**Git clone:** run `git config --global core.longpaths true` first. Some bundled file paths are longer than Windows allows by default.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `python` is not recognized | Reinstall Python with "Add python.exe to PATH" ticked, then reopen PowerShell. |
| `Install FFmpeg first` | FFmpeg is not on PATH. Do step 1 again and reopen PowerShell. |
| `Run setup.ps1 from the CDVEA plugin folder` | Setup has not finished. Run the step 2 commands again. |
| `interface.longDescription is required` | You uploaded an old plugin ZIP. Download CDVEA.zip again (step 2, first line). |
| CDVEA tools don't respond in Codex | Check `python --version` works, run step 2 again, restart Codex and open a new chat. |
| `claude CLI is not on PATH` | You're using the Claude desktop app. Run setup with `-Hosts none` and register the plugin with the commands in step 3. |
| CDVEA tools appear twice, or an old version loads | Two copies are enabled. Disable the older one (step 3, "Older CDVEA already installed?"). |
| doctor says Blender is missing after installing it | Set `BLENDER_PATH` (see Optional software) and restart the AI app. New environment variables only reach apps opened afterwards. |
| `Filename too long` when cloning | Run `git config --global core.longpaths true`, then `git restore --source=HEAD :/` in the clone. |

**Uninstall:** remove the plugin in Codex, then delete `%LOCALAPPDATA%\CDVEA` and `%LOCALAPPDATA%\CDVEA-Plugin`.

---

## বাংলা নির্দেশিকা

CDVEA একটি AI প্লাগইন। এডিটিংয়ের কাজ আপনার নিজের কম্পিউটারের সফটওয়্যার দিয়ে হয়। তাই সফটওয়্যারগুলো একবার ইনস্টল করুন, CDVEA setup চালান, তারপর প্লাগইনটি Codex বা Claude Code-এ যোগ করুন।

### ১. দরকারি সফটওয়্যার ইনস্টল করুন

- **Python 3.12:** [python.org/downloads/windows](https://www.python.org/downloads/windows/) থেকে নামান। ইনস্টলের প্রথম পাতায় **"Add python.exe to PATH"**-এ টিক দিন। অথবা PowerShell-এ: `winget install --id Python.Python.3.12 -e`
- **FFmpeg:** PowerShell-এ `winget install --id Gyan.FFmpeg -e` চালান। অথবা [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) থেকে "release full" নামিয়ে `C:\ffmpeg`-এ রাখুন, আর `C:\ffmpeg\bin` PATH-এ যোগ করুন।
- **Codex** ([লিঙ্ক](https://developers.openai.com/codex/quickstart)) বা **Claude Code** ([লিঙ্ক](https://code.claude.com/docs/en/setup))।

PowerShell বন্ধ করে আবার খুলুন, তারপর `python --version` আর `ffmpeg -version` দুটোই কাজ করছে কিনা দেখুন।

### ২. প্লাগইন নামিয়ে setup চালান

PowerShell খুলে ওপরের **ধাপ ২-এর তিনটি লাইন** পেস্ট করুন। Setup নিজেই CDVEA-র Python, দরকারি প্যাকেজ আর বাংলা/হিন্দি/ইংরেজি স্পিচ মডেল (প্রায় ৪৮৪ MB) নামিয়ে নেবে। `"status": "ready"` দেখা পর্যন্ত অপেক্ষা করুন। মাঝপথে থেমে গেলে শেষ লাইনটি আবার চালান, যেখানে থেমেছিল সেখান থেকে চলবে।

### ৩. প্লাগইন যোগ করুন

- **Codex অ্যাপ:** **New Plugin** খুলে **Choose file**-এ `Downloads\CDVEA.zip` বেছে নিন (এক্সট্র্যাক্ট করবেন না), তারপর **Add plugin**। Codex রিস্টার্ট করে নতুন চ্যাট খুলুন।
- **Claude Code CLI:** আপলোড না করে ওপরের ধাপ ৩-এর `-Hosts claude` কমান্ডটি চালান।
- **Claude ডেস্কটপ অ্যাপ:** ডেস্কটপ অ্যাপ `claude` কমান্ড PATH-এ রাখে না, তাই `-Hosts claude` কাজ করবে না। `-Hosts none` দিয়ে setup চালান, তারপর ওপরের ধাপ ৩-এর চারটি `claude plugin` কমান্ড এমন টার্মিনালে চালান যেখানে `claude` কাজ করে।
- **পুরনো CDVEA আগে থেকে আছে?** একটাই চালু রাখুন। Codex-এ `%USERPROFILE%\.codex\config.toml` খুলে পুরনো `[plugins."cdvea@…"]`-এর নিচে `enabled = false` করুন, তারপর Codex রিস্টার্ট করুন।

লিখে দেখুন: *"Use CDVEA doctor to check my setup."*

### ৪. মোশন গ্রাফিক্স আর 3D (দরকার হলে)

| কাজ | সফটওয়্যার | ইনস্টল |
| --- | --- | --- |
| HyperFrames আর Remotion চালাতে | Node.js LTS | `winget install --id OpenJS.NodeJS.LTS -e` |
| অ্যানিমেটেড টাইটেল, লোগো, HTML মোশন | HyperFrames | `npm install -g hyperframes`, তারপর `hyperframes doctor` |
| React মোশন গ্রাফিক্স, স্বচ্ছ ওভারলে | Remotion | ওপরের Optional software অংশের কমান্ডগুলো চালান |
| 3D লোগো, পণ্যের অ্যানিমেশন, ক্যামেরা মুভমেন্ট | Blender | `winget install --id BlenderFoundation.Blender -e` |

Blender ইনস্টলের পর ওপরের `BLENDER_PATH` কমান্ড দুটো চালান আর AI অ্যাপ রিস্টার্ট করুন। না হলে CDVEA doctor Blender খুঁজে পাবে না।

**সমস্যা হলে:** ওপরের Troubleshooting টেবিল দেখুন। `python` চিনতে না পারলে "Add python.exe to PATH" টিক দিয়ে Python আবার ইনস্টল করুন।
