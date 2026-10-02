"""Offline contract tests. Fake transport data is not inference evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest

HERE = Path(__file__).resolve().parent


def runner():
    path = HERE / 'frontier_bench.py'
    if not path.exists():
        raise AssertionError('frontier runner missing')
    spec = importlib.util.spec_from_file_location('frontier', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def config(b):
    def route(model):
        return dict(model=model, provider='test-route', observed_provider='Test',
                    returned_models=[model], reasoning={'effort':'medium'})
    return dict(routes=[route(m) for m in b.MODELS],
                judges=[dict(route(m), kind='decisions' if m.startswith('typesafe/') else 'chat')
                        for m in b.JUDGES])


class FrontierTests(unittest.TestCase):
    def test_freeze_snapshots_exact_balanced_design_and_rejects_tampering(self):
        b = runner()
        tasks = b.strict_json((HERE / 'frontier_cases.json').read_text())
        self.assertEqual(len(tasks), 8)
        self.assertEqual(sum(t['language']=='en' for t in tasks), 4)
        self.assertEqual(sum(t['language']=='pt' for t in tasks), 4)
        self.assertEqual(len({t['id'] for t in tasks}), 8)
        for category in {t['category'] for t in tasks}:
            pair = [t for t in tasks if t['category']==category]
            self.assertEqual({t['language'] for t in pair}, {'en','pt'})
            self.assertEqual(pair[0]['reference'], pair[1]['reference'])
            self.assertEqual(pair[0]['rubric'], pair[1]['rubric'])
        slots = b.schedule(tasks, 42)
        self.assertEqual(len(slots), 336)
        self.assertEqual(len({s['id'] for s in slots}), 336)
        self.assertEqual(slots, b.schedule(tasks, 42))
        self.assertEqual([s['repeat'] for s in slots], [0]*168+[1]*168)
        for i in range(0, 336, 3):
            trio = slots[i:i+3]
            self.assertEqual(len({(s['model'],s['task'],s['repeat']) for s in trio}), 1)
            self.assertEqual({s['arm'] for s in trio}, set(b.ARMS))
        skill = (HERE.parents[1] / 'SKILL.md').read_bytes()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b.freeze(root, config(b))
            p = b.verify(root)
            self.assertEqual(p['tasks'], tasks)
            self.assertEqual(p['settings']['max_tokens'], 8192)
            self.assertEqual(p['settings']['max_calls'], 8)
            self.assertEqual((root/'SKILL.snapshot.md').read_bytes(), skill)
            self.assertEqual((root/'frontier.snapshot.py').read_bytes(), (HERE/'frontier_bench.py').read_bytes())
            for arm in b.ARMS:
                request = b.payload({'model':b.MODELS[0], 'arm':arm}, tasks[0], p['routes'][0], skill.decode())
                self.assertEqual(request['max_tokens'], 8192)
                self.assertFalse(request['stream'])
                self.assertFalse(request['provider']['allow_fallbacks'])
                self.assertTrue(request['provider'].get('require_parameters'), 'required parameter enforcement missing')
                self.assertNotIn('temperature', request)
                self.assertEqual(request['reasoning'], {'effort':'medium'})
                self.assertEqual(request['messages'][0]['content'], b.NEUTRAL)
                if arm=='skill': self.assertEqual(request['messages'][1]['content'], skill.decode())
                if arm=='short_control': self.assertEqual(request['messages'][1]['content'], b.SHORT)
            (root/'frontier_cases.json').write_text('[]')
            with self.assertRaises(ValueError): b.verify(root)
        bad = config(b)
        bad['routes'][0]['model'] = 'replacement'
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): b.freeze(Path(d), bad)


class EpisodeTests(unittest.TestCase):
    def test_dependent_tools_durable_resume_and_full_episode_accounting(self):
        b = runner()
        self.assertTrue(hasattr(b, 'run'), 'episode runner missing')
        tasks = b.strict_json((HERE/'frontier_cases.json').read_text())
        task = next(t for t in tasks if t['id']=='agentic_structured_en')
        c = config(b)
        c['tasks'] = [task]
        slot = dict(id='offline', task=task['id'], model=b.MODELS[0], arm='skill', repeat=0)
        c['slots'] = [slot]
        names = task['required_reads']
        final = json.dumps(task['expected_by_language']['en'])
        calls = []
        def call(kind, body):
            n = len(calls)
            calls.append(copy.deepcopy(body))
            message = {'content':'Checking the next source.', 'reasoning_details':[{'type':'reasoning.encrypted','data':'offline-opaque-continuation'}]}
            if n < 4:
                message['tool_calls'] = [{'id':f't{n}', 'type':'function', 'function':{'name':'read_record','arguments':json.dumps({'name':names[n]})}}]
            else: message['content'] = final
            return 200, dict(id=f'gen-{n}', model=slot['model'], provider='Test',
                             choices=[dict(message=message, finish_reason='tool_calls' if n<4 else 'stop')],
                             usage=dict(prompt_tokens=10, completion_tokens=4, total_tokens=14, cost=0.01,
                                        prompt_tokens_details={'cached_tokens':0}, completion_tokens_details={'reasoning_tokens':5}))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertEqual(b.run(root,c,'exact skill',call), 'complete')
            self.assertEqual(b.run(root,c,'exact skill',call), 'complete')
            self.assertEqual(len(calls),5)
            events = b.rows(root/'events.jsonl')
            self.assertEqual(sum(e['event']=='call_start' for e in events),5)
            self.assertEqual(sum(e['event']=='call_result' for e in events),5)
            result = events[-1]
            self.assertEqual(result['final'],final)
            self.assertEqual(len(result['progress']),4)
            self.assertTrue(result['mechanical']['pass'])
            self.assertEqual(result['totals']['in'],50)
            self.assertEqual(result['totals']['out'],20)
            self.assertEqual(result['totals']['cache_read'],0)
            self.assertIsNone(result['totals']['cache_write'])
            self.assertEqual(result['totals']['cost'],'0.05')
            self.assertTrue(result['totals']['reasoning_inconsistent'])
            self.assertEqual(calls[1]['messages'][-1]['role'],'tool')
            self.assertIn('reasoning_details',calls[1]['messages'][-2], 'native continuation must be retained')
            self.assertNotIn('reasoning_details',json.dumps(result['transcript']))
            self.assertEqual(json.loads(calls[1]['messages'][-1]['content']),task['records'][names[0]])

    def test_ambiguous_episode_blocks_even_with_equal_call_counts(self):
        b = runner()
        self.assertTrue(hasattr(b,'run'), 'episode runner missing')
        for events in ([{'event':'episode_start','slot':'x'}, {'event':'call_start','slot':'x','call_id':'c'}, {'event':'call_result','slot':'x','call_id':'c','protocol_error':None}],
                       [{'event':'episode_start','slot':'x'}]):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                for e in events: b.append(root/'events.jsonl',e)
                self.assertEqual(b.run(root,dict(tasks=[],routes=[],slots=[]),'',lambda *a:self.fail('replayed')), 'blocked')

    def test_allowlist_dependencies_invalid_arguments_and_missing_source(self):
        b = runner()
        self.assertTrue(hasattr(b,'read_record'), 'frozen record tool missing')
        task = next(t for t in b.strict_json((HERE/'frontier_cases.json').read_text()) if t['id']=='agentic_investigation_en')
        seen = []
        for name in task['required_reads']:
            value, valid = b.read_record(task,'read_record',json.dumps({'name':name}),seen)
            self.assertTrue(valid)
            self.assertEqual(value,task['records'][name])
            seen.append(name)
        value, valid = b.read_record(task,'read_record','{"name":"certificate-007"}',seen)
        self.assertTrue(valid)
        self.assertEqual(value, {'found':False,'name':'certificate-007','error':'missing_source'})
        for fn,arg in [('shell','{"name":"case-index"}'),('read_record','{"name":"/etc/passwd"}'),('read_record','{"name":"case-index","extra":1}'),('read_record','{"name":3}'),('read_record','{"name":"case-index","name":"case-index"}'),('read_record','bad')]:
            self.assertFalse(b.read_record(task,fn,arg,seen)[1])
        self.assertFalse(b.read_record(task,'read_record','{"name":"release-policy"}',[])[1])

    def test_valid_empty_truncated_refusal_are_failure_outcomes_without_retry(self):
        b = runner()
        self.assertTrue(hasattr(b,'run'), 'episode runner missing')
        for text,finish,refusal in [('', 'stop',None), ('partial','length',None), (None,'stop','No')]:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d)
                c=config(b)
                c['tasks']=[{'id':'x','prompt':'x'}]
                c['slots']=[dict(id='x',task='x',model=b.MODELS[0],repeat=0,arm='baseline')]
                seen=[]
                def call(*args):
                    seen.append(1)
                    return 200, dict(id='gen-x',model=b.MODELS[0],provider='Test',choices=[dict(message={'content':text,'refusal':refusal},finish_reason=finish)],usage={'prompt_tokens':2,'completion_tokens':3,'total_tokens':5,'cost':0})
                self.assertEqual(b.run(root,c,'',call),'complete')
                self.assertEqual(b.run(root,c,'',call),'complete')
                result=b.rows(root/'events.jsonl')[-1]
                self.assertFalse(result['mechanical']['pass'])
                self.assertEqual(result['totals']['cost'],'0')
                self.assertIsNone(result['totals']['cache_read'])
                self.assertEqual(len(seen),1)
        task={'word_range':[350,500]}
        self.assertFalse(b.mechanical(task,'word '*349,'stop',[],[],[],False)['pass'])
        self.assertTrue(b.mechanical(task,'word '*350,'stop',[],[],[],False)['pass'])

    def test_unknown_cost_and_transport_ambiguity_halt_and_never_replay(self):
        b=runner()
        self.assertTrue(hasattr(b,'run'),'episode runner missing')
        for mode in ['network','cost','model']:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d); c=config(b); c['tasks']=[{'id':'x','prompt':'x'}]
                c['slots']=[dict(id=str(n),task='x',model=b.MODELS[0],repeat=0,arm='baseline') for n in range(2)]
                seen=[]
                def call(*args):
                    seen.append(1)
                    if mode=='network': raise TimeoutError('sensitive exception')
                    return 200,dict(id='gen-x',model=b.MODELS[0] if mode!='model' else 'wrong',provider='Test',choices=[dict(message={'content':'done'},finish_reason='stop')],usage={'prompt_tokens':1,'completion_tokens':1,'total_tokens':2,**({'cost':0} if mode!='cost' else {})})
                self.assertEqual(b.run(root,c,'',call),'blocked')
                self.assertEqual(b.run(root,c,'',call),'blocked')
                self.assertEqual(len(seen),1)
                self.assertNotIn('sensitive exception',(root/'events.jsonl').read_text())


class JudgeTests(unittest.TestCase):
    def candidate_fixture(self,b,root,count=5):
        c=config(b)
        c['tasks']=[dict(id=str(n),prompt=str(n),reference='Ref',rubric=['Accuracy']) for n in range(count)]
        c['slots']=[dict(id=str(n),task=str(n),model=b.MODELS[0],arm='baseline',repeat=0) for n in range(count)]
        def candidate(kind,body):
            return 200,dict(id='gen-c',model=body['model'],provider='Test',choices=[dict(message={'content':body['messages'][-1]['content']},finish_reason='stop')],usage={'prompt_tokens':1,'completion_tokens':1,'total_tokens':2,'cost':0})
        self.assertEqual(b.run(root,c,'',candidate),'complete')
        return c

    def vote_response(self,b,kind,body):
        result=dict(id='gen-j',model=body['model'],provider='Test')
        if kind=='decisions': result.update(answers={'pass':{'type':'noul','noul':0.5}},usage={'input_tokens':1,'output_tokens':1,'cost':0})
        else: result.update(choices=[dict(message={'content':'{"pass":true,"reason":"ok"}'},finish_reason='stop')],usage={'prompt_tokens':1,'completion_tokens':1,'total_tokens':2,'cost':0})
        return 200,result

    def test_concurrent_judges_own_sequential_trios_in_bounded_waves_and_resume(self):
        import inspect
        b=runner()
        self.assertIn('concurrency',inspect.signature(b.judge).parameters,'judge ignores CLI concurrency')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); c=self.candidate_fixture(b,root)
            barrier=threading.Barrier(2); lock=threading.Lock(); order={}; active=set(); peak=[0]; wave_errors=[]
            def call(kind,body):
                state=body['state'] if kind=='decisions' else json.loads(body['messages'][-1]['content'])
                candidate=state['final']
                with lock:
                    if kind=='decisions':
                        if candidate=='2' and active: wave_errors.append('next wave started before prior trio ended')
                        active.add(candidate); peak[0]=max(peak[0],len(active))
                    order.setdefault(candidate,[]).append(body['model'])
                if kind=='decisions' and candidate in ('0','1'): barrier.wait(timeout=5)
                if body['model']==b.JUDGES[-1]:
                    with lock: active.remove(candidate)
                return self.vote_response(b,kind,body)
            self.assertEqual(b.judge(root,c,call,max_new=3,concurrency=2),'paused')
            self.assertEqual(peak[0],2)
            self.assertFalse(wave_errors)
            self.assertEqual(order,{str(n):b.JUDGES for n in range(3)})
            events=b.rows(root/'events.jsonl')
            for n in range(3):
                history=[e for e in events if e['slot']=='judge|'+str(n)]
                self.assertEqual([e['event'] for e in history],['episode_start','call_start','call_result','call_start','call_result','call_start','call_result','episode_terminal'])
                self.assertTrue(history[-1]['valid_terminal'])
                self.assertTrue(history[-1]['majority'])
            self.assertEqual(b.judge(root,c,call,concurrency=4),'complete')
            self.assertEqual(order,{str(n):b.JUDGES for n in range(5)})
            self.assertEqual(b.judge(root,c,lambda *a:self.fail('score replayed'),concurrency=4),'complete')
            for concurrency in (0,5):
                with self.assertRaises(ValueError): b.judge(root,c,call,concurrency=concurrency)

    def test_invalid_native_or_chat_vote_halts_without_next_call_or_replay(self):
        b=runner()
        for invalid_kind in ('decisions','chat'):
            with tempfile.TemporaryDirectory() as d:
                root=Path(d); c=self.candidate_fixture(b,root,count=2); calls=[]
                def call(kind,body):
                    calls.append(body['model'])
                    status,data=self.vote_response(b,kind,body)
                    if kind==invalid_kind:
                        if kind=='decisions': data['answers']['pass']['noul']=True
                        else: data['choices'][0]['message']['content']='{"pass":1,"reason":"ok"}'
                    return status,data
                self.assertEqual(b.judge(root,c,call),'blocked')
                self.assertEqual(calls,b.JUDGES[:1 if invalid_kind=='decisions' else 2])
                self.assertEqual(b.judge(root,c,lambda *a:self.fail('invalid vote replayed')),'blocked')
                terminal=b.rows(root/'events.jsonl')[-1]
                self.assertFalse(terminal['valid_terminal'])
                self.assertEqual(terminal['failure'],'invalid_judge_vote')
                self.assertIsNone(terminal['majority'])

    def test_resume_rejects_invalid_completed_score_shapes(self):
        b=runner()
        for field in ('votes','majority','success'):
            with tempfile.TemporaryDirectory() as d:
                root=Path(d); c=self.candidate_fixture(b,root,count=1)
                self.assertEqual(b.judge(root,c,lambda kind,body:self.vote_response(b,kind,body)),'complete')
                events=b.rows(root/'events.jsonl'); terminal=events[-1]
                if field=='votes': terminal['votes'][0].update(valid=False,**{'pass':None})
                else: terminal[field]=None
                (root/'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))
                self.assertEqual(b.judge(root,c,lambda *a:self.fail('malformed score replayed')),'blocked')

    def test_concurrent_failure_stops_peer_followups_and_later_waves(self):
        from unittest.mock import patch
        b=runner()
        for mode in ('cost','model','network','vote'):
            with tempfile.TemporaryDirectory() as d:
                root=Path(d); c=self.candidate_fixture(b,root,count=4)
                barrier=threading.Barrier(2); failed=threading.Event(); calls=[]; lock=threading.Lock(); waits=[]
                record=b.record
                def observe(root,event):
                    record(root,event)
                    if event['event']=='episode_terminal' and event['slot']=='judge|0': failed.set()
                def call(kind,body):
                    state=body['state'] if kind=='decisions' else json.loads(body['messages'][-1]['content'])
                    candidate=state['final']
                    with lock: calls.append((candidate,body['model']))
                    if candidate in ('0','1') and kind=='decisions': barrier.wait(timeout=5)
                    status,data=self.vote_response(b,kind,body)
                    if candidate=='0':
                        if mode=='cost': data['usage'].pop('cost')
                        elif mode=='model': data['model']='wrong-model'
                        elif mode=='network': raise TimeoutError('synthetic-secret')
                        else: data['answers']['pass']['noul']=True
                    elif candidate=='1': waits.append(failed.wait(timeout=5))
                    return status,data
                with patch.object(b,'record',side_effect=observe):
                    self.assertEqual(b.judge(root,c,call,concurrency=2),'blocked')
                self.assertEqual(waits,[True])
                self.assertCountEqual(calls,[('0',b.JUDGES[0]),('1',b.JUDGES[0])])
                events=[e for e in b.rows(root/'events.jsonl') if e['slot'].startswith('judge|')]
                for slot in ('judge|0','judge|1'):
                    history=[e for e in events if e['slot']==slot]
                    self.assertEqual([e['event'] for e in history],['episode_start','call_start','call_result','episode_terminal'])
                    self.assertFalse(history[-1]['valid_terminal'])
                self.assertEqual(b.judge(root,c,lambda *a:self.fail('failed wave replayed'),concurrency=4),'blocked')
                self.assertNotIn('synthetic-secret',(root/'events.jsonl').read_text())

    def test_chat_judges_explicitly_require_probed_json_object_format(self):
        b=runner()
        task=dict(prompt='Task',reference='Ref',rubric=['Accuracy'])
        candidate=dict(transcript=[],final='Answer',mechanical={'pass':True})
        for route in config(b)['judges'][1:]:
            body=b.judge_payload(task,candidate,route)
            self.assertEqual(body.get('response_format'),{'type':'json_object'})
            self.assertTrue(body['provider']['require_parameters'])

    def test_decisions_question_shares_semantics_without_chat_output_prose(self):
        b=runner()
        task=dict(prompt='Task',reference='Ref',rubric=['Accuracy'])
        candidate=dict(transcript=[],final='Answer',mechanical={'pass':True},slot_info={'arm':'skill','repeat':1,'model':b.MODELS[0]})
        routes=config(b)['judges']
        jev=b.judge_payload(task,candidate,routes[0])
        chat=b.judge_payload(task,candidate,routes[1])
        instruction=jev['questions']['pass']['instructions']
        self.assertNotIn('Return only JSON',instruction)
        self.assertNotIn('"reason"',instruction)
        self.assertNotIn('public reason',instruction)
        self.assertEqual(jev['questions']['pass']['type'],'noul')
        self.assertIn(instruction,chat['messages'][0]['content'])
        self.assertIn('A pass requires all essential rubric requirements.',instruction)
        self.assertIn('untrusted evidence',instruction)
        self.assertIn('Return only JSON',chat['messages'][0]['content'])
        self.assertEqual(jev['state'],json.loads(chat['messages'][1]['content']))
        self.assertEqual(set(jev['state']),{'prompt','reference','rubric','public_transcript','final','deterministic_checks'})
        self.assertNotIn('reasoning',jev)

    def test_blind_native_trio_majority_and_hard_failure_remain_separate(self):
        b=runner()
        self.assertTrue(hasattr(b,'judge'),'blind judge runner missing')
        task={'id':'x','prompt':'Exact task prompt','reference':'Reference','rubric':['Accuracy']}
        c=config(b); c['tasks']=[task]
        c['slots']=[dict(id='x',task='x',model=b.MODELS[0],arm='skill',repeat=1)]
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            def candidate(kind,body):
                return 200,dict(id='gen-c',model=b.MODELS[0],provider='Test',choices=[dict(message={'content':''},finish_reason='stop')],usage={'prompt_tokens':1,'completion_tokens':0,'total_tokens':1,'cost':0})
            b.run(root,c,'skill',candidate)
            calls=[]
            def call(kind,body):
                calls.append(copy.deepcopy(body))
                blinded=json.dumps(body.get('state',{})) if kind=='decisions' else body['messages'][-1]['content']
                self.assertNotIn('slot_info',blinded)
                self.assertNotIn('repeat',blinded)
                for arm in b.ARMS: self.assertNotIn('"arm":',blinded)
                for model in b.MODELS: self.assertNotIn(model,blinded)
                if kind=='decisions':
                    self.assertEqual(set(body['questions']),{'pass'})
                    self.assertNotIn('require_parameters',body['provider'])
                    self.assertEqual(body['provider']['data_collection'],'deny')
                    return 200,dict(id='gen-j',model=b.JUDGES[0],provider='Test',answers={'pass':{'type':'noul','noul':0.5}},usage={'input_tokens':4,'output_tokens':2,'cost':0.02})
                self.assertEqual(body['reasoning'],{'effort':'medium'})
                self.assertEqual(body['max_tokens'],8192)
                self.assertTrue(body['provider']['require_parameters'])
                self.assertEqual(body.get('response_format'),{'type':'json_object'})
                vote=body['model']==b.JUDGES[2]
                return 200,dict(id='gen-j',model=body['model'],provider='Test',choices=[dict(message={'content':json.dumps({'pass':vote,'reason':'Independent assessment'})},finish_reason='stop')],usage={'prompt_tokens':4,'completion_tokens':2,'total_tokens':6,'cost':0.02})
            self.assertEqual(b.judge(root,c,call),'complete')
            self.assertEqual(b.judge(root,c,call),'complete')
            self.assertEqual(b.run(root,c,'skill',lambda *a:self.fail('candidate replayed')),'complete')
            self.assertEqual(len(calls),3)
            terminal=b.rows(root/'events.jsonl')[-1]
            self.assertTrue(terminal['majority'])
            self.assertFalse(terminal['success'])
            self.assertEqual(terminal['totals']['cost'],'0.06')
            self.assertEqual(terminal['totals']['in'],12)
            self.assertEqual(terminal['votes'][0]['value'],0.5)

    def test_strict_judge_shapes_and_all_three_valid_requirement(self):
        b=runner()
        self.assertTrue(hasattr(b,'judge_vote'),'typed judge validator missing')
        good={'answers':{'pass':{'type':'noul','noul':0.5}}}
        self.assertTrue(b.judge_vote('decisions',good)['pass'])
        for value in [True,-1,1.1,float('nan'),float('inf'),'0.5']:
            bad=copy.deepcopy(good); bad['answers']['pass']['noul']=value
            self.assertFalse(b.judge_vote('decisions',bad)['valid'])
        for answers in [{}, {'pass':{'type':'noul','noul':1},'extra':{'type':'noul','noul':1}}]:
            self.assertFalse(b.judge_vote('decisions',{'answers':answers})['valid'])
        for text,finish in [('{"pass":true,"reason":"ok"}','length'),('{"pass":1,"reason":"ok"}','stop'),('{"pass":true,"reason":1}','stop'),('{"pass":true,"reason":"ok","extra":0}','stop'),('{"pass":true,"pass":false,"reason":"ok"}','stop')]:
            self.assertFalse(b.judge_vote('chat',{'choices':[{'finish_reason':finish,'message':{'content':text}}]})['valid'])
        yes={'valid':True,'pass':True}; no={'valid':True,'pass':False}; invalid={'valid':False,'pass':None}
        self.assertTrue(b.majority([yes,yes,no]))
        self.assertFalse(b.majority([yes,no,no]))
        self.assertIsNone(b.majority([yes,yes,invalid]))
        self.assertIsNone(b.majority([yes,yes]))


class ReportTests(unittest.TestCase):
    def test_latency_ratios_use_episode_percentiles_not_summed_http(self):
        b=runner(); c=config(b)
        c['tasks']=[dict(id=str(n),prompt='Task',reference='Ref',rubric=['Accuracy'],language='en',category='explanation') for n in range(3)]
        c['slots']=[dict(id=f'{n}|{arm}',task=str(n),model=b.MODELS[0],repeat=0,arm=arm) for n in range(3) for arm in ['baseline','skill']]
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for slot in c['slots']:
                baseline=slot['arm']=='baseline'
                http=[1,1,10][int(slot['task'])] if baseline else 2
                e=dict(event='episode_terminal',phase='candidate',slot=slot['id'],slot_info=slot,valid_terminal=True,
                       transcript=[],progress=[],final='Answer',mechanical={'pass':True,'reasons':[]},wall_seconds=http*(2 if baseline else 3),
                       totals=dict(in_=1,out=1,cache_read=2 if baseline else 3,cache_write=4 if baseline else 2,reasoning=0,cost='1',http_seconds=http))
                e['totals']['in']=e['totals'].pop('in_')
                b.append(root/'events.jsonl',e)
                b.append(root/'events.jsonl',dict(event='episode_terminal',phase='judge',slot='judge|'+e['slot'],candidate_slot=e['slot'],votes=[{'valid':True,'pass':True}]*3,majority=True,valid_terminal=True))
            target=root/'offline-report.md'
            stats=b.report(root,c,target)['comparisons']['baseline_vs_skill']['overall']
            r=stats['ratios']
            self.assertEqual(r.get('http_seconds_p50'),2)
            self.assertAlmostEqual(r['http_seconds_p95'],2/9.1)
            self.assertEqual(r['wall_seconds_p50'],3)
            self.assertAlmostEqual(r['wall_seconds_p95'],6/18.2)
            self.assertNotEqual(r['http_seconds_p50'],r['http_seconds'])
            self.assertEqual(r['cache_read'],1.5)
            self.assertEqual(r['cache_write'],0.5)
            text=target.read_text()
            self.assertIn('| HTTP p50 ratio | HTTP p95 ratio | Wall p50 ratio | Wall p95 ratio |',text)
            self.assertIn('| overall | 2.0000 | 0.2198 | 3.0000 | 0.3297 |',text)
            self.assertIn('| overall | 6 | 9 | 1.5000 | 12 | 6 | 0.5000 |',text)
            # One absent counter makes the aggregate unavailable, not a declared zero.
            events=b.rows(root/'events.jsonl')
            candidates={e['slot']:e for e in events if e['phase']=='candidate'}
            judgments={e['candidate_slot']:e for e in events if e['phase']=='judge'}
            candidates['0|skill']['totals']['cache_read']=None
            missing=b.comparison(c,candidates,judgments,'baseline','skill')['overall']
            self.assertIsNone(missing['ratios']['cache_read'])
            self.assertIsNone(missing['arms']['skill']['cache_read'])
            self.assertEqual(missing['arms']['skill']['known_cache_read'],6)

    def test_complete_primary_pairs_zero_ratios_and_public_evidence_report(self):
        b=runner()
        self.assertTrue(hasattr(b,'report'),'paired report missing')
        c=config(b)
        c['tasks']=[dict(id=x,prompt='Prompt '+x,reference='Ref',rubric=['Accuracy'],language='en',category='explanation') for x in ['x','y','z']]
        c['slots']=[dict(id=x+'|'+arm,task=x,model=b.MODELS[0],repeat=0,arm=arm) for x in ['x','y','z'] for arm in b.ARMS]
        def result(x,arm,inp,out):
            slot=next(s for s in c['slots'] if s['task']==x and s['arm']==arm)
            return dict(event='episode_terminal',phase='candidate',slot=slot['id'],slot_info=slot,valid_terminal=True,transcript=[{'role':'assistant','content':'Complete public answer'}],progress=[],final='Complete public answer',mechanical={'pass':True,'reasons':[]},wall_seconds=2,call_count=1,totals={'in':inp,'out':out,'cache_read':0,'cache_write':None,'reasoning':0,'reasoning_inconsistent':False,'cost':'0','http_seconds':1})
        candidates=[result('x','baseline',10,0),result('x','skill',12,2),result('y','baseline',10,1),result('y','skill',10,1),result('z','baseline',10,1)]
        judgments=[dict(event='episode_terminal',phase='judge',slot='judge|'+e['slot'],candidate_slot=e['slot'],votes=[{'valid':True,'pass':False}]*3,majority=False,success=False,valid_terminal=True) for e in candidates if not e['slot'].startswith('y|skill')]
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for event in candidates+judgments: b.append(root/'events.jsonl',event)
            target=root/'REPORT.md'
            self.assertFalse(target.exists())
            summary=b.report(root,c,target)
            primary=summary['comparisons']['baseline_vs_skill']['overall']
            self.assertEqual(primary['complete_pairs'],1)
            self.assertEqual(primary['planned_pairs'],3)
            self.assertEqual(set(primary['ratios']),{'in','out','cache_read','cache_write','total_tokens','cost','http_seconds','accuracy','http_seconds_p50','http_seconds_p95','wall_seconds_p50','wall_seconds_p95'})
            self.assertIsNone(primary['ratios']['cache_read'])
            self.assertIsNone(primary['ratios']['cache_write'])
            self.assertEqual(primary['arms']['baseline']['cache_read'],0)
            self.assertIsNone(primary['arms']['baseline']['cache_write'])
            text=target.read_text()
            self.assertIn('CACHED (read/write)',text)
            self.assertNotIn('All six ratios',text)
            self.assertIn('| Read first | Read second | Read ratio | Write first | Write second | Write ratio |',text)
            self.assertIn('| overall | 0 | 0 | null | null | null | null |',text)
            self.assertEqual(primary['ratios']['in'],1.2)
            self.assertIsNone(primary['ratios']['out'])
            self.assertIsNone(primary['ratios']['accuracy'])
            self.assertIsNone(primary['ratios']['cost'])
            for dimension in ['model','language','category','repetition']:
                self.assertTrue(summary['comparisons']['baseline_vs_skill'][dimension])
            self.assertEqual(summary['coverage']['by_task']['x']['primary_complete'],1)
            self.assertEqual(summary['coverage']['by_task']['y']['primary_complete'],0)
            self.assertIn('No universal savings',target.read_text())
            limitations=' '.join(summary['limitations'])
            for disclosure in ('Astra and Opus also run as candidates','self-evaluation bias','8 prompts','4 source scenarios','do not guarantee cold/warm'):
                self.assertIn(disclosure,limitations)
                self.assertIn(disclosure,target.read_text())
            self.assertNotIn('\u2014',target.read_text())
            evidence=b.strict_json((root/'evidence.json').read_text())
            self.assertEqual(len(evidence),len(candidates))
            self.assertEqual(evidence[0]['final'],'Complete public answer')
            self.assertEqual(evidence[0]['prompt'],'Prompt x')
            self.assertEqual(len(evidence[0]['judge_votes']),3)
            self.assertTrue((root/'summary.json').exists())


class FixtureContractTests(unittest.TestCase):
    def test_structured_string_copy_contract_is_explicit(self):
        tasks=json.loads((HERE/'frontier_cases.json').read_text())
        for task in tasks:
            if task['category']!='agentic_structured': continue
            self.assertIn('Copy order_id, sku, owner, and next_review exactly from the source records, preserving date format.' if task['language']=='en' else 'Copie order_id, sku, owner e next_review exatamente dos registros de origem, preservando o formato da data.',task['prompt'])

    def test_mechanically_enforced_json_literals_and_types_are_in_prompt(self):
        tasks=json.loads((HERE/'frontier_cases.json').read_text())
        for task in tasks:
            if 'expected_by_language' not in task: continue
            prompt=task['prompt']
            expected=task['expected_by_language'][task['language']]
            for key in expected: self.assertIn(key,prompt)
            for literal in ['release','hold'] if task['language']=='en' else ['liberar','reter']:
                self.assertIn('"'+literal+'"',prompt,'decision vocabulary must be explicit')
            self.assertIn('JSON integers' if task['language']=='en' else 'inteiros JSON',prompt)
            self.assertIn('JSON boolean' if task['language']=='en' else 'booleano JSON',prompt)


class InterfaceTests(unittest.TestCase):
    def test_transport_bounds_success_and_error_response_reads(self):
        import io,urllib.error
        from unittest.mock import patch
        b=runner(); cap=16*1024*1024
        class Stream(io.BytesIO):
            status=200
            def read(self,size=-1):
                self.requested_size=size
                return super().read(size)
        for error in (False,True):
            stream=Stream(b'x'*(cap+2))
            with patch('urllib.request.OpenerDirector.open',side_effect=urllib.error.HTTPError('https://openrouter.ai/',502,'Error',{},stream) if error else None,return_value=stream):
                with self.assertRaises(RuntimeError): b.transport('chat','synthetic-secret-value',{})
            self.assertEqual(stream.requested_size,cap+1)

    def test_judge_cli_forwards_concurrency_without_network(self):
        from unittest.mock import patch
        b=runner(); c=config(b)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            argv=['frontier_bench.py','judge','--artifacts',d,'--max-new','0','--concurrency','4']
            with patch('sys.argv',argv), patch.object(b,'verify',return_value=c), patch.object(b,'digest',return_value='same'), patch.object(b,'judge',return_value='paused') as judge, patch.object(b,'transport') as transport:
                b.main()
                self.assertEqual(judge.call_args.args[-2:],(0,4),'CLI discarded judge concurrency')
                self.assertEqual(judge.call_args.args[:2],(root,c))
                transport.assert_not_called()
            self.assertFalse((root/'.frontier.lock').exists())

    def test_cli_help_temporary_freeze_verify_zero_call_run_and_explicit_report(self):
        import subprocess,sys
        script=HERE/'frontier_bench.py'
        help_result=subprocess.run([sys.executable,str(script),'--help'],capture_output=True,text=True)
        self.assertIn('freeze',help_result.stdout,'command interface missing')
        with tempfile.TemporaryDirectory() as d:
            base=Path(d); root=base/'artifacts'; conf=base/'routes.json'; target=base/'REPORT.md'
            conf.write_text(json.dumps(config(runner())))
            commands=[['freeze','--config',str(conf)],['verify'],['run','--max-new','0'],['judge','--max-new','0'],['report','--report',str(target)]]
            for command in commands:
                result=subprocess.run([sys.executable,str(script),*command,'--artifacts',str(root)],capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                if command[0]!='report': self.assertFalse(target.exists())
            self.assertTrue(target.exists())
            self.assertEqual(runner().verify(root)['settings']['max_tokens'],8192)

    def test_transport_installs_no_redirect_and_preserves_redacted_3xx(self):
        import io,urllib.error,urllib.request
        from unittest.mock import patch
        b=runner(); key='synthetic-secret-value'
        for kind in ('chat','decisions'):
            for code in (301,302,303,307,308):
                error=urllib.error.HTTPError('https://openrouter.ai/',code,'Moved',{'Location':'https://redirect.invalid/'},io.BytesIO(('redirect '+key).encode()))
                with patch('urllib.request.urlopen',side_effect=error) as open_url, patch('urllib.request.OpenerDirector.open',open_url), patch('urllib.request.build_opener',wraps=urllib.request.build_opener) as build:
                    status,data=b.transport(kind,key,{})
                    self.assertEqual(build.call_count,1,'credential-bearing default redirect opener used')
                    handler=build.call_args.args[0]
                    if isinstance(handler,type): handler=handler()
                    self.assertIsInstance(handler,urllib.request.HTTPRedirectHandler)
                    request=open_url.call_args.args[0]
                    self.assertIsNone(handler.redirect_request(request,None,code,'Moved',error.headers,'https://redirect.invalid/'))
                    self.assertEqual(open_url.call_count,1)
                self.assertEqual(status,code)
                self.assertEqual(data,{'unparseable_body':'redirect [REDACTED]'})

    def test_non_json_responses_are_preserved_sanitized_without_retry(self):
        import io
        from unittest.mock import patch
        b=runner(); key='synthetic-secret-value'
        for kind,url in [('chat','https://openrouter.ai/api/v1/chat/completions'),('decisions','https://openrouter.ai/api/alpha/decisions')]:
            stream=io.BytesIO(('gateway failure '+key).encode()); stream.status=502
            with patch('urllib.request.urlopen',return_value=stream) as open_url, patch('urllib.request.OpenerDirector.open',open_url):
                try: status,data=b.transport(kind,key,{})
                except RuntimeError: self.fail('Raw non-JSON response was discarded')
                self.assertEqual(open_url.call_count,1)
                self.assertEqual(open_url.call_args.args[0].full_url,url)
            self.assertEqual(status,502)
            self.assertEqual(data,{'unparseable_body':'gateway failure [REDACTED]'})

    def test_decisions_endpoint_and_redaction_preserve_native_raw_response(self):
        import io
        from unittest.mock import patch
        b=runner()
        self.assertTrue(hasattr(b,'transport'),'raw OpenRouter transport missing')
        key='synthetic-secret-value'
        body={'model':b.JUDGES[0],'questions':{}}
        source={'id':'gen-x','model':b.JUDGES[0],'answers':{},'usage':{'input_tokens':1,'output_tokens':1,'cost':0},'echo':key,'authorization':'other-secret'}
        stream=io.BytesIO(json.dumps(source).encode()); stream.status=200
        with patch('urllib.request.urlopen',return_value=stream) as open_url, patch('urllib.request.OpenerDirector.open',open_url):
            status,data=b.transport('decisions',key,body)
            req=open_url.call_args.args[0]
            self.assertEqual(req.full_url,'https://openrouter.ai/api/alpha/decisions')
            self.assertEqual(json.loads(req.data),body)
        self.assertEqual(status,200)
        self.assertEqual(data['usage'],source['usage'])
        self.assertNotIn(key,json.dumps(data))
        self.assertNotIn('other-secret',json.dumps(data))
        with patch('urllib.request.urlopen',side_effect=TimeoutError(key)) as open_url, patch('urllib.request.OpenerDirector.open',open_url):
            with self.assertRaises(RuntimeError) as caught: b.transport('decisions',key,body)
            self.assertNotIn(key,str(caught.exception))
        with patch('urllib.request.urlopen') as open_url, patch('urllib.request.OpenerDirector.open',open_url):
            with self.assertRaises(ValueError): b.transport('shell',key,body)
            open_url.assert_not_called()


class HardeningTests(unittest.TestCase):
    def test_jsonl_ledger_preserves_unicode_line_separators(self):
        b=runner()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'events.jsonl'
            values=[{'content':'left\u2028right\u2029end'},{'content':'second'}]
            for value in values: b.append(path,value)
            self.assertEqual(b.rows(path),values)

    def test_arm_stats_retains_known_partial_cache_counters(self):
        b=runner()
        episode={'slot':'x','totals':{'cache_read':None,'known_cache_read':6,'http_seconds':1},'wall_seconds':1,'mechanical':{'pass':False}}
        stats=b.arm_stats([episode],{})
        self.assertIsNone(stats['cache_read'])
        self.assertEqual(stats['known_cache_read'],6)

    def test_incomplete_terminal_and_orphan_call_records_block_replay(self):
        b=runner()
        histories=[
            [{'event':'episode_start','slot':'x'},{'event':'episode_terminal','slot':'x','valid_terminal':True,'totals':{},'transcript':[]}],
            [{'event':'call_start','slot':'x','call_id':'x#0'},{'event':'call_result','slot':'x','call_id':'x#0','protocol_error':None}],
        ]
        for history in histories:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d)
                for e in history: b.append(root/'events.jsonl',e)
                self.assertEqual(b.run(root,dict(tasks=[],routes=[],slots=[]),'',lambda *a:self.fail('replayed')),'blocked')

    def test_malformed_function_and_nonfinal_tool_use_are_deterministic_failures(self):
        b=runner(); c=config(b); c['tasks']=[{'id':'x','prompt':'x'}]
        c['slots']=[dict(id='x',task='x',model=b.MODELS[0],arm='baseline',repeat=0)]
        for function,finish in [([], 'tool_calls'), ({'name':'read_record','arguments':'{}'},'stop')]:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d)
                response=dict(id='gen-x',model=b.MODELS[0],provider='Test',usage={'prompt_tokens':1,'completion_tokens':1,'total_tokens':2,'cost':0},choices=[dict(finish_reason=finish,message={'content':'Public text','tool_calls':[{'id':'t','type':'function','function':function}]})])
                self.assertEqual(b.run(root,c,'',lambda *a:(200,response)),'complete')
                self.assertFalse(b.rows(root/'events.jsonl')[-1]['mechanical']['pass'])


if __name__ == '__main__':
    unittest.main()
