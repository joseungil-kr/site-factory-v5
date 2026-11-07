import json
import re
import unittest
from v5 import markup
from v5.config import ConfigError
from v5.purpose_render import assemble, products_html, render, render_service, regional_index, schema, service_schema
from v5.site_plan import initial_spec, validate_plan

class V51PurposeTests(unittest.TestCase):
    def setUp(self):
        self.site={'brand':'꽃이랑','domain':'https://flower.example.test','publishEnabled':True,
                   'theme':'classic','phone':'1844-0644','orderBaseUrl':'https://shop.example.test',
                   'imagePool':['hero.webp'],'keyword':'개업화환','region':'안산','analytics':{'enabled':False}}
        self.products=[{'sku':'A1','name':'축하화환','orderUrl':'https://shop.example.test/a',
                        'imageUrl':'https://shop.example.test/image.jpg','referencePrice':59000}]
        self.page={'id':'ansan','number':1,'region':'안산','purpose':'opening','title':'안산 개업화환',
                   'productSkus':['A1'],'intro':'예전 소개','sections':[{'heading':'안내','paragraph':'본문'}]}
        self.pool={'opening':{'productSkus':['A1'],'introductions':['{region} 개업화환'],
                  'sections':[{'slot':'choice','heading':'선택 안내','paragraph':'축하할 때 고르세요'},{'slot':'order','heading':'주문 안내','paragraph':'주문 방법을 살펴보세요'}],
                  'faqs':[{'q':'어떻게 주문하나요?','a':'상품을 골라 주문하세요.'}]}}
    def test_purpose_isolation_and_deterministic_choice(self):
        a=assemble(self.page,self.pool,self.products)
        self.assertEqual(a,assemble(self.page,self.pool,self.products))
        self.assertEqual(a['intro'],'안산 개업화환')
        with self.assertRaises(ConfigError):assemble({**self.page,'purpose':'funeral'},self.pool,self.products)
        with self.assertRaises(ConfigError):assemble({**self.page,'productSkus':['B2']},self.pool,self.products)
    def test_unverified_price_and_unapproved_image_are_not_displayed(self):
        html=products_html(self.products,['A1'])
        self.assertNotIn('59,000',html)
        self.assertNotIn('image.jpg',html)
        self.assertIn('https://shop.example.test/a',html)
    def test_confirmed_flag_without_price_never_outputs_a_price_or_offer(self):
        p={k:v for k,v in self.products[0].items() if k!='referencePrice'}
        p.update(priceConfirmed=True,priceEvidence='seller',priceCheckedOn='2026-11-07')
        self.assertNotIn('원',products_html([p],['A1']))
        self.assertNotIn('Offer',schema(self.site,assemble(self.page,self.pool,[p]),[p]))
    def test_verified_evidence_displays_image_and_price(self):
        p={**self.products[0],'priceConfirmed':True,'priceEvidence':'seller page',
           'priceCheckedOn':'2026-11-07','imageUseApproved':True,'imageApprovalEvidence':'permission 1','imageApprovedFor':['demo']}
        html=products_html([p],['A1'],'demo')
        self.assertIn('59,000원',html);self.assertIn('image.jpg',html)
        self.assertNotIn('seller page',html)
    def test_schema_matches_actual_products_and_is_safe_json(self):
        page=assemble(self.page,self.pool,self.products)
        html=schema(self.site,page,self.products)
        raw=re.search(r'<script[^>]*>(.*?)</script>',html).group(1)
        doc=json.loads(raw); graph=doc['@graph']
        self.assertEqual(graph[0]['url'],'https://flower.example.test/')
        self.assertEqual(graph[1]['itemListElement'][0]['item']['url'],self.products[0]['orderUrl'])
        self.assertNotIn('Offer',raw)
        bad={**page,'title':'x</script><script>alert(1)</script>'}
        self.assertNotIn('</script><script>',schema(self.site,bad,self.products))
    def test_confirmed_price_in_schema_matches_visible_price(self):
        product={**self.products[0],'priceConfirmed':True,'priceEvidence':'seller',
                 'priceCheckedOn':'2026-11-07'}
        raw=schema(self.site,assemble(self.page,self.pool,[product]),[product])
        obj=json.loads(re.search(r'<script[^>]*>(.*?)</script>',raw).group(1))
        offer=obj['@graph'][1]['itemListElement'][0]['item']['offers']
        self.assertEqual(offer['price'],'59000');self.assertEqual(offer['priceCurrency'],'KRW')
        self.assertIn('59,000원',products_html([product],['A1']))
    def test_preview_does_not_advertise_production_schema(self):
        self.assertEqual(schema({**self.site,'publishEnabled':False},self.page,self.products),'')
    def test_render_puts_products_before_explanation_and_navigation_is_explicit(self):
        child={**self.page,'id':'child','number':2,'region':'고잔동','parentPageId':'ansan'}
        unrelated={**self.page,'id':'other','number':3,'region':'인천'}
        html=render(self.site,self.page,[self.page,child,unrelated],self.products,[],self.pool)
        self.assertLess(html.index('상품과 가격'),html.index('선택 안내'))
        nav=html.split('aria-label="관련 지역"',1)[1].split('</nav>',1)[0]
        self.assertIn('고잔동',nav);self.assertNotIn('인천',nav)
    def test_service_schema_never_fabricates_offer_or_local_business(self):
        raw=service_schema(self.site,self.page)
        self.assertIn('WebPage',raw);self.assertNotIn('Offer',raw);self.assertNotIn('LocalBusiness',raw)
    def test_service_purpose_displays_only_selected_rates(self):
        site={**self.site,'id':'demo','serviceLabel':'스카이차','serviceHours':'전화 상담'}
        page={**self.page,'serviceIds':['truck'],'purpose':'equipment'}
        pool={'equipment':{'serviceIds':['truck'],'introductions':['{region} 스카이차'],
              'sections':[{'slot':'choice','heading':'장비 선택','paragraph':'작업 높이를 알려주세요'},
                          {'slot':'order','heading':'견적 문의','paragraph':'전화로 상담하세요'}],
              'faqs':[{'q':'상담은 어떻게 하나요?','a':'전화로 문의하세요.'}]}}
        services=[{'id':'truck','name':'1톤'},{'id':'other','name':'5톤'}]
        rates={'plans':[{'serviceId':'truck','hour':100000,'halfDay':200000,'fullDay':300000},
                        {'serviceId':'other','hour':400000,'halfDay':500000,'fullDay':600000}]}
        html=render_service(site,page,[page],services,rates,pool)
        self.assertIn('100,000원',html);self.assertNotIn('400,000원',html)
        self.assertLess(html.index('서비스와 요금'),html.index('장비 선택'))
        self.assertNotIn('운영자 승인',html)
    def test_image_approval_is_scoped_to_site(self):
        p={**self.products[0],'imageUseApproved':True,'imageApprovalEvidence':'permission',
           'imageApprovedFor':['other']}
        self.assertNotIn('image.jpg',products_html([p],['A1'],'demo'))
        self.assertIn('image.jpg',products_html([p],['A1'],'other'))
    def test_region_graph_rejects_invalid_and_cyclic_parent(self):
        with self.assertRaises(ConfigError):regional_index([{**self.page,'parentPageId':'missing'}])
        a={**self.page,'id':'a','parentPageId':'b'}; b={**self.page,'id':'b','parentPageId':'a'}
        with self.assertRaises(ConfigError):regional_index([a,b])
    def test_service_publish_promotion_adds_actual_page_schema(self):
        import tempfile
        from pathlib import Path
        from v5.shared_release import promote_service
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/'index.html').write_text('<html><head><meta name="robots" content="noindex,nofollow"></head><body></body></html>')
            page={**self.page,'intro':'선택된 설명'}
            promote_service(root,{'site':self.site,'pages':[page],'v51PurposeMode':True})
            html=(root/'index.html').read_text()
            self.assertIn('application/ld+json',html)
            self.assertIn('선택된 설명',html)
            self.assertIn('index,follow',html)
    def test_new_plan_demands_research_and_purpose_pools(self):
        plan=initial_spec('demo','꽃','화환','안산','1844-0644')
        self.assertEqual(plan['version'],2)
        errors=validate_plan(plan,'demo')['errors']
        self.assertTrue(any('research' in x for x in errors));self.assertTrue(any('purposePools' in x for x in errors))
    def test_research_pool_invalid_types_are_rejected(self):
        plan=initial_spec('demo','꽃','화환','안산','1844-0644')
        plan.update(approved=True,purposePools={'x':{'productSkus':['A1'],'introductions':[None],
                        'sections':[{'slot':'choice','heading':'x','paragraph':'y'},{'slot':'order','heading':'a','paragraph':'b'}],'faqs':[{'q':'q','a':'a'}]}})
        self.assertTrue(any('invalid introductions' in e for e in validate_plan(plan,'demo')['errors']))

