import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
class RuntimeTests(unittest.TestCase):
    def test_offline_determinism_controls_and_cta(self):
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
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
