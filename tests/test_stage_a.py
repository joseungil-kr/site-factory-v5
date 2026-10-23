import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FoundationTests(unittest.TestCase):
    def test_site_is_independent_and_domain_unset(self):
        conf = json.loads((ROOT / 'sites/ansan-promotion-plant/site.json').read_text(encoding='utf-8'))
        self.assertEqual(conf['id'], 'ansan-promotion-plant')
        self.assertIsNone(conf['domain'])
        self.assertFalse(conf['publishEnabled'])
        self.assertEqual(conf['keyword'], '승진화분')
        self.assertIn('fwith.co.kr', conf['orderBaseUrl'])

    def test_v4_only_provenance_reference(self):
        prov = json.loads((ROOT / 'docs/provenance.json').read_text(encoding='utf-8'))
        self.assertEqual(len(prov['auditedMain']), 40)
        self.assertIn('no code imported', prov['status'])
        self.assertTrue(all(len(x['sha']) == 40 for x in prov['references']))


if __name__ == '__main__':
    unittest.main()
