import csv
import re
import xml.etree.ElementTree as ET
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from v5.local_data import resolve

class LocalDataTests(unittest.TestCase):
    def test_official_inputs_without_network(self):
        with patch('socket.socket',side_effect=AssertionError('Network prohibited')):
            archive=resolve('official-legal-codes')
            with zipfile.ZipFile(archive) as z:
                rows=list(csv.reader(io.StringIO(z.read(z.namelist()[0]).decode('cp949')),delimiter='\t'))
            self.assertEqual(len(rows)-1,53403)
            parents=json.loads(resolve('official-parent-regions').read_text())
            self.assertEqual(len(parents['regions']),284)
            candidates=json.loads(resolve('locality-candidates').read_text())
            self.assertEqual(len(candidates['records']),5034)
    def test_sanitized_funeral_input_without_network(self):
        with patch('socket.socket',side_effect=AssertionError('Network prohibited')):
            archive=resolve('funeral-halls')
            self.assertEqual(archive.stat().st_size,332696)
            with zipfile.ZipFile(archive) as z:
                for name in z.namelist():
                    if name.startswith('xl/worksheets/') and name.endswith('.xml'):
                        text=' '.join(ET.fromstring(z.read(name)).itertext())
                        self.assertIsNone(re.search(r'01[016789][ -]?\d{3,4}[ -]?\d{4}',text))
    def test_missing_copy_does_not_fetch(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'data').mkdir()
            (root/'data/local-data-manifest.json').write_text(json.dumps({'datasets':{'missing':{'status':'available','path':'missing.zip','bytes':1,'sha256':'0'*64}}}))
            with patch('socket.socket',side_effect=AssertionError('Network prohibited')):
                with self.assertRaises(FileNotFoundError):resolve('missing',root)
    def test_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'data').mkdir()
            (root/'data/local-data-manifest.json').write_text(json.dumps({'datasets':{'bad':{'status':'available','path':'../outside','bytes':1,'sha256':'0'*64}}}))
            with self.assertRaisesRegex(ValueError,'escapes'):resolve('bad',root)
