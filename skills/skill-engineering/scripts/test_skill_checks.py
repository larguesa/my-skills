"""Fixtures artificiais: testes do auxiliar, não de qualidade de modelos."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

try:
    import skill_checks as checks
except ModuleNotFoundError as exc:
    if exc.name != "skill_checks":
        raise
    checks = None


class SkillChecksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "example-skill"
        self.root.mkdir()

    def write_skill(self, header="name: example-skill\ndescription: Do one useful thing.", body="# Instructions\nRead the input."):
        (self.root / "SKILL.md").write_text(f"---\n{header}\n---\n{body}\n", encoding="utf-8")

    def test_validate_happy_path(self):
        self.assertIsNotNone(checks, "O auxiliar skill_checks ainda não existe")
        self.write_skill()
        result = checks.validate_skill(self.root, profile="portable")
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["profile"], "portable")

    def test_validate_frontmatter_and_required_fields(self):
        invalid = ["{}", "[]", "null", "name: [", "!!python/object:os.system {}",
                   "name: example-skill", "name: example-skill\ndescription: ' '"]
        for header in invalid:
            with self.subTest(header=header):
                self.write_skill(header)
                self.assertFalse(checks.validate_skill(self.root)["valid"])
        self.write_skill(body=" ")
        self.assertFalse(checks.validate_skill(self.root)["valid"])
        (self.root / "SKILL.md").write_text("No frontmatter", encoding="utf-8")
        self.assertFalse(checks.validate_skill(self.root)["valid"])
        (self.root / "SKILL.md").unlink()
        self.assertFalse(checks.validate_skill(self.root)["valid"])

    def test_name_format_directory_and_length(self):
        for name in ["Other", "other", "-example-skill", "example--skill", "example-skill-", "x" * 65]:
            with self.subTest(name=name):
                self.write_skill(f"name: {name}\ndescription: Useful.")
                self.assertFalse(checks.validate_skill(self.root)["valid"])

    def test_profile_specific_fields_and_description_limits(self):
        self.write_skill("name: example-skill\ndescription: " + "x" * 61)
        self.assertFalse(checks.validate_skill(self.root, "hermes")["valid"])
        self.assertTrue(checks.validate_skill(self.root, "portable")["valid"])
        self.write_skill("name: example-skill\ndescription: " + "x" * 1025)
        self.assertFalse(checks.validate_skill(self.root, "portable")["valid"])
        self.write_skill("name: example-skill\ndescription: Useful.\nversion: 1\nauthor: Someone\nplatforms: [linux]\ncustom-extension: yes")
        self.assertTrue(checks.validate_skill(self.root, "hermes")["valid"])
        self.assertFalse(checks.validate_skill(self.root, "portable")["valid"])
        self.write_skill("name: example-skill\ndescription: Useful.\nlicense: MIT\ncompatibility: Python\nmetadata: {}\nallowed-tools: Read")
        self.assertTrue(checks.validate_skill(self.root, "portable")["valid"])

    def test_missing_relative_links_and_reference_definitions(self):
        refs = self.root / "references"
        refs.mkdir()
        (refs / "guide.md").write_text("[missing][ref]\n[ref]: missing.txt\n", encoding="utf-8")
        self.write_skill(body="[guide](references/guide.md) [remote](https://example.org) [anchor](#section)")
        result = checks.validate_skill(self.root)
        self.assertFalse(result["valid"])
        self.assertIn("missing.txt", " ".join(result["errors"]))
        (refs / "missing.txt").touch()
        self.assertTrue(checks.validate_skill(self.root)["valid"])
        self.write_skill(body="![missing](missing.png)")
        self.assertFalse(checks.validate_skill(self.root)["valid"])

    def test_absolute_traversal_and_encoded_paths_are_rejected(self):
        outside = Path(self.tmp.name) / "outside.txt"
        outside.touch()
        for link in ["../outside.txt", "%2e%2e/outside.txt", str(outside), "C:\\outside.txt", "..%5coutside.txt"]:
            with self.subTest(link=link):
                self.write_skill(body=f"[unsafe]({link})")
                self.assertFalse(checks.validate_skill(self.root)["valid"])

    def test_symlinks_cannot_escape_package(self):
        outside = Path(self.tmp.name) / "outside.md"
        outside.write_text("Do not read outside.", encoding="utf-8")
        link = self.root / "linked.md"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks indisponíveis neste sistema")
        self.write_skill(body="[unsafe](linked.md)")
        self.assertFalse(checks.validate_skill(self.root)["valid"])
        link.unlink()
        refs = self.root / "references"
        refs.mkdir()
        (refs / "linked.md").symlink_to(outside)
        self.write_skill()
        self.assertFalse(checks.validate_skill(self.root)["valid"])

    def test_markdown_code_is_not_a_link_and_nested_paths_work(self):
        (self.root / "a(b).txt").touch()
        (self.root / "space name.txt").touch()
        self.write_skill(body='[nested](a(b).txt) [space](<space name.txt> "title")\n`[code](missing)`\n```md\n[code](missing)\n```')
        self.assertTrue(checks.validate_skill(self.root)["valid"])

    def test_size_warning_is_not_quality_certification(self):
        self.write_skill(body="# Instructions\n" + "Read input.\n" * 501)
        result = checks.validate_skill(self.root)
        self.assertTrue(result["valid"])
        self.assertTrue(result["warnings"])
        self.assertIn("quality", result["scope"])

    def test_bad_directory_and_profile_are_expected_input_errors(self):
        with self.assertRaises(ValueError):
            checks.validate_skill(self.root / "absent")
        with self.assertRaises(ValueError):
            checks.validate_skill(self.root, "unknown")


class AggregateTests(unittest.TestCase):
    @staticmethod
    def run_fixture(case="case", condition="with_skill", **changes):
        run = dict(case_id=case, replicate=1, condition=condition, status="completed",
                   task_success=True, critical_failures=0)
        run.update(changes)
        return run

    def aggregate(self, runs, baseline="without_skill"):
        self.assertTrue(hasattr(checks, "aggregate_runs"), "Agregação ainda não implementada")
        return checks.aggregate_runs(dict(schema_version=1, baseline=baseline, runs=runs))

    def test_paired_success_failure_technical_error_and_missing_condition(self):
        runs = [self.run_fixture("a"), self.run_fixture("a", "baseline", task_success=False),
                self.run_fixture("b", critical_failures=1), self.run_fixture("b", "baseline"),
                self.run_fixture("c", status="technical_error", task_success=None, critical_failures=None),
                self.run_fixture("c", "baseline"), self.run_fixture("d"),
                self.run_fixture("e", status="not_run", task_success=None, critical_failures=None),
                self.run_fixture("e", "baseline")]
        report = self.aggregate(runs, "old_skill")
        self.assertEqual(report["baseline"], "old_skill")
        self.assertEqual(report["run_count"], 9)
        self.assertEqual(report["conditions"]["with_skill"]["technical_error"], 1)
        self.assertEqual(report["conditions"]["with_skill"]["not_run"], 1)
        self.assertEqual(report["pairs"], dict(total=5, completed=2, incomplete=3, missing_condition=1, non_completed=2))
        self.assertEqual(report["success"]["n_pairs"], 2)
        self.assertEqual(report["success"]["with_skill"]["rate_pct"], 50.0)
        self.assertEqual(report["success"]["baseline"]["rate_pct"], 50.0)
        self.assertEqual(report["success"]["delta_pp"], 0.0)
        self.assertEqual(report["inconsistencies"], [dict(case_id="b", replicate=1, condition="with_skill")])

    def test_positive_delta_is_in_percentage_points(self):
        report = self.aggregate([self.run_fixture(), self.run_fixture(condition="baseline", task_success=False)])
        self.assertEqual(report["success"]["delta_pp"], 100.0)

    def test_metrics_use_only_observed_completed_pairs(self):
        runs = [self.run_fixture("a", duration_ms=10, input_tokens=100, output_tokens=None, cost_usd=0),
                self.run_fixture("a", "baseline", duration_ms=20, input_tokens=None, output_tokens=9, cost_usd=0),
                self.run_fixture("b", duration_ms=30, output_tokens=0),
                self.run_fixture("b", "baseline", duration_ms=40, output_tokens=0),
                self.run_fixture("c", status="technical_error", task_success=None, critical_failures=None, duration_ms=100),
                self.run_fixture("c", "baseline", duration_ms=200)]
        metrics = self.aggregate(runs)["metrics"]
        duration = metrics["duration_ms"]
        self.assertEqual(duration["n_pairs"], 2)
        self.assertEqual(duration["with_skill"]["mean"], 20)
        self.assertAlmostEqual(duration["with_skill"]["sample_stddev"], 14.142135623730951)
        self.assertEqual(duration["baseline"]["mean"], 30)
        self.assertEqual(duration["delta_mean"], -10)
        self.assertEqual(metrics["input_tokens"]["n_pairs"], 0)
        self.assertIsNone(metrics["input_tokens"]["with_skill"]["mean"])
        self.assertIsNone(metrics["input_tokens"]["delta_mean"])
        self.assertEqual(metrics["output_tokens"]["n_pairs"], 1)
        self.assertEqual(metrics["output_tokens"]["with_skill"]["mean"], 0)
        self.assertIsNone(metrics["output_tokens"]["with_skill"]["sample_stddev"])
        self.assertEqual(metrics["cost_usd"]["n_pairs"], 1)

    def test_no_complete_pairs_means_unknown_success_not_zero(self):
        for runs in [[], [self.run_fixture()], [self.run_fixture(status="not_run", task_success=None, critical_failures=None), self.run_fixture(condition="baseline")]]:
            with self.subTest(runs=runs):
                report = self.aggregate(runs)
                self.assertEqual(report["success"]["n_pairs"], 0)
                self.assertIsNone(report["success"]["delta_pp"])
                self.assertIsNone(report["success"]["with_skill"]["rate_pct"])

    def test_rejects_duplicate_run_keys(self):
        with self.assertRaises(ValueError):
            self.aggregate([self.run_fixture(), self.run_fixture()])

    def test_rejects_invalid_states_and_required_values(self):
        changes = [dict(case_id=""), dict(case_id=" "), dict(replicate=True), dict(replicate=0),
                   dict(replicate=1.0), dict(condition="without_skill"), dict(condition=[]),
                   dict(status="failed"), dict(status=None), dict(task_success=1), dict(task_success=None),
                   dict(critical_failures=True), dict(critical_failures=-1), dict(critical_failures=0.0),
                   dict(status="technical_error"), dict(status="not_run", task_success=None),
                   dict(status="not_run", critical_failures=None)]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.aggregate([self.run_fixture(**change)])
        for field in ["case_id", "replicate", "condition", "status", "task_success", "critical_failures"]:
            run = self.run_fixture()
            del run[field]
            with self.subTest(missing=field), self.assertRaises(ValueError):
                self.aggregate([run])

    def test_rejects_nonfinite_negative_numeric_strings_and_bools(self):
        for field in ["duration_ms", "cost_usd", "input_tokens", "output_tokens"]:
            bad = [True, False, -1, "12", float("nan"), float("inf"), -float("inf")]
            if field.endswith("tokens"):
                bad.append(1.5)
            for value in bad:
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    self.aggregate([self.run_fixture(**{field: value})])

    def test_rejects_wrong_envelope(self):
        self.assertTrue(hasattr(checks, "aggregate_runs"), "Agregação ainda não implementada")
        for data in [[], {}, {"baseline": "new", "runs": []}, {"baseline": "without_skill", "runs": {}},
                     {"baseline": "without_skill", "runs": [None]},
                     {"schema_version": True, "baseline": "without_skill", "runs": []}]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                checks.aggregate_runs(data)

    def test_json_loader_rejects_duplicates_and_nonfinite_literals(self):
        self.assertTrue(hasattr(checks, "load_results"), "Leitura JSON ainda não implementada")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.json"
            for text in ['{', '{"runs": [], "runs": []}', '{"x": NaN}', '{"x": Infinity}', '{"x": 1e999}']:
                path.write_text(text, encoding="utf-8")
                with self.subTest(text=text), self.assertRaises(ValueError):
                    checks.load_results(path)
            path.write_text('{"baseline":"without_skill","runs":[]}', encoding="utf-8")
            self.assertEqual(checks.load_results(path)["runs"], [])


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "example-skill"
        self.root.mkdir()
        self.skill = self.root / "SKILL.md"
        self.skill.write_text("---\nname: example-skill\ndescription: Useful.\n---\nRead input.\n", encoding="utf-8")

    def call(self, args):
        self.assertTrue(hasattr(checks, "main"), "CLI ainda não implementada")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = checks.main(args)
        self.assertEqual(err.getvalue(), "")
        self.assertNotIn("Traceback", out.getvalue())
        return status, json.loads(out.getvalue())

    def test_validate_cli_returns_zero_or_one_and_json(self):
        status, result = self.call(["validate", str(self.root), "--profile", "hermes"])
        self.assertEqual(status, 0)
        self.assertTrue(result["valid"])
        self.skill.write_text("Not a skill.", encoding="utf-8")
        status, result = self.call(["validate", str(self.root), "--profile", "portable"])
        self.assertEqual(status, 1)
        self.assertFalse(result["valid"])

    def test_expected_errors_return_two_as_json_without_traceback(self):
        source = self.root / "bad.json"
        source.write_text("{", encoding="utf-8")
        for args in [[], ["unknown"], ["validate"], ["validate", str(self.root), "--profile", "unknown"],
                     ["validate", str(self.root / "missing")], ["aggregate", str(source)],
                     ["aggregate", str(source.parent / "missing.json")]]:
            with self.subTest(args=args):
                status, result = self.call(args)
                self.assertEqual(status, 2)
                self.assertTrue(result["error"])
        self.skill.write_bytes(b"\xff")
        self.assertEqual(self.call(["validate", str(self.root)])[0], 2)

    def test_aggregate_cli_is_a_real_json_roundtrip(self):
        source = self.root / "fixture.json"
        source.write_text(json.dumps(dict(baseline="without_skill", runs=[
            AggregateTests.run_fixture(), AggregateTests.run_fixture(condition="baseline", task_success=False)])), encoding="utf-8")
        status, result = self.call(["aggregate", str(source)])
        self.assertEqual(status, 0)
        self.assertEqual(result["success"]["delta_pp"], 100.0)
        self.assertIsNone(result["metrics"]["output_tokens"]["with_skill"]["mean"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
