import unittest
from v5.purpose_render import assemble
from v5.config import ConfigError

PRODUCTS=[{'sku':'D144'},{'sku':'D156'}]
PAGE={'id':'w6-regression-1','region':'경기도 안산시','purpose':'promotion','productSkus':['D144'],
      'title':'승진화분','intro':'fixture','sections':[{'heading':'x','paragraph':'y'},{'heading':'z','paragraph':'w'}]}
def pool(sections):
    return {'promotion':{'productSkus':['D144','D156'],
            'introductions':['{region} 승진 선물입니다.'],
            'sections':sections,'faqs':[{'q':'주문?','a':'상품 링크 확인'}]}}
def sec(slot,heading,role=None):
    result={'slot':slot,'heading':heading,'paragraph':heading+' 설명'}
    if role is not None:result['role']=role
    return result

class Worker6SectionContract(unittest.TestCase):
    def test_legacy_alternatives_not_all_rendered(self):
        p=pool([sec('choice','A'),sec('choice','B'),sec('order','C'),sec('order','D')])
        page=assemble(PAGE,p,PRODUCTS)
        self.assertEqual(len(page['sections']),2)
        self.assertEqual({x['heading'] for x in page['sections']} & {'A','B'} in ({'A'},{'B'}),True)
    def test_required_and_variant(self):
        p=pool([sec('choice','Required','required'),sec('choice','A','variant'),sec('choice','B','variant'),
                sec('order','Order required','required'),sec('order','Order option','variant')])
        page=assemble(PAGE,p,PRODUCTS)
        headings=[s['heading'] for s in page['sections']]
        self.assertEqual(len(headings),4)
        self.assertIn('Required',headings)
        self.assertIn('Order required',headings)
        self.assertIn('Order option',headings)
        self.assertEqual(len(set(headings)&{'A','B'}),1)
    def test_no_wrong_particle_in_worker6_intro(self):
        from pathlib import Path
        import json
        p=json.loads(Path('sites/promotion-gift-plants/site-spec.json').read_text())
        for purpose in p['purposePools']:
            page={**PAGE,'purpose':purpose,'productSkus':p['purposePools'][purpose]['productSkus'][:1]}
            result=assemble(page,p['purposePools'],[{'sku':s} for x in p['purposePools'].values() for s in x['productSkus']])
            self.assertNotIn('안산시으로',result['intro'])
    def test_invalid_role_rejected(self):
        p=pool([sec('choice','X','anything'),sec('order','Y')])
        with self.assertRaises(ConfigError):assemble(PAGE,p,PRODUCTS)

if __name__=='__main__':unittest.main()
