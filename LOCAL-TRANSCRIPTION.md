# Automatic local transcription

Run the one-time [setup](SETUP-GUIDE.md). It stores the Python environment, model and configuration under `%LOCALAPPDATA%\CDVEA` by default.

Both host declarations run `mcp/launch.py`. This small bootstrap reads the per-user runtime configuration and starts the correct Python with the local model path. It does not load the model on startup. `cdvea_transcribe` loads the model only for a speech job.

Call `cdvea_transcribe` with a local input path. Optional languages include bn, hi and en. Omit output_dir for a new folder beside the source. The tool returns SRT and word-timing JSON paths. Do not ask the user to activate an environment or open a launcher.

For shell helpers, use `python cdvea/run.py` from the plugin root. Examples: `doctor`, `transcribe INPUT --language bn`, or `tool audio INPUT --denoise -o OUTPUT`.

The plugin cache and per-user runtime are separate. Keep the runtime on disk. Do not commit machine configuration, model weights, virtual environments or account credentials. The host’s normal permission controls still apply.
