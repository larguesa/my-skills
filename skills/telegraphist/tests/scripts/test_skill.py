"""Offline package checks, not a model-quality benchmark."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PROMPT = '''You are a 19th-century telegraph operator. Every word is expensive. Your
absolute priority is to save tokens and transmit information with extreme
brevity.

Reply only in laconic, objective, succinct, and direct language, no fluff.

Strict rules:
1. NO user question repetition
2. Write in ultra-short, fragmented phrases. Omit articles (a, an, the),
pronouns, and non-essential connectives whenever meaning remains clear.
3. Use common abbreviations aggressively (e.g., w/, w/o, info, approx, msg,
b/c, etc.).
4. Use symbols and punctuation to replace words and show relationships
(e.g., use arrows "->" for "leads to" or "then", "=" for "is/equals", "+"
for "and").
5. Answer only what is strictly asked. Deliver raw data or direct answers
immediately.

Example:
USER: What is the weather like in New York today and what should I wear?
ASSISTANT: NY weather today: rain + 15°C. -> Wear raincoat + boots. PARE.
'''


class SkillTests(unittest.TestCase):
    def test_skill_uses_supplied_prompt_without_extra_instructions(self):
        text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        frontmatter, body = text[4:].split('\n---\n', 1)
        self.assertTrue(text.startswith('---\n'))
        self.assertIn('name: telegraphist', frontmatter.splitlines())
        self.assertEqual(body.lstrip('\n'), PROMPT)

    def test_skill_root_contains_only_skill_and_tests(self):
        self.assertEqual({p.name for p in ROOT.iterdir()}, {'SKILL.md', 'tests'})

    def test_tests_root_contains_only_scripts_results_report(self):
        self.assertEqual({p.name for p in (ROOT / 'tests').iterdir()},
                         {'scripts', 'results', 'REPORT.md'})


if __name__ == '__main__':
    unittest.main()
