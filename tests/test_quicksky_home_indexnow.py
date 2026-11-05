import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from scripts import quicksky_home_indexnow as m

class HomeIndexNowTests(unittest.TestCase):
    def test_payload_is_exactly_one_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            response = MagicMock()
            response.__enter__.return_value.status = 200
            response.__enter__.return_value.read.return_value = b""
            with patch.object(m, "key_and_scope", return_value="a"*32), patch.object(m, "verify", return_value={"publicSitemapUrls":1,"regionsIndexable":False}), patch.object(m, "read", return_value=(200,{},("a"*32).encode())), patch.object(m,"urlopen",return_value=response) as send:
                result = m.submit(Path(tmp)/"receipt.json")
                payload = json.loads(send.call_args.args[0].data)
                self.assertEqual(payload["urlList"], ["https://quicksky.nalmada.net/"])
                self.assertEqual(result["http"],200)
                with self.assertRaises(ValueError):
                    m.submit(Path(tmp)/"receipt.json")
                self.assertEqual(send.call_count,1)

    def test_bad_public_key_never_submits(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(m,"key_and_scope",return_value="a"*32), patch.object(m,"verify",return_value={"publicSitemapUrls":1,"regionsIndexable":False}), patch.object(m,"read",return_value=(200,{},b"wrong")), patch.object(m,"urlopen") as send:
                with self.assertRaises(ValueError):
                    m.submit(Path(tmp)/"receipt.json")
                send.assert_not_called()

    def test_transport_error_keeps_uncertain_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt=Path(tmp)/"receipt.json"
            with patch.object(m,"key_and_scope",return_value="a"*32), patch.object(m,"verify",return_value={"publicSitemapUrls":1,"regionsIndexable":False}), patch.object(m,"read",return_value=(200,{},("a"*32).encode())), patch.object(m,"urlopen",side_effect=TimeoutError) as send:
                with self.assertRaises(TimeoutError): m.submit(receipt)
                self.assertEqual(json.loads(receipt.read_text())["outcome"],"uncertain")
                self.assertEqual(send.call_count,1)

    def test_rerun_never_submits(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(m.os.environ,{"GITHUB_RUN_ATTEMPT":"2"}), patch.object(m,"urlopen") as send:
            with self.assertRaises(ValueError): m.submit(Path(tmp)/"receipt.json")
            send.assert_not_called()