if __name__=='__main__':unittest.main()

class V51BuildIntegrationTests(unittest.TestCase):
    def test_new_site_preview_runs_end_to_end_without_touching_legacy(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from v5 import engine, audit, config, site_plan
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'sites'/'demo').mkdir(parents=True)
            evidence={k:[{'source':'https://example.test/'+k,'checkedOn':'2026-11-07'}] for k in ('topic','price','order')}
            pools={
                'opening':{'productSkus':['A1'],'introductions':['안산 개업 축하화환을 선택하세요.'],
                   'sections':[{'slot':'choice','heading':'축하 꽃 고르기','paragraph':'붉은색 꽃과 밝은 리본으로 새로운 출발을 축하합니다. 아주 넓은 장소에 어울리는 구성과 필요한 문구를 살펴보세요.'},{'slot':'order','heading':'개업 주문','paragraph':'받는 주소와 행사 날짜를 알려주세요.'}],
                   'faqs':[{'q':'어떤 리본을 고르나요?','a':'축하 문구를 선택하세요.'}]},
                'condolence':{'productSkus':['B1'],'introductions':['고양 장례식장 근조화환을 안내합니다.'],
                   'sections':[{'slot':'choice','heading':'조문 상품 선택','paragraph':'흰색 계열을 중심으로 조의를 전하고, 빈소와 수령인을 알려주시면 주문에 도움이 됩니다. 보낼 문구를 미리 정하세요.'},{'slot':'order','heading':'조문 주문','paragraph':'장례식장과 수령인을 알려주세요.'}],
                   'faqs':[{'q':'받을 곳은 어디인가요?','a':'시설 이름을 알려주세요.'}]}}
            spec=site_plan.initial_spec('demo','꽃','화환','전국','1844-0644')
            spec.update(approved=True, domain='https://demo.example.test', businessModel='webshop',
                serviceScope={'region':'전국','granularity':'city'},pageTypes=['city'],targetPageCount=2,
                titlePattern='{region} {keyword}',urlPattern='/{number}.html',
                copyPoolPlan={'industry':'flower','source':'test','sentenceTarget':1},
                conversion={'mode':'shop','phone':'1844-0644'},images={'source':'test','approved':True},
                publishPolicy={'mode':'preview'},research=evidence,purposePools=pools)
            (root/'sites'/'demo'/'site-spec.json').write_text(json.dumps(spec,ensure_ascii=False))
            s={'id':'demo','brand':'꽃','siteTitle':'꽃','domain':None,'publishEnabled':False,'theme':'classic',
               'phone':'1844-0644','orderBaseUrl':'https://shop.example.test','keyword':'화환','region':'전국',
               'imagePool':['hero.webp'],'imageLibrary':'demo','staticAssetSoftLimit':18000,
               'analytics':{'enabled':False},'siteSearch':{'enabled':False}}
            p1={'id':'p1','number':1,'region':'안산','purpose':'opening','title':'안산 개업화환','intro':'original',
                'sections':[{'heading':'x','paragraph':'x'*300}],'productSkus':['A1'],'faq':[]}
            p2={'id':'p2','number':2,'region':'고양','purpose':'condolence','title':'고양 근조화환','intro':'original',
                'sections':[{'heading':'z','paragraph':'z'*300}],'productSkus':['B1'],'faq':[],'parentPageId':'p1'}
            products=[{'sku':x,'name':n,'orderUrl':'https://shop.example.test/'+x,'referencePrice':59000} for x,n in [('A1','축하화환'),('B1','근조화환')]]
            data={'site':s,'pages':[p1,p2],'products':products,'links':[],'special':[]}
            def static(site,out):
                (out/'assets').mkdir(exist_ok=True)
                for f in ('site.css','theme-classic.css'):(out/'assets'/f).write_text('')
            with patch.object(engine,'ROOT',root),patch.object(config,'ROOT',root),patch.object(site_plan,'ROOT',root), \
                 patch.object(engine,'read_site',return_value=data),patch.object(audit,'read_site',return_value=data), \
                 patch.object(engine,'_copy_static',side_effect=static):
                result=engine.build('demo',output=root/'dist'/'demo',reports=root/'reports'/'demo',mode='preview')
                home=(root/'dist'/'demo'/'index.html').read_text(); child=(root/'dist'/'demo'/'2.html').read_text()
                self.assertIn('축하화환',home);self.assertNotIn('근조화환',home)
                self.assertIn('근조화환',child);self.assertNotIn('축하화환',child)
                self.assertIn('고양',home);self.assertEqual(result['manifest']['pageCount'],2)
                self.assertFalse(result['audit']['errors'])
            # Separate synthetic publication build: no network/deploy operation.
            from v5.review_gate import review_digest, sample_ids
            published_site={**s,'domain':'https://demo.example.test','publishEnabled':True,
                            'workerName':'test-worker','imageAssetsApproved':True,'cookiePrivacyReviewed':True}
            published={**data,'site':published_site,'products':[{**x,'verifiedLive':True} for x in products]}
            spec['qualityReview']={'approved':True,'reviewer':'fixture','reviewedOn':'2026-11-07',
                'evidence':'synthetic fixture','inputDigest':review_digest(published,spec),
                'samples':[{'id':i,'score':90} for i in sample_ids(published['pages'])]}
            (root/'sites'/'demo'/'site-spec.json').write_text(json.dumps(spec,ensure_ascii=False))
            with patch.object(engine,'ROOT',root),patch.object(config,'ROOT',root),patch.object(site_plan,'ROOT',root), \
                 patch.object(engine,'read_site',return_value=published),patch.object(audit,'read_site',return_value=published), \
                 patch.object(engine,'_copy_static',side_effect=static):
                result=engine.build('demo',output=root/'dist'/'publish',reports=root/'reports'/'publish',mode='publish')
                html=(root/'dist'/'publish'/'2.html').read_text()
                self.assertIn('application/ld+json',html)
                self.assertIn('BreadcrumbList',html)
                self.assertIn('FAQPage',html)
                self.assertFalse(result['audit']['errors'])

