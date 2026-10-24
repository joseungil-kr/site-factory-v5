import json
import tempfile
import unittest
from pathlib import Path
from v5 import markup
from v5.config import read_site,ConfigError
from v5.engine import build
from v5.audit import audit,similarity

ROOT=Path(__file__).resolve().parents[1]

class StageB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site=read_site('ansan-promotion-plant')
    def test_inventory_and_product_destinations(self):
        self.assertEqual(len(self.site['pages']),10)
        self.assertEqual([p['number'] for p in self.site['pages']],list(range(1,11)))
        self.assertTrue(all(p['orderUrl'].startswith('https://fwith.co.kr/shop/item.php?it_id=') for p in self.site['products']))
    def test_number_navigation_499_and_missing_number(self):
        pages=[{'number':n} for n in range(1,500)]
        self.assertEqual(markup.pagination(pages,1),list(range(1,8)))
        self.assertEqual(markup.pagination(pages,250),list(range(247,254)))
        self.assertEqual(markup.pagination(pages,499),list(range(493,500)))
        pages=[{'number':n} for n in [1,2,4,6,10,50,99]]
        self.assertEqual(markup.pagination(pages,4),[1,2,4,6,10,50,99])
        self.assertEqual(markup.pagination(pages,99),[1,2,4,6,10,50,99])
        with self.assertRaises(ValueError):markup.pagination(pages,5)
    def test_special_links_scopes(self):
        links=self.site['links'];page=self.site['pages'][0]
        self.assertEqual([x['id'] for x in markup.relevant_links(links,page,'footer')],['estimate'])
        self.assertEqual([x['id'] for x in markup.relevant_links(links,page,'body')],['delivery'])
    def test_build_and_local_qa(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'output';reports=Path(t)/'reports'
            result=build('ansan-promotion-plant',output=out,reports=reports)
            self.assertEqual(result['manifest']['pageCount'],10)
            self.assertEqual(result['manifest']['specialPageCount'],2)
            self.assertEqual(result['manifest']['assetFileCount'],27)
            self.assertTrue((out/'견적계산기.html').exists())
            self.assertIn('noindex,nofollow',(out/'index.html').read_text(encoding='utf-8'))
            self.assertNotIn('rel="canonical"',(out/'index.html').read_text(encoding='utf-8'))
            self.assertFalse((out/'sitemap.xml').exists())
            self.assertTrue((out/'assets/images/plant-a.svg').exists())
            inspected=audit('ansan-promotion-plant',output=out,write_report=False)
            self.assertEqual(inspected['errors'],[])
            self.assertLess(inspected['maxBodyChar5gramJaccard'],0.49)
    def test_html_escapes_user_input(self):
        p=dict(self.site['pages'][0]);p['title']='<script>inject</script> 승진화분'
        output=markup.detail(self.site['site'],p,self.site['pages'],self.site['products'],self.site['links'])
        self.assertNotIn('<script>inject</script>',output)
        self.assertIn('&lt;script&gt;inject&lt;/script&gt;',output)

if __name__=='__main__':unittest.main()
