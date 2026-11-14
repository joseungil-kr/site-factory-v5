import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class T4ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.r=json.loads((ROOT/'docs/V5_T4_CLEAN_RESTORE_RESULT_20261108.json').read_text())
    def test_scope_does_not_claim_new_machine_or_deployment(self):
        self.assertFalse(self.r['environment']['freshOS'])
        self.assertFalse(self.r['environment']['previousInputOutputDirectoriesUsed'])
        self.assertFalse(self.r['deploymentPerformed'])
        self.assertFalse(self.r['productionChanged'])
    def test_fresh_sources_pinned(self):
        self.assertEqual(len(self.r['freshGitHubFiles']),30)
        for f in self.r['freshGitHubFiles']:
            self.assertRegex(f['ref'],r'^[a-f0-9]{40}$')
            self.assertRegex(f['sha256'],r'^[a-f0-9]{64}$')
    def test_expected_delta(self):
        result=self.r['result']
        self.assertEqual(result['todayflowerDelta']['unchangedFiles'],5087)
        self.assertEqual(result['todayflowerDelta']['added'],['rss.xml'])
        self.assertEqual(result['clinicDelta']['unchangedHTML'],15906)
        self.assertEqual(len(result['clinicDelta']['changed']),3)
    def test_commands_successful(self):
        self.assertTrue(self.r['passed'])
        self.assertTrue(all(x['returncode']==0 for x in self.r['commands']))
