"""Real generator and renderer regression for shared seller operational policy."""
import copy,json,unittest
from pathlib import Path
from scripts.worker6_core_five_preview import generate_inputs,operator_policy
from v5.purpose_render import render
SITE=Path('sites/promotion-gift-plants')
class OperatorFivePages(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=json.loads((SITE/'core-five-seller-evidence.json').read_text())
  cls.spec=json.loads((SITE/'site-spec.json').read_text())
  cls.site=json.loads((SITE/'site.json').read_text())
  cls.products=json.loads((SITE/'products.json').read_text())
  cls.operator=json.loads((SITE/'operator-service-confirmation-20261109.json').read_text())
 def test_real_five_pages_identical_policy_and_correct_conditions(self):
  spec,pages,_,site=generate_inputs(self.source,self.spec,self.site,operator_source=self.operator)
  shared=operator_policy(self.operator)
  self.assertEqual(len(pages),5)
  for page in pages:
   with self.subTest(purpose=page['purpose']):
    html=render(site,page,pages,self.products,[],spec['purposePools'])
    self.assertIn(shared,html)
    self.assertEqual(html.count(shared),1)
    self.assertIn('08:00~23:00',html)
    self.assertIn('06:00~20:00',html)
    self.assertIn('전국 당일배송 서비스',html)
    self.assertIn('23시 전화 주문이 그날 도착한다는 뜻은 아닙니다',html)
    self.assertIn('1844-0644',html)
    self.assertNotIn('당일배송 서비스가 불가능',html)
  day=render(site,pages[4],pages,self.products,[],spec['purposePools'])
  self.assertIn('개별 주문의 실제 도착 가능 시간',day)
 def test_single_source_change_propagates_to_all_pages(self):
  changed=copy.deepcopy(self.operator)
  changed['phoneOrderHours']['start']='09:00'
  spec,pages,_,site=generate_inputs(self.source,self.spec,self.site,operator_source=changed)
  for page in pages:
   html=render(site,page,pages,self.products,[],spec['purposePools'])
   self.assertIn('09:00~23:00',html)
   self.assertNotIn('08:00~23:00',html)
 def test_guarantee_and_cutoff_fail_closed(self):
  changed=copy.deepcopy(self.operator)
  changed['individualSameDayArrivalGuaranteed']=True
  with self.assertRaises(ValueError):operator_policy(changed)
  changed=copy.deepcopy(self.operator)
  changed['individualCutoff']='23:00'
  with self.assertRaises(ValueError):operator_policy(changed)
if __name__=='__main__':unittest.main()
