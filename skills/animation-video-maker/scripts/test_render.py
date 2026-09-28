"""Real browser/FFmpeg integration tests; no downloaded HTML or dependencies."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('render.py')
BROWSER = os.environ.get('RENDER_BROWSER', '')
HTML = '''<!doctype html><canvas id="canvas" width="1920" height="1080"></canvas>
<script>
window.DURATION=20; window.ready=Promise.resolve();
window.renderFrame=t=>{const c=document.querySelector('canvas').getContext('2d');
c.fillStyle='#22262b';c.fillRect(0,0,1920,1080);c.fillStyle='#00b4e8';
c.fillRect(50+t*10,50,300,200);};
window.draw=({t})=>{renderFrame(t);return canvas.toDataURL('image/jpeg',.94).split(',')[1]};
</script>'''

class RenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='canvas-render-test-')
        self.root = Path(self.tmp.name)
        self.html = self.root/'fixture.html'
        self.html.write_text(HTML)
        self.out = self.root/'fixture.mp4'
    def tearDown(self):
        self.tmp.cleanup()
    def run_cli(self, *args):
        browser_args=['--browser',BROWSER] if BROWSER else []
        return subprocess.run([sys.executable,str(SCRIPT),str(self.html),str(self.out),
            *browser_args,*args],capture_output=True,text=True,timeout=90)
    def test_real_video_and_qa(self):
        r = self.run_cli('--duration','0.4','--fps','5')
        self.assertEqual(r.returncode,0,r.stderr)
        qa=json.loads(self.out.with_suffix('.qa.json').read_text())
        self.assertEqual(qa['status'],'ok')
        self.assertEqual(qa['probe']['frames'],2)
        self.assertEqual(qa['probe']['width'],1920)
        self.assertEqual(qa['probe']['height'],1080)
        self.assertAlmostEqual(qa['probe']['duration'],.4,places=3)
        self.assertEqual([s['t'] for s in qa['samples']],[0,4,8,12,16,19.9])
        self.assertTrue(all(s['deterministic'] for s in qa['samples']))
        self.assertEqual(len(list(self.root.glob('fixture.samples/*.png'))),6)
        print('REAL QA:', json.dumps(qa['probe']), 'elapsed:',qa['elapsed_seconds'])

    def test_other_declared_duration_and_overrun(self):
        self.html.write_text(HTML.replace('window.DURATION=20', 'window.DURATION=10'))
        r = self.run_cli('--duration', '10', '--samples-only')
        self.assertEqual(r.returncode, 0, r.stderr)
        qa = json.loads(self.out.with_suffix('.qa.json').read_text())
        self.assertEqual([s['t'] for s in qa['samples']], [0,2,4,6,8,9.95])
        r = self.run_cli('--duration', '11', '--samples-only', '--overwrite')
        self.assertEqual(r.returncode, 1, r.stderr)

    def test_portrait_and_square_video(self):
        for width,height in [(1080,1920),(1080,1080)]:
            with self.subTest(size=(width,height)):
                self.html.write_text(HTML.replace('width="1920" height="1080"',f'width="{width}" height="{height}"'))
                r=self.run_cli('--duration','.4','--fps','5','--overwrite')
                self.assertEqual(r.returncode,0,r.stderr)
                qa=json.loads(self.out.with_suffix('.qa.json').read_text())
                self.assertEqual((qa['probe']['width'],qa['probe']['height']),(width,height))
                self.assertEqual(qa['canvas'],dict(width=width,height=height))
                self.assertEqual(qa['probe']['frames'],2)
                self.assertTrue(all(s['deterministic'] for s in qa['samples']))

    def test_unsafe_canvas_dimensions_rejected(self):
        for width,height in [(0,1080),(1,2),(1081,1920),(1920,1079),(8194,2),(4096,4096)]:
            with self.subTest(size=(width,height)):
                self.html.write_text(HTML.replace('width="1920" height="1080"',f'width="{width}" height="{height}"'))
                r=self.run_cli('--samples-only')
                self.assertEqual(r.returncode,1,r.stderr)
                self.assertIn('canvas dimensions',r.stderr)
                self.assertFalse(self.out.exists())

    def test_invalid_cli(self):
        for flags in [('--fps','0'),('--fps','-1'),('--fps','121'),('--fps','nan'),
                      ('--duration','nan'),('--duration','inf'),('--duration','0'),
                      ('--duration','-3'),('--duration','601'),('--duration','.01'),
                      ('--browser',str(self.root/'missing'))]:
            with self.subTest(flags=flags):
                r=self.run_cli(*flags)
                self.assertEqual(r.returncode,2,r.stderr)
                self.assertFalse(self.out.exists())
        self.html.unlink()
        self.assertEqual(self.run_cli().returncode,2)

    def test_samples_only(self):
        r=self.run_cli('--samples-only')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertFalse(self.out.exists())
        qa=json.loads(self.out.with_suffix('.qa.json').read_text())
        self.assertNotIn('probe',qa)
        self.assertEqual(qa['console_errors'],[])
        self.assertEqual(qa['js_errors'],[])
        self.assertEqual(len(qa['samples']),6)
        self.assertTrue(all(s['deterministic'] for s in qa['samples']))
        self.assertEqual(self.run_cli('--samples-only').returncode,2)

    def test_existing_output_and_failed_overwrite_preserved(self):
        self.out.write_bytes(b'previous user output')
        r=self.run_cli('--samples-only')
        self.assertEqual(r.returncode,2,r.stderr)
        self.assertEqual(self.out.read_bytes(),b'previous user output')
        previous_qa=self.out.with_suffix('.qa.json')
        previous_qa.write_text('previous QA')
        self.html.write_text(HTML.replace('window.ready=Promise.resolve()',
                                         "window.ready=Promise.reject(Error('fixture failure'))"))
        r=self.run_cli('--overwrite','--duration','.4','--fps','5')
        self.assertEqual(r.returncode,1,r.stderr)
        self.assertEqual(self.out.read_bytes(),b'previous user output')
        self.assertEqual(previous_qa.read_text(),'previous QA')
        failure=json.loads(next(self.root.glob('*.failed-*.qa.json')).read_text())
        self.assertEqual(failure['status'],'failed')
        self.assertIn('fixture failure',failure['error'])
        self.assertEqual(list(self.root.glob('.fixture-*')),[])

    def test_failed_ffprobe_preserves_previous_video(self):
        self.out.write_bytes(b'previous video')
        self.html.write_text(HTML.replace("return canvas.toDataURL('image/jpeg',.94)",
            "const tiny=document.createElement('canvas');tiny.width=64;tiny.height=64;return tiny.toDataURL('image/jpeg',.94)"))
        r=self.run_cli('--overwrite','--duration','.2','--fps','5')
        self.assertEqual(r.returncode,1,r.stderr)
        self.assertEqual(self.out.read_bytes(),b'previous video')
        failure=json.loads(next(self.root.glob('*.failed-*.qa.json')).read_text())
        self.assertIn('ffprobe geometry/frame mismatch',failure['error'])
        self.assertEqual(list(self.root.glob('.fixture-*')),[])

    def test_successful_explicit_overwrite(self):
        self.out.write_bytes(b'old output')
        r=self.run_cli('--overwrite','--duration','.2','--fps','5')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertNotEqual(self.out.read_bytes(),b'old output')
        self.assertEqual(json.loads(self.out.with_suffix('.qa.json').read_text())['probe']['frames'],1)

    def test_network_is_blocked_and_console_error_reported(self):
        self.html.write_text(HTML.replace('</script>', """
        window.ready=fetch('https://example.com/must-not-connect').then(
          ()=>{throw Error('network was not blocked')},()=>{});
        console.error('intentional fixture console error');
        </script>"""))
        r=self.run_cli('--samples-only')
        self.assertEqual(r.returncode,1,r.stderr)
        qa=json.loads(next(self.root.glob('*.failed-*.qa.json')).read_text())
        self.assertIn('https://example.com/must-not-connect',qa['blocked_requests'])
        self.assertIn('intentional fixture console error',qa['console_errors'])
        self.assertFalse(self.out.exists())

    def test_javascript_errors_reported(self):
        self.html.write_text(HTML.replace('</script>',"throw Error('intentional JS error');</script>"))
        r=self.run_cli('--samples-only')
        self.assertEqual(r.returncode,1,r.stderr)
        qa=json.loads(next(self.root.glob('*.failed-*.qa.json')).read_text())
        self.assertTrue(any('intentional JS error' in x for x in qa['js_errors']))

    def test_nondeterminism_is_rejected(self):
        self.html.write_text(HTML.replace('window.renderFrame=t=>{',
                             'let tick=0; window.renderFrame=t=>{t=++tick;'))
        r=self.run_cli('--samples-only')
        self.assertEqual(r.returncode,1,r.stderr)
        qa=json.loads(next(self.root.glob('*.failed-*.qa.json')).read_text())
        self.assertIn('non-deterministic',qa['error'])
        self.assertFalse(all(s['deterministic'] for s in qa['samples']))

if __name__ == '__main__':
    unittest.main(verbosity=2)
