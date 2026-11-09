"""Inspect actual six-region assembled HTML for three concrete recipient questions."""
import json,unittest
from pathlib import Path
from scripts.worker6_core_five_preview import generate_inputs,operator_policy
from v5.purpose_render import assemble,render
from scripts.worker6_operator_three_diagnostic import with_required_receipt_paths
SITE=Path('sites/promotion-gift-plants')
class RecipientPaths(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.seller=json.loads((SITE/'core-five-seller-evidence.json').read_text())
  cls.spec=json.loads((SITE/'site-spec.json').read_text())
  cls.site=json.loads((SITE/'site.json').read_text())
  cls.products=json.loads((SITE/'products.json').read_text())
  cls.operator=json.loads((SITE/'operator-service-confirmation-20261109.json').read_text())
 def test_each_recipient_has_a_real_question_in_actual_html(self):
  spec,_,_,site=generate_inputs(self.seller,self.spec,self.site,operator_source=self.operator)
  pool=with_required_receipt_paths(spec['purposePools']['promotion'])
  qs=['회사명과 새 부서, 건물 층·호실을 확인했나요?',
      '도로명주소와 건물번호, 동·호수를 확인했나요?',
      '행사 시작시각과 물품 반입 가능 시간을 확인했나요?']
  for n,region in enumerate(['경기도 파주시 적성면','경기도 양평군 단월면','경기도 가평군 설악면','경기도 포천시 이동면','전라남도 강진군 대구면','전라남도 영광군 법성면'],1):
   page={'id':f'qa-{n}','number':n,'pageType':'regional-detail','purpose':'promotion','region':region,'title':region+' 승진화분','productSkus':[x['sku'] for x in self.products]}
   assembled=assemble(page,{'promotion':pool},self.products)
   body=' '.join(x['paragraph'] for x in assembled['sections'])
   html=render(site,page,[page],self.products,[],{'promotion':pool})
   for q in qs:
    self.assertEqual(body.count(q),1,(region,q))
    self.assertEqual(html.count(q),1,(region,q))
   self.assertEqual(html.count(operator_policy(self.operator)),1)
   self.assertEqual(html.count('data-product-sku='),6)
 def test_replacement_fails_if_questions_removed(self):
  spec,_,_,_=generate_inputs(self.seller,self.spec,self.site,operator_source=self.operator)
  pool=spec['purposePools']['promotion']
  self.assertFalse(any('도로명주소와 건물번호, 동·호수' in x['paragraph'] for x in pool['sections']))
  restored=with_required_receipt_paths(pool)
  self.assertTrue(any('도로명주소와 건물번호, 동·호수' in x['paragraph'] for x in restored['sections']))
if __name__=='__main__':unittest.main()
