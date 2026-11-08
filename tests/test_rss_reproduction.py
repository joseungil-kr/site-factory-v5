import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('rss_reproduction',Path(__file__).resolve().parents[1]/'scripts/audit_rss_reproduction.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

class RSSReproductionTests(unittest.TestCase):
    def test_rss_add_only(self):
        result=audit.compare({'index.html':'a'},{'index.html':'a','rss.xml':'b'},added=['rss.xml'])
        self.assertEqual(result['unchangedHTML'],1)
    def test_html_mutation_fails(self):
        with self.assertRaises(ValueError):audit.compare({'index.html':'a'},{'index.html':'b','rss.xml':'c'},added=['rss.xml'])
    def test_unexpected_removal_fails(self):
        with self.assertRaises(ValueError):audit.compare({'index.html':'a'},{})
    def test_only_expected_rss_change(self):
        self.assertEqual(audit.compare({'rss.xml':'old','index.html':'a'},{'rss.xml':'new','index.html':'a'},changed=['rss.xml'])['changed'],['rss.xml'])
