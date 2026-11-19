"""CDVEA local project tools. Standard library only; FFmpeg handles media."""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def run(args, timeout=1800, cwd=None):
    p = subprocess.run([str(a) for a in args], capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=timeout, cwd=cwd)
    if p.returncode:
        raise ValueError(p.stderr[-5000:] or p.stdout[-5000:] or 'Command failed')
    return p.stdout

def binary(name):
    result = os.environ.get(name.upper() + '_PATH') or shutil.which(name)
    if not result:
        raise ValueError(f'{name} missing. Install it or set {name.upper()}_PATH.')
    return result

def probe(path):
    return json.loads(run([binary('ffprobe'), '-v', 'error', '-show_streams',
                           '-show_format', '-of', 'json', str(path)], 120))

def number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name} must be a finite number')
    return value

def load_plan(path, inspect=True):
    path = Path(path).resolve()
    plan = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(plan, dict):
        raise ValueError('The plan must be a JSON object')
    unknown = set(plan) - {'version', 'name', 'width', 'height', 'fps', 'clips', 'output'}
    if unknown:
        raise ValueError(f'Unknown plan fields: {sorted(unknown)}')
    if plan.get('version') != 1:
        raise ValueError('Expected plan version 1')
    for key, default in [('width',1920), ('height',1080), ('fps',30)]:
        plan[key] = number(plan.get(key, default), key)
    if any(int(plan[k]) != plan[k] or not 16 <= plan[k] <= 8192 or plan[k] % 2 for k in ['width','height']):
        raise ValueError('Width and height must be even integers from 16 to 8192')
    if not 1 <= plan['fps'] <= 120:
        raise ValueError('fps must be from 1 to 120')
    if not isinstance(plan.get('clips'), list) or not plan['clips']:
        raise ValueError('Supply at least one clip')
    if len(plan['clips']) > 200:
        raise ValueError('Limit this assembly to 200 clips')
    cursor = 0.0
    cache = {}
    for clip in plan['clips']:
        if not isinstance(clip, dict) or set(clip) - {'source','start','end','speed','label'}:
            raise ValueError('Clip fields: source, start, end, speed, label')
        source = Path(clip['source'])
        if not source.is_absolute():
            source = path.parent / source
        source = source.resolve(strict=True)
        if not source.is_file():
            raise ValueError('Source must be a local file')
        start = number(clip.get('start',0), 'start')
        end = number(clip['end'], 'end')
        speed = number(clip.get('speed',1), 'speed')
        if start < 0 or end <= start or not 0.25 <= speed <= 4:
            raise ValueError('Require 0 <= start < end and speed from 0.25 to 4')
        duration = (end-start)/speed
        frames = round(duration*plan['fps'])
        if frames < 1:
            raise ValueError('A clip must last at least one output frame')
        clip.update(source=str(source), start=start, end=end, speed=speed,
                    output_start=cursor, output_duration=frames/plan['fps'])
        cursor += frames/plan['fps']
        if inspect:
            if str(source) not in cache:
                cache[str(source)] = probe(source)
            data = cache[str(source)]
            video = next((s for s in data['streams'] if s['codec_type']=='video' and not s.get('disposition',{}).get('attached_pic')), None)
            if not video:
                raise ValueError(f'No video stream: {source}')
            if video.get('color_transfer') in ['smpte2084','arib-std-b67'] or video.get('color_primaries')=='bt2020':
                raise ValueError('Convert HDR/wide-gamut footage with scripts/color.py before this SDR assembly')
            if end > float(data['format']['duration']) + 0.04:
                raise ValueError(f'Clip end exceeds source duration: {source}')
            clip['has_audio'] = any(s['codec_type']=='audio' for s in data['streams'])
    plan['duration'] = cursor
    output = Path(plan.get('output','final.mp4'))
    if not output.is_absolute():
        output = path.parent/output
    plan['output'] = str(output.resolve())
    if output.suffix.lower() != '.mp4':
        raise ValueError('This assembly lane outputs .mp4; use core export.py for other formats')
    if plan['output'] in [c['source'] for c in plan['clips']]:
        raise ValueError('Output cannot replace a source')
    return plan

def doctor():
    report = {'python':sys.version.split()[0], 'core':{}, 'optional':{}}
    for name in ['ffmpeg','ffprobe','node','npm','uv','blender','whisper-cli','tesseract']:
        exe = os.environ.get(name.upper()+'_PATH') or shutil.which(name)
        row = {'available':bool(exe), 'path':exe}
        if exe and name in ['ffmpeg','ffprobe','node']:
            try: row['version']=run([exe,'-version' if name.startswith('ff') else '--version'],20).splitlines()[0]
            except Exception as e: row.update(available=False,error=str(e))
        report['core' if name in ['ffmpeg','ffprobe'] else 'optional'][name]=row
    for name in ['faster_whisper','scenedetect','PIL','opentimelineio']:
        report['optional'][name]={'available':importlib.util.find_spec(name) is not None}
    if report['core']['ffmpeg']['available']:
        text=run([binary('ffmpeg'),'-hide_banner','-filters'],30)
        report['filters']={k:bool(re.search(r'\s'+re.escape(k)+r'\s',text)) for k in ['subtitles','loudnorm','vidstabdetect','zscale','chromakey','minterpolate']}
    report['ready']=all(x['available'] for x in report['core'].values())
    report['note']='Optional tools are reported, never installed or downloaded automatically.'
    return report

