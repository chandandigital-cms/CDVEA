"""Lightweight MCP bootstrap. Does not import or load the speech model."""
import subprocess
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'cdvea'))
from runtime import load_runtime
try:
    python,env=load_runtime()
    raise SystemExit(subprocess.call([str(python), str(ROOT/'mcp/cdvea_server.py'), *sys.argv[1:]], env=env))
except (OSError,RuntimeError,ValueError,KeyError) as e:
    print('CDVEA: '+str(e),file=sys.stderr)
    raise SystemExit(1)
