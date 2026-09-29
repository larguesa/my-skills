"""End-to-end tests: exact compact JSON bytes, no appended LF; no API calls."""
import pathlib
import subprocess
import sys
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "pack.py"


class PackTests(unittest.TestCase):
    def run_pack(self, raw):
        return subprocess.run([sys.executable, str(SCRIPT)], input=raw,
                              capture_output=True, timeout=10)

    @unittest.skipUnless(sys.platform.startswith("linux"),
                         "requires POSIX RLIMIT_AS with Linux address-space semantics")
    def test_escape_heavy_input_under_memory_limit(self):
        import resource

        def limit_memory():
            ceiling = 256 * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (ceiling, ceiling))

        raw = b'"' + b'\\n' * 2000000 + b'"'
        result = subprocess.run([sys.executable, str(SCRIPT)], input=raw,
                                capture_output=True, timeout=20,
                                preexec_fn=limit_memory)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, raw)

    @unittest.skipUnless(pathlib.Path('/dev/full').exists(), "requires /dev/full")
    def test_output_failure_is_sanitized_including_buffered_flush(self):
        for raw in [b'{}', b'"' + b'x' * 10000 + b'"']:
            with self.subTest(size=len(raw)), open('/dev/full', 'wb') as sink:
                result = subprocess.run([sys.executable, str(SCRIPT)], input=raw,
                                        stdout=sink, stderr=subprocess.PIPE, timeout=10)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(result.stderr, b'pack: output error\n')

    def test_preserves_exact_number_lexemes_and_string_bytes(self):
        raw = b' { "id": "001", "n": 1.234567890123456789012345, "e": 1e+999, "z": -0, "s": "a  b \\n \\" x" } \n'
        expected = b'{"id":"001","n":1.234567890123456789012345,"e":1e+999,"z":-0,"s":"a  b \\n \\" x"}'
        result = self.run_pack(raw)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, expected)

    def test_rejects_ambiguous_or_nonstandard_input_without_partial_output(self):
        for raw in [b'{"a":1,"a":2}', b'{"a":1,"\\u0061":2}',
                    b'{"n":NaN}', b'Infinity', b'-Infinity', b'[1,]',
                    b'{} {}', b'"unterminated', b'\xff', b'', b' \t\r\n',
                    b'\xef\xbb\xbf{}', b'01', b'-01', b'+1', b'.1', b'1.',
                    b'1e', b'1e+', b'--1', b'"a\x00b"', b'"a\nb"',
                    b'"\\x41"', b'"\\u123"', b'"\\uZZZZ"', b'"abc\\',
                    b'"\xc0\xaf"', b'\xc2\xa0{}', b'{}\x0b']:
            with self.subTest(raw=raw):
                result = self.run_pack(raw)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, b'')
                self.assertEqual(result.stderr, b'pack: invalid JSON input\n')

    def test_oversize_input_rejected_before_output(self):
        result = self.run_pack(b'"' + b'x' * (10 * 1024 * 1024) + b'"')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b'')
        self.assertEqual(result.stderr, b'pack: invalid JSON input\n')

    def test_valid_scalar_and_size_boundary(self):
        for raw in [b' null ', b' true ', b' false ', b' 12 ',
                    b'"' + b'x' * (10 * 1024 * 1024 - 2) + b'"']:
            with self.subTest(size=len(raw)):
                result = self.run_pack(raw)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, raw.strip())

    def test_exact_input_cap_is_idempotent(self):
        raw = b'"' + b'x' * (10 * 1024 * 1024 - 2) + b'"'
        first = self.run_pack(raw)
        second = self.run_pack(first.stdout)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, raw)
        self.assertEqual(second.stdout, raw)

    def test_long_integer_lexeme_is_not_converted(self):
        raw = b'-' + b'9' * 10000
        result = self.run_pack(b' [ ' + raw + b' ] ')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, b'[' + raw + b']')

    def test_escape_parity_and_unicode_bytes_are_preserved(self):
        tokens = [b'"\\\\"', b'"\\\\\\\" x"', b'"\\u0061\\/\\t"',
                  b'"\\ud800"', '"á 水 🙂  x"'.encode('utf-8')]
        result = self.run_pack(b' [ \n' + b' , \t'.join(tokens) + b'\r ] ')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, b'[' + b','.join(tokens) + b']')

    def test_nested_duplicate_and_depth_errors_are_sanitized(self):
        for raw in [b'{"x":{"a":1,"a":2}}', b'[' * 20000 + b']' * 20000]:
            result = self.run_pack(raw)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, b'')
            self.assertEqual(result.stderr, b'pack: invalid JSON input\n')

    def test_unicode_nested_values_and_idempotence(self):
        import json
        data = {"a": [None, True, False, {"á": "line\n tab\t \\ \""}], "empty": []}
        raw = json.dumps(data, ensure_ascii=False, indent=2).encode()
        first = self.run_pack(raw)
        second = self.run_pack(first.stdout)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(json.loads(first.stdout), data)


if __name__ == "__main__":
    unittest.main()
