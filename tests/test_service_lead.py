"""Service-lead mode and composable product-site add-ons.

An existing product catalog must continue working without opt-in changes.
"""
import copy
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from v5 import addons, markup
from v5.config import ConfigError, read_site
from v5.engine import build
from v5.audit import audit

ROOT = Path(__file__).resolve().parents[1]


class ServiceMode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=read_site('daysky')

    def test_daysky_inventory_is_independent(self):
        d=self.data
        self.assertEqual(len(d['pages']),1736)
        self.assertEqual(len(d['services']),3)
        self.assertEqual(d['products'],[])
        self.assertEqual(d['site']['brand'],'당일스카이')
        self.assertEqual(d['site']['phone'],'010-5322-1952')
        self.assertFalse(d['site']['publishEnabled'])
        self.assertEqual(d['site']['domain'],'https://daysky.nalmada.net')
        self.assertTrue(d['site']['publicIndexingApproved'])
        self.assertEqual(d['site']['publicIndexingScope'],'daysky-seoul-gyeonggi-1736-20261025')
        self.assertTrue(all(x.endswith('.webp') for x in d['site']['imagePool']))
        self.assertEqual(d['site']['requestedDomain'],'https://daysky.nalmada.net')
        self.assertEqual(list(map(lambda x:x['number'],d['pages'])),list(range(1,1737)))
        self.assertEqual(d['services'][0]['name'],'1톤 스카이차')
        self.assertEqual({r['serviceId'] for r in d['rates']['plans']},{'sky-1t','sky-35t','sky-5t'})
        self.assertEqual([(x['hour'],x['halfDay'],x['fullDay']) for x in d['rates']['plans']],
                         [(300000,400000,600000),(300000,400000,600000),(400000,500000,700000)])

    def test_preview_29_pages_noindex_phone_and_pricing(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'out';reports=Path(d)/'reports'
            result=build('daysky',mode='preview',output=out,reports=reports)
            self.assertEqual(result['manifest']['pageCount'],1736)
            self.assertEqual(result['manifest']['specialPageCount'],0)
            self.assertEqual(result['audit']['errors'],[])
            self.assertLess(result['audit']['maxBodyChar5gramJaccard'],0.49)
            self.assertEqual(len(list(out.glob('*.html'))),1737)
            self.assertFalse((out/'sitemap.xml').exists())
            self.assertIn('Disallow: /',(out/'robots.txt').read_text())
            for number in (1,2,29,30,1736):
                p=out/markup.filename(number)
                html=p.read_text()
                self.assertIn('noindex,nofollow',html)
                self.assertNotIn('rel="canonical"',html)
                self.assertIn('tel:01053221952',html)
                self.assertNotIn('영진',html)
                self.assertNotIn('fwith',html.lower())
                self.assertNotIn('1844-0644',html)
                self.assertNotIn('온라인 주문',html)
                self.assertIn('부가세 별도',html)
                self.assertIn('400,000원',html)
                self.assertIn('700,000원',html)
                expected_nums=markup.pagination(self.data['pages'],number)
                for n in expected_nums:
                    if n != number:self.assertIn(f'href="{markup.url_path(n)}"',html)
            self.assertEqual( len(re.findall('<h1', (out/'index.html').read_text())), 1)
            self.assertEqual( len(re.findall('<h1', (out/'29.html').read_text())), 1)
            self.assertIn('페이지를 찾을 수 없습니다',(out/'404.html').read_text())
            self.assertNotIn('daysky.nalmada.net',(out/'index.html').read_text())

    def test_service_cannot_publish_without_explicit_gate(self):
        with self.assertRaises(ConfigError): build('daysky',mode='publish')

    def test_approved_public_indexed_daysky_release_and_safe_preview(self):
        from xml.etree import ElementTree as ET
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/'indexed'
            report=Path(directory)/'reports'
            result=build('daysky',mode='public-indexing',output=out,reports=report)
            self.assertEqual(result['manifest']['pageCount'],1736)
            self.assertEqual(result['audit']['errors'],[])
            self.assertEqual(len(list(out.glob('*.html'))),1737)
            self.assertEqual(len(list((out/'assets/images').glob('*.webp'))),3)
            for n in (1,2,29,30,1736):
                path=markup.filename(n)
                html=(out/path).read_text(encoding='utf-8')
                url='https://daysky.nalmada.net'+markup.url_path(n)
                self.assertIn('<meta name="robots" content="index,follow">',html)
                self.assertIn('<link rel="canonical" href="'+url+'">',html)
                self.assertIn('010-5322-1952',html)
                self.assertNotIn('영진',html)
                self.assertNotIn('1844-0644',html)
            not_found=(out/'404.html').read_text(encoding='utf-8')
            self.assertIn('noindex,nofollow',not_found)
            self.assertNotIn('rel="canonical"',not_found)
            self.assertIn('Allow: /',(out/'robots.txt').read_text(encoding='utf-8'))
            sitemap=ET.parse(out/'sitemap.xml')
            urls=[x.text for x in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
            self.assertEqual(len(urls),1736)
            self.assertEqual(urls[0],'https://daysky.nalmada.net/')
            self.assertEqual(urls[-1],'https://daysky.nalmada.net/29.html')
            self.assertEqual(len(set(urls)),1736)
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/'preview'
            build('daysky',mode='preview',output=out,reports=Path(directory)/'reports')
            self.assertNotIn('canonical',(out/'index.html').read_text(encoding='utf-8'))
            self.assertIn('noindex,nofollow',(out/'index.html').read_text(encoding='utf-8'))
            self.assertNotIn('sitemap.xml',(out/'robots.txt').read_text(encoding='utf-8'))

    def test_wrong_host_is_rejected_for_indexing(self):
        mutated=copy.deepcopy(self.data)
        mutated['site']['domain']='https://other.nalmada.net'
        with tempfile.TemporaryDirectory() as directory:
            with patch('v5.engine.read_site',return_value=mutated):
                with self.assertRaises(ConfigError):
                    build('daysky',mode='public-indexing',
                          output=Path(directory)/'out',reports=Path(directory)/'reports')

    def test_addon_schema_rejects_unsafe_prices(self):
        good={'pricingTable':{'enabled':True,'title':'별도 서비스 가격표',
            'headers':['4시간','8시간'],
            'rows':[{'label':'작업비','prices':[400000,600000]}],
            'placements':['home'],'pageNumbers':[1]}}
        addons.validate(good,self.data['pages'])
        bad=copy.deepcopy(good);bad['pricingTable']['rows'][0]['prices'][0]=-2
        with self.assertRaises(addons.AddOnError):addons.validate(bad,self.data['pages'])
        bad=copy.deepcopy(good);bad['pricingTable']['pageNumbers']=[1737]
        with self.assertRaises(addons.AddOnError):addons.validate(bad,self.data['pages'])

    def test_existing_flower_shop_can_add_phone_and_pricing_on_selected_pages(self):
        product_data=read_site('ansan-promotion-plant')
        site=copy.deepcopy(product_data['site'])
        addons_config={
          'pricingTable':{'enabled':True,'title':'추가 서비스 요금표','headers':['반나절','하루'],
              'rows':[{'label':'배송 서비스','prices':[12000,20000]}],
              'vatIncluded':False,'placements':['home','detail'],'pageNumbers':[1,2],
              'note':'선택적 서비스 안내'},
          'phoneCTA':{'enabled':True,'title':'구매 전 상담','description':'구매와 상담 중 편한 방법을 선택하세요.',
              'label':'상담 전화','placements':['detail'],'pageNumbers':[2]}
        }
        addons.validate(addons_config,product_data['pages'])
        site['addOns']=addons_config
        first=markup.home(site,product_data['pages'][0],product_data['pages'],product_data['products'],product_data['links'])
        first=addons.enhance_html(first,site,1)
        self.assertIn('추가 서비스 요금표',first)
        self.assertIn('12,000원',first)
        self.assertIn('온라인 주문',first)
        self.assertIn('tel:18440644',first)
        self.assertNotIn('구매 전 상담',first)
        second=markup.detail(site,product_data['pages'][1],product_data['pages'],product_data['products'],product_data['links'])
        second=addons.enhance_html(second,site,2)
        self.assertIn('data-track-event="shop"',second)
        self.assertIn('구매 전 상담',second)
        self.assertIn('20,000원',second)
        self.assertIn('tel:18440644',second)
        third=markup.detail(site,product_data['pages'][2],product_data['pages'],product_data['products'],product_data['links'])
        self.assertNotIn('v5-price-scroll',addons.enhance_html(third,site,3))
        original=markup.home(product_data['site'],product_data['pages'][0],product_data['pages'],product_data['products'],product_data['links'])
        self.assertEqual(addons.enhance_html(original,product_data['site'],1),original)

    def test_user_content_is_html_escaped(self):
        data={'enabled':True,'title':'<script>alert(1)</script>',
              'headers':['기본'], 'rows':[{'label':'<b>비용</b>','prices':[10000]}]}
        rendered=addons.pricing_table(data)
        self.assertNotIn('<script>',rendered)
        self.assertIn('&lt;script&gt;',rendered)
        self.assertIn('&lt;b&gt;',rendered)

if __name__=='__main__': unittest.main()
