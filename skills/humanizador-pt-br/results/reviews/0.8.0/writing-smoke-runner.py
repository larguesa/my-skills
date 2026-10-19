import os,pathlib,sys,json,subprocess,hashlib,time,urllib.request,urllib.error,concurrent.futures,datetime
W=pathlib.Path(os.environ['HUMANIZADOR_SMOKE_OUTPUT']);W.mkdir(parents=True,exist_ok=True);S=pathlib.Path(__file__).resolve().parents[3];R=S.parents[1];D=W/'writing-smoke'
sys.path.insert(0,str(S/'results/scripts'));from generation_eval import parse_prompts,SELECTORS
D.mkdir(exist_ok=True)
key=os.environ['OPENROUTER_API_KEY']
cases=[c for c in parse_prompts((S/'results/PROMPTS.md').read_text()) if c['ordinal'] in [1,3,13,17,23,24]]
assert len(cases)==6
inputs=[]
for c in cases:
 profile,genre=SELECTORS[c['ordinal']-1]
 brief=subprocess.check_output(['python3',str(S/'scripts/humanizar.py'),'brief','--profile',profile,'--genre',genre,'--breadth','2','--randomness','0','--seed','17'],text=True)
 payload={'model':'xiaomi/mimo-v2.6-pro','messages':[{'role':'system','content':(S/'SKILL.md').read_text()+'\n\n'+brief},{'role':'user','content':c['prompt']}],'reasoning':{'enabled':False},'max_tokens':16384,'provider':{'allow_fallbacks':False,'require_parameters':True},'stream':False}
 inputs.append({'case':c,'payload':payload})
plan={'kind':'Functional writing smoke, not A/B nor perception benchmark','model':'xiaomi/mimo-v2.6-pro','case_ids':[c['ordinal'] for c in cases],'frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':inputs,'source_hashes':{f:hashlib.sha256((S/f).read_bytes()).hexdigest() for f in ['SKILL.md','scripts/humanizar.py','references/catalogo.json','references/estilos.json','results/PROMPTS.md']}}
with (D/'plan.json').open('x') as f:json.dump(plan,f,ensure_ascii=False,indent=2)
def run(entry):
 c=entry['case']; n=f'{c["ordinal"]:02}';payload=entry['payload']
 with (D/f'{n}-request.json').open('x') as f:json.dump(payload,f,ensure_ascii=False)
 t=time.monotonic();req=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=1200) as r:raw=r.read();status=r.status
 except urllib.error.HTTPError as e:raw=e.read();status=e.code
 (D/f'{n}-response.json').write_bytes(raw);data=json.loads(raw)
 record={'case':c,'http':status,'seconds':time.monotonic()-t,'model':data.get('model'),'id':data.get('id'),'usage':data.get('usage'),'finish_reason':data.get('choices',[{}])[0].get('finish_reason')}
 if status==200 and record['finish_reason']=='stop':
  text=data['choices'][0]['message'].get('content',''); (D/f'{n}-text.txt').write_text(text);(D/f'{n}-prompt.txt').write_text(c['prompt'])
  p=subprocess.run(['python3',str(S/'scripts/humanizar.py'),'check',str(D/f'{n}-text.txt'),'--briefing',str(D/f'{n}-prompt.txt')],capture_output=True,text=True)
  record.update(check_exit=p.returncode,check=json.loads(p.stdout),text=text)
 (D/f'{n}-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(n,status,record['finish_reason'],record.get('check_exit'),flush=True);return record
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(run,inputs))
(D/'summary.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('completed',len(records),'deliverable',sum(r.get('check',{}).get('deliverable',False) for r in records))