def atempo(speed):
    filters=[]
    while speed>2: filters.append('atempo=2');speed/=2
    while speed<0.5: filters.append('atempo=0.5');speed/=0.5
    filters.append(f'atempo={speed:.10g}')
    return ','.join(filters)

def render(plan_path, dry_run=False):
    plan=load_plan(plan_path)
    if dry_run:
        return {'status':'planned','plan':plan,'writes':False}
    output=Path(plan['output'])
    if output.exists():
        raise ValueError('Output exists. Choose a new output filename.')
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='cdvea-',dir=output.parent) as temp:
        temp=Path(temp); parts=[]
        for i,c in enumerate(plan['clips']):
            # PCM intermediates avoid accumulating AAC encoder delay at every cut.
            part=temp/f'clip-{i:04d}.mov';parts.append(part)
            dur=c['output_duration']; fps=plan['fps']
            vf=(f"setpts=(PTS-STARTPTS)/{c['speed']},scale={int(plan['width'])}:{int(plan['height'])}:"
                f"force_original_aspect_ratio=decrease,pad={int(plan['width'])}:{int(plan['height'])}:(ow-iw)/2:(oh-ih)/2,"
                f"setsar=1,fps={fps},format=yuv420p")
            args=[binary('ffmpeg'),'-hide_banner','-v','error','-nostdin','-n','-ss',c['start'], '-t',c['end']-c['start'],'-i',c['source']]
            if not c['has_audio']:
                args += ['-f','lavfi','-i','anullsrc=r=48000:cl=stereo']
            af=atempo(c['speed']) if c['has_audio'] else 'anull'
            fade=min(0.015,dur/4)
            af+=f',aresample=48000,apad,atrim=duration={dur},asetpts=PTS-STARTPTS,afade=t=in:d={fade},afade=t=out:st={dur-fade}:d={fade}'
            args += ['-map','0:v:0','-map','0:a:0' if c['has_audio'] else '1:a:0','-vf',vf,'-af',af,'-t',dur,
                     '-c:v','libx264','-preset','medium','-crf','18','-c:a','pcm_s16le','-ac','2','-ar','48000',str(part)]
            run(args)
        # Numeric local filenames keep concat quoting independent of source names.
        listing=temp/'concat.txt';listing.write_text(''.join(f"file '{p.name}'\n" for p in parts))
        candidate=temp/'candidate.mp4'
        run([binary('ffmpeg'),'-hide_banner','-v','error','-nostdin','-n','-f','concat','-safe','1','-i',listing.name,
             '-c:v','copy','-c:a','aac','-b:a','192k','-af','aresample=async=1:first_pts=0','-t',plan['duration'],'-movflags','+faststart',candidate.name],cwd=temp)
        data=probe(candidate);actual=float(data['format']['duration'])
        video=next(s for s in data['streams'] if s['codec_type']=='video')
        if (video['width'],video['height'])!=(plan['width'],plan['height']) or abs(actual-plan['duration'])>max(0.12,2/plan['fps']):
            raise ValueError('Candidate failed geometry/duration validation')
        run([binary('ffmpeg'),'-hide_banner','-v','error','-xerror','-nostdin','-i',candidate,'-f','null','-'])
        # Exclusive creation prevents a concurrent render from overwriting a deliverable.
        try:
            with output.open('xb') as dest, candidate.open('rb') as source:
                shutil.copyfileobj(source,dest)
        except FileExistsError:
            raise ValueError('Output appeared during render; kept the existing file')
    with output.open('rb') as rendered:
        checksum=hashlib.sha256()
        for chunk in iter(lambda:rendered.read(1024*1024),b''):
            checksum.update(chunk)
        digest=checksum.hexdigest()
    return {'status':'rendered','output':str(output),'duration':actual,'sha256':digest,'validation':'geometry, duration and full decode passed','visual_review':'not performed'}

def parse_stamp(text):
    h,m,s,ms=map(int,re.split('[:,.]',text))
    return h*3600+m*60+s+ms/1000

def stamp(value):
    value=max(0,round(value*1000));h,value=divmod(value,3600000);m,value=divmod(value,60000);s,ms=divmod(value,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def write_new(path,text):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='') as f:f.write(text)

