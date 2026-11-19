"""Find the bundled runtime, with a fallback for earlier CDVEA installations."""

import json
import os
from pathlib import Path


def runtime_directory():
    override = os.environ.get('CDVEA_RUNTIME_DIR')
    if override:
        return Path(override).expanduser().resolve()
    if os.name == 'nt':
        return Path(os.environ['LOCALAPPDATA']) / 'CDVEA'
    return Path.home() / '.local/share/cdvea'


def bundled_config(folder):
    return {
        'python': str(folder / 'python/python.exe'),
        'model': str(folder / 'models/faster-whisper-small'),
        'FFMPEG_PATH': str(folder / 'ffmpeg/bin/ffmpeg.exe'),
        'FFPROBE_PATH': str(folder / 'ffmpeg/bin/ffprobe.exe'),
    }


def load_runtime():
    bundled = Path(__file__).resolve().parents[2] / 'runtime'
    if (bundled / 'python/python.exe').is_file():
        config = bundled_config(bundled)
    else:
        path = runtime_directory() / 'runtime.json'
        if not path.is_file():
            raise RuntimeError('Extract the complete CDVEA ZIP and run Install-CDVEA.cmd.')
        config = json.loads(path.read_text(encoding='utf-8'))

    python = Path(config['python'])
    model = Path(config['model'])
    if not python.is_file() or not (model / 'model.bin').is_file():
        raise RuntimeError('CDVEA could not find Python or the speech model. Extract the complete ZIP again.')

    env = dict(os.environ, FFMPEG_SKILL_MCP_FULL='1', FFMPEG_SKILL_ASR_ENGINE='faster-whisper',
               FFMPEG_SKILL_ASR_MODEL=str(model), HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
               HF_HUB_DISABLE_TELEMETRY='1', PYTHONUTF8='1', PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONHOME', None)
    env.pop('PYTHONPATH', None)
    for key in ('FFMPEG_PATH', 'FFPROBE_PATH'):
        if config.get(key):
            env[key] = config[key]
    if config.get('FFMPEG_PATH'):
        media_bin = str(Path(config['FFMPEG_PATH']).parent)
        env['PATH'] = os.pathsep.join((str(python.parent), media_bin, env.get('PATH', os.defpath)))
    return python, env
