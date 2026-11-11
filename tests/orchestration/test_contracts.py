"""Development checks for the shipped contracts and protocol-screening recipes.
No flow engine, model invocation, network, publication or dangerous command execution.
"""
from pathlib import Path
import json
import re
import shlex
import shutil
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / 'skills'
NAMES = ('agentic-orchestrator', 'claude-code-user', 'codex-user', 'pi-user', 'opencode-user', 'antigravity-user')
CLI_NAMES = NAMES[1:]


def blocks(name, language='bash'):
    text = (SKILLS / name / 'SKILL.md').read_text()
    return re.findall(r'```' + language + r'\n(.*?)```', text, re.S)


def protocol_command(name):
    candidates = [b for b in blocks(name) if b.startswith('# protocol-check\n')]
    if len(candidates) != 1:
        raise AssertionError(f'{name}: expected one executable protocol screen')
    args = shlex.split(candidates[0].splitlines()[1])
    if args[:3] != ['jq', '-e', '-s']:
        raise AssertionError('check must use jq -e -s without an exit-masking pipeline')
    return args


class PackageContracts(unittest.TestCase):
    def test_frontmatter_and_context_budget(self):
        for name in NAMES:
            with self.subTest(skill=name):
                text = (SKILLS / name / 'SKILL.md').read_text()
                self.assertTrue(text.startswith('---\n'))
                _, front, body = text.split('---', 2)
                meta = yaml.safe_load(front)
                self.assertEqual(meta['name'], name)
                self.assertTrue(meta['description'].startswith('Use when '))
                self.assertTrue(meta['description'].endswith('.'))
                self.assertLessEqual(len(meta['description']), 60)
                self.assertTrue(body.strip())
                # A documented editorial context budget, not a behavioral-quality score.
                self.assertLessEqual(len(text), 15000)

    def test_catalog_keeps_all_nine_packages(self):
        index = (SKILLS / 'index.md').read_text()
        readme = (ROOT / 'README.md').read_text()
        actual = {p.parent.name for p in SKILLS.glob('*/SKILL.md')}
        self.assertEqual(len(actual), 9)
        for name in actual:
            self.assertIn(name, index)
            self.assertIn(name, readme)

    def test_active_package_references_exist(self):
        for name in NAMES:
            folder = SKILLS / name
            text = (folder / 'SKILL.md').read_text()
            refs = re.findall(r'`((?:references/|hooks/|rules/|docs/)[\w./-]+\.\w+)`', text)
            for ref in refs:
                with self.subTest(skill=name, reference=ref):
                    target = (folder / ref).resolve()
                    self.assertTrue(target.is_relative_to(folder.resolve()))
                    self.assertTrue(target.is_file(), ref)
            for required in ('reference.md', 'docs/README.md') if name in CLI_NAMES else ('references/execution-contract.md',):
                self.assertTrue((folder / required).is_file())

    def test_markdown_links_are_local_and_resolve(self):
        for name in NAMES:
            folder = SKILLS / name
            for p in folder.rglob('*.md'):
                if 'docs' in p.relative_to(folder).parts:
                    continue  # Immutable upstream snapshots retain their original link base.
                for ref in re.findall(r'\]\(([^)\s]+)\)', p.read_text()):
                    if '://' in ref or ref.startswith(('#', 'mailto:')):
                        continue
                    target = (p.parent / ref.split('#')[0]).resolve()
                    with self.subTest(file=str(p.relative_to(ROOT)), reference=ref):
                        self.assertTrue(target.is_relative_to(folder.resolve()))
                        self.assertTrue(target.exists())

    def test_no_live_host_paths_or_credentials(self):
        for name in NAMES:
            for p in (SKILLS / name).rglob('*'):
                if not p.is_file() or 'docs' in p.relative_to(SKILLS / name).parts:
                    continue
                text = p.read_text()
                self.assertNotIn('/home/hermes/', text, str(p))
                self.assertNotRegex(text, r'sk-or-v1-[A-Za-z0-9]{30,}')
                self.assertNotIn('rlarguesa@gmail.com', text)

    def test_no_runtime_orchestration_script(self):
        files = list((SKILLS / 'agentic-orchestrator').rglob('*'))
        self.assertFalse([p for p in files if p.is_file() and p.suffix in {'.py', '.js', '.ts', '.sh'}])


