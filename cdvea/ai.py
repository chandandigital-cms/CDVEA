"""Optional local analysis adapters. Models are never downloaded by this helper."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import uuid
from cli import write_new, stamp

def main():
    parser=argparse.ArgumentParser(description='CDVEA optional local transcription and shot detection')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('transcribe');p.add_argument('input');p.add_argument('--model',default=os.environ.get('FFMPEG_SKILL_ASR_MODEL'),help='Existing local model directory; defaults to the installed CDVEA model')
    p.add_argument('--language',help='Language code, for example bn, hi or en')
    p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--compute-type',default='int8');p.add_argument('--output-dir',help='New output folder; defaults to a new transcript folder beside the source')
    p=sub.add_parser('scenes');p.add_argument('input');p.add_argument('--threshold',type=float,default=27);p.add_argument('--output',required=True)
    args=parser.parse_args()
    try:
        source=Path(args.input).resolve(strict=True)
        if args.command=='transcribe':
            if not args.model:raise ValueError('No local model configured. Set FFMPEG_SKILL_ASR_MODEL to the installed model directory.')
            model=Path(args.model).resolve(strict=True)
            if not model.is_dir():raise ValueError('Supply a local converted model directory; model names cannot trigger downloads')
            from faster_whisper import WhisperModel
            output=Path(args.output_dir).resolve() if args.output_dir else source.parent/(source.stem+'-transcript-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6])
            if output.exists():raise ValueError('Choose a new transcript output directory')
            engine=WhisperModel(str(model),device=args.device,compute_type=args.compute_type,local_files_only=True)
            segments,info=engine.transcribe(str(source),language=None if args.language=='auto' else args.language,word_timestamps=True)
            rows=[]
            for segment in segments:
                rows.append({'start':segment.start,'end':segment.end,'text':segment.text,'words':[
                    {'start':w.start,'end':w.end,'word':w.word,'probability':w.probability} for w in segment.words or []]})
            output.mkdir(parents=True)
            write_new(output/'transcript.json',json.dumps({'source':str(source),'language':info.language,'segments':rows},ensure_ascii=False,indent=2)+'\n')
            write_new(output/'transcript.srt','\n\n'.join(f"{i}\n{stamp(s['start'])} --> {stamp(s['end'])}\n{s['text'].strip()}" for i,s in enumerate(rows,1))+'\n')
            result={'output':str(output),'srt':str(output/'transcript.srt'),'word_timing_json':str(output/'transcript.json'),'segments':len(rows),'language':info.language,'processing':'local','review':'Check names, numbers and cut boundaries against the speech.'}
        else:
            from scenedetect import detect, ContentDetector
            scenes=detect(str(source),ContentDetector(threshold=args.threshold))
            rows=[{'start':a.get_seconds(),'end':b.get_seconds(),'start_frame':a.get_frames(),'end_frame':b.get_frames()} for a,b in scenes]
            write_new(args.output,json.dumps({'source':str(source),'scenes':rows,'threshold':args.threshold},indent=2)+'\n')
            result={'output':str(Path(args.output).resolve()),'scenes':len(rows),'note':'Scene boundaries are suggestions, not story highlights.'}
        print(json.dumps(result,ensure_ascii=False));return 0
    except ImportError as e:
        print(json.dumps({'error':'Optional dependency missing','detail':str(e),'setup':'Read INSTALL.md and use a separate Python environment.'}),file=sys.stderr);return 1
    except (ValueError,OSError,RuntimeError) as e:
        print(json.dumps({'error':str(e)}),file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
