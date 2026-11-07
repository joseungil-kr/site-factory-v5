import unittest
from pathlib import Path

class ExistingSiteProtection(unittest.TestCase):
 def test_daysky_release_is_user_initiated_only(self):
  root=Path(__file__).resolve().parents[1]
  text=(root/'.github/workflows/daysky-1736-deploy.yml').read_text(encoding='utf-8')
  triggers=text.split('permissions:',1)[0]
  self.assertIn('  workflow_dispatch:',triggers)
  self.assertNotIn('\n  push:',triggers)
  self.assertNotIn('\n  pull_request:',triggers)

if __name__=='__main__':unittest.main()
