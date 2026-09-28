"""Public library integrity, independently of optional inference services."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]

class CreativeLibraryTests(unittest.TestCase):
    def test_every_style_is_discoverable(self):
        rows = json.loads((ROOT / 'references/style-catalog.json').read_text())
        ids = [row['id'] for row in rows]
        self.assertEqual(len(ids), len(set(ids)))
        actual = {p.parent.name for p in (ROOT / 'styles').glob('*/SKILL.md')}
        self.assertEqual(set(ids), actual)
        root = (ROOT / 'SKILL.md').read_text()
        for row in rows:
            self.assertIn('styles/' + row['id'] + '/SKILL.md', root)
            self.assertTrue(row['best_for'].strip())
        candidates = (ROOT / 'references/style-candidates.txt').read_text().splitlines()
        self.assertEqual(ids, [line.split(' | ')[0] for line in candidates])

    def test_recipe_library_and_brief_are_connected(self):
        index = ROOT / 'recipes/README.md'
        self.assertTrue(index.is_file())
        recipes = sorted(p for p in index.parent.glob('*.md') if p != index)
        self.assertTrue(recipes)
        for path in recipes:
            with self.subTest(recipe=path.name):
                self.assertIn(path.name, index.read_text())
                self.assertGreater(len(path.read_text().split()), 180)
                self.assertNotIn(chr(8212), path.read_text())
        self.assertIn('templates/creative-brief.md', (ROOT / 'SKILL.md').read_text())
        self.assertTrue((ROOT / 'references/creative-sources.md').is_file())

    def test_research_notes_preserve_provenance_without_raw_prompts(self):
        data = json.loads((ROOT / 'references/creative-research.json').read_text())
        self.assertEqual(data['distinct_texts'], len(data['notes']))
        sources = [url for note in data['notes'] for url in note['source_prompts']]
        self.assertEqual(data['entries'], len(sources))
        self.assertEqual(len(sources), len(set(sources)))
        for note in data['notes']:
            self.assertTrue(note['concept'] and note['rationale'])
            self.assertIn(note['decision'], {'adapt principle', 'reject as recipe'})
            self.assertNotIn('prompt', note)
            for url in note['source_prompts']:
                self.assertIn('/blob/' + data['source_revision'] + '/prompts/', url)

    def test_new_guides_have_portable_frontmatter(self):
        for path in (ROOT / 'styles').glob('*/SKILL.md'):
            front, body = path.read_text()[4:].split('\n---\n', 1)
            fields = dict(re.findall(r'^(\w+):\s*(.+)$', front, re.M))
            self.assertEqual(fields['name'], 'animation-' + path.parent.name)
            self.assertLessEqual(len(fields['description'].strip('\"\'')), 60)
            self.assertIn('Ricardo', fields['author'])
            self.assertIn('license', fields)
            self.assertGreater(len(body), 1000)

if __name__ == '__main__':
    unittest.main()
