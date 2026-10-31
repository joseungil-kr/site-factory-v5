import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import quicksky_bound_home_account as m

class ExistingPublicPreflightTests(unittest.TestCase):
    def test_public_update_requires_full_live_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"before.json"
            replies=[{"deployments":[{"versions":[{"percentage":100,"version_id":"existing-version"}]}]}, {"subdomain":"joseungil"}]
            with patch.object(m,"inventory",return_value=("a"*32, [["quicksky.nalmada.net",m.WORKER]])), patch.object(m,"get",side_effect=replies), patch("scripts.verify_quicksky_home_release.verify",side_effect=RuntimeError("regional noindex missing")) as verify:
                with self.assertRaises(RuntimeError):
                    m.preflight(output,existing_home_public=True)
                verify.assert_called_once()
                self.assertFalse(output.exists())

    def test_public_update_records_verified_previous_public_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"before.json"
            replies=[{"deployments":[{"versions":[{"percentage":100,"version_id":"existing-version"}]}]}, {"subdomain":"joseungil"}]
            with patch.object(m,"inventory",return_value=("a"*32, [["quicksky.nalmada.net",m.WORKER]])), patch.object(m,"get",side_effect=replies), patch("scripts.verify_quicksky_home_release.verify") as verify, patch.dict(m.os.environ,{"GITHUB_OUTPUT":""}):
                m.preflight(output,existing_home_public=True)
                verify.assert_called_once()
                record=json.loads(output.read_text())
                self.assertTrue(record["previousHomeOnlyPublicVerified"])
                self.assertFalse(record["previousNoindexVerified"])