def retime(plan_path, source, subtitles, output):
    plan=load_plan(plan_path,inspect=False);source=str(Path(source).resolve(strict=True))
    cues=[]
    pattern=r'(\d{2,}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2,}:\d{2}:\d{2}[,.]\d{3})'
    for block in re.split(r'\n\s*\n',Path(subtitles).read_text(encoding='utf-8-sig').replace('\r\n','\n').strip()):
        match=re.search(pattern,block)
        if not match:raise ValueError('Invalid SRT cue')
        a,b=map(parse_stamp,match.groups());body=block[match.end():].lstrip('\n')
        if b<=a:raise ValueError('Subtitle end must follow start')
        for c in plan['clips']:
            if c['source']!=source:continue
            left,right=max(a,c['start']),min(b,c['end'])
            if right>left:
                begin=c['output_start']+(left-c['start'])/c['speed']
                end=min(c['output_start']+c['output_duration'],c['output_start']+(right-c['start'])/c['speed'])
                if end>begin:cues.append((begin,end,body))
    cues.sort()
    write_new(output,'\n\n'.join(f'{i}\n{stamp(a)} --> {stamp(b)}\n{text}' for i,(a,b,text) in enumerate(cues,1))+'\n')
    return {'output':str(Path(output).resolve()),'cues':len(cues),'note':'Cues crossing removed ranges split; review word boundaries by listening.'}

def export_edl(plan_path,output):
    plan=load_plan(plan_path,inspect=False);fps=plan['fps']
    if fps not in [24,25,30]:raise ValueError('CMX export supports integer 24, 25 or 30 fps only; no drop-frame conversion')
    if any(c['speed']!=1 for c in plan['clips']):raise ValueError('CMX export does not support speed changes')
    def tc(frame):
        frame=round(frame);sec,f=divmod(frame,int(fps));minute,s=divmod(sec,60);h,m=divmod(minute,60)
        if h>=24:raise ValueError('CMX timecode exceeds 24 hours')
        return f'{h:02}:{m:02}:{s:02}:{f:02}'
    lines=['TITLE: CDVEA CUT ASSEMBLY','FCM: NON-DROP FRAME',''];rows=[];record=0
    for i,c in enumerate(plan['clips'],1):
        start=round(c['start']*fps);length=round(c['output_duration']*fps);reel=f'CD{i:06d}'
        lines += [f'{i:03d}  {reel} V     C        {tc(start)} {tc(start+length)} {tc(record)} {tc(record+length)}',f"* FROM CLIP NAME: {Path(c['source']).name}",'']
        rows.append([reel,c['source'],start,length,record]);record+=length
    # Sidecar is necessary to relink local paths. Avoid partial overwrites of either file.
    sidecar=Path(str(output)+'.sources.csv')
    if Path(output).exists() or sidecar.exists():raise ValueError('EDL or source map already exists')
    write_new(output,'\n'.join(lines)+'\n')
    with sidecar.open('x',encoding='utf-8',newline='') as f:
        writer=csv.writer(f);writer.writerow(['reel','source','source_start_frame','duration_frames','record_start_frame']);writer.writerows(rows)
    return {'output':str(Path(output).resolve()),'source_map':str(sidecar.resolve()),'scope':'Video cuts only, zero-based media time. Audio, titles, source timecode and grades do not transfer. Test relinking in your editor.'}

def catalog():
    skills=[]
    for p in sorted((ROOT/'skills').glob('*/SKILL.md')):
        match=re.search(r'^description:\s*(.+)',p.read_text(encoding='utf-8'),re.M)
        skills.append({'name':p.parent.name,'description':match.group(1) if match else '', 'path':str(p.relative_to(ROOT))})
    return {'name':'CDVEA by Chandan Digital','skills':skills,'agents':[p.stem for p in sorted((ROOT/'agents').glob('*.md'))]}

def main():
    parser=argparse.ArgumentParser(description='CDVEA by Chandan Digital')
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ['doctor','catalog']:sub.add_parser(name)
    p=sub.add_parser('init');p.add_argument('directory')
    for name in ['validate-plan','render-plan']:
        p=sub.add_parser(name);p.add_argument('plan')
        if name=='render-plan':p.add_argument('--dry-run',action='store_true')
    p=sub.add_parser('retime-srt');p.add_argument('plan');p.add_argument('--source',required=True);p.add_argument('--srt',required=True);p.add_argument('--output',required=True)
    p=sub.add_parser('export-edl');p.add_argument('plan');p.add_argument('--output',required=True)
    args=parser.parse_args()
    try:
        if args.command=='doctor': result=doctor()
        elif args.command=='catalog':result=catalog()
        elif args.command=='init':
            target=Path(args.directory).resolve();target.mkdir(parents=True,exist_ok=True)
            for name in ['media','work','review','outputs']: (target/name).mkdir(exist_ok=True)
            write_new(target/'edit-plan.json',json.dumps({'version':1,'name':target.name,'width':1920,'height':1080,'fps':30,'clips':[],'output':'outputs/final.mp4'},indent=2)+'\n')
            result={'project':str(target),'next':'Add local sources and start/end times to edit-plan.json. Empty projects cannot render.'}
        elif args.command=='validate-plan':result={'valid':True,'plan':load_plan(args.plan)}
        elif args.command=='render-plan':result=render(args.plan,args.dry_run)
        elif args.command=='retime-srt':result=retime(args.plan,args.source,args.srt,args.output)
        elif args.command=='export-edl':result=export_edl(args.plan,args.output)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if args.command!='doctor' or result['ready'] else 1
    except (ValueError,KeyError,OSError,subprocess.SubprocessError) as e:
        print(json.dumps({'error':str(e)},ensure_ascii=False),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
