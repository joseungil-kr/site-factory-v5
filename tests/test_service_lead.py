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
        self.assertEqual(len(d['pages']),29)
        self.assertEqual(len(d['services']),3)
        self.assertEqual(d['products'],[])
        self.assertEqual(d['site']['brand'],'당일스카이')
        self.assertEqual(d['site']['phone'],'010-5322-1952')
        self.assertFalse(d['site']['publishEnabled'])
        self.assertEqual(d['site']['domain'],None)
        self.assertEqual(d['site']['requestedDomain'],'https://daysky.nalmada.net')
        self.assertEqual(list(map(lambda x:x['number'],d['pages'])),list(range(1,30)))
        self.assertEqual(d['services'][0]['name'],'1톤 스카이차')
        self.assertEqual({r['serviceId'] for r in d['rates']['plans']},{'sky-1t','sky-35t','sky-5t'})
        self.assertEqual([(x['hour'],x['halfDay'],x['fullDay']) for x in d['rates']['plans']],
                         [(300000,400000,600000),(300000,400000,600000),(400000,500000,700000)])

    def test_preview_29_pages_noindex_phone_and_pricing(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'out';reports=Path(d)/'reports'
            result=build('daysky',mode='preview',output=out,reports=reports)
            self.assertEqual(result['manifest']['pageCount'],29)
            self.assertEqual(result['manifest']['specialPageCount'],0)
            self.assertEqual(result['audit']['errors'],[])
            self.assertLess(result['audit']['maxBodyChar5gramJaccard'],0.49)
            self.assertEqual(len(list(out.glob('*.html'))),30)
            self.assertFalse((out/'sitemap.xml').exists())
            self.assertIn('Disallow: /',(out/'robots.txt').read_text())
            for number in range(1,30):
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

    def test_addon_schema_rejects_unsafe_prices(self):
        good={'pricingTable':{'enabled':True,'title':'별도 서비스 가격표',
            'headers':['4시간','8시간'],
            'rows':[{'label':'작업비','prices':[400000,600000]}],
            'placements':['home'],'pageNumbers':[1]}}
        addons.validate(good,self.data['pages'])
        bad=copy.deepcopy(good);bad['pricingTable']['rows'][0]['prices'][0]=-2
        with self.assertRaises(addons.AddOnError):addons.validate(bad,self.data['pages'])
        bad=copy.deepcopy(good);bad['pricingTable']['pageNumbers']=[300]
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
        self.assertIn('상품 확인',second)
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