class Recipes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for command in ('bash', 'jq'):
            if not shutil.which(command):
                raise RuntimeError(f'mandatory recipe-check tool missing: {command}')

    def test_shell_syntax_without_execution(self):
        for name in CLI_NAMES:
            for i, block in enumerate(blocks(name)):
                with self.subTest(skill=name, block=i):
                    result = subprocess.run(['bash', '-n'], input=block, text=True, capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_invocations_keep_supervision_and_protocol_separate(self):
        for name in CLI_NAMES:
            invocations = [b for b in blocks(name) if '# protocol-check' not in b]
            self.assertGreaterEqual(len(invocations), 2, name)
            for b in invocations:
                with self.subTest(skill=name):
                    self.assertNotIn('nohup', b)
                    self.assertNotIn('2>&1', b)
                    self.assertNotIn('--fallback-model', b)
                    self.assertNotIn('--bare', b)
                    self.assertNotIn('--full-auto', b)
                    self.assertIn('2> ', b)
                    self.assertIn('$MODEL', b)
                    self.assertIn('$EFFORT', b)
                    self.assertTrue('</dev/null' in b or '< "$RUN/prompt.txt"' in b or '< "$NEXT_RUN/prompt.txt"' in b)
                    if name == 'claude-code-user':
                        self.assertIn('--verbose', b)
                        self.assertIn('--settings "$SKILL_DIR/hooks/settings-guard.json"', b)
                    if name == 'pi-user':
                        self.assertIn('-e "$SKILL_DIR/hooks/guard.ts"', b)

    def test_resume_is_exact_and_attempt_specific(self):
        flags = {'claude-code-user': '--resume "$SESSION_ID"', 'codex-user': 'exec resume "$THREAD_ID"', 'pi-user': '--session "$SESSION_ID"', 'opencode-user': '--session "$SESSION_ID"', 'antigravity-user': '--conversation "$CONVERSATION_ID"'}
        for name, exact in flags.items():
            resume = [b for b in blocks(name) if '$NEXT_RUN/' in b]
            self.assertEqual(len(resume), 1, name)
            self.assertIn(exact, resume[0])
            self.assertNotRegex(resume[0], r'--(?:continue|last|session-id)\b')
            self.assertIn('$MODEL', resume[0])
            self.assertIn('$EFFORT', resume[0])

    def screen(self, name, events=None, raw=None):
        args = protocol_command(name)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'events.jsonl'
            if raw is None and events is None:
                raise ValueError("provide events or raw fixture")
            path.write_text(raw if raw is not None else ''.join(json.dumps(e) + '\n' for e in (events or [])))
            args[-1] = str(path)
            result = subprocess.run(args, capture_output=True, text=True, timeout=10)
            return result.returncode == 0

    def test_protocol_positive_controls(self):
        fixtures = {
            'claude-code-user': [{'type': 'result', 'subtype': 'success', 'is_error': False, 'terminal_reason': 'completed', 'result': 'complete'}],
            'codex-user': [{'type': 'thread.started', 'thread_id': 'fixture'}, {'type': 'turn.completed', 'usage': {}}],
            'pi-user': [{'type': 'message_end', 'message': {'role': 'assistant', 'stopReason': 'stop'}}, {'type': 'agent_settled', 'aborted': False}],
            'opencode-user': [{'type': 'text', 'part': {'text': 'complete'}}, {'type': 'step_finish', 'part': {'reason': 'stop'}}],
            'antigravity-user': [{'event': 'result', 'result': {'status': 'SUCCESS', 'response': 'complete'}}],
        }
        for name, events in fixtures.items():
            with self.subTest(skill=name):
                self.assertTrue(self.screen(name, events))

    def test_structured_output_without_redundant_prose(self):
        self.assertTrue(self.screen('claude-code-user', [{'type': 'result', 'subtype': 'success', 'is_error': False, 'structured_output': {'ok': True}, 'result': ''}]))
        self.assertTrue(self.screen('antigravity-user', [{'event': 'result', 'result': {'status': 'SUCCESS', 'structured_output': {'ok': True}}}]))

    def test_claude_false_success_turn_limit_and_missing_status(self):
        base = {'type': 'result', 'subtype': 'success', 'is_error': False, 'terminal_reason': 'completed', 'result': 'complete'}
        for change in ({'is_error': True, 'terminal_reason': 'api_error'}, {'subtype': 'error_max_turns'}, {'terminal_reason': 'api_error'}, {'result': ''}):
            self.assertFalse(self.screen('claude-code-user', [base | change]))
        missing = dict(base)
        del missing['is_error']
        self.assertFalse(self.screen('claude-code-user', [missing]))
        self.assertFalse(self.screen('claude-code-user', [base, base | {'is_error': True}]))

    def test_codex_prior_success_does_not_mask_failure(self):
        self.assertFalse(self.screen('codex-user', [{'type': 'thread.started'}]))
        self.assertFalse(self.screen('codex-user', [{'type': 'turn.completed'}, {'type': 'turn.failed', 'error': {'message': 'fixture'}}]))

    def test_pi_requires_settled_and_final_stop(self):
        stopped = {'type': 'message_end', 'message': {'role': 'assistant', 'stopReason': 'stop'}}
        self.assertFalse(self.screen('pi-user', [stopped, {'type': 'agent_end'}]))
        self.assertFalse(self.screen('pi-user', [stopped, {'type': 'agent_settled', 'aborted': True}]))
        for reason in ('error', 'aborted', 'length', 'toolUse'):
            self.assertFalse(self.screen('pi-user', [{'type': 'message_end', 'message': {'role': 'assistant', 'stopReason': reason}}, {'type': 'agent_settled', 'aborted': False}]))

    def test_opencode_intermediate_event_alone_is_not_evidence(self):
        self.assertFalse(self.screen('opencode-user', [{'type': 'step_finish', 'part': {'reason': 'tool-calls'}}]))
        self.assertFalse(self.screen('opencode-user', [{'type': 'text', 'part': {'text': 'partial'}}]))

    def test_opencode_screen_is_not_a_final_turn_validator(self):
        # The docs explicitly require native final-turn evidence and independent artifacts.
        partial = [{'type': 'text', 'part': {'text': 'working'}}, {'type': 'step_finish', 'part': {'reason': 'tool-calls'}}]
        self.assertTrue(self.screen('opencode-user', partial))
        self.assertIn('only protocol screening', (SKILLS / 'opencode-user/SKILL.md').read_text())

    def test_antigravity_nonterminal_and_empty_results(self):
        for payload in ({'status': 'RUNNING', 'response': 'working'}, {'status': 'SUCCESS', 'response': ''}, {'status': 'ERROR', 'response': 'failed'}):
            self.assertFalse(self.screen('antigravity-user', [{'event': 'result', 'result': payload}]))

    def test_empty_and_truncated_streams_fail(self):
        for name in CLI_NAMES:
            for raw in ('', '{"type":', 'not-json\n'):
                with self.subTest(skill=name, raw=raw):
                    self.assertFalse(self.screen(name, raw=raw))


class FlowExamples(unittest.TestCase):
    def test_five_flows_have_resolved_dependencies_and_routes(self):
        folder = SKILLS / 'agentic-orchestrator/references/examples'
        examples = list(folder.glob('*.yaml')) + list(folder.glob('*.json'))
        self.assertEqual(len(examples), 5)
        for p in examples:
            data = yaml.safe_load(p.read_text())
            steps = data['steps']
            ids = {s['id'] for s in steps}
            self.assertEqual(len(ids), len(steps), str(p))
            self.assertTrue(data['objective']['done_when'])
            for step in steps:
                self.assertTrue(set(step.get('needs', [])) <= ids)
                roles = step.get('agents', [step['agent']] if 'agent' in step else [])
                self.assertTrue(set(roles) <= set(data['agents']))
                self.assertTrue(any(k in step for k in ('accept', 'verify', 'human')))
                for route in step.get('route', []):
                    if 'goto' in route:
                        self.assertIn(route['goto'], ids)
                    if 'default' in route:
                        self.assertIn(route['default'], ids)
                if isinstance(step.get('on_fail'), dict) and 'goto' in step['on_fail']:
                    self.assertIn(step['on_fail']['goto'], ids)

    def test_explicit_content_approval_never_defaults_to_consent(self):
        path = SKILLS / 'agentic-orchestrator/references/examples/feature-with-review.yaml'
        data = yaml.safe_load(path.read_text())
        approve = next(s for s in data['steps'] if s['id'] == 'approve')
        self.assertFalse(any('default' in r for r in approve['route']))
        self.assertTrue(any('explicitly approves' in r.get('when', '') for r in approve['route']))

    def test_authorized_release_keeps_effects_in_controller(self):
        path = SKILLS / 'agentic-orchestrator/references/examples/authorized-release.yaml'
        data = yaml.safe_load(path.read_text())
        external = [s for s in data['steps'] if s.get('effects') == 'external']
        self.assertEqual([s['id'] for s in external], ['publish', 'install', 'deliver'])
        for step in external:
            self.assertEqual(step['agent'], 'controller')
            self.assertEqual(step['authorization'], data['authorization']['id'])
            self.assertIn('undo', step)
        self.assertTrue(data['limits']['closing_reserve'])
        self.assertEqual(data['agents']['builder']['effort'], 'max')

    def test_documented_canonical_events_have_sequence(self):
        text = (SKILLS / 'agentic-orchestrator/references/flow-spec.md').read_text()
        json_blocks = re.findall(r'```json\n(.*?)```', text, re.S)
        events = [json.loads(line) for block in json_blocks for line in block.splitlines() if line.startswith('{"seq"')]
        self.assertEqual([e['seq'] for e in events], [1, 2, 3])
        self.assertTrue(all(e['flow_version'] == 1 for e in events))


if __name__ == '__main__':
    unittest.main()
