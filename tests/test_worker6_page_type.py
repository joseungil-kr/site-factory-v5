import unittest
from v5.purpose_render import assemble
from v5.config import ConfigError
PRODUCTS=[{'sku':'D144'}]
def pool(text):
 return {'promotion':{'productSkus':['D144'],'introductions':[text],
 'sections':[{'slot':'choice','heading':'선택','paragraph':'상품 비교'},{'slot':'order','heading':'주문','paragraph':'수령 정보'}],
 'faqs':[{'q':'문의?','a':'전화'}]}}
PAGE={'id':'p1','purpose':'promotion','productSkus':['D144'],'region':'당일 배송 문의 안내'}
class PageTypeRegionContract(unittest.TestCase):
 def test_purpose_guide_never_renders_fake_region(self):
  p={**PAGE,'pageType':'purpose-guide'}
  self.assertEqual(assemble(p,pool('오늘 수령할 상품을 확인합니다.'),PRODUCTS)['intro'],'오늘 수령할 상품을 확인합니다.')
 def test_purpose_guide_rejects_region_placeholder(self):
  p={**PAGE,'pageType':'purpose-guide'}
  with self.assertRaises(ConfigError):assemble(p,pool('{region}에 오늘 수령할 상품'),PRODUCTS)
 def test_real_region_kept(self):
  p={**PAGE,'pageType':'regional-detail','region':'전라남도 강진군 대구면'}
  self.assertIn('전라남도 강진군 대구면',assemble(p,pool('{region}에서 상품을 확인합니다.'),PRODUCTS)['intro'])
 def test_unknown_page_type_rejected(self):
  with self.assertRaises(ConfigError):assemble({**PAGE,'pageType':'invented'},pool('소개'),PRODUCTS)
if __name__=='__main__':unittest.main()
