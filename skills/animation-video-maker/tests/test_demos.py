"""Exercise the actual creative players and published video streams."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

ROOT = Path(__file__).resolve().parents[1]

class DemoTests(unittest.TestCase):
    @unittest.skipUnless(sync_playwright, 'Playwright is not installed')
    def test_verifier_rejects_missing_video_before_browser(self):
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            shutil.copy2(ROOT / 'demos/verify.py', target / 'verify.py')
            (target / 'catalog.json').write_text(json.dumps([{'video': 'missing.mp4'}]))
            result = subprocess.run([sys.executable, str(target / 'verify.py'), '--browser', 'not-a-browser', '--evidence', str(target / 'evidence')], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Missing demo video', result.stderr)

    @unittest.skipUnless(sync_playwright, 'Playwright is not installed')
    def test_players_are_accessible_offline_and_seekable(self):
        pages = sorted((ROOT / 'demos').glob('*/index.html'))
        self.assertTrue(pages, 'Creative players must ship with the library')
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, executable_path=os.environ.get('RENDER_BROWSER'), args=['--allow-file-access-from-files'])
            try:
                for path in pages:
                    with self.subTest(demo=path.parent.name):
                        page = browser.new_page(reduced_motion='reduce')
                        errors, remote = [], []
                        page.on('pageerror', lambda e: errors.append(str(e)))
                        page.on('request', lambda r: remote.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
                        page.goto(path.as_uri())
                        page.evaluate('() => window.ready')
                        duration = page.evaluate('window.DURATION')
                        self.assertGreater(duration, 0)
                        self.assertLessEqual(duration, 600)
                        self.assertTrue(page.evaluate('Boolean(window.TRANSCRIPT && window.TRANSCRIPT.length > 20)'))
                        self.assertTrue(page.locator('canvas').get_attribute('aria-label'))
                        snap = lambda t: hashlib.sha256(page.evaluate('(t) => window.draw({t})', t).encode()).hexdigest()
                        first = snap(duration * .2)
                        other = snap(duration * .6)
                        self.assertNotEqual(first, other, 'The demo must actually animate')
                        self.assertEqual(first, snap(duration * .2), 'Out-of-order seeks changed the frame')
                        snap(0)
                        still = page.evaluate("document.querySelector('canvas').toDataURL()")
                        page.wait_for_timeout(150)
                        self.assertEqual(still, page.evaluate("document.querySelector('canvas').toDataURL()"))
                        self.assertTrue(page.locator('#play').is_visible())
                        self.assertTrue(page.locator('#replay').is_visible())
                        self.assertEqual(errors, [])
                        self.assertEqual(remote, [])
                        page.close()
            finally:
                browser.close()

    @unittest.skipUnless(shutil.which('ffprobe'), 'ffprobe is not installed')
    def test_delivered_videos_have_real_streams(self):
        pages = sorted((ROOT / 'demos').glob('*/index.html'))
        self.assertTrue(pages)
        manifest = json.loads((ROOT / 'demos/catalog.json').read_text())
        self.assertEqual({p.parent.name for p in pages}, {r['id'] for r in manifest})
        self.assertEqual(len(manifest), len({r['id'] for r in manifest}))
        for path in pages:
            with self.subTest(demo=path.parent.name):
                row = next(r for r in manifest if r['id'] == path.parent.name)
                video = path.parent / 'video.mp4'
                self.assertTrue(video.is_file(), 'Editable demo needs a rendered deliverable')
                data = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video)]))
                streams = [s for s in data['streams'] if s['codec_type'] == 'video']
                self.assertEqual(len(streams), 1)
                stream = streams[0]
                self.assertEqual(stream['codec_name'], 'h264')
                self.assertEqual(stream['pix_fmt'], 'yuv420p')
                self.assertEqual(stream['width'] % 2, 0)
                self.assertEqual(stream['height'] % 2, 0)
                self.assertEqual((stream['width'], stream['height']), (row['width'], row['height']))
                numerator, denominator = map(int, stream['r_frame_rate'].split('/'))
                self.assertEqual(numerator / denominator, row['fps'])
                self.assertAlmostEqual(float(data['format']['duration']), row['duration'], delta=.05)
                self.assertEqual(any(s['codec_type'] == 'audio' for s in data['streams']), row['audio'])
                for key in ('player', 'scene', 'video', 'poster'):
                    self.assertTrue((ROOT / 'demos' / row[key]).is_file())
                self.assertTrue((ROOT / 'styles' / row['style'] / 'SKILL.md').is_file())

if __name__ == '__main__':
    unittest.main()
