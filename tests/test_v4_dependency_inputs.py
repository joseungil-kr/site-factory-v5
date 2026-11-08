import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('dependency_inputs',ROOT/'scripts/verify_v4_dependency_inputs.py')
checks=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)

class DependencyInputsTests(unittest.TestCase):
    def test_backup_matches_pinned_artifact(self):
        manifest=json.loads((ROOT/'docs/v4-dependency-manifest.json').read_text())
        dep=next(x for x in manifest['dependencies'] if x['id']=='todayflower-artifact')
        backup=dep['backup']
        self.assertEqual(backup['sha256'],dep['sha256'])
        self.assertEqual(backup['sizeBytes'],84218864)
        self.assertEqual(backup['restoredManifestFilesVerified'],5087)
        self.assertFalse(backup['sharingChanged'])

    def test_correct_digest_and_size(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(b'known');f.flush()
            self.assertEqual(checks.verify_digest(f.name,checks.digest(b'known'),5),b'known')

    def test_wrong_digest_fails(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(b'changed');f.flush()
            with self.assertRaises(ValueError):checks.verify_digest(f.name,checks.digest(b'known'))

    def test_wrong_size_fails(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(b'known');f.flush()
            with self.assertRaises(ValueError):checks.verify_digest(f.name,checks.digest(b'known'),99)

    def test_archive_path_traversal_fails(self):
        content=io.BytesIO()
        with zipfile.ZipFile(content,'w') as z:z.writestr('../outside','bad')
        with zipfile.ZipFile(content) as z:
            with self.assertRaises(ValueError):checks.safe_members(z)

    def test_safe_members_accepted(self):
        content=io.BytesIO()
        with zipfile.ZipFile(content,'w') as z:z.writestr('dist/page.html','ok')
        with zipfile.ZipFile(content) as z:
            self.assertEqual(checks.safe_members(z),['dist/page.html'])

    def test_missing_source_is_not_available(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                checks.verify_sources(d,{'sourceFiles':[{'localPath':'missing.py','sha256':'0'*64}]})
