import json,unittest
from pathlib import Path
from scripts.worker6_shipping_render import lookup,evidence_section
ROOT=Path('sites/promotion-gift-plants')
class BuyerModules(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/'customer-decision-modules-20261109.json').read_text())
  cls.modules={x['id']:x for x in cls.data['modules']}
 def test_modules_are_distinct_decisions(self):
  self.assertEqual(len(self.modules),len(self.data['modules']))
  self.assertGreaterEqual(len(self.modules),9)
  self.assertTrue(all(x['decision'] and len(x['body'])>70 for x in self.modules.values()))
 def test_recipient_scenarios_not_region_claims(self):
  for x in ('workplace-receipt','home-receipt','venue-receipt'):
   self.assertTrue(any(term in self.modules[x]['body'] for term in ('상황','수령','사무실')))
   self.assertFalse(any(term in self.modules[x]['body'] for term in ('파주시','가평군','강진군')))
  self.assertIn('All recipients can choose any',self.data['editorialStructure']['rule'])
  self.assertEqual(self.data['scenarioChoices'],[])
 def test_operator_general_service_not_undeliverable(self):
  for args in [('경기도','파주시','적성면'),('경기도','가평군','설악면'),('전라남도','강진군','대구면')]:
   text=evidence_section(lookup(*args))['paragraph']
   self.assertIn('1844-0644',text)
   self.assertNotIn('실제 배송 가능 여부는 확인되지 않았습니다',text)
   self.assertTrue(any(word in text for word in ('최종 요금','적용 요금','추가 배송비')))
if __name__=='__main__':unittest.main()
