"""Verify all official lower-level region pages, links, prices, and noindex."""
import argparse,hashlib,json,unittest
from pathlib import Path
from html.parser import HTMLParser
import expand_lower
ROOT=Path(__file__).resolve().parent

class H(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.img=[];self.robots=[];self.canonical=[]
    def handle_starttag(self,t,attrs):
        d=dict(attrs)
        if t=='a':self.links.append(d.get('href',''))
        if t=='img':self.img.append(d)
        if t=='meta' and d.get('name')=='robots':self.robots.append(d.get('content'))
        if t=='link' and d.get('rel')=='canonical':self.canonical.append(d.get('href'))

class QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=expand_lower.main(ARCHIVE)
        cls.out=ROOT/'dist-all-localities'
    def test_counts_codes_and_exclusions(self):
        r=self.r
        self.assertEqual((r['activeRows'],r['eligibleEupMyeonDong'],r['verifiedParentLocalities']),(20560,4632,4632))
        self.assertEqual(r['unmatched'],[])
        self.assertEqual(r['grandTotalHTML'],4935)
        self.assertEqual(len(list(self.out.rglob('*.html'))),4935)
        self.assertFalse(r['uniqueContentProven'])
        self.assertEqual(r['verifiedDeliveryAreas'],0)
        self.assertFalse(r['indexable'])
        self.assertFalse((self.out/'sitemap.xml').exists())
    def test_internal_links_and_safe_customer_copy(self):
        pages=list(self.out.rglob('*.html'))
        targets={'/':self.out/'ansan/index.html'}
        for p in pages:
            name='/'+p.relative_to(self.out).as_posix()
            targets[name]=p
            if name.endswith('/index.html'):targets[name[:-10]]=p
        eligible=set()
        for p in pages:
            text=p.read_text(encoding='utf-8')
            parser=H();parser.feed(text)
            self.assertEqual(parser.robots,['noindex,nofollow'],p)
            self.assertFalse(parser.canonical,p)
            for u in parser.links:
                if u.startswith('/'):
                    self.assertIn(u,targets,(p,u))
            if p.parent.name=='locality':
                self.assertEqual(len(parser.img),5)
                self.assertEqual(len({x['src'] for x in parser.img}),5)
                self.assertEqual(len([u for u in parser.links if u.startswith('https://fwith.co.kr/shop/item.php?it_id=')]),5)
                self.assertIn('실제 배송 가능 여부',text)
                self.assertIn('0건',text)
                eligible.add(p.stem)
                self.assertNotIn('municipality 등급',text)
                self.assertNotIn('가장 높은 B205은',text)
        self.assertEqual(len(eligible),4632)
        directory=(self.out/'localities/index.html').read_text()
        self.assertEqual(directory.count('href="/localities/'),16)
        self.assertIn('href="/localities/"',(self.out/'ansan/index.html').read_text())
    def test_five_real_webp_hashes(self):
        manifest=json.loads((ROOT/'image-manifest.json').read_text())['images']
        for item in manifest:
            raw=(self.out/'assets'/item['filename']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),item['sha256'])

if __name__=='__main__':
    q=argparse.ArgumentParser();q.add_argument('--archive',type=Path,required=True)
    args=q.parse_args();ARCHIVE=args.archive
    unittest.main(argv=['test_lower.py'],verbosity=2)
