#!/usr/bin/env python3
"""Check neutral demos offline. Existing Playwright, FFmpeg required."""
import argparse
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--browser', required=True)
    p.add_argument('--evidence', required=True, type=Path)
    a = p.parse_args()
    a.evidence.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parent
    rows = json.loads((root/'catalog.json').read_text())
    for row in rows:
        if not (root/row['video']).is_file():
            raise FileNotFoundError('Missing demo video: ' + row['video'])
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=a.browser, headless=True,
                                     args=['--allow-file-access-from-files'])
        for row in rows:
            page = browser.new_page(reduced_motion='reduce')
            errors = []
            remote = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('request', lambda r: remote.append(r.url) if r.url.startswith(('https:', 'http:')) else None)
            page.goto((root/row['player']).as_uri())
            page.evaluate('()=>window.ready')
            snap = lambda: page.evaluate('document.getElementById("canvas").toDataURL()')
            first = snap()
            page.wait_for_timeout(160)
            assert first == snap(), 'Reduced-motion preview moved'
            assert page.locator('#transcript').text_content()
            page.locator('#play').click()
            page.wait_for_timeout(1400)
            assert first != snap(), 'Play did not move'
            page.locator('#play').click()
            paused = snap()
            page.wait_for_timeout(130)
            assert paused == snap(), 'Pause did not stop'
            page.locator('#replay').click()
            assert first == snap(), 'Reduced-motion replay should reset and pause'
            page.locator('#seek').fill(format(row['duration']/2, 'g'))
            assert first != snap(), 'Seek did not move'
            page.goto((root/row['player']).as_uri()+'?render=1')
            page.evaluate('()=>window.ready')
            hashes = []
            for t in [0, .5, 2.4, 4.2, 6.9, row['duration']-.01]:
                frame = page.evaluate('t=>window.draw({t})', t)
                page.evaluate('t=>window.draw({t})', row['duration']-t)
                assert frame == page.evaluate('t=>window.draw({t})', t)
                hashes.append(t)
            loop = None
            if row['id'] in ('ui-morph', 'recursive-portal'):
                loop = page.evaluate('window.draw({t:0})===window.draw({t:window.DURATION})')
                assert loop, 'Loop endpoints differ'
            assert not errors and not remote, (errors, remote)
            result = dict(id=row['id'], controls=True, reduced_motion=True,
                          deterministic_times=hashes, loop_endpoint_identical=loop,
                          errors=errors, remote_requests=remote)
            video = root/row['video']
            probe = subprocess.run(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(video)],check=True,capture_output=True,text=True)
            streams = json.loads(probe.stdout)['streams']
            visual = next(s for s in streams if s['codec_type']=='video')
            assert (visual['width'],visual['height']) == (row['width'],row['height'])
            assert int(visual['nb_read_frames']) == row['duration']*row['fps']
            assert visual['r_frame_rate'] == '30/1'
            assert abs(float(visual['duration'])-row['duration']) < .002
            assert visual['codec_name'] == 'h264' and visual['pix_fmt'] == 'yuv420p'
            assert any(s['codec_type']=='audio' for s in streams) == row['audio']
            result['streams'] = streams
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f"fps=1/{row['duration']/6},scale=320:-1,tile=3x2",'-frames:v','1',str(a.evidence/(row['id']+'-decoded.jpg'))],check=True)
            results.append(result)
            page.close()
        browser.close()
    (a.evidence/'demo-checks.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps([{'id':r['id'],'passed':True} for r in results]))

if __name__ == '__main__':
    main()
