import unittest
from v5.purpose_render import assemble
from v5 import markup
P={'id':'ref','region':'전국','purpose':'promotion','productSkus':['D144'],'pageType':'purpose-guide'}
PRODUCTS=[{'sku':'D144'}]
def pools(url):
 return {'promotion':{'productSkus':['D144'],'introductions':['소개'],
  'sections':[{'slot':'choice','heading':'메시지','paragraph':'축하 예시','sourceUrl':url},
              {'slot':'order','heading':'주문','paragraph':'수령지 확인'}],
  'faqs':[{'q':'문의?','a':'전화'}]}}
class SourceLinkContract(unittest.TestCase):
 def test_https_source_visible_and_escaped(self):
  a=assemble(P,pools('https://fwith.co.kr/data/common/flower379/congratulatory_words.jpg'),PRODUCTS)
  html=markup.article_body(a)
  self.assertIn('참고 원문 보기',html)
  self.assertIn('href="https://fwith.co.kr/data/common/flower379/congratulatory_words.jpg"',html)
 def test_unsafe_source_not_linked(self):
  a=assemble(P,pools('javascript:alert(1)'),PRODUCTS)
  self.assertNotIn('참고 원문 보기',markup.article_body(a))
 def test_legacy_sections_without_sources_unchanged(self):
  a=assemble(P,pools(None),PRODUCTS)
  self.assertNotIn('source-reference',markup.article_body(a))
if __name__=='__main__':unittest.main()
