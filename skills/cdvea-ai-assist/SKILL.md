---
name: cdvea-ai-assist
description: "Run optional local speech transcription and scene detection, or plan model-based restoration."
---

# cdvea-ai-assist

Resolve the plugin root two directories above this file. Keep sources intact and follow the user’s current scope.

Use `../../cdvea/ai.py --help`. Transcription requires faster-whisper and an existing local model directory. Pass `--language bn`, hi or en when known. It creates segment SRT and word JSON. Scene detection requires PySceneDetect/OpenCV and creates boundary suggestions. The helper never downloads models. Read ../../INSTALL.md before selecting an environment. These adapters have not passed an engine test in this release.

For AI restoration or segmentation, use [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) or [SAM 2](https://github.com/facebookresearch/sam2) only when their separate engines, models and hardware are available. Inspect current usage documentation before choosing flags. Record model identity, licences, sample quality and temporal errors. Do not claim a workflow-only integration performs tracking, upscaling or object removal without an actual run.

## Automatic local tools

Use the bundled MCP tools directly in an ordinary Codex or Claude Code session. For speech transcription or automatic subtitles, call `cdvea_transcribe` with the media file path and, when known, language `bn`, `hi` or `en`. The installed tool selects the local Python and downloaded model; the user does not need a launcher, activation command or model path. Omit output_dir to create a new folder beside the source. The model loads only during transcription and exits with the job. Never tell the user to manually turn on the model.

For other edits, use the bundled FFmpeg tools. When a shell helper is necessary, run `python ../../cdvea/run.py` with the desired helper command; it selects the configured local runtime. Technical details are in [the local setup](../../LOCAL-TRANSCRIPTION.md). The normal host may ask for file or tool permission under its existing policy.
