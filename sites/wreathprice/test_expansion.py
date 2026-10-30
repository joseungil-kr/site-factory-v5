"""Strict offline QA for evidence-limited 16-area WreathPrice extension."""
from __future__ import annotations
import hashlib,json,sys,unittest
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import expand

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__();self.images=[];self.links=[];self.meta=[];self.titles=[];self._title=False
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='img':self.images.append(d)
        if tag=='a':self.links.append(d.get('href',''))
        if tag=='meta' and d.get('name')=='robots':self.meta.append(d.get('content'))
        if tag=='title':self._title=True
    def handle_endtag(self,tag):
        if tag=='title':self._title=False
    def handle_data(self,data):
        if self._title:self.titles.append(data)

class VerifiedRegionExpansionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        expand.build()
        cls.root=ROOT/'dist-expansion'
        cls.report=json.loads((cls.root/'expansion-report.json').read_text(encoding='utf-8'))
    def test_only_pinned_official_upper_level_codes(self):
        evidence=json.loads((ROOT/'verified-regions.json').read_text(encoding='utf-8'))
        rows=evidence['expandEntries']
        self.assertEqual(len(rows),16)
        self.assertEqual({x['code'] for x in rows},{x['officialCode'] for x in self.report['records']})
        self.assertTrue(all(x['sourceStatus']=='존재' and x['level'] in ('municipality','ward') for x in rows))
        self.assertEqual(self.report['verifiedDeliveryAreas'],0)
        self.assertNotIn('1732',json.dumps(evidence))
    def test_all_19_html_and_five_real_images(self):
        pages=list(self.root.rglob('*.html'))
        self.assertEqual(len(pages),19)
        self.assertEqual(self.report['expandedPages'],16)
        self.assertFalse((self.root/'sitemap.xml').exists())
        self.assertEqual((self.root/'robots.txt').read_text(),chr(10).join(['User-agent: *','Disallow: /','']))
        manifest={x['filename']:x for x in json.loads((ROOT/'image-manifest.json').read_text())['images']}
        for name,m in manifest.items():
            data=(self.root/'assets'/name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(),m['sha256'])
            self.assertGreaterEqual(m['width'],768)
        titles=[]
        for p in pages:
            h=p.read_text(encoding='utf-8')
            scan=PageParser();scan.feed(h)
            self.assertEqual(scan.meta,['noindex,nofollow'],str(p))
            self.assertEqual(len(scan.images),5,str(p))
            self.assertEqual(len(set(x['src'] for x in scan.images)),5,str(p))
            self.assertEqual(sum(x.startswith('https://fwith.co.kr/shop/item.php?it_id=') for x in scan.links),5,str(p))
            self.assertNotIn('rel="canonical"',h)
            self.assertTrue(all(x.get('alt') and int(x.get('width',0))>=768 and int(x.get('height',0))>0 for x in scan.images))
            self.assertIn('배송비',h)
            titles.append(''.join(scan.titles))
        self.assertEqual(len(set(titles)),19)
    def test_not_just_name_substitution(self):
        self.assertEqual(len({tuple(x['comparedSKUs']) for x in self.report['records']}),1)
        self.assertEqual(self.report['distinctComparisonSets'],1)
        self.assertEqual(self.report['contentUniquenessClaim'],False)
        self.assertEqual(self.report['editorialFocusCount'],16)
        self.assertEqual(len({x['htmlSHA256'] for x in self.report['records']}),16)
        for row in self.report['records']:
            html=(self.root/row['url'].lstrip('/')).read_text()
            self.assertIn(row['focus'],html)
            self.assertIn(format(row['referenceSpread'],','),html)
            self.assertIn('확인되지 않았습니다',html)
            self.assertIn('AI로 생성한',html)
            self.assertIn('동일 용도 근조 3단 화환 기준가 비교',html)
            self.assertIn('용도와 형태가 다른 상품 안내',html)
            self.assertNotIn('municipality',html)
            self.assertNotIn('ward 등급',html)
            self.assertNotIn('가장 높은 B205은',html)
            self.assertNotIn(row['officialCode']+'에 대응',html)
            self.assertIn('배송 가능 여부',html)

if __name__=='__main__':unittest.main(verbosity=2)
