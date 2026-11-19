# Make subtitles from a local audio or video file

After [setup](SETUP-GUIDE.md), run this from the CDVEA plugin folder:

```powershell
python cdvea/run.py transcribe "D:\Videos\interview.mp4" --language bn
```

Use `bn` for Bengali, `hi` for Hindi or `en` for English. Leave out `--language` so the model can detect the language. The command creates a new folder beside the input and writes `transcript.srt` for subtitles and `transcript.json` for word timing. Use `--output-dir` with a new folder if you want to choose the destination.

In a host chat, ask CDVEA to transcribe a local file. The `cdvea_transcribe` tool uses the same local model. Review names, numbers and spellings before adding subtitles to your final video.
