"""CDVEA MCP adapter; preserves the upstream transport and cancellation support."""
import json
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import server as core

ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('FFMPEG_SKILL_MCP_FULL','1')
SPECS={
 'cdvea_doctor':('Report local media tools and optional dependencies','doctor',{}),
 'cdvea_catalog':('List CDVEA skills and specialist agents','catalog',{}),
 'cdvea_validate_plan':('Validate a local CDVEA cut assembly','validate-plan',{'plan':'string'}),
 'cdvea_render_plan':('Render a cut assembly, or inspect it without writing','render-plan',{'plan':'string','dry_run':'boolean'}),
 'cdvea_retime_srt':('Retime one source subtitle file against an edit plan','retime-srt',{'plan':'string','source':'string','srt':'string','output':'string'}),
 'cdvea_export_edl':('Export cut-only CMX EDL and source relink CSV','export-edl',{'plan':'string','output':'string'}),
 'cdvea_transcribe':('Transcribe local audio/video into SRT subtitles and word timestamps. Uses the already installed local model automatically. Supports Bengali (bn), Hindi (hi), English (en) and automatic detection. The model loads only for this call.','transcribe',{'input':'string','language':'string','output_dir':'string'})}
_list=core.tool_list
_call=core.call_tool
_handle=core.handle

def tool_list():
    tools=_list()
    for name,(description,command,props) in SPECS.items():
        tools.append({'name':name,'description':description,'inputSchema':{'type':'object',
          'properties':{k:{'type':v} for k,v in props.items()},'required':[k for k in props if k not in ['dry_run','language','output_dir']],
          'additionalProperties':False},'annotations':{'readOnlyHint':command in ['doctor','catalog','validate-plan'],
          'destructiveHint':False,'openWorldHint':False}})
    return tools

def call_tool(name,args,on_start=None):
    if name not in SPECS:return _call(name,args,on_start)
    description,command,props=SPECS[name]
    if not isinstance(args,dict) or set(args)-set(props):
        return {'isError':True,'content':[{'type':'text','text':'Unexpected arguments'}]}
    for key,kind in props.items():
        if key in ['dry_run','language','output_dir'] and key not in args:continue
        if key not in args or (kind=='string' and (not isinstance(args[key],str) or not args[key] or args[key].startswith('-'))) or (kind=='boolean' and not isinstance(args[key],bool)):
            return {'isError':True,'content':[{'type':'text','text':f'Invalid argument: {key}'}]}
    argv=[str(ROOT/('cdvea/ai.py' if command=='transcribe' else 'cdvea/cli.py')),command]
    if command=='transcribe':
        argv.append(args['input'])
        if 'language' in args:argv.extend(['--language',args['language']])
        if 'output_dir' in args:argv.extend(['--output-dir',args['output_dir']])
    if 'plan' in args:argv.append(args['plan'])
    for key in ['source','srt','output']:
        if key in args:argv.extend(['--'+key,args[key]])
    if args.get('dry_run'):argv.append('--dry-run')
    p=core._common.run_tool(argv,per_call=1800,env=dict(os.environ),**({'on_start':on_start} if on_start else {}))
    text=p.stdout.strip() if p.returncode==0 else p.stderr.strip()
    result={'content':[{'type':'text','text':text}],'isError':p.returncode!=0}
    try:result['structuredContent']=json.loads(text)
    except ValueError:pass
    return result

def handle(req,on_start=None):
    result=_handle(req,on_start)
    if req.get('method')=='initialize':
        result['serverInfo']={'name':'cdvea','version':'1.2.1'}
    return result

core.tool_list=tool_list
core.call_tool=call_tool
core.handle=handle
if __name__=='__main__':raise SystemExit(core.main())
