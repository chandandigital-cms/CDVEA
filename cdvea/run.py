"""Run shell helpers through the configured local Python, without manual activation."""
import subprocess
from pathlib import Path
import sys
from runtime import load_runtime
ROOT=Path(__file__).resolve().parents[1]
try:
    python,env=load_runtime()
    if len(sys.argv)<2:raise ValueError('Use: run.py doctor | transcribe FILE | tool NAME ARGS')
    args=sys.argv[1:]
    if args[0]=='tool':
        if len(args)<2 or args[1] not in {p.stem for p in (ROOT/'scripts').glob('*.py') if not p.name.startswith('_')}:
            raise ValueError('Select an existing bundled FFmpeg tool')
        script=ROOT/'scripts'/(args[1]+'.py');args=args[2:]
    elif args[0] in ['transcribe','scenes']:script=ROOT/'cdvea/ai.py'
    else:script=ROOT/'cdvea/cli.py'
    raise SystemExit(subprocess.call([str(python), str(script), *args], env=env))
except (OSError,ValueError,RuntimeError) as e:
    print('CDVEA: '+str(e),file=sys.stderr);raise SystemExit(1)
