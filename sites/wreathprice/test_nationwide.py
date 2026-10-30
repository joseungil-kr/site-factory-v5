"""Nationwide 284 administrative-name coverage QA; no unverified delivery claims."""
import hashlib,json,sys,unittest
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import expand_nationwide

class Scan(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.images=[];self.robots=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='a':self.links.append(d.get('href',''))
        if tag=='img':self.images.append(d)
        if tag=='meta' and d.get('name')=='robots':self.robots.append(d.get('content',''))

class NationwideQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        expand_nationwide.build()
        cls.root=ROOT/'dist-nationwide'
        cls.report=json.loads((cls.root/'expansion-report.json').read_text(encoding='utf-8'))
        cls.pages=list(cls.root.rglob('*.html'))
    def test_pinned_284_codes_and_286_page_output(self):
        registry=json.loads((ROOT/'verified-regions-nationwide.json').read_text(encoding='utf-8'))
        self.assertEqual(len(registry['entries']),284)
        self.assertEqual(len({x['code'] for x in registry['entries']}),284)
        self.assertEqual(len(self.report['records']),282)
        self.assertEqual(self.report['totalPages'],286)
        self.assertEqual(len(self.pages),286)
        self.assertEqual(self.report['listedAdministrativeRegions'],284)
        self.assertEqual(self.report['regionSpecificServiceEvidenceCount'],0)
        self.assertEqual(self.report['verifiedDeliveryAreas'],0)
        self.assertEqual(self.report['distinctComparisonSets'],1)
        self.assertFalse(self.report['contentUniquenessClaim'])
        self.assertFalse((self.root/'sitemap.xml').exists())
    def test_home_and_hub_reach_16_and_284_regions(self):
        home=(self.root/'ansan/index.html').read_text()
        directory=(self.root/'regions/index.html').read_text()
        self.assertIn('/regions/',home)
        for item in self.report['records'][:16]:
            self.assertIn('href="'+item['url']+'"',home)
        reg=json.loads((ROOT/'verified-regions-nationwide.json').read_text())
        for item in reg['entries']:
            path='/ansan/' if item['code']=='4127000000' else ('/ansan/sangnok/' if item['code']=='4127100000' else '/region/'+item['code']+'.html')
            self.assertIn('href="'+path+'"',directory)
        self.assertIn('배송 가능',directory)
    def test_all_internal_paths_and_sales_assets(self):
        targets={'/':self.root/'ansan/index.html'}
        for page in self.pages:
            rel='/'+page.relative_to(self.root).as_posix()
            targets[rel]=page
            if rel.endswith('/index.html'):targets[rel.removesuffix('index.html')]=page
        for page in self.pages:
            body=page.read_text(encoding='utf-8')
            s=Scan();s.feed(body)
            self.assertEqual(s.robots,['noindex,nofollow'],str(page))
            self.assertNotIn('rel="canonical"',body)
            self.assertNotIn('municipality 등급',body)
            self.assertNotIn('ward 등급',body)
            self.assertNotIn('가장 높은 B205은',body)
            for link in s.links:
                if link.startswith('/'):
                    self.assertTrue(link in targets or (self.root/link.lstrip('/')).is_file(),(str(page),link))
            if '/region/' in str(page):
                self.assertEqual(len(s.images),5)
                self.assertEqual(len({i['src'] for i in s.images}),5)
                self.assertEqual(sum(x.startswith('https://fwith.co.kr/shop/item.php?it_id=') for x in s.links),5)
                self.assertIn('동일 용도 근조 3단 화환 기준가 비교',body)
                self.assertIn('용도와 형태가 다른 상품 안내',body)
                self.assertIn('배송 가능 여부',body)
        images=json.loads((ROOT/'image-manifest.json').read_text())['images']
        self.assertEqual(len(images),5)
        for im in images:
            raw=(self.root/'assets'/im['filename']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),im['sha256'])
            self.assertGreaterEqual(im['width'],768)

if __name__=='__main__':unittest.main(verbosity=2)
