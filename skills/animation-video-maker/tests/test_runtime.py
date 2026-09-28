import unittest
import os
import tempfile
from pathlib import Path
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

ROOT=Path(__file__).resolve().parents[1]
@unittest.skipUnless(sync_playwright, "Playwright is not installed")
class RuntimeTests(unittest.TestCase):
    def open_fixture(self, page, folder, options, brand=False, width=1080, height=1920):
        html = (ROOT/"tests/fixture.html").read_text()
        html = html.replace("../assets/", (ROOT/"assets").as_uri()+"/")
        if not brand:
            html = html.replace(f'<script src="{(ROOT/"assets").as_uri()}/brand.js"></script>', "")
        html = html.replace('width="1920" height="1080"', f'width="{width}" height="{height}"')
        html = html[:html.index("<script>window.scene")] + "<script>window.scene=t=>{window.lastTime=t;A.frame('#fff');A.ctx.fillStyle='#f00';A.ctx.fillRect(t*10,1200,80,80);};A.start("+options+");</script>"
        path=Path(folder)/"fixture.html"
        path.write_text(html)
        page.goto(path.as_uri()+"?render=1")
        page.evaluate("()=>window.ready")

    def test_brand_is_optional(self):
        with tempfile.TemporaryDirectory() as folder, sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True, executable_path=os.environ.get("RENDER_BROWSER"), args=["--allow-file-access-from-files"])
            page=browser.new_page()
            errors=[]
            page.on("pageerror",lambda e: errors.append(str(e)))
            self.open_fixture(page,folder,'{title:"Neutral",description:"Neutral scene",duration:8,endcard:false}')
            self.assertEqual(errors,[])
            self.assertEqual(page.evaluate("typeof A"),"object")
            self.assertEqual(page.evaluate("DURATION"),8)
            page.evaluate("renderFrame(8)")
            self.assertEqual(page.evaluate("lastTime"),8)
            self.assertEqual(page.locator("canvas").get_attribute("aria-label"),"Neutral scene")
            # No shared CTA is injected even when endcard is omitted.
            self.open_fixture(page,folder,'{title:"Neutral"}')
            page.evaluate("renderFrame(20)")
            self.assertEqual(page.evaluate("lastTime"),20)
            # Clearing must cover the entire backing canvas even without A.frame.
            page.evaluate("window.scene=t=>{A.ctx.fillStyle='#f00';A.ctx.fillRect(t*10,1200,80,80)}")
            first=page.evaluate("draw({t:1})")
            page.evaluate("draw({t:12})")
            self.assertEqual(first,page.evaluate("draw({t:1})"))
            browser.close()
    def test_duration_endcard_and_geometry(self):
        with tempfile.TemporaryDirectory() as folder, sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True, executable_path=os.environ.get("RENDER_BROWSER"), args=["--allow-file-access-from-files"])
            page=browser.new_page()
            for width,height in [(1080,1920),(1080,1080),(1920,1080)]:
                with self.subTest(size=(width,height)):
                    self.open_fixture(page,folder,'{title:"Neutral",duration:8,endcard:false}',brand=True,width=width,height=height)
                    self.assertEqual(page.evaluate("DURATION"),8)
                    page.evaluate("renderFrame(99)")
                    self.assertEqual(page.evaluate("lastTime"),8)
                    first=page.evaluate("draw({t:4})")
                    page.evaluate("draw({t:7})")
                    self.assertEqual(first,page.evaluate("draw({t:4})"))
                    pixel=page.evaluate("Array.from(A.ctx.getImageData(A.canvas.width-1,A.canvas.height-1,1,1).data)")
                    self.assertEqual(pixel,[255,255,255,255])
            self.open_fixture(page,folder,'{title:"CTA",duration:8}',brand=True,width=1920,height=1080)
            self.assertEqual(page.evaluate("draw({t:5})"),page.evaluate("draw({t:8})"))
            self.assertNotEqual(page.evaluate("draw({t:4})"),page.evaluate("draw({t:5})"))
            for value in ['0','-1','601','NaN','Infinity','"8"','null']:
                with self.subTest(duration=value):
                    with self.assertRaisesRegex(Exception,'duration'):
                        page.evaluate('value=>A.start({duration:eval(value)})',value)
            browser.close()

    def test_short_playback_stops_and_restarts(self):
        with tempfile.TemporaryDirectory() as folder, sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True, executable_path=os.environ.get("RENDER_BROWSER"), args=["--allow-file-access-from-files"])
            page=browser.new_page(reduced_motion='reduce')
            self.open_fixture(page,folder,'{title:"Short",duration:.1,endcard:false}')
            page.goto(page.url.split('?')[0])
            page.evaluate('()=>window.ready')
            page.locator('#play').click()
            page.wait_for_function("lastTime===.1 && document.getElementById('play').textContent==='Play'")
            page.locator('#play').click()
            page.wait_for_function("lastTime<.1")
            page.wait_for_function("lastTime===.1")
            page.locator('#replay').click()
            page.wait_for_function("lastTime<.1")
            page.wait_for_function("lastTime===.1")
            browser.close()

    def test_offline_determinism_controls_and_cta(self):
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True, executable_path=os.environ.get("RENDER_BROWSER"), args=["--allow-file-access-from-files"])
            page=browser.new_page(reduced_motion='reduce')
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto((ROOT/'tests/fixture.html').as_uri())
            self.assertTrue(page.evaluate("typeof window.ready !== 'undefined'"), 'runtime readiness contract is missing')
            page.evaluate('()=>window.ready')
            self.assertEqual(page.evaluate('window.DURATION'),20)
            snap=lambda:page.evaluate("document.querySelector('canvas').toDataURL()")
            a=snap();page.wait_for_timeout(200);self.assertEqual(a,snap())
            page.locator('#play').click();page.wait_for_timeout(250);self.assertNotEqual(a,snap())
            page.locator('#play').click();a=snap();page.wait_for_timeout(120);self.assertEqual(a,snap())
            page.locator('#replay').click();page.wait_for_timeout(100);self.assertNotEqual(a,snap())
            page.goto((ROOT/'tests/fixture.html').as_uri()+'?render=1');page.evaluate('()=>window.ready')
            first=page.evaluate('window.draw({t:4})');page.evaluate('window.draw({t:12})');self.assertEqual(first,page.evaluate('window.draw({t:4})'))
            self.assertEqual(page.evaluate('window.draw({t:17})'),page.evaluate('window.draw({t:19.9})'))
            self.assertFalse(page.locator('#play').is_visible())
            self.assertEqual(errors,[])
            browser.close()
if __name__=='__main__':unittest.main()
