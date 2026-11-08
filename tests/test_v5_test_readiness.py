import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import check_v5_test_readiness as readiness

class ReadinessTests(unittest.TestCase):
    def test_same_path_rejected(self):
        with self.assertRaises(ValueError):readiness.require_isolated_paths([Path('/tmp/a'),Path('/tmp/a')])
    def test_nested_path_rejected(self):
        with self.assertRaises(ValueError):readiness.require_isolated_paths([Path('/tmp/a'),Path('/tmp/a/b')])
    def test_sibling_paths_allowed(self):
        readiness.require_isolated_paths([Path('/tmp/a'),Path('/tmp/b')])
    def test_missing_main_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'page.html';p.write_text('<html><h1>Title</h1></html>')
            with self.assertRaises(ValueError):readiness.check_page(p,False)
    def test_canonical_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'page.html';p.write_text('<html><main><h1>Title</h1></main></html>')
            with self.assertRaises(ValueError):readiness.check_page(p,True)