class V51ConfigCompatibilityTests(unittest.TestCase):
    def test_missing_price_allowed_only_for_new_unconfirmed_site(self):
        import json, shutil, tempfile
        from pathlib import Path
        from unittest.mock import patch
        from v5 import config
        source=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); sites=root/'sites'; sites.mkdir()
            shutil.copytree(source/'sites/ansan-promotion-plant',sites/'demo')
            shutil.copytree(source/'assets/library/promotion-plant',root/'assets/library/promotion-plant')
            site_path=sites/'demo'/'site.json'; site=json.loads(site_path.read_text());site['id']='demo'
            site_path.write_text(json.dumps(site,ensure_ascii=False))
            products_path=sites/'demo'/'products.json'; products=json.loads(products_path.read_text());products[0].pop('referencePrice')
            products_path.write_text(json.dumps(products,ensure_ascii=False))
            spec_path=sites/'demo'/'site-spec.json';spec_path.write_text('{"version":2}')
            with patch.object(config,'ROOT',root),patch.object(config,'SITES',sites):
                self.assertNotIn('referencePrice',config.read_site('demo')['products'][0])
                products[0]['priceConfirmed']=True
                products_path.write_text(json.dumps(products,ensure_ascii=False))
                with self.assertRaises(ConfigError):config.read_site('demo')
                spec_path.write_text('{"version":1}')
                with self.assertRaises(ConfigError):config.read_site('demo')
