import unittest,json
from pathlib import Path
from html.parser import HTMLParser
from scripts.worker6_official_three_text_preview import build,OUT
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,t,a):
  if t=='a':
   h=dict(a).get('href','')
   if h.startswith('/'):self.links.append(h)
class OfficialThree(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rows=build()
 def test_three_source_specific_buyer_questions(self):
  self.assertEqual(len(self.rows),3)
  snippets=['산업단지 내 기업','한서로 8','화동로 2048']
  for row,term in zip(self.rows,snippets):
   body=(OUT/row['file']).read_text()
   self.assertIn(term,body)
   self.assertIn('공식자료 확인일 2026-11-11',body)
   self.assertIn('D144',body)
   self.assertIn('noindex,nofollow',body)
   self.assertNotIn('<img',body)
 def test_fee_exact_rows_and_scope(self):
  self.assertEqual([x['sellerRows'] for x in self.rows],[[7],[5,8],[5,9]])
  self.assertEqual([x['feeState'] for x in self.rows],['exact-locality-display','overlap-unknown-priority','overlap-unknown-priority'])
  for row in self.rows:
   text=(OUT/row['file']).read_text()
   self.assertIn('다른 SKU에 적용한다고 주장하지 않습니다',text)
   self.assertIn('최종 배송비',text)
 def test_all_internal_targets_exist(self):
  for p in [OUT/'index.html',OUT/'guide.html']+[OUT/x['file'] for x in self.rows]:
   scan=Links();scan.feed(p.read_text())
   for href in scan.links:self.assertTrue((OUT/(href.lstrip('/') or 'index.html')).is_file(),(p,href))
 def test_no_release_or_score_claim(self):
  m=json.loads((OUT/'manifest.json').read_text())
  self.assertFalse(m['similarity49Pass'])
  self.assertFalse(m['editorial85Pass'])
  self.assertFalse(m['imageLoadPass'])
if __name__=='__main__':unittest.main()
