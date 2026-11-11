"""Exercise actual guard handlers and candidate generators using synthetic inputs only."""
from pathlib import Path
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / 'skills'
sys.dont_write_bytecode = True  # Import tested helpers without modifying installed packages.


def required_command(name):
    value = shutil.which(name)
    if value is None:
        raise RuntimeError(f'mandatory guard-check tool unavailable: {name}')
    return value
BLOCK = [
    'git push origin main', 'git -C "/work tree" push origin main',
    'git -c core.quotepath=false push', 'echo hi && git push --help',
    'git \\\n push origin main', 'curl -X PATCH https://example.invalid/row',
    'curl --request=DELETE https://example.invalid/row',
    'curl -d x https://example.invalid/row', 'npm publish', 'sudo true',
    'terraform apply', 'gh pr create', 'rm -rf /', 'rm -fr /home/test-user',
    'cat /workspace/.env.local',
]
CLEAN = ['git status --short', 'git diff', 'git stash push', 'curl -X GET https://example.invalid/', 'python3 -m unittest', 'rm -rf /workspace/cache', 'cat /workspace/.env.example']
SENSITIVE = ['.env', '.env.local', '/project/.secrets/token', '/project/auth.json', '/project/.credentials.json', r'C:\project\.env.production']


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError('cannot load tested helper')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def boundary_cases():
    cases = []
    for separator in (' && ', ' ; ', ' || ', ' | ', '\n', '\r\n'):
        cases.extend([
            (f'rm -rf scratch-cache{separator}printf -- /', False),
            (f'curl https://example.invalid/{separator}printf -- -d', False),
            (f'rm scratch-cache{separator}printf -- -rf /', False),
            (f'printf -- /{separator}rm -rf /', True),
            (f'curl https://example.invalid/{separator}curl -d x https://example.invalid/row', True),
        ])
    # Quoted separators remain arguments, not simple-command boundaries.
    cases.extend([
        ('curl ";" -d x https://example.invalid/row', True),
        ('rm -rf ";" /', True),
        ('curl 2>&1 -d x https://example.invalid/row', True),
        ('rm -rf scratch-cache 2>&1 /', True),
        ('rm -rf "scratch;cache" && printf -- /', False),
    ])
    return cases


def native_permission_decision(config, tool, target):
    """Independent explicit-rule oracle: flatten in order, last two-pattern match wins.

    This models the stored rule layer, not native default policies or enforcement.
    It intentionally calls neither the merge helper nor its effective() evaluator.
    """
    def matches(value, pattern):
        expression = re.escape(pattern).replace(r'\*', '.*').replace(r'\?', '.')
        return re.fullmatch(expression, value, re.DOTALL) is not None

    permission = config.get('permission', {})
    if isinstance(permission, str):
        permission = {'*': permission}
    decision = None
    for tool_pattern, policy in permission.items():
        targets = {'*': policy} if isinstance(policy, str) else policy
        for target_pattern, action in targets.items():
            if matches(tool, tool_pattern) and matches(target, target_pattern):
                decision = action
    return decision


class ClaudeGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bash = required_command('bash')
        cls.folder = SKILLS / 'claude-code-user/hooks'

    def run_guard(self, payload=None, raw=None, path=None, env=None):
        return subprocess.run([self.bash, str(path or self.folder / 'guard.sh')], input=raw if raw is not None else json.dumps(payload), text=True, capture_output=True, env=env, timeout=10)

    def test_direct_commands_block_and_clean_controls_pass(self):
        for command, expected in [(s, 2) for s in BLOCK] + [(s, 0) for s in CLEAN]:
            with self.subTest(command=command):
                result = self.run_guard({'tool_name': 'Bash', 'tool_input': {'command': command}})
                self.assertEqual(result.returncode, expected, result.stderr)

    def test_simple_command_boundaries_do_not_lend_arguments(self):
        for command, blocked in boundary_cases():
            with self.subTest(command=command):
                result = self.run_guard({'tool_name': 'Bash', 'tool_input': {'command': command}})
                self.assertEqual(result.returncode, 2 if blocked else 0, result.stderr)

    def test_paths_across_all_guarded_file_tools(self):
        for tool in ('Read', 'Edit', 'Write'):
            for path in SENSITIVE:
                self.assertEqual(self.run_guard({'tool_name': tool, 'tool_input': {'file_path': path}}).returncode, 2)
            for path in ('README.md', '/project/.env.example'):
                self.assertEqual(self.run_guard({'tool_name': tool, 'tool_input': {'file_path': path}}).returncode, 0)

    def test_malformed_payloads_are_blocking_not_generic_errors(self):
        for raw in ('bad-json', '', 'null', '[]', '{}', '{"tool_name":"Bash","tool_input":{"command":42}}'):
            with self.subTest(raw=raw):
                self.assertEqual(self.run_guard(raw=raw).returncode, 2)
        self.assertEqual(self.run_guard({'tool_name': 'Bash', 'tool_input': {'command': 'echo "'}}).returncode, 2)

    def test_missing_python_and_missing_helper_fail_closed(self):
        environment = dict(os.environ, PATH='')
        valid = {'tool_name': 'Bash', 'tool_input': {'command': 'git status'}}
        self.assertEqual(self.run_guard(valid, env=environment).returncode, 2)
        with tempfile.TemporaryDirectory() as directory:
            wrapper = Path(directory) / 'guard.sh'
            shutil.copy2(self.folder / 'guard.sh', wrapper)
            self.assertEqual(self.run_guard(valid, path=wrapper).returncode, 2)

    def test_settings_command_is_portable_and_missing_hook_blocks(self):
        settings = json.loads((self.folder / 'settings-guard.json').read_text())
        event = settings['hooks']['PreToolUse'][0]
        self.assertEqual(set(event['matcher'].split('|')), {'Bash', 'Read', 'Edit', 'Write'})
        command = event['hooks'][0]['command']
        with tempfile.TemporaryDirectory(prefix='skill path ') as directory:
            target = Path(directory) / 'hooks'
            shutil.copytree(self.folder, target)
            environment = dict(os.environ, CLAUDE_CODE_USER_GUARD=str(target / 'guard.sh'))
            for payload, expected in [({'tool_name': 'Bash', 'tool_input': {'command': 'git status'}}, 0), ({'tool_name': 'Bash', 'tool_input': {'command': 'git push --help'}}, 2)]:
                result = subprocess.run([self.bash, '-c', command], input=json.dumps(payload), text=True, capture_output=True, env=environment, timeout=10)
                self.assertEqual(result.returncode, expected, result.stderr)
            environment['CLAUDE_CODE_USER_GUARD'] = str(target / 'missing.sh')
            result = subprocess.run([self.bash, '-c', command], input='{}', text=True, capture_output=True, env=environment, timeout=10)
            self.assertEqual(result.returncode, 2)


class PiGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.node = required_command('node')
        cls.guard = (SKILLS / 'pi-user/hooks/guard.ts').as_uri()

    def call(self, events):
        script = """import fs from 'node:fs';
const {default: register} = await import(process.argv[1]);
let handler;
register({on: (name, fn) => {if (name !== 'tool_call') throw Error('wrong event'); handler=fn;}});
const events=JSON.parse(fs.readFileSync(0,'utf8'));
console.log(JSON.stringify(await Promise.all(events.map(async e => (await handler(e))?.block === true))));
"""
        result = subprocess.run([self.node, '--input-type=module', '-e', script, self.guard], input=json.dumps(events), text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_actual_handler_direct_command_controls(self):
        for tool in ('bash', 'powershell'):
            commands = BLOCK + CLEAN
            actual = self.call([{'toolName': tool, 'input': {'command': s}} for s in commands])
            self.assertEqual(actual, [True] * len(BLOCK) + [False] * len(CLEAN), tool)

    def test_powershell_git_exe_publication_and_clean_controls(self):
        commands = [
            'git.exe push origin main',
            r'& "C:\Program Files\Git\cmd\git.exe" push origin main',
            'git.exe stash push',
            'git.exe status --short',
            r'& "C:\Program Files\Git\cmd\git.exe" stash push',
            r'& "C:\Program Files\Git\cmd\git.exe" status --short',
        ]
        events = [{'toolName': 'powershell', 'input': {'command': command}} for command in commands]
        self.assertEqual(self.call(events), [True, True, False, False, False, False])

    def test_simple_command_boundaries_do_not_lend_arguments(self):
        cases = boundary_cases()
        for tool in ('bash', 'powershell'):
            with self.subTest(tool=tool):
                events = [{'toolName': tool, 'input': {'command': command}} for command, _ in cases]
                self.assertEqual(self.call(events), [blocked for _, blocked in cases])

    def test_paths_windows_separators_and_malformed_input(self):
        events = [{'toolName': t, 'input': {'path': p}} for t in ('read', 'write', 'edit', 'grep', 'find', 'ls') for p in SENSITIVE]
        self.assertTrue(all(self.call(events)))
        invalid = [None, {}, {'toolName': 'bash', 'input': {'command': 1}}, {'toolName': 'read', 'input': {'path': {}}}]
        self.assertEqual(self.call(invalid), [True] * len(invalid))
        self.assertEqual(self.call([{'toolName': 'read', 'input': {'path': '.env.example'}}, {'toolName': 'ls', 'input': {}}]), [False, False])

    def test_unknown_tool_is_explicitly_outside_coverage(self):
        self.assertEqual(self.call([{'toolName': 'codemode', 'input': {'code': 'fixture'}}]), [False])


class OpenCodeOverlay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = SKILLS / 'opencode-user/hooks'
        cls.helper = module(cls.folder / 'merge-permissions.py', 'opencode_guard_merge')
        cls.overlay = json.loads((cls.folder / 'guard-permissions.json').read_text())

    def test_overlay_has_no_broad_allow(self):
        for tool, rules in self.overlay['permission'].items():
            self.assertNotEqual(rules.get('*'), 'allow')
            self.assertTrue(all(v == 'deny' or (k == '*.env.example' and v == 'allow') for k, v in rules.items()), tool)

    def test_scalar_ask_and_deny_are_not_widened(self):
        for policy in ('ask', 'deny'):
            config = {'permission': policy, 'model': 'preserved'}
            candidate = self.helper.merge(config, self.overlay)
            self.assertEqual(self.helper.effective(candidate, 'bash', 'git status'), policy)
            self.assertEqual(self.helper.effective(candidate, 'read', 'private/.env.example'), 'deny')
            self.assertEqual(candidate['model'], 'preserved')
            self.assertEqual(config['permission'], policy)

    def test_duplicate_patterns_move_after_later_allow_and_other_denials_survive(self):
        config = {'permission': {'bash': {'git push *': 'deny', '*': 'allow', 'npm test': 'deny'}, 'read': {'*': 'allow', 'private/*': 'deny'}}}
        candidate = self.helper.merge(config, self.overlay)
        self.assertEqual(self.helper.effective(candidate, 'bash', 'git push origin main'), 'deny')
        self.assertEqual(self.helper.effective(candidate, 'bash', 'npm test'), 'deny')
        self.assertEqual(self.helper.effective(candidate, 'bash', 'git status'), 'allow')
        self.assertEqual(self.helper.effective(candidate, 'read', 'private/.env.example'), 'deny')
        self.assertEqual(self.helper.effective(candidate, 'read', 'private/ordinary.txt'), 'deny')

    def test_actual_overlay_matching_for_common_direct_commands(self):
        candidate = self.helper.merge({'permission': 'allow'}, self.overlay)
        unsafe = [s for s in BLOCK if '\n' not in s and s not in {'rm -fr /home/test-user', 'cat /workspace/.env.local'}]
        # Native OpenCode parses compound commands. Here we test the stored wildcard layer only.
        for command in unsafe:
            with self.subTest(command=command):
                self.assertEqual(self.helper.effective(candidate, 'bash', command), 'deny')
        for command in CLEAN:
            # Native wildcard policy deliberately retains its original absolute-removal deny.
            expected = 'deny' if command == 'rm -rf /workspace/cache' else 'allow'
            self.assertEqual(self.helper.effective(candidate, 'bash', command), expected, command)
        self.assertEqual(self.helper.effective(candidate, 'bash', 'rm -rf scratch-cache'), 'allow')
        for tool in ('read', 'edit'):
            self.assertEqual(self.helper.effective(candidate, tool, '.env.local'), 'deny')
            self.assertEqual(self.helper.effective(candidate, tool, '.env.example'), 'allow')

    def test_independent_oracle_uses_last_matching_tool_and_target_patterns(self):
        config = {'permission': {
            '*': 'ask',
            'b*': 'deny',
            'r*': {'*': 'deny', 'public/*': 'allow'},
            'read': {'public/private/*': 'ask'},
        }}
        for tool, target, expected in (
            ('bash', 'git status', 'deny'),
            ('build', 'ordinary', 'deny'),
            ('read', 'ordinary.txt', 'deny'),
            ('read', 'public/info.txt', 'allow'),
            ('read', 'public/private/info.txt', 'ask'),
            ('edit', 'ordinary.txt', 'ask'),
        ):
            self.assertEqual(native_permission_decision(config, tool, target), expected)
        config['permission']['*'] = config['permission'].pop('*')
        self.assertEqual(native_permission_decision(config, 'bash', 'git status'), 'ask')
        self.assertEqual(native_permission_decision(config, 'read', 'public/info.txt'), 'ask')

    def test_candidates_preserve_native_precedence_for_supported_tools(self):
        configs = [
            {'permission': policy} for policy in ('allow', 'ask', 'deny')
        ] + [
            {'permission': {'*': 'allow', 'bash': {'npm test': 'deny'}, 'read': {'private/*': 'deny'}}},
            {'permission': {'bash': {'*': 'deny'}, 'read': {'*': 'deny'}, '*': 'ask'}},
            {'permission': {'*': {'*': 'ask', 'public/*': 'allow'}, 'read': {'private/*': 'deny'}}},
        ]
        rank = {'allow': 0, 'ask': 1, 'deny': 2}
        for config in configs:
            with self.subTest(config=config):
                candidate = self.helper.merge(config, self.overlay)
                for tool, target in (
                    ('bash', 'git status'), ('bash', 'npm test'),
                    ('read', 'ordinary.txt'), ('read', 'private/notes.txt'),
                    ('read', 'private/.env.example'), ('read', 'public/info.txt'),
                    ('edit', 'ordinary.txt'), ('grep', 'ordinary.txt'),
                ):
                    before = native_permission_decision(config, tool, target)
                    after = native_permission_decision(candidate, tool, target)
                    assert before is not None
                    assert after is not None
                    self.assertGreaterEqual(rank[after], rank[before], (tool, target, before, after))
                self.assertEqual(native_permission_decision(candidate, 'bash', 'git push origin main'), 'deny')
                self.assertEqual(native_permission_decision(candidate, 'read', '.env.local'), 'deny')

    def test_tool_name_patterns_must_be_preserved_or_explicitly_rejected(self):
        for pattern, tool, target in (('b*', 'bash', 'git status'), ('r*', 'read', 'ordinary.txt')):
            with self.subTest(pattern=pattern):
                config = {'permission': {'*': 'allow', pattern: 'deny'}}
                self.assertEqual(native_permission_decision(config, tool, target), 'deny')
                try:
                    candidate = self.helper.merge(config, self.overlay)
                except ValueError as error:
                    self.assertRegex(str(error), 'tool-name pattern')
                else:
                    self.assertEqual(native_permission_decision(candidate, tool, target), 'deny')

    def test_global_guard_selector_must_not_override_later_tool_denial(self):
        config = {'permission': {'*': 'allow', 'bash': 'deny'}}
        overlay = {'permission': {'*': {'git push *': 'deny'}}}
        self.assertEqual(native_permission_decision(config, 'bash', 'git status'), 'deny')
        try:
            candidate = self.helper.merge(config, overlay)
        except ValueError as error:
            self.assertRegex(str(error), 'tool-name pattern')
        else:
            self.assertEqual(native_permission_decision(candidate, 'bash', 'git status'), 'deny')

    def test_cli_rejects_tool_name_patterns_without_writing_candidate(self):
        for pattern in ('b*', 'r*'):
            with self.subTest(pattern=pattern), tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / 'existing.json'
                target = Path(directory) / 'candidate.json'
                raw = json.dumps({'permission': {'*': 'allow', pattern: 'deny'}})
                source.write_text(raw)
                result = subprocess.run([sys.executable, str(self.folder / 'merge-permissions.py'), str(source), str(self.folder / 'guard-permissions.json'), str(target)], capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('tool-name pattern', result.stderr)
                self.assertFalse(target.exists())
                self.assertEqual(source.read_text(), raw)

    def test_real_cli_writes_candidate_only_and_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'existing.json'
            target = Path(directory) / 'candidate.json'
            raw = '{"permission":"ask","unrelated":{"retain":true}}'
            source.write_text(raw)
            result = subprocess.run([sys.executable, str(self.folder / 'merge-permissions.py'), str(source), str(self.folder / 'guard-permissions.json'), str(target)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(source.read_text(), raw)
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            source.write_text('{"permission":"ask","permission":"allow"}')
            invalid = Path(directory) / 'invalid.json'
            result = subprocess.run([sys.executable, str(self.folder / 'merge-permissions.py'), str(source), str(self.folder / 'guard-permissions.json'), str(invalid)], capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(invalid.exists())


class CodexRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.codex = required_command('codex')
        cls.folder = SKILLS / 'codex-user/rules'

    def decision(self, path, *command):
        result = subprocess.run([self.codex, 'execpolicy', 'check', '--rules', str(path), '--', *command], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout).get('decision')

    def test_native_checker_denies_seeded_commands_and_preserves_clean_control(self):
        guard = self.folder / 'guard.rules'
        for command in (['git', 'push', 'origin', 'main'], ['sudo', 'true'], ['npm', 'publish'], ['rm', '-rf', '/']):
            self.assertEqual(self.decision(guard, *command), 'forbidden')
        self.assertNotEqual(self.decision(guard, 'git', 'status'), 'forbidden')
        self.assertNotEqual(self.decision(guard, 'git', 'stash', 'push'), 'forbidden')

    def test_prefix_limit_is_recorded_not_claimed_protection(self):
        guard = self.folder / 'guard.rules'
        self.assertNotEqual(self.decision(guard, 'cat', '/home/USER/.secrets/token'), 'forbidden')
        self.assertNotEqual(self.decision(guard, 'git', '-C', '/workspace', 'push'), 'forbidden')

    def test_generator_handles_space_path_and_does_not_modify_template(self):
        template = (self.folder / 'guard.rules').read_bytes()
        with tempfile.TemporaryDirectory(prefix='guard candidate ') as directory:
            target = Path(directory) / 'candidate.rules'
            secret = str(Path(directory) / 'secret folder')
            command = [sys.executable, str(self.folder / 'install-guard.py'), '--secrets-dir', secret, '--output', str(target)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn('/home/USER', target.read_text())
            self.assertEqual(self.decision(target, 'cat', secret), 'forbidden')
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            self.assertNotEqual(subprocess.run(command, capture_output=True, timeout=10).returncode, 0)
        self.assertEqual((self.folder / 'guard.rules').read_bytes(), template)


class AntigravityOverlay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = SKILLS / 'antigravity-user/rules'
        cls.helper = module(cls.folder / 'merge-permissions.py', 'agy_guard_merge')
        cls.overlay = json.loads((cls.folder / 'guard-permissions.json').read_text())
        cls.patterns = [re.compile(s[len('command(regex:'):-1]) for s in cls.overlay['permissions']['deny'] if s.startswith('command(regex:')]

    def test_actual_regex_seeded_and_clean_controls(self):
        for command in ('git push origin main', 'git -C "/work tree" push origin main', 'echo hi && git push --help', 'curl -X PATCH https://example.invalid/', 'curl --request=DELETE https://example.invalid/', 'curl -d x https://example.invalid/', 'npm publish', 'sudo true', 'rm -rf /'):
            self.assertTrue(any(p.fullmatch(command) for p in self.patterns), command)
        for command in CLEAN:
            self.assertFalse(any(p.fullmatch(command) for p in self.patterns), command)

    def test_generator_preserves_denials_and_resolves_placeholders(self):
        config = {'permissions': {'deny': ['command(custom)'], 'ask': ['command(other)']}, 'model': 'preserved'}
        result = self.helper.merge(config, self.overlay, str(Path.home() / 'fixture-secret-dir'))
        self.assertIn('command(custom)', result['permissions']['deny'])
        self.assertEqual(result['permissions']['ask'], ['command(other)'])
        self.assertEqual(result['model'], 'preserved')
        self.assertNotIn('/home/USER', json.dumps(result))
        self.assertEqual(config['permissions']['deny'], ['command(custom)'])
        invalid = {'permissions': {'deny': ['command(regex:broken[)']}}
        with self.assertRaises(re.error):
            self.helper.merge({}, invalid, str(Path.home() / 'fixture-secret-dir'))

    def test_cli_rejects_duplicates_and_relative_secret_path(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.json'
            source.write_text('{"permissions":{},"permissions":{}}')
            target = Path(directory) / 'target.json'
            result = subprocess.run([sys.executable, str(self.folder / 'merge-permissions.py'), str(source), str(self.folder / 'guard-permissions.json'), str(Path(directory) / 'secrets'), str(target)], capture_output=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(target.exists())
        with self.assertRaises(ValueError):
            self.helper.merge({}, self.overlay, 'relative-secrets')


if __name__ == '__main__':
    unittest.main()
