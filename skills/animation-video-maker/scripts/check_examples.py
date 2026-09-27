#!/usr/bin/env python3
"""Exercise every original example offline. Outputs review evidence, not a quality score."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
INSTRUMENT=r'''(() => {
const proto=CanvasRenderingContext2D.prototype,original=proto.fillText;
window.__texts=[];window.__overflow=[];
proto.fillText=function(s,x,y,...rest){
 if(this.globalAlpha>.1){
  window.__texts.push(String(s));const m=this.measureText(s),tr=this.getTransform();
  let left=x-(this.textAlign==='center'?m.width/2:['right','end'].includes(this.textAlign)?m.width:0);
  let corners=[[left,y-m.actualBoundingBoxAscent],[left+m.width,y-m.actualBoundingBoxAscent],[left,y+m.actualBoundingBoxDescent],[left+m.width,y+m.actualBoundingBoxDescent]].map(([a,b])=>[tr.a*a+tr.c*b+tr.e,tr.b*a+tr.d*b+tr.f]);
  if(corners.some(([a,b])=>a<0||a>1920||b<0||b>1080))window.__overflow.push(String(s));
 }return original.call(this,s,x,y,...rest);
};})();'''

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Evidence directory, defaults to a fresh system temporary directory')
    parser.add_argument('--style',help='Check one exact catalog id')
    args=parser.parse_args()
    output=args.output or Path(tempfile.mkdtemp(prefix='animation-qa-'))
    output.mkdir(parents=True,exist_ok=True)
    rows=json.loads((ROOT/'references/catalog.json').read_text())
    if args.style:
        rows=[r for r in rows if r['id']==args.style]
        if not rows:parser.error('unknown style id')
    results=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--allow-file-access-from-files'])
        for row in rows:
            errors=[];network=[]
            context=browser.new_context(viewport={'width':1920,'height':1080},offline=True,reduced_motion='reduce')
            page=context.new_page();page.add_init_script(INSTRUMENT)
            page.on('pageerror',lambda err:errors.append(str(err)))
            page.on('request',lambda req:network.append(req.url) if req.url.startswith(('http:','https:')) else None)
            path=ROOT/'examples'/row['id']/'index.html'
            record={'style':row['id'],'errors':errors,'network':network}
            try:
                page.goto(path.as_uri()+'?render=1');page.evaluate('()=>window.ready')
                checks=page.evaluate('''() => {
                  for(let i=0;i<=80;i++)window.renderFrame(i/4);
                  const a=window.draw({t:4});window.draw({t:12});const b=window.draw({t:4});
                  return {overflow:[...new Set(window.__overflow)],texts:[...new Set(window.__texts)],
                    deterministic:a===b,ctaStable:window.draw({t:17})===window.draw({t:19.9}),
                    fonts:[...document.fonts].map(f=>({family:f.family,status:f.status})),
                    transcript:window.TRANSCRIPT,dimensions:[canvas.width,canvas.height,window.DURATION]};
                }''')
                record.update(checks)
                folder=output/row['id'];folder.mkdir(exist_ok=True)
                for t in (0,2,5,8,11,14,16.8,19.9):
                    page.evaluate('t=>window.renderFrame(t)',t)
                    page.locator('canvas').screenshot(path=str(folder/f'{t:04.1f}.png'))
                page.goto(path.as_uri());page.evaluate('()=>window.ready')
                snapshot=lambda:page.evaluate("canvas.toDataURL()")
                first=snapshot();page.wait_for_timeout(150);reduced=first==snapshot()
                page.locator('#play').click();page.wait_for_timeout(1800);playing=first!=snapshot()
                page.locator('#play').click();paused=snapshot();page.wait_for_timeout(150);pause_ok=paused==snapshot()
                page.locator('#replay').click();page.wait_for_timeout(100);replay=paused!=snapshot()
                record['controls']={'reduced_motion':reduced,'play':playing,'pause':pause_ok,'replay':replay}
                record['scene_sha256']=hashlib.sha256(path.with_name('scene.js').read_bytes()).hexdigest()
                record['passed']=not errors and not network and not checks['overflow'] and checks['deterministic'] and checks['ctaStable'] and checks['dimensions']==[1920,1080,20] and bool(checks['transcript']) and all(f['status']=='loaded' for f in checks['fonts']) and all(record['controls'].values())
            except Exception as exc:
                record.update(passed=False,error=str(exc))
            finally:context.close()
            results.append(record)
            (output/'checks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
            print(json.dumps({'style':row['id'],'passed':record['passed'],'overflow':record.get('overflow',[]),'errors':errors}),flush=True)
        browser.close()
    return 0 if results and all(r['passed'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
