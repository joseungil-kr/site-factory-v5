"""QA three evidence-backed, distinct-intent local editorial review drafts."""
import hashlib,re,unittest
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parent
CASES={
 'funeral-budget-cheongun.html':{'focus':'근조 3단 예산별 선택','must':['20,000원','30,000원','50,000원','예산','실제 주문서 합계']},
 'funeral-receipt-singyo.html':{'focus':'근조화환 수령시설·반입 조건 점검','must':['반입','B212','빈소 번호','시설명']},
 'congratulations-format-bono.html':{'focus':'축하 3단 화환과 오브제 형태 선택','must':['51,000원','개업','설치 공간','C205','C030']}
}
SKUS={'B201','B203','B205','C205','C030'}
MEDIA={'funeral-wreath.webp','celebration-wreath.webp','flower-detail.webp','ribbon-guide.webp','florist-preparation.webp'}
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.images=[];self.robots=[];self.canonical=[];self.title=[];self.h1=[];self._tag=None
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=='a':self.links.append(d.get('href',''))
  if t=='img':self.images.append(d)
  if t=='meta' and d.get('name')=='robots':self.robots.append(d.get('content'))
  if t=='link' and d.get('rel')=='canonical':self.canonical.append(d.get('href'))
  if t in ('title','h1'):self._tag=t
 def handle_endtag(self,t):
  if self._tag==t:self._tag=None
 def handle_data(self,s):
  if self._tag=='title':self.title.append(s)
  if self._tag=='h1':self.h1.append(s)
class QA(unittest.TestCase):
 def test_three_only_with_distinct_purchase_intents(self):
  directory=ROOT/'editorial-review'
  self.assertEqual({x.name for x in directory.glob('*.html')},set(CASES))
  focus=[]
  bodies=[]
  for file,check in CASES.items():
   p=directory/file
   h=p.read_text(encoding='utf-8')
   z=Parser();z.feed(h)
   self.assertEqual(z.robots,['noindex,nofollow'],file)
   self.assertFalse(z.canonical,file)
   self.assertEqual(len(z.images),5,file)
   self.assertEqual({x['src'].split('/')[-1] for x in z.images},MEDIA,file)
   for img in z.images:
    self.assertTrue((p.parent/img['src']).resolve().is_file(),(file,img['src']))
    self.assertIn('실제 판매상품',img['alt'])
   skus={x.split('it_id=')[-1] for x in z.links if 'shop/item.php?it_id=' in x}
   self.assertTrue(SKUS.issubset(skus),file)
   self.assertIn(check['focus'],''.join(z.h1))
   for phrase in check['must']:self.assertIn(phrase,h,(file,phrase))
   self.assertIn('미확인',h)
   self.assertIn('리본',h)
   self.assertIn('수령',h)
   self.assertNotIn('배송 보장',h)
   self.assertNotIn('최저가 보장',h)
   self.assertNotIn('rel="canonical"',h)
   focus.append(check['focus'])
   bodies.append(h)
  self.assertEqual(len(set(focus)),3)
  self.assertEqual(len(set(bodies)),3)
 def test_fixed_prices_and_source_links(self):
  for file in CASES:
   h=(ROOT/'editorial-review'/file).read_text()
   for sku,price in [('B201','59,000원'),('B203','79,000원'),('B205','109,000원'),('C205','149,000원'),('C030','200,000원')]:
    self.assertIn(sku,h);self.assertIn(price,h)
   for fragment in ['data/funeral-products/CATALOGUE.json','https://fwith.co.kr/page/notice.php']:
    self.assertIn(fragment,h)
   self.assertIn('2026-10-22',h)
if __name__=='__main__':unittest.main(verbosity=2)
