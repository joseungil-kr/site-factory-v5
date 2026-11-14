import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("integration_check", ROOT / "scripts/check_v5_integration.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

class IntegrationTests(unittest.TestCase):
    def test_documents_and_pending_status(self):
        self.assertIn("migration INCOMPLETE", check.validate(ROOT))

    def test_wrong_archive_fails(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"not-the-official-archive")
            f.flush()
            with self.assertRaisesRegex(ValueError, "archive mismatch"):
                check.validate(ROOT, f.name)
