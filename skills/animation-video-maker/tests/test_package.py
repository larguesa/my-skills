"""Structural checks for the distributable package; no network calls."""
import collections
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
class PackageTests(unittest.TestCase):
    def test_twenty_styles_and_balanced_services(self):
        rows=json.loads((ROOT/'references/catalog.json').read_text())
        self.assertEqual(len(rows),20)
        self.assertEqual(len({r['id'] for r in rows}),20)
        self.assertEqual(sorted(collections.Counter(r['service'] for r in rows).values()),[4]*5)
        for r in rows:
            with self.subTest(style=r['id']):
                skill=ROOT/'styles'/r['id']/'SKILL.md'
                self.assertTrue(skill.is_file(),f'Missing style guide: {r["id"]}')
                text=skill.read_text();self.assertTrue(text.startswith('---\n'))
                front,body=text[4:].split('\n---\n',1)
                fields=dict(re.findall(r'^(\w+):\s*(.+)$',front,re.M))
                self.assertEqual(fields['name'],'animation-'+r['id'])
                self.assertLessEqual(len(fields['description'].strip('"\'')),60)
                self.assertIn('license',fields);self.assertGreater(len(body),1000)
                scene=ROOT/'examples'/r['id']/'scene.js'
                self.assertTrue(scene.is_file())
                self.assertIn('window.scene',scene.read_text())
                self.assertIn('window.TRANSCRIPT',scene.read_text())
                match=re.search(r'''window\.TRANSCRIPT\s*=\s*(['"])(.*?)\1\s*;''',scene.read_text(),re.S)
                self.assertIsNotNone(match,'Example transcript must be a literal string.')
                transcript=match.group(2) if match else ''
                self.assertIn('t2stech.com/contact',transcript,'Accessible transcript must include the shared CTA destination.')
                self.assertTrue((scene.parent/'index.html').is_file())

    def test_local_document_links(self):
        for path in ROOT.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
                if '://' in target or target.startswith('#'):continue
                clean=unquote(target.split('#')[0])
                self.assertTrue((path.parent/clean).exists(),f'{path.relative_to(ROOT)} -> {clean}')

    def test_no_local_deployment_paths_or_remote_scene_calls(self):
        for path in ROOT.rglob('*'):
            if path.suffix not in {'.md','.py','.js','.html','.json'}:continue
            text=path.read_text()
            for prefix in ['/'+'home/hermes','/'+'opt/data','C:'+chr(92)+'Users']:
                self.assertNotIn(prefix,text,str(path.relative_to(ROOT)))
            if path.name=='scene.js':
                self.assertNotRegex(text,r'\b(fetch|eval|XMLHttpRequest|WebSocket)\s*\(')
                self.assertNotIn('Math.random(',text)
                self.assertNotIn(chr(8212),text,'Use a colon or comma in example copy.')

    def test_candidate_file_covers_exact_catalog(self):
        rows=json.loads((ROOT/'references/style-catalog.json').read_text())
        p=ROOT/'references/style-candidates.txt';lines=p.read_text().splitlines()
        self.assertEqual([r['id'] for r in rows],[line.split(' | ')[0] for line in lines])
        self.assertLessEqual(p.stat().st_size,16384);self.assertLessEqual(len(lines),64)
        self.assertTrue(all(len(line.encode())<=2048 for line in lines))

if __name__=='__main__':unittest.main()
