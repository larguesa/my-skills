"""OFFLINE only: explicit fake transport fixtures, never API evidence."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SKILL = HERE.parents[1]
# v1-full-json is frozen to 0.5.1: use the preserved snapshot of 13/10, read-only.
EVIDENCE_13 = HERE.parent / 'runs/2026-10-13/evidence'
LEGACY_SKILL = EVIDENCE_13 / 'frozen/skill'
FIXTURES = HERE / 'fixtures'
HISTORY = Path(os.environ.get('HUMANIZADOR_HISTORY', FIXTURES / 'history.json'))
CATALOG = Path(os.environ.get('HUMANIZADOR_CATALOG', FIXTURES / 'catalog.json'))
ENDPOINTS = Path(os.environ.get('HUMANIZADOR_ENDPOINTS', FIXTURES / 'endpoints.json'))
AMENDMENTS = Path(os.environ.get('HUMANIZADOR_AMENDMENTS', FIXTURES / 'amendments.json'))
PROBES = Path(os.environ.get('HUMANIZADOR_PROBES', FIXTURES / 'probes'))


def runner():
    assert (HERE / 'generation_eval.py').exists(), 'prepare/run/render runner not implemented'
    import generation_eval
    return generation_eval


class PreparationTests(unittest.TestCase):
    def test_real_inputs_frozen_independent_generation_contract(self):
        g = runner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'study'
            manifest = g.prepare(root, LEGACY_SKILL,HISTORY, CATALOG, ENDPOINTS)
            self.assertEqual(manifest['expected']['generations'], 912)
            self.assertEqual(manifest['expected']['pair_judgments'], 1368)
            self.assertEqual(manifest['expected']['judge_calls'], 432)
            self.assertIsNone(manifest['monetary_ceiling'])
            config = g.load_frozen(root)
            calls = list(g.generation_calls(root, config))
            self.assertEqual(len({c['slot'] for c in calls}), 912)
            cases = g.parse_prompts((LEGACY_SKILL / 'results/PROMPTS.md').read_text())
            self.assertEqual(len(cases), 24)
            for base, treat in zip(calls[::2], calls[1::2]):
                prompt = next(c['prompt'] for c in cases if c['ordinal'] == base['ordinal'])
                self.assertEqual(base['payload']['messages'], [{'role': 'user', 'content': prompt}])
                self.assertEqual(treat['payload']['messages'][-1], base['payload']['messages'][0])
                self.assertEqual(len(treat['payload']['messages']), 5)
                for message, path in zip(treat['payload']['messages'][:3],
                    ['SKILL.md', 'references/catalogo.json', 'references/estilos.json']):
                    self.assertEqual(message, {'role': 'system', 'content': (LEGACY_SKILL / path).read_text()})
                local = json.loads(treat['payload']['messages'][3]['content'])
                self.assertTrue(local['catalog']['result'])
                self.assertTrue(local['styles']['result'])
                self.assertTrue(local['structure']['result']['blocks'])
                self.assertEqual(base['payload']['reasoning'], treat['payload']['reasoning'])
                self.assertFalse(base['payload']['provider']['allow_fallbacks'])
            self.assertEqual([c['prompt'] for c in config['cases']], [c['prompt'] for c in cases])
            self.assertEqual(config['routes'], json.loads(HISTORY.read_text())['routes'])
            with self.assertRaises(FileExistsError):
                g.prepare(root, LEGACY_SKILL,HISTORY, CATALOG, ENDPOINTS)
            (root / 'frozen/skill/SKILL.md').chmod(0o600)
            (root / 'frozen/skill/SKILL.md').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'hash'):
                g.load_frozen(root)
    def test_explicit_amendments_preserve_originals_and_do_not_import_probes_as_candidates(self):
        g = runner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'study'
            amendments = AMENDMENTS
            manifest = g.prepare(root, LEGACY_SKILL,HISTORY, CATALOG, ENDPOINTS,
                amendments=amendments, probe_dir=PROBES)
            config = g.load_frozen(root)
            self.assertEqual(config['historical_routes'], json.loads(HISTORY.read_text())['routes'])
            for original, effective in zip(config['historical_routes'], config['routes']):
                self.assertEqual(original['model'], effective['model'])
                self.assertEqual(original['mode'], effective['mode'])
                self.assertEqual(original['reasoning'], effective['reasoning'])
                declared = next((a for a in json.loads(amendments.read_text())['amendments']
                                 if a['model'] == original['model']), None)
                if declared:
                    self.assertEqual(effective['endpoint']['tag'], declared['effective_provider'])
                else:
                    self.assertEqual(original, effective)
            self.assertEqual(manifest['distinct_models'], 14)
            self.assertFalse((root / 'requests').exists())
            self.assertTrue(list((root / 'frozen/probe-evidence').glob('*.json')))


def current_version():
    import re
    return re.search(r'^version: (\S+)$', (SKILL / 'SKILL.md').read_text(), re.M).group(1)


class PackagingTests(unittest.TestCase):
    """v1 stays byte-identical; v2-brief is opt-in and changes only the treatment."""

    def test_legacy_v1_reproduces_frozen_13_10_plan_byte_for_byte(self):
        g = runner()
        frozen = EVIDENCE_13 / 'frozen'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'study'
            g.prepare(root, LEGACY_SKILL, frozen / 'history.json', frozen / 'catalog.json',
                      frozen / 'endpoints.json', amendments=frozen / 'route-amendments.json')
            for name in ['generation-plan.json', 'config.json', 'blind-plan.json']:
                self.assertEqual((root / 'frozen' / name).read_bytes(), (frozen / name).read_bytes(), name)
            for path in sorted((frozen / 'local').glob('*.json')):
                self.assertEqual((root / 'frozen/local' / path.name).read_bytes(), path.read_bytes())
            self.assertNotIn('treatment_packaging', g.read_json(root / 'manifest.json'))

    def test_packaging_controls_are_explicit(self):
        g = runner()
        with tempfile.TemporaryDirectory() as tmp:
            for n, options in enumerate([dict(skill=SKILL), dict(skill=SKILL, packaging='v3-tools', skill_version=current_version()),
                                         dict(skill=SKILL, packaging='v2-brief'),
                                         dict(skill=SKILL, packaging='v2-brief', skill_version='0.5.1'),
                                         dict(skill=LEGACY_SKILL, packaging='v2-brief', skill_version='0.5.1'),
                                         dict(skill=LEGACY_SKILL, skill_version=current_version())]):
                skill = options.pop('skill')
                with self.subTest(n=n), self.assertRaises(ValueError):
                    g.prepare(Path(tmp) / f'study{n}', skill, HISTORY, CATALOG, ENDPOINTS, **options)

    def test_v2_brief_is_opt_in_compact_and_keeps_baseline_literal(self):
        g = runner()
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            legacy, compact = Path(tmp) / 'v1', Path(tmp) / 'v2'
            g.prepare(legacy, LEGACY_SKILL, HISTORY, CATALOG, ENDPOINTS)
            manifest = g.prepare(compact, SKILL, HISTORY, CATALOG, ENDPOINTS,
                                 packaging='v2-brief', skill_version=current_version())
            self.assertEqual(manifest['treatment_packaging'], 'v2-brief')
            self.assertEqual(manifest['expected']['generations'], 912)
            old_config, config = g.load_frozen(legacy), g.load_frozen(compact)
            self.assertEqual(config['treatment_packaging'], 'v2-brief')
            self.assertEqual(config['skill_version'], current_version())
            self.assertNotEqual(config['blind_seed'], old_config['blind_seed'])
            self.assertEqual([c['prompt'] for c in config['cases']], [c['prompt'] for c in old_config['cases']])
            old_calls = {c['slot']: c for c in g.generation_calls(legacy, old_config)}
            calls = list(g.generation_calls(compact, config))
            self.assertEqual(set(old_calls), {c['slot'] for c in calls})
            briefs = {}
            for call in calls:
                if call['arm'] == 'baseline':
                    self.assertEqual(call, old_calls[call['slot']], 'baseline must not change')
                    continue
                messages = call['payload']['messages']
                self.assertEqual([m['role'] for m in messages], ['system', 'system', 'user'])
                self.assertEqual(messages[0]['content'], (SKILL / 'SKILL.md').read_text())
                self.assertEqual(messages[2], old_calls[call['slot']]['payload']['messages'][-1])
                self.assertNotIn('"pattern"', messages[1]['content'])
                self.assertIn('não repita comandos', messages[1]['content'])
                old_size = sum(len(m['content']) for m in old_calls[call['slot']]['payload']['messages'][:-1])
                self.assertLess(sum(len(m['content']) for m in messages[:-1]), 0.4 * old_size)
                briefs.setdefault(call['case'], messages[1]['content'])
                self.assertEqual(briefs[call['case']], messages[1]['content'])
            profile, genre = g.SELECTORS[0]
            expected = subprocess.run([sys.executable, 'scripts/humanizar.py', 'brief', '--profile', profile,
                                       '--genre', genre, '--breadth', '2', '--randomness', '0', '--seed', '17'],
                                      cwd=SKILL, capture_output=True, text=True, check=True).stdout
            self.assertEqual(briefs[config['cases'][0]['id']], expected)

    def test_v2_offline_pilot_and_read_only_delivery_report(self):
        g = runner()
        from eval_delivery import delivery
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'study'
            g.prepare(root, SKILL, HISTORY, CATALOG, ENDPOINTS, packaging='v2-brief',
                      skill_version=current_version())
            base = FakeOfflineTransport(root)

            class CommandsForSkill:
                offline_only = True

                def __call__(self, call):
                    response = base(call)
                    if call['phase'] == 'generation' and call['arm'] == 'skill':
                        data = json.loads(response['body'])
                        data['choices'][0]['message']['content'] = (
                            '<tool_call><function=terminal><parameter=command>python3 scripts/humanizar.py brief'
                            '</parameter></function></tool_call>')
                        response['body'] = json.dumps(data).encode()
                    return response
            result = g.run(root, offline=True, transport=CommandsForSkill(), pilot=True)
            self.assertIsNone(result['stop_reason'])
            before = {p: p.read_bytes() for p in (root / 'requests').rglob('*') if p.is_file()}
            report = delivery(root, Path(tmp) / 'delivery.json')
            self.assertEqual(report['treatment_packaging'], 'v2-brief')
            self.assertEqual(report['summary']['baseline'], {'completed': 1, 'deliverable': 1, 'blocking': {}})
            self.assertEqual(report['summary']['skill']['deliverable'], 0)
            self.assertIn('saida_somente_comandos', report['summary']['skill']['blocking'])
            self.assertEqual(before, {p: p.read_bytes() for p in before})
            with self.assertRaises(FileExistsError):
                delivery(root, Path(tmp) / 'delivery.json')
            from eval_render import render
            import html
            import re
            render(root, Path(tmp) / 'reports')
            case = g.load_frozen(root)['cases'][0]['id']
            text = (Path(tmp) / 'reports/experiments' / case / 'REPORT.md').read_text()
            self.assertIn(f'| Skill {current_version()} |', text)
            self.assertIn(f'SKILL.md {current_version()} e o briefing local compacto', text)
            self.assertNotIn('0.5.1', text)
            cells = re.findall(r'<pre>(.*?)</pre>', text)
            raws = [g.read_json(root / 'requests' / f'g.{case}.r00.{arm}' / 'result.json')['text'] for arm in g.ARMS]
            self.assertEqual([html.unescape(c) for c in cells], raws)

    def test_render_cells_decode_exactly_and_hide_markdown(self):
        import html
        from eval_render import cell
        for raw in ['**negrito** _itálico_ `código` [link](x) # título | pipe',
                    'linha\r\nnova separador\tTab <b>&amp;</b> 😀 ação — – -',
                    '1. item\n- item\n> citação\n\\escape']:
            with self.subTest(raw=raw):
                rendered = cell(raw)
                inner = rendered[len('<pre>'):-len('</pre>')]
                self.assertEqual(html.unescape(inner), raw)
                import re
                literal = re.sub(r'&#\d+;', '', inner)
                self.assertFalse(set(literal) & set('*_`[]()#|<>&;\\\n\r\t -'))
                if 'ação' in raw:
                    self.assertIn('ação', inner, 'acentos permanecem legíveis')


def snapshot(root):
    return {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in Path(root).rglob('*') if p.is_file()}


def writable_copy(source, target):
    import shutil
    shutil.copytree(source, target, symlinks=True)
    for path in Path(target).rglob('*'):
        path.chmod(0o700 if path.is_dir() else 0o600)
    return Path(target)


class DeliveryIntegrityTests(unittest.TestCase):
    """Read-only delivery report: verified sources, untouched evidence, safe destination."""

    def test_historical_13_10_evidence_is_verified_and_untouched(self):
        from eval_delivery import delivery
        before = snapshot(EVIDENCE_13)
        with tempfile.TemporaryDirectory() as tmp:
            report = delivery(EVIDENCE_13, Path(tmp) / 'delivery.json')
        self.assertEqual(before, snapshot(EVIDENCE_13))
        self.assertEqual(report['treatment_packaging'], 'v1-full-json')
        self.assertEqual(report['summary']['baseline']['completed'], 15)
        self.assertEqual(report['summary']['baseline']['deliverable'], 11)
        self.assertEqual(report['summary']['skill']['completed'], 15)
        self.assertEqual(report['summary']['skill']['deliverable'], 12)
        self.assertEqual(report['summary']['skill']['blocking']['saida_somente_comandos'], 2)
        self.assertTrue(all(row['result_cache'] for row in report['rows']))

    def test_destination_inside_evidence_is_rejected_even_via_symlink(self):
        from eval_delivery import delivery
        before = snapshot(EVIDENCE_13)
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / 'atalho'
            link.symlink_to(EVIDENCE_13, target_is_directory=True)
            file_link = Path(tmp) / 'saida.json'
            file_link.symlink_to(Path(tmp) / 'alvo.json')
            for output in [EVIDENCE_13 / 'DELIVERY.json', EVIDENCE_13 / 'requests/novo/DELIVERY.json',
                           link / 'DELIVERY.json', EVIDENCE_13, file_link]:
                with self.subTest(output=output), self.assertRaises(ValueError):
                    delivery(EVIDENCE_13, output)
            self.assertFalse((Path(tmp) / 'alvo.json').exists())
        self.assertEqual(before, snapshot(EVIDENCE_13))

    def test_historical_tampering_is_rejected(self):
        from eval_delivery import delivery
        with tempfile.TemporaryDirectory() as tmp:
            root = writable_copy(EVIDENCE_13, Path(tmp) / 'evidence')
            path = root / 'requests/g.01-noticia-bibliotecas.r00.skill/result.json'
            data = json.loads(path.read_bytes())
            data['text'] = data['text'].replace('1.200', '1.300')
            path.write_bytes(json.dumps(data).encode())
            with self.assertRaisesRegex(ValueError, 'cached result'):
                delivery(root, Path(tmp) / 'out.json')
            self.assertFalse((Path(tmp) / 'out.json').exists())

    def test_offline_run_tampering_and_missing_cache(self):
        g = runner()
        from eval_delivery import delivery
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'study'
            g.prepare(source, SKILL, HISTORY, CATALOG, ENDPOINTS, packaging='v2-brief',
                      skill_version=current_version())
            g.run(source, offline=True, transport=FakeOfflineTransport(source), pilot=True)
            slot = next(p.name for p in (source / 'requests').iterdir() if p.name.endswith('.skill'))

            def edit_json(name, change):
                def apply(root):
                    path = root / name
                    data = json.loads(path.read_bytes())
                    change(data)
                    path.write_bytes(g.encoded(data))
                return apply

            def edit_raw(root):
                import base64
                path = root / 'requests' / slot / 'raw.json'
                raw = json.loads(path.read_bytes())
                body = json.loads(base64.b64decode(raw['body_base64']))
                body['choices'][0]['message']['content'] = 'texto trocado depois da execução'
                raw['body_base64'] = base64.b64encode(json.dumps(body).encode()).decode()
                path.write_bytes(g.encoded(raw))

            def remap(root):
                path = root / 'frozen/blind-plan.json'
                blinds = json.loads(path.read_bytes())
                pair = blinds[0]['pairs']['p000']
                pair['A'], pair['B'] = pair['B'], pair['A']
                path.write_bytes(g.encoded(blinds))
                manifest = json.loads((root / 'manifest.json').read_bytes())
                manifest['sha256']['frozen/blind-plan.json'] = g.digest(path.read_bytes())
                (root / 'manifest.json').write_bytes(g.encoded(manifest))

            def resign_brief(root):
                name = 'frozen/local/' + g.load_frozen(source)['cases'][0]['id'] + '.json'
                path = root / name
                data = json.loads(path.read_bytes())
                data['stdout_utf8'] += 'Orientação nova.\n'
                path.write_bytes(g.encoded(data))
                manifest = json.loads((root / 'manifest.json').read_bytes())
                manifest['sha256'][name] = g.digest(path.read_bytes())
                (root / 'manifest.json').write_bytes(g.encoded(manifest))

            def stray(root):
                (root / 'requests' / slot / 'extra.json').write_text('{}')
            tampers = {
                'result': (edit_json(f'requests/{slot}/result.json', lambda d: d.update(text='outro')), 'cached result'),
                'raw': (edit_raw, 'cached result'),
                'intent': (edit_json(f'requests/{slot}/intent.json', lambda d: d.update(started_at='x')), 'raw/intent'),
                'config': (edit_json('frozen/config.json', lambda d: d.update(blind_seed='x')), 'frozen hash'),
                'mapa': (remap, 'blind map'),
                'briefing': (resign_brief, 'payload hash'),
                'arquivo': (stray, 'unexpected file'),
            }
            for name, (tamper, message) in tampers.items():
                with self.subTest(tamper=name):
                    root = writable_copy(source, Path(tmp) / ('copy-' + name))
                    tamper(root)
                    with self.assertRaisesRegex(ValueError, message):
                        delivery(root, Path(tmp) / (name + '.json'))
                    self.assertFalse((Path(tmp) / (name + '.json')).exists())
            root = writable_copy(source, Path(tmp) / 'sem-cache')
            (root / 'requests' / slot / 'result.json').unlink()
            before = snapshot(root)
            report = delivery(root, Path(tmp) / 'sem-cache.json',
                              checker=root / 'frozen/skill/scripts/humanizar.py')
            self.assertEqual(before, snapshot(root))
            self.assertFalse(list(root.rglob('__pycache__')))
            self.assertFalse((root / 'requests' / slot / 'result.json').exists())
            self.assertFalse(next(r for r in report['rows'] if r['slot'] == slot)['result_cache'])


class FakeOfflineTransport:
    """Synthetic test data. Explicitly OFFLINE; no network, no API credentials."""
    offline_only = True

    def __init__(self, root):
        self.root = Path(root)
        self.calls = []

    def __call__(self, call):
        g = runner()
        intent = self.root / 'requests' / call['slot'] / 'intent.json'
        assert intent.exists(), 'intent must be durable before transport'
        assert g.read_json(intent)['call'] == call
        self.calls.append(call)
        data = {'id': 'OFFLINE-FAKE-' + call['slot'], 'model': call['model'],
                'provider': call['endpoint']['provider_name'],
                'usage': {'prompt_tokens': 10, 'completion_tokens': 20,
                          'cost': 0.000001, 'prompt_tokens_details': {'cached_tokens': 2,
                          'cache_write_tokens': 0}, 'completion_tokens_details': {'reasoning_tokens': 5}}}
        if call['api'] == 'decisions':
            data['usage'] = {'input_tokens': 10, 'output_tokens': 20, 'cost': 0.000001}
            data['answers'] = {}
            for key, question in call['payload']['questions'].items():
                kind = question['type']
                value = {'type': kind}
                value.update({'noul': 0.5} if kind == 'noul' else {'score': 3} if kind == 'score'
                             else {'choice': 'no' if key.endswith('_critico') else 'empate'})
                data['answers'][key] = value
        else:
            text = 'OFFLINE FAKE: texto de teste, nunca evidência de geração.\u2028Continuação.'
            if call['phase'] == 'judge':
                state = call['judge_state']
                text = json.dumps({'deteccao': {tid: 50 for tid in state['textos']},
                    'preferencia': {pid: 'empate' for pid in state['pares']},
                    'qualidade': {tid: {'naturalidade': 75, 'clareza': 75, 'adequacao': 75,
                        'correcao': 75, 'critico': False, 'justificativa': 'OFFLINE FAKE'}
                        for tid in state['textos']}}, ensure_ascii=False)
            data['choices'] = [{'finish_reason': 'stop', 'message': {'content': text}}]
        return {'http_status': 200, 'body': json.dumps(data, ensure_ascii=False).encode()}


class RuntimeTests(unittest.TestCase):
    def test_full_offline_matrix_unique_coverage_no_replay_and_aggregate(self):
        g = runner()
        from eval_render import render
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'study'
            g.prepare(root, LEGACY_SKILL,HISTORY, CATALOG, ENDPOINTS)
            fake = FakeOfflineTransport(root)
            result = g.run(root, offline=True, transport=fake)
            self.assertIsNone(result['stop_reason'])
            self.assertEqual(result['submitted_generations'], 912)
            self.assertEqual(result['submitted_judge_calls'], 432)
            self.assertEqual(len({c['slot'] for c in fake.calls}), 1344)
            self.assertTrue(all(len(c['judge_state']['pares']) <= 4 for c in fake.calls if c['phase'] == 'judge'))
            summary = render(root, Path(tmp) / 'reports')
            self.assertEqual(summary['pair_judgments'], 1368)
            self.assertEqual(summary['individual_impression_scores'], 2736)
            self.assertEqual(summary['preferences'], {'empate': 1368})
            again = g.run(root, offline=True, transport=fake)
            self.assertEqual(again['new_calls'], 0)
            self.assertEqual(len(fake.calls), 1344)
            path = root / 'requests' / fake.calls[0]['slot'] / 'raw.json'
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                g.immutable(path, {'forged': 'OFFLINE negative test'})
            self.assertEqual(before, path.read_bytes())
            result_path = path.with_name('result.json')
            data = g.read_json(result_path)
            data['text'] = 'tampered OFFLINE fixture'
            result_path.chmod(0o600)
            result_path.write_bytes(g.encoded(data))
            with self.assertRaisesRegex(ValueError, 'cached result'):
                g.run(root, offline=True, transport=fake)

    def test_transport_ambiguity_blocks_all_new_slots_and_never_replays(self):
        g = runner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'study'
            g.prepare(root, LEGACY_SKILL,HISTORY, CATALOG, ENDPOINTS)
            fake = FakeOfflineTransport(root)

            class AmbiguousOffline:
                offline_only = True
                calls = 0
                def __call__(self, call):
                    self.calls += 1
                    self_intent = root / 'requests' / call['slot'] / 'intent.json'
                    assert self_intent.exists()
                    raise TimeoutError('explicit offline fixture: unknown submission')
            transport = AmbiguousOffline()
            result = g.run(root, offline=True, transport=transport, pilot=True)
            self.assertEqual(result['stop_reason'], 'ambiguous_intent_without_raw')
            self.assertEqual(transport.calls, 1)
            g.run(root, offline=True, transport=fake)
            self.assertEqual(fake.calls, [])
            with g.locked(root):
                with self.assertRaisesRegex(RuntimeError, 'lock'):
                    g.run(root, offline=True, transport=fake)

    def test_render_offline_pilot_preserves_text_and_reports_pending_denominators(self):
        g = runner()
        self.assertTrue((HERE / 'eval_render.py').exists(), 'render not implemented')
        from eval_render import render
        with tempfile.TemporaryDirectory() as tmp:
            root, reports = Path(tmp) / 'study', Path(tmp) / 'reports'
            g.prepare(root, LEGACY_SKILL,HISTORY, CATALOG, ENDPOINTS)
            fake = FakeOfflineTransport(root)
            g.run(root, offline=True, transport=fake, pilot=True)
            summary = render(root, reports)
            self.assertEqual(summary['valid_generations'], 2)
            self.assertEqual(summary['pair_judgments'], 3)
            self.assertEqual(summary['individual_impression_scores'], 6)
            self.assertEqual(len(list((reports / 'experiments').glob('*/REPORT.md'))), 24)
            self.assertIn('OFFLINE_FAKE', (reports / 'SUMMARY.md').read_text())
            report = reports / 'experiments' / fake.calls[0]['case'] / 'REPORT.md'
            text = report.read_text()
            self.assertIn('| Jev | Astra | Opus |', text)
            self.assertIn('PENDENTE', text)
            prompt = g.load_frozen(root)['cases'][0]['prompt']
            self.assertIn('\n' + prompt + '\n', text)
            result = g.read_json(root / 'requests' / fake.calls[0]['slot'] / 'result.json')
            output = report.parent / 'outputs/r00-baseline.txt'
            self.assertEqual(output.read_bytes(), result['text'].encode())
            self.assertIsNone(summary['accounting']['probes']['total_usd'])
            self.assertEqual(summary['accounting']['generation']['costs_known'], 2)

    def test_offline_pilot_intent_raw_cache_and_three_blind_judges(self):
        g = runner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'study'
            g.prepare(root, LEGACY_SKILL,HISTORY, CATALOG, ENDPOINTS)
            fake = FakeOfflineTransport(root)
            result = g.run(root, offline=True, transport=fake, pilot=True)
            self.assertEqual(result['execution_mode'], 'OFFLINE_FAKE')
            self.assertEqual(len(fake.calls), 5)
            self.assertEqual([c['phase'] for c in fake.calls], ['generation'] * 2 + ['judge'] * 3)
            self.assertEqual({c['judge'] for c in fake.calls[2:]}, {'jev', 'astra', 'opus'})
            for call in fake.calls[2:]:
                self.assertEqual(len(call['judge_state']['pares']), 1)
                self.assertNotIn('mapping', call['judge_state'])
            before = {p: p.read_bytes() for p in (root / 'requests').rglob('*') if p.is_file()}
            again = g.run(root, offline=True, transport=fake, pilot=True)
            self.assertEqual(len(fake.calls), 5)
            self.assertEqual(result['completed'], again['completed'])
            self.assertEqual(before, {p: p.read_bytes() for p in before})
            with self.assertRaisesRegex(ValueError, 'OFFLINE|offline'):
                g.run(root, key='not-a-real-key', execute_paid=True)
            first = root / 'requests' / fake.calls[0]['slot']
            (first / 'result.json').chmod(0o600)
            (first / 'result.json').unlink()
            g.run(root, offline=True, transport=fake, pilot=True)
            self.assertEqual(len(fake.calls), 5, 'raw-only recovery must never POST again')
            self.assertEqual(before[first / 'result.json'], (first / 'result.json').read_bytes())


if __name__ == '__main__':
    unittest.main()
