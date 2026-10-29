import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from v5.site_plan import validate_plan
from scripts.build_wreath_region import BASE,INTENTS,pick,area_url,all_rows
class WreathRegionTests(unittest.TestCase):
    def test_approved_spec_and_fixed_target(self):
        p=json.loads((BASE/'site-spec.json').read_text())
        self.assertTrue(validate_plan(p,'wreath-region')['ready'])
        self.assertEqual(p['targetPageCount'],10336)
    def test_region_count_and_two_distinct_intents(self):
        rows=all_rows(False);self.assertEqual(len(rows),5034)
        self.assertEqual(len({tuple(r[:3]) for r in rows}),5034)
        for row in all_rows(True):
            self.assertNotEqual(area_url(row,INTENTS[0]),area_url(row,INTENTS[1]))
        self.assertTrue(any(r[2].endswith('읍') for r in rows))
        self.assertTrue(any(r[2].endswith('면') for r in rows))
        self.assertTrue(any(r[2].endswith('동') for r in rows))
    def test_product_source_checkout_cannot_leak_customer_fields(self):
        p=json.loads((BASE/'products.json').read_text())
        self.assertEqual(len(p['list']),6)
        for x in p['list']:
            self.assertEqual(x['orderUrl'],'https://fwith.co.kr/shop/item.php?it_id='+x['id'])
            self.assertTrue(x['imageUrl'].startswith('https://fwith.co.kr/data/item/'))
            self.assertTrue(x['buyButtonPresent'])
    def test_intent_separation_and_fixed_copy(self):
        d=json.loads((BASE/'copy-pool.json').read_text())
        self.assertEqual(set(d['leads']),set(INTENTS))
        self.assertEqual(len(d['sections']),6)
        for values in list(d['sections'].values())+list(d['leads'].values()):
            self.assertEqual(len(values),8)
            self.assertEqual(len(values),len(set(values)))
            self.assertTrue(all(len(x)>=35 for x in values))
        self.assertEqual(pick(d['leads']['same-day'],'hello',2),pick(d['leads']['same-day'],'hello',2))
if __name__=='__main__':unittest.main()
