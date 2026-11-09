import json,unittest
from pathlib import Path
from scripts.worker6_core_five_preview import generate_inputs
SITE=Path('sites/promotion-gift-plants')
class OrchidPurposeGate(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.evidence=json.loads((SITE/'core-five-seller-evidence.json').read_text())
  cls.spec=json.loads((SITE/'site-spec.json').read_text())
  cls.site=json.loads((SITE/'site.json').read_text())
  cls.products=json.loads((SITE/'products.json').read_text())
 def test_verified_orchid_categories(self):
  rows={x['sku']:x for x in self.evidence['sources']}
  for sku,category in [('E008','동양란'),('F055','서양란')]:
   self.assertEqual(rows[sku]['category'],category)
   self.assertEqual(rows[sku]['choiceOptions'],0)
   self.assertEqual(rows[sku]['extraOptions'],0)
   self.assertEqual(rows[sku]['shippingPayment'],'주문시 결제')
   self.assertTrue(rows[sku]['directOriginalHtmlVerified'])
   self.assertTrue(any(x['sku']==sku and x['imageUseApproved'] is False for x in self.products))
 def test_missing_orchid_fails_production(self):
  evidence={'sources':[x for x in self.evidence['sources'] if x['sku']!='E008']}
  with self.assertRaisesRegex(ValueError,'orchid evidence missing'):
   generate_inputs(evidence,self.spec,self.site)
 def test_promotion_transfer_include_both_orchids(self):
  spec,pages,_,_=generate_inputs(self.evidence,self.spec,self.site)
  for purpose in ('promotion','transfer'):
   pool=spec['purposePools'][purpose]
   text=' '.join(x['paragraph'] for x in pool['sections'])
   self.assertIn('E008, 110,000원',text)
   self.assertIn('F055, 60,000원',text)
   self.assertIn('실제 크기·관리방법·재고',text)
   self.assertTrue(any('난류' in x.get('paragraph','') or '동양란' in x.get('paragraph','') for x in pool['sections']))
 def test_no_funeral_orchid(self):
  evidence={'sources':self.evidence['sources']+[{'sku':'B214','name':'장례식장 근조 서양란(서양란)','priceKRW':200000}]}
  with self.assertRaisesRegex(ValueError,'funeral product'):
   generate_inputs(evidence,self.spec,self.site)
if __name__=='__main__':unittest.main()
