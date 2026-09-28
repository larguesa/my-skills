#!/usr/bin/env python3
"""Offline Canvas HTML -> MP4. Requires Playwright, FFmpeg and ffprobe."""
import argparse
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit

TIMES = (0, 4, 8, 12, 16, 19.9)


def arguments():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--duration', type=float, default=20)
    p.add_argument('--fps', type=int, default=30)
    p.add_argument('--browser', help='Chrome/Chromium executable; default: Playwright Chromium')
    p.add_argument('--samples-only', action='store_true')
    p.add_argument('--overwrite', action='store_true')
    a = p.parse_args()
    if not math.isfinite(a.duration) or not .01 <= a.duration <= 600:
        p.error('duration must be finite and between 0.01 and 600 seconds')
    if not 1 <= a.fps <= 120:
        p.error('fps must be an integer between 1 and 120')
    a.frames = round(a.duration * a.fps)
    if not 1 <= a.frames <= 36000 or abs(a.frames - a.duration*a.fps) > 1e-7:
        p.error('duration * fps must be an integer from 1 to 36000')
    a.input = a.input.resolve()
    a.output = a.output.absolute()
    if not a.input.is_file() or a.input.suffix.lower() not in ('.html', '.htm'):
        p.error('input must be an existing local HTML file')
    if a.output.suffix.lower() != '.mp4' or a.output.resolve() == a.input:
        p.error('output must be a distinct .mp4 path')
    if a.browser and not Path(a.browser).is_file():
        p.error('browser executable does not exist')
    a.qa = a.output.with_suffix('.qa.json')
    a.samples = a.output.with_suffix('.samples')
    for target in (a.output, a.qa, a.samples):
        if target.exists() and not a.overwrite:
            p.error(f'output exists (use --overwrite): {target}')
    if not a.samples_only:
        for executable in ('ffmpeg', 'ffprobe'):
            if not shutil.which(executable):
                p.error(f'{executable} not found on PATH')
    return a


def probe(path, frames, fps, width=1920, height=1080):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-count_frames', '-show_entries', 'stream=width,height,nb_read_frames,duration,r_frame_rate',
        '-of', 'json', str(path)], check=True, capture_output=True, text=True, timeout=120)
    s = json.loads(r.stdout)['streams'][0]
    result = dict(width=int(s['width']), height=int(s['height']),
                  frames=int(s['nb_read_frames']), duration=float(s['duration']), fps=s['r_frame_rate'])
    numerator, denominator = map(int, result['fps'].split('/'))
    if (result['width'], result['height'], result['frames']) != (width, height, frames):
        raise RuntimeError(f'ffprobe geometry/frame mismatch: {result}')
    if abs(result['duration'] - frames/fps) > .002 or numerator/denominator != fps:
        raise RuntimeError(f'ffprobe duration/fps mismatch: {result}')
    return result


