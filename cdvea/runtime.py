"""Resolve the one-time, per-user installation from any plugin cache directory."""
import json,os
from pathlib import Path

def runtime_directory():
    override=os.environ.get('CDVEA_RUNTIME_DIR')
    if override:return Path(override).expanduser().resolve()
    if os.name=='nt':return Path(os.environ['LOCALAPPDATA'])/'CDVEA'
    return Path.home()/'.local/share/cdvea'

def load_runtime():
    folder=runtime_directory()
    path=folder/'runtime.json'
    if not path.is_file():raise RuntimeError('CDVEA needs one-time setup. Run python setup.py from the source checkout, then restart the host.')
    config=json.loads(path.read_text(encoding='utf-8'))
    python=Path(config['python']);model=Path(config['model'])
    if not python.is_file() or not (model/'model.bin').is_file():raise RuntimeError('The configured CDVEA runtime or model is missing. Run setup.py again.')
    env=dict(os.environ,FFMPEG_SKILL_MCP_FULL='1',FFMPEG_SKILL_ASR_ENGINE='faster-whisper',
        FFMPEG_SKILL_ASR_MODEL=str(model),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',
        HF_HUB_DISABLE_TELEMETRY='1',PYTHONUTF8='1',CDVEA_RUNTIME_DIR=str(folder))
    for key in ['FFMPEG_PATH','FFPROBE_PATH']:
        if config.get(key):env[key]=config[key]
    return python,env
