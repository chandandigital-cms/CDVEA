# CDVEA setup guide (Windows 10/11 x64)

CDVEA is an AI plugin. It does the editing with software that runs on your own computer, so you install that software once, run CDVEA setup, and then add the plugin to Codex or Claude Code.

**[বাংলা নির্দেশিকা নিচে আছে ↓](#বাংলা-নির্দেশিকা)**

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

Try: *"Use CDVEA doctor to check my setup."*

## 4. Use the tools without an AI app (optional)

```powershell
python "$env:LOCALAPPDATA\CDVEA-Plugin\CDVEA\cdvea\run.py" doctor
python "$env:LOCALAPPDATA\CDVEA-Plugin\CDVEA\cdvea\run.py" transcribe "D:\Videos\interview.mp4" --language bn
```

Use `--language hi` for Hindi or `en` for English, or leave it out for automatic detection.

## Optional software

Only needed for some features. See [CAPABILITIES.md](CAPABILITIES.md).

| Software | Used for | Download |
| --- | --- | --- |
| Node.js LTS | HyperFrames and Remotion motion graphics, some social helpers | [nodejs.org](https://nodejs.org/) |
| Blender | 3D and Blender workflows | [blender.org/download](https://www.blender.org/download/) |
| Git | Cloning the source instead of downloading CDVEA.zip | [git-scm.com](https://git-scm.com/download/win) |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `python` is not recognized | Reinstall Python with "Add python.exe to PATH" ticked, then reopen PowerShell. |
| `Install FFmpeg first` | FFmpeg is not on PATH. Do step 1 again and reopen PowerShell. |
| `Run setup.ps1 from the CDVEA plugin folder` | Setup has not finished. Run the step 2 commands again. |
| `interface.longDescription is required` | You uploaded an old plugin ZIP. Download CDVEA.zip again (step 2, first line). |
| CDVEA tools don't respond in Codex | Check `python --version` works, run step 2 again, restart Codex and open a new chat. |

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

লিখে দেখুন: *"Use CDVEA doctor to check my setup."*

**সমস্যা হলে:** ওপরের Troubleshooting টেবিল দেখুন। `python` চিনতে না পারলে "Add python.exe to PATH" টিক দিয়ে Python আবার ইনস্টল করুন।
