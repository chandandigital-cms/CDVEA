"""One-time Windows setup. Installs a per-user runtime, local model and host plugins."""
import argparse,hashlib,importlib.util,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'cdvea'))
from runtime import runtime_directory
MODEL_REPO='Systran/faster-whisper-small'
MODEL_REVISION='536b0662742c02347bc0e980a01041f333bce120'
MODEL_HASH='3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671'

def run(args,env=None,capture=False):
    p=subprocess.run([str(x) for x in args],env=env,capture_output=capture,text=True,encoding='utf-8',errors='replace')
    if p.returncode:raise RuntimeError('Command failed: '+str(args[0])+((': '+p.stderr[-2000:]) if capture else ''))
    return p.stdout if capture else None

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser(description='Set up CDVEA once; use normal Claude Code and Codex chats afterwards')
    p.add_argument('--runtime-dir',type=Path,default=runtime_directory())
    p.add_argument('--hosts',choices=['auto','claude','codex','both','none'],default='auto')
    p.add_argument('--check',action='store_true',help='Read-only readiness check; no downloads, registration or config changes')
    args=p.parse_args();folder=args.runtime_dir.expanduser().resolve()
    if args.check:
        config=folder/'runtime.json';data=json.loads(config.read_text()) if config.exists() else {}
        print(json.dumps({'runtime':str(folder),'configured':bool(data),'python_exists':Path(data.get('python','__missing__')).is_file(),
            'model_exists':(Path(data.get('model','__missing__'))/'model.bin').is_file(),
            'claude_cli':bool(shutil.which('claude')),'codex_cli':bool(shutil.which('codex'))},indent=2));return 0
    if os.name!='nt':raise RuntimeError('Automatic installer currently supports Windows. See INSTALL.md for manual setup on other systems.')
    ffmpeg=os.environ.get('FFMPEG_PATH') or shutil.which('ffmpeg')
    ffprobe=os.environ.get('FFPROBE_PATH') or shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:raise RuntimeError('Install FFmpeg first, reopen the terminal, then run setup.py again. See SETUP-GUIDE.md step 1.')
    uv=[shutil.which('uv')] if shutil.which('uv') else None
    if not uv:
        if importlib.util.find_spec('uv') is None:run([sys.executable,'-m','pip','install','--user','uv'])
        uv=[sys.executable,'-m','uv']
    folder.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,UV_CACHE_DIR=str(folder/'cache/uv'),HF_HOME=str(folder/'cache/huggingface'),
             HF_HUB_DISABLE_TELEMETRY='1',HF_HUB_DISABLE_XET='1',HF_HUB_DOWNLOAD_TIMEOUT='120',PYTHONUTF8='1')
    candidates=list((folder/'python').glob('cpython-3.12.15-*/python.exe'))
    if not candidates:
        run([*uv,'python','install','3.12.15','--install-dir',folder/'python','--no-bin','--no-registry'],env)
        candidates=list((folder/'python').glob('cpython-3.12.15-*/python.exe'))
    if not candidates:raise RuntimeError('Managed Python 3.12.15 was not found after installation')
    python=folder/'.venv/Scripts/python.exe'
    if not python.is_file():run([*uv,'venv',folder/'.venv','--python',candidates[0],'--no-python-downloads'],env)
    run([*uv,'pip','install','--python',python,'-r',ROOT/'requirements-local.lock.txt'],env)
    model=folder/'models/faster-whisper-small'
    if not (model/'model.bin').is_file() or digest(model/'model.bin')!=MODEL_HASH:
        code="from huggingface_hub import snapshot_download; snapshot_download(repo_id="+repr(MODEL_REPO)+",revision="+repr(MODEL_REVISION)+",local_dir="+repr(str(model))+",allow_patterns=['config.json','model.bin','tokenizer.json','vocabulary.*','README.md','LICENSE*'],max_workers=2)"
        print('Downloading the multilingual small model. This can take several minutes; interrupted downloads can resume.',flush=True)
        run([python,'-c',code],env)
    if digest(model/'model.bin')!=MODEL_HASH:raise RuntimeError('Model SHA-256 verification failed')
    config={'python':str(python),'model':str(model),'model_repo':MODEL_REPO,'model_revision':MODEL_REVISION,
        'model_sha256':MODEL_HASH,'FFMPEG_PATH':str(ffmpeg),'FFPROBE_PATH':str(ffprobe)}
    (folder/'runtime.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    env['CDVEA_RUNTIME_DIR']=str(folder)
    # Keep one stable discovery location even when the large files live elsewhere.
    default_folder=Path(os.environ['LOCALAPPDATA'])/'CDVEA'
    if folder!=default_folder.resolve():
        default_folder.mkdir(parents=True,exist_ok=True)
        (default_folder/'runtime.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
        print('Custom runtime recorded in the standard per-user configuration.',flush=True)
    run([sys.executable,ROOT/'cdvea/run.py','doctor'],env)
    # Check model loading without downloading, transcribing personal media, or creating audio files.
    run([python,'-c',"from faster_whisper import WhisperModel; m=WhisperModel("+repr(str(model))+",device='cpu',compute_type='int8',local_files_only=True); assert all(x in m.supported_languages for x in ['bn','hi','en']); print('Local model ready: Bengali, Hindi and English')"],dict(env,HF_HUB_OFFLINE='1'))
    installed=[]
    for host in ['claude','codex']:
        if args.hosts not in ['auto','both',host]:continue
        executable=shutil.which(host)
        if not executable:
            if args.hosts in ['both',host]:raise RuntimeError(host+' CLI is not on PATH. Install it, reopen the terminal and run setup.py again.')
            continue
        run([executable,'plugin','marketplace','add',ROOT],env)
        plugin_id='cdvea@'+json.loads((ROOT/'.claude-plugin/marketplace.json').read_text(encoding='utf-8'))['name']
        if host=='claude':run([executable,'plugin','install',plugin_id,'--scope','user'],env)
        else:run([executable,'plugin','add',plugin_id],env)
        installed.append(host)
    print(json.dumps({'status':'ready','runtime':str(folder),'installed_hosts':installed,
        'next':'Restart the host app once, open a new chat and ask for the edit. No launcher or model switch is needed.'},indent=2))
    if args.hosts=='auto' and not installed:print('No host CLI found. Install Claude Code or Codex and rerun setup.py to register the plugin.')
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,RuntimeError,ValueError,KeyError) as e:
        print('CDVEA setup: '+str(e),file=sys.stderr);raise SystemExit(1)
