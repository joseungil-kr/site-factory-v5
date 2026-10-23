import unittest
from pathlib import Path
from unittest.mock import patch
from v5.config import ConfigError
from v5.publiccheck import check
from v5.indexnow import submission

ROOT=Path(__file__).resolve().parents[1]
class StageF(unittest.TestCase):
    def test_public_verification_is_blocked_without_domain(self):
        with self.assertRaises(ConfigError):check('ansan-promotion-plant')
    def test_indexnow_cannot_submit_from_preview(self):
        with self.assertRaises(ConfigError):submission('ansan-promotion-plant','a'*32,submit=True)
    def test_workflow_has_no_automatic_deploy_trigger(self):
        file=(ROOT/'.github/workflows/publish.yml').read_text(encoding='utf-8')
        self.assertIn('workflow_dispatch:',file)
        self.assertNotIn('on:\n  push:',file)
        self.assertIn('expected_sha:',file)
        self.assertIn('python -m v5 publish-check',file)
        self.assertIn('false', (ROOT/'sites/ansan-promotion-plant/site.json').read_text(encoding='utf-8').lower())

if __name__=='__main__':unittest.main()
