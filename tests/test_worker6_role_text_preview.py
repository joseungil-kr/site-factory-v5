import unittest
from pathlib import Path
from html.parser import HTMLParser
from scripts.worker6_role_text_preview import render,OUT,evidence
class Scan(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,t,a):
  if t=='a':
   h=dict(a).get('href','')
   if h.startswith('/'):self.links.append(h)
class RolePreview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rows=render()
 def test_links_and_noindex(self):
  self.assertEqual(len(self.rows),4)
  for path in [OUT/'index.html',OUT/'guide.html']+[OUT/r['file'] for r in self.rows]:
   text=path.read_text(encoding='utf-8')
   self.assertIn('noindex,nofollow',text)
   p=Scan();p.feed(text)
   for href in p.links:
    target=OUT/(href.lstrip('/') or 'index.html')
    self.assertTrue(target.is_file(),(path,href))
 def test_no_invented_shipping_or_other_sku(self):
  for row in self.rows:
   t=(OUT/row['file']).read_text()
   self.assertIn('D144',t)
   self.assertIn('2026-11-09',t)
   self.assertIn('최종 추가요금',t)
   self.assertNotIn('배송보장',t)
   self.assertFalse(row['finalShippingConfirmed'])
   self.assertFalse(row['localStockConfirmed'])
 def test_fee_scope_distinctions(self):
  x={r['region']:r for r in self.rows}
  self.assertEqual(x['경기도 파주시 적성면']['sellerRowState'],'exact-locality-display')
  self.assertEqual(x['경기도 가평군 설악면']['sellerRowState'],'overlap-unknown-priority')
  self.assertEqual(x['경기도 포천시 이동면']['sellerRowState'],'overlap-unknown-priority')
 def test_unverified_sku_is_not_inferred_from_d144(self):
  x=evidence('경기도','가평군','설악면','F055')
  self.assertEqual(x['state'],'sku-source-unverified')
  self.assertEqual(x['rows'],[])
if __name__=='__main__':unittest.main()
