"""Integration tests using generated local media. No model or service calls."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import cli

class EditingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='cdvea-test-')
        cls.root=Path(cls.temp.name)
        cls.a=cls.root/"speech ' Bengali বাংলা.mp4"
        cls.b=cls.root/'silent.mp4'
        ff=cli.binary('ffmpeg')
        cli.run([ff,'-v','error','-f','lavfi','-i','testsrc2=s=160x90:r=25:d=2','-f','lavfi','-i','sine=frequency=440:duration=2','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',cls.a])
        cli.run([ff,'-v','error','-f','lavfi','-i','color=c=blue:s=160x90:r=25:d=2','-c:v','libx264',cls.b])
        cls.hash=hashlib.sha256(cls.a.read_bytes()).hexdigest()

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def plan(self,name='plan.json',speed=1):
        p=self.root/name
        p.write_text(json.dumps({'version':1,'width':160,'height':90,'fps':25,'clips':[
          {'source':str(self.a),'start':0.2,'end':1.2,'speed':speed},
          {'source':str(self.b),'start':0,'end':1}], 'output':name+'.mp4'}),encoding='utf-8')
        return p

    def test_render_audio_and_silent_sources(self):
        result=cli.render(self.plan('render.json'))
        self.assertAlmostEqual(result['duration'],2,delta=0.12)
        data=cli.probe(result['output'])
        self.assertEqual({s['codec_type'] for s in data['streams']},{'video','audio'})
        self.assertEqual(hashlib.sha256(self.a.read_bytes()).hexdigest(),self.hash)
        with self.assertRaises(ValueError):cli.render(self.root/'render.json')

    def test_speed_and_dry_run(self):
        p=self.plan('fast.json',2)
        before=set(self.root.iterdir());result=cli.render(p,True)
        self.assertFalse(result['writes']);self.assertEqual(before,set(self.root.iterdir()))
        result=cli.render(p);self.assertAlmostEqual(result['duration'],1.52,delta=0.12)

    def test_many_cuts_keep_every_video_frame(self):
        p=self.plan('many.json');data=json.loads(p.read_text())
        data['clips']=[{'source':str(self.a),'start':0.2,'end':0.4} for _ in range(10)]
        p.write_text(json.dumps(data))
        result=cli.render(p)
        video=next(s for s in cli.probe(result['output'])['streams'] if s['codec_type']=='video')
        self.assertEqual(int(video['nb_frames']),50)
        self.assertAlmostEqual(result['duration'],2,delta=0.05)

    def test_core_probe_cut_and_check(self):
        output=self.root/'core-cut.mp4'
        report=json.loads(cli.run([sys.executable,cli.ROOT/'scripts/probe.py',self.a,'--json']))
        self.assertIsInstance(report,dict)
        cli.run([sys.executable,cli.ROOT/'scripts/cut.py',self.a,'--start','0.2','--end','1.2','--accurate','-o',output,'--json'])
        self.assertAlmostEqual(float(cli.probe(output)['format']['duration']),1,delta=0.1)
        report=json.loads(cli.run([sys.executable,cli.ROOT/'scripts/check.py',output,'--json']))
        self.assertIsInstance(report,dict)

    def test_invalid_ranges_and_fields(self):
        for change in [{'clips':[]},{'fps':float('nan')},{'width':161},{'transitions':['fade']},{'clips':[{'source':str(self.a),'start':0,'end':20}]}]:
            p=self.plan('bad.json');data=json.loads(p.read_text());data.update(change);p.write_text(json.dumps(data))
            with self.assertRaises(ValueError):cli.load_plan(p)

    def test_refuses_source_output(self):
        p=self.plan('overwrite.json');data=json.loads(p.read_text());data['output']=str(self.a);p.write_text(json.dumps(data))
        with self.assertRaises(ValueError):cli.load_plan(p)

    def test_srt_speed_and_repeated_source(self):
        p=self.plan('subtitles.json',2)
        data=json.loads(p.read_text());data['clips'].append({'source':str(self.a),'start':0.2,'end':1.2})
        p.write_text(json.dumps(data))
        srt=self.root/'speech.srt';srt.write_text('1\n00:00:00,000 --> 00:00:00,800\nনমস্কার\n\n2\n00:00:01,000 --> 00:00:01,500\nHello\n',encoding='utf-8')
        output=self.root/'retimed.srt';result=cli.retime(p,self.a,srt,output)
        self.assertEqual(result['cues'],4)
        self.assertIn('00:00:00,000 --> 00:00:00,300',output.read_text(encoding='utf-8'))
        with self.assertRaises(FileExistsError):cli.retime(p,self.a,srt,output)

    def test_edl_and_source_map(self):
        p=self.plan('edl.json');output=self.root/'cuts.edl';result=cli.export_edl(p,output)
        self.assertTrue(Path(result['source_map']).exists())
        self.assertIn('00:00:00:05 00:00:01:05',output.read_text())
        with self.assertRaises(ValueError):cli.export_edl(self.plan('edl-fast.json',2),self.root/'fast.edl')

    def test_mcp_protocol(self):
        requests=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{}},
          {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},
          {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'cdvea_catalog','arguments':{}}}]
        p=subprocess.run([sys.executable,str(cli.ROOT/'mcp/cdvea_server.py')],input=''.join(json.dumps(x)+'\n' for x in requests),capture_output=True,text=True,timeout=180)
        self.assertEqual(p.returncode,0,p.stderr)
        replies={x['id']:x['result'] for x in map(json.loads,p.stdout.splitlines())}
        self.assertEqual(replies[1]['serverInfo']['name'],'cdvea')
        self.assertEqual(len(replies[2]['tools']),49)
        self.assertFalse(replies[3]['isError'])

if __name__=='__main__':unittest.main(verbosity=2)