def render(a):
    from playwright.sync_api import sync_playwright
    started = time.monotonic()
    qa = dict(status='running', input=str(a.input), output=str(a.output),
              duration=a.duration, fps=a.fps, samples=[], console_errors=[], js_errors=[], blocked_requests=[])
    a.output.parent.mkdir(parents=True, exist_ok=True)
    # Same filesystem as destination: never expose a partial MP4.
    with tempfile.TemporaryDirectory(prefix=f'.{a.output.stem}-', dir=a.output.parent) as tmp:
        stage = Path(tmp)
        sample_dir = stage/'samples'
        sample_dir.mkdir()
        movie = stage/'video.mp4'
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, executable_path=a.browser,
                    args=['--disable-background-networking', '--disable-component-update',
                          '--disable-sync', '--no-first-run', '--disable-quic',
                          '--host-resolver-rules=MAP * ~NOTFOUND', '--allow-file-access-from-files'])
                qa['browser_version'] = browser.version
                context = browser.new_context(viewport={'width':1920,'height':1080},
                    device_scale_factor=1, service_workers='block', offline=True,
                    accept_downloads=False)
                def route(request):
                    if urlsplit(request.request.url).scheme in ('file', 'data'):
                        request.continue_()
                    else:
                        qa['blocked_requests'].append(request.request.url)
                        request.abort()
                context.route('**/*', route)
                context.route_web_socket('**/*', lambda ws: ws.close())
                page = context.new_page()
                context.on('page', lambda extra: extra.close() if extra != page else None)
                page.on('console', lambda msg: qa['console_errors'].append(msg.text) if msg.type == 'error' else None)
                page.on('pageerror', lambda error: qa['js_errors'].append(str(error)))
                page.goto(a.input.as_uri()+'?render=1', wait_until='load', timeout=30000)
                contract = page.evaluate('''async requested => {
                    if (!window.ready || typeof window.ready.then !== 'function') throw Error('window.ready Promise missing');
                    await Promise.race([window.ready, new Promise((_, reject) => setTimeout(()=>reject(Error('ready timeout')),30000))]);
                    await document.fonts.ready;
                    const c=document.getElementById('canvas');
                    if (!c || c.tagName!=='CANVAS' || c.width<2 || c.height<2 || c.width>8192 || c.height>8192 || c.width%2 || c.height%2 || c.width*c.height>8294400) throw Error('canvas dimensions must be even, 2..8192 per side and at most 8294400 pixels');
                    if (typeof window.renderFrame!=='function' || typeof window.draw!=='function') throw Error('renderFrame/draw missing');
                    if (!Number.isFinite(window.DURATION) || window.DURATION <= 0 || window.DURATION > 600 || window.DURATION < requested) throw Error('DURATION must be finite, positive, at most 600 and cover requested duration');
                    return {duration:window.DURATION,width:c.width,height:c.height};
                }''', a.duration)
                declared_duration = contract['duration']
                width, height = contract['width'], contract['height']
                qa['canvas'] = dict(width=width, height=height)
                page.set_viewport_size(qa['canvas'])
                def png(t):
                    return base64.b64decode(page.evaluate('''async t => {
                        await window.renderFrame(t);
                        return document.getElementById('canvas').toDataURL('image/png').split(',')[1];
                    }''', t), validate=True)
                # Revisit samples in reverse order to detect accumulated drawing state.
                for t in (round(value * declared_duration / 20, 6) for value in TIMES):
                    raw = png(t)
                    name = f't-{t:08.3f}.png'
                    (sample_dir/name).write_bytes(raw)
                    qa['samples'].append(dict(t=t, file=str(a.samples/name), sha256=hashlib.sha256(raw).hexdigest()))
                for sample in reversed(qa['samples']):
                    sample['repeat_sha256'] = hashlib.sha256(png(sample['t'])).hexdigest()
                    sample['deterministic'] = sample['sha256'] == sample['repeat_sha256']
                if not all(s['deterministic'] for s in qa['samples']):
                    raise RuntimeError('non-deterministic sample rendering')
                if not a.samples_only:
                    with tempfile.TemporaryFile() as log:
                        command = ['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y',
                            '-f','image2pipe','-vcodec','mjpeg','-framerate',str(a.fps),'-i','pipe:0',
                            '-an','-c:v','libx264','-threads','2','-preset','fast','-crf','18',
                            '-pix_fmt','yuv420p','-movflags','+faststart',str(movie)]
                        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log)
                        try:
                            for i in range(a.frames):
                                jpeg = page.evaluate('t => window.draw({t})', i/a.fps)
                                proc.stdin.write(base64.b64decode(jpeg, validate=True))
                            proc.stdin.close()
                            code = proc.wait(timeout=120)
                            if code:
                                log.seek(0)
                                raise RuntimeError('ffmpeg: '+log.read().decode(errors='replace'))
                        finally:
                            if proc.poll() is None:
                                proc.kill()
                                proc.wait()
                            if proc.stdin and not proc.stdin.closed:
                                proc.stdin.close()
                    qa['probe'] = probe(movie, a.frames, a.fps, width, height)
                if qa['console_errors'] or qa['js_errors']:
                    raise RuntimeError('browser console/JavaScript errors; see QA JSON')
                context.close()
                browser.close()
            # Recheck collisions before publishing. No previous video is removed on failure.
            for target in (a.output, a.qa, a.samples):
                if target.exists() and not a.overwrite:
                    raise FileExistsError(str(target))
            a.samples.mkdir(exist_ok=True)
            for image in sample_dir.iterdir():
                os.replace(image, a.samples/image.name)
            qa['status'] = 'ok'
            qa['elapsed_seconds'] = round(time.monotonic()-started, 3)
            report = stage/'qa.json'
            report.write_text(json.dumps(qa, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
            os.replace(report, a.qa)
            if not a.samples_only:
                os.replace(movie, a.output)
        except Exception as error:
            qa['status'] = 'failed'
            qa['error'] = str(error)
            qa['elapsed_seconds'] = round(time.monotonic()-started, 3)
            # Do not replace a prior successful QA report on failure.
            with tempfile.NamedTemporaryFile(mode='w', prefix=a.output.stem+'.failed-', suffix='.qa.json',
                    dir=a.output.parent, encoding='utf-8', delete=False) as failure:
                json.dump(qa, failure, indent=2, ensure_ascii=False)
                print(f'Failure QA: {failure.name}', file=sys.stderr)
            raise
    print(json.dumps(dict(status='ok', qa=str(a.qa), elapsed_seconds=qa['elapsed_seconds'],
                         output=None if a.samples_only else str(a.output))))


def main():
    a = arguments()
    try:
        render(a)
    except Exception as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
