"""Isolated 95-page county trial SKU, price, and intent regression tests."""
import json,re,unittest
from pathlib import Path
from scripts.build_county_funeral_trial_inputs import main as generate,ID,SITE,PRICES
KNOWN_PRICES={**PRICES,'B213':120000,'B054':90000,'B211':59000}
from scripts.county_copy_pools import product_skus_in_text,listed_prices_in_text
from v5.config import read_site,ConfigError
from v5.purpose_render import assemble

class CountySelectedSkuContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generate()
        cls.data=read_site(ID)
        cls.plan=json.loads((SITE/'site-spec.json').read_text(encoding='utf-8'))
    def test_sku_regex_real_fixture(self):
        self.assertEqual(product_skus_in_text('B201 59,000원, B205 109,000원'),{'B201','B205'})
        self.assertEqual(listed_prices_in_text('B201 59,000원, B205 109,000원'),{'59,000원','109,000원'})
        self.assertEqual(product_skus_in_text('그냥 가격을 비교합니다'),set())
        # Unicode word boundaries lose tokens when followed by Korean particles.
        self.assertEqual(product_skus_in_text('B201과 B205는 B206의'),{'B201','B205','B206'})
        self.assertEqual(product_skus_in_text('B201·B202, B205/B206을'),{'B201','B202','B205','B206'})
        self.assertEqual(product_skus_in_text('XB201 AB202'),set())
        self.assertEqual(product_skus_in_text('B299를'),{'B299'})
        self.assertEqual(listed_prices_in_text('59,000원입니다. 149,000원으로'),
                         {'59,000원','149,000원'})
        self.assertEqual(listed_prices_in_text('59000원도 50,000원 차이입니다.'),
                         {'59,000원','50,000원'})
        self.assertEqual(listed_prices_in_text('가격 정보를 확인합니다.'),set())
    def test_all_82_county_pages_selected_skus_and_prices(self):
        rows=[p for p in self.data['pages'] if p['pageType']=='county']
        self.assertEqual(len(rows),82)
        catalog=self.data['products']
        for p in rows:
            with self.subTest(page=p['number'],purpose=p['purpose']):
                a=assemble(p,self.plan['purposePools'],catalog)
                selected=set(p['productSkus'])
                text=' '.join([a['intro']]+[x['heading']+' '+x['paragraph'] for x in a['sections']]+
                    [x['q']+' '+x['a'] for x in a['faq']])
                self.assertTrue(product_skus_in_text(text)<=selected,
                    f"{p['number']}: prose names products missing from cards")
                product_prices={KNOWN_PRICES[x] for x in selected if x in KNOWN_PRICES}
                permitted={format(x,',')+'원' for x in product_prices}
                permitted|={format(fact['amount'],',')+'원' for fact in p.get('verifiedSkuShipping',[])
                            if fact.get('sku') in selected and fact.get('scope')==p.get('county')
                            and fact.get('source')=='https://fwith.co.kr/shop/item.php?it_id='+fact['sku']}
                permitted|={format(abs(x-y),',')+'원' for x in product_prices for y in product_prices if x!=y}
                self.assertTrue(listed_prices_in_text(text)<=permitted,
                    f"{p['number']}: prose contains prices of products absent from cards")
                self.assertNotIn(a['intro'],[x['paragraph'] for x in a['sections']])
                self.assertNotIn('{townships}',text)
                self.assertIn(p['townships'],text)
                self.assertEqual(p['siteVariantPolicy'],'county-v51')
                self.assertEqual([s['slot'] for s in a['sections']],
                    (['choice','order','verified-townships'] if p['purpose'].startswith('restricted-')
                     else ['choice','order','ribbon','verified-townships']))
                self.assertEqual(len(a['faq']),0 if p['purpose']=='restricted-basket' else 1)
                self.assertGreater(int(p['townshipCount']),0)
                if len(selected)<4:
                    self.assertFalse(any(x in text for x in ('네 상품만 비교한','같은 등급으로 간주하지 않습니다')))
    def test_destination_truth_and_official_B202_title_in_all_95_html(self):
        from scripts.build_county_trial_review_only import main as make, OUT
        make()
        catalog={x['sku']:x for x in self.data['products']}
        self.assertEqual(catalog['B202']['name'],'근조 3단 화환')
        for p in self.data['pages']:
            fn='index.html' if p['number']==1 else str(p['number'])+'.html'
            body=(OUT/fn).read_text(encoding='utf-8')
            with self.subTest(page=fn):
                self.assertNotIn('근조화환 B202',body,
                    'fallback code must never be attributed as official title')
                if 'B202' in p['productSkus']:
                    self.assertIn('data-product-sku="B202"',body)
                    self.assertIn('근조 3단 화환',body)
                if p['pageType']=='county':
                    self.assertNotIn('장례식장명과 도로명주소를 찾을 수 있습니다',body)
        gangwon=(OUT/'12.html').read_text(encoding='utf-8')
        self.assertNotIn('수령 시설의 읍·면과 상세 주소를 찾을 수 있습니다',gangwon)
        self.assertIn('읍·면',gangwon)

    def test_venue_77_78_action_roles_and_new_faq(self):
        from scripts.build_county_trial_review_only import main as make, OUT
        make()
        for number in (77,78):
            p=next(x for x in self.data['pages'] if x['number']==number)
            a=assemble(p,self.plan['purposePools'],self.data['products'])
            with self.subTest(number=number):
                self.assertEqual([x['slot'] for x in a['sections']],
                                 ['choice','order','ribbon','verified-townships'])
                self.assertTrue(a['faq'])
                self.assertIn('주문내역',a['faq'][0]['a'])
                self.assertNotIn('반입 가능 여부는 어떻게 확인',a['faq'][0]['q'])
                self.assertEqual(a['intro'].count('반입 가능 여부'),0)
                self.assertIn(p['townships'],a['sections'][-1]['paragraph'])
                self.assertNotIn('장례식장명과 도로명주소를 찾을 수',a['sections'][-1]['paragraph'])
        # A single purpose reused across counties must produce different
        # substantive buyer tasks, not a copied sequence plus a changed county.
        for intent in ('venue-form','venue-shipping'):
            pages=[p for p in self.data['pages'] if p['purpose']==intent]
            if len(pages)>1:
                texts=[tuple(s['paragraph'] for s in assemble(p,self.plan['purposePools'],self.data['products'])['sections'][:3])
                       for p in pages]
                self.assertEqual(len(texts),len(set(texts)),intent)

    def test_customer_html_never_exposes_internal_data_scope_or_confuses_product_number(self):
        from scripts.build_county_trial_review_only import main as render_review, OUT
        render_review()
        banned=[
            '이 목록은 행정지역명이며 장례식장명이나 시설 도로명주소가 아닙니다',
            '페이지가 제공하는 내용은 읍면 이름이고 시설 주소는 직접 준비합니다',
            '군 페이지의 읍면 목록은 행정지역명이지 시설 주소록은 아닙니다',
            '가격 외 주문번호','주문번호는 서로 다릅니다',
        ]
        seen=0
        for p in self.data['pages']:
            filename='index.html' if p['number']==1 else f"{p['number']}.html"
            html=(OUT/filename).read_text(encoding='utf-8')
            with self.subTest(filename=filename):
                for phrase in banned:
                    self.assertNotIn(phrase,html)
                if p['pageType']=='county':
                    seen+=1
        self.assertEqual(seen,82)
        # Focused checks on formerly failed county pages and valid order/SKU terms.
        for number in (14,26,24,42,86):
            html=(OUT/f'{number}.html').read_text(encoding='utf-8')
            self.assertIn('상품번호',html)
            self.assertNotIn('주문번호는 서로 다릅니다',html)
        for number in (12,77,78):
            html=(OUT/f'{number}.html').read_text(encoding='utf-8')
            self.assertIn('읍·면',html)
        shipping=(OUT/'78.html').read_text(encoding='utf-8')
        self.assertIn('20,000원',shipping)
        self.assertIn('data-product-sku="B201"',shipping)
        self.assertIn('data-product-sku="B206"',shipping)

    def test_all_12_province_hubs_have_distinct_information_owners(self):
        # Source-level assertions: the navigation owns child county names;
        # introductory text owns count; article owns a grounded buying task.
        # SKU/card prices do not belong in receiving/address sections.
        provinces=[p for p in self.data['pages'] if p['pageType']=='province']
        self.assertEqual(len(provinces),12)
        for p in provinces:
            with self.subTest(province=p['region']):
                a=assemble(p,self.plan['purposePools'],self.data['products'])
                self.assertEqual([x['slot'] for x in a['sections']],['choice','order'])
                body=' '.join(x['heading']+' '+x['paragraph'] for x in a['sections'])
                self.assertFalse(product_skus_in_text(body),
                    'province body must not recite product SKUs instead of localized buying information')
                self.assertFalse(listed_prices_in_text(body),
                    'province body must not recite card prices or price differences')
                children=[x for x in self.data['pages'] if x.get('parentPageId')==p['id']]
                joined='·'.join(x['county'] for x in children)
                if len(children)>1:
                    self.assertNotIn(joined,body)
                    self.assertNotIn(joined,a['intro'])
                else:
                    # For single-county provinces, naming the sole county is
                    # genuine purchase context, not a repeated multi-county list.
                    self.assertLessEqual(body.count(joined),2)
                self.assertIn(str(len(children))+'곳',a['intro'])
        for number in (2,7):
            p=next(x for x in provinces if x['number']==number)
            a=assemble(p,self.plan['purposePools'],self.data['products'])
            content=' '.join([a['intro']]+[x['paragraph'] for x in a['sections']])
            self.assertNotIn('B201',content)
            self.assertNotIn('40,000원',content)
            self.assertNotIn('연천군·가평군·양평군',content)

    def test_buyer_intent_headline_and_early_region_navigation(self):
        # Inspect generated HTML instead of just trusting the page specification.
        from scripts.build_county_trial_review_only import main as render_review, OUT
        from scripts.county_copy_pools import INTENTS
        render_review()
        headings={row[0]:row[3] for row in INTENTS}
        for p in self.data['pages']:
            html=(OUT/('index.html' if p['number']==1 else str(p['number'])+'.html')).read_text(encoding='utf-8')
            with self.subTest(page=p['number']):
                nav=html.find('<nav aria-label="관련 지역">')
                products=html.find('<section class="recommendations">')
                self.assertGreaterEqual(nav,0)
                self.assertGreater(products,nav, 'Regional navigation must precede the long product/FAQ sections')
                self.assertEqual(html.count('<nav aria-label="관련 지역">'),1)
                if p['pageType']=='county':
                    if p.get('verifiedSkuShipping') and p['county']=='의성군':
                        self.assertIn('B205 추가 배송비',p['title'])
                    elif p['purpose'] in headings:
                        self.assertIn(headings[p['purpose']],p['title'])
                    else:
                        self.assertIn('반입 안내',p['title'])
                    self.assertIn(p['county'],p['title'])
                    self.assertIn(p['title'],html)

    def test_headline_promise_and_semantic_duplication_regressions(self):
        # This is a text-overlap warning gate, NOT a substitute for editorial reading.
        from difflib import SequenceMatcher
        from scripts.build_county_trial_review_only import main as make, OUT
        make()
        pages={p['number']:p for p in self.data['pages']}
        for n in (1,14,26,37,95):
            p=pages[n]
            a=assemble(p,self.plan['purposePools'],self.data['products'])
            html=(OUT/('index.html' if n==1 else str(n)+'.html')).read_text(encoding='utf-8')
            blocks=[a['intro']]+[s['paragraph'] for s in a['sections']]+[f['a'] for f in a['faq']]
            for i,left in enumerate(blocks):
                for right in blocks[i+1:]:
                    overlap=SequenceMatcher(None,left,right,autojunk=False).ratio()
                    self.assertLess(overlap,0.85,(n,'nearly duplicated buyer information',round(overlap,3)))
            self.assertIn(p['title'],html)
            if n==1:
                self.assertNotIn('단정하지 말고',html)
                self.assertIn('근조 특대 3단',html)
            elif n==14:
                self.assertIn('기본 주문 정보',p['title'])
                self.assertIn('근조 3단 화환',a['sections'][0]['paragraph'])
                self.assertIn('근조 3단 화환',a['sections'][0]['paragraph'])
                self.assertIn('주문한 근조화환 내역',a['faq'][0]['q'])
            elif n==26:
                self.assertIn('문구 예시',a['intro'])
                ribbon=next(s for s in a['sections'] if s['slot']=='ribbon')
                self.assertTrue(any(x in ribbon['paragraph'] for x in
                    ('삼가 고인의 명복','깊은 애도','謹弔')),(n,ribbon))
                self.assertIn('주문한 뒤',a['faq'][0]['q'])
            elif n in (37,95):
                self.assertEqual(p['productSkus'],['B213'])
                self.assertIn('data-product-sku="B213"',html)
                for sku in ('B201','B202','B205','B206'):
                    self.assertNotIn('data-product-sku="'+sku+'"',html)
                self.assertIn('근조 2단 오브제',p['title']+html)

    def test_verified_shipping_is_not_reused_across_skus_or_counties(self):
        from scripts.build_county_trial_review_only import main as make, OUT
        make()
        pages={p['county']:p for p in self.data['pages'] if p['pageType']=='county'}
        checks=[('연천군','B213',37,10000),('의성군','B205',55,10000),
                ('횡성군','B201',78,20000)]
        for county,sku,number,fee in checks:
            p=pages[county]
            facts=p['verifiedSkuShipping']
            self.assertEqual(len(facts),1)
            fact=facts[0]
            self.assertEqual((fact['scope'],fact['sku'],fact['amount'],fact['checkedOn']),
                             (county,sku,fee,'2026-11-08'))
            self.assertEqual(fact['source'],
                             'https://fwith.co.kr/shop/item.php?it_id='+sku)
            html=(OUT/f'{number}.html').read_text(encoding='utf-8')
            self.assertIn(f'{fee:,}원',html)
            self.assertIn('data-product-sku="'+sku+'"',html)
        for p in self.data['pages']:
            if p['pageType']=='county' and p['county'] not in ('연천군','의성군','횡성군'):
                self.assertFalse(p['verifiedSkuShipping'],p['county'])
    def test_uiseong_facts_instead_of_price_list(self):
        from scripts.build_county_trial_review_only import main as make, OUT
        make()
        p=next(x for x in self.data['pages'] if x.get('county')=='의성군')
        a=assemble(p,self.plan['purposePools'],self.data['products'])
        self.assertIn('B205 추가 배송비',p['title'])
        choice=next(s for s in a['sections'] if s['slot']=='choice')
        delivery=next(s for s in a['sections'] if s['slot']=='order')
        self.assertIn('재생 꽃 미사용',choice['paragraph'])
        self.assertIn('10,000원',delivery['paragraph'])
        self.assertEqual(delivery['paragraph'].count('10,000원'),1)
        self.assertNotIn('B201·B202·B205·B206',choice['paragraph'])
        html=(OUT/f"{p['number']}.html").read_text(encoding='utf-8')
        self.assertIn('10,000원',html)

    def test_seller_notice_is_evidence_bound_and_precedes_products(self):
        from scripts.build_county_trial_review_only import main as render_review, OUT
        render_review()
        seller_notice='https://fwith.co.kr/page/notice.php'
        affected={'연천군':'오브제','부안군':'오브제','거창군':'오브제',
                  '고령군':'영정바구니','청도군':'쌀화환',
                  '완도군':'쌀화환 또는 꽃바구니'}
        for p in self.data['pages']:
            if p['pageType']!='county':
                continue
            filename=str(p['number'])+'.html'
            html=(OUT/filename).read_text(encoding='utf-8')
            n=p.get('sellerVenueNotice')
            with self.subTest(region=p['region']):
                if p['county'] in affected:
                    self.assertIsInstance(n,dict)
                    self.assertIn(affected[p['county']],n['text'])
                    self.assertEqual(n['sourceUrl'],seller_notice)
                    self.assertIn('판매처 공지 확인',html)
                    if affected[p['county']]=='오브제':
                        self.assertEqual(p['productSkus'],['B213'])
                        self.assertIn('data-product-sku="B213"',html)
                    elif p['county']=='고령군':
                        self.assertEqual(p['productSkus'],['B211'])
                        self.assertIn('영정바구니 상품 분류 보기',html)
                        self.assertIn('data-product-sku="B211"',html)
                    else:
                        self.assertEqual(p['productSkus'],['B054'])
                        self.assertIn('data-product-sku="B054"',html)
                        if p['county']=='완도군':
                            self.assertIn('영정바구니 상품 분류 보기',html)
                            self.assertIn('https://fwith.co.kr/shop/list.php?ca_id=2090',html)
                    self.assertNotIn('data-product-sku="B201"',html)
                    self.assertLess(html.find('class="county-venue-notice"'),
                                    html.find('class="recommendations"'))
                else:
                    self.assertFalse(n)
                    self.assertNotIn('class="county-venue-notice"',html)
    def test_restriction_product_fit_and_cta_fail_closed(self):
        from scripts.build_county_trial_review_only import main as render_review, OUT
        render_review()
        special={'연천군':('B213',),'부안군':('B213',),'거창군':('B213',),
                 '고령군':('B211',),'청도군':('B054',),'완도군':('B054',)}
        for page in self.data['pages']:
            if page.get('pageType')!='county':continue
            with self.subTest(region=page['county']):
                html=(OUT/(str(page['number'])+'.html')).read_text(encoding='utf-8')
                if page['county'] in special:
                    self.assertEqual(tuple(page['productSkus']),special[page['county']])
                    self.assertNotIn('data-product-sku="B201"',html)
                    self.assertNotIn('data-product-sku="B205"',html)
                    if page['county']=='고령군':
                        self.assertIn('shop/item.php?it_id=B211',html)
                        self.assertIn('59,000원',html)
                        self.assertIn('영정바구니 상품 분류 보기',html)
                    else:
                        self.assertIn('shop/item.php?it_id='+special[page['county']][0],html)
                else:
                    self.assertNotIn('CAT2090',html)
    def test_real_product_card_headings_and_current_prices(self):
        from scripts.build_county_trial_review_only import main as render_review, OUT
        render_review()
        from html.parser import HTMLParser
        for p in self.data['pages']:
            if p['pageType']!='county':
                continue
            page_file=OUT/('index.html' if p['number']==1 else str(p['number'])+'.html')
            body=page_file.read_text(encoding='utf-8')
            a=assemble(p,self.plan['purposePools'],self.data['products'])
            self.assertEqual(body.count('data-product-sku='),len(p['productSkus']),p['number'])
            for sku in p['productSkus']:
                self.assertIn('data-product-sku="'+sku+'"',body,p['number'])
                if sku in KNOWN_PRICES:
                    expected=format(KNOWN_PRICES[sku],',')+'원'
                    self.assertIn(expected,body,p['number'])
                else:
                    self.assertEqual(sku,'CAT2090')
                    self.assertIn('영정바구니 상품 목록 보기',body)
            self.assertIn('읍·면',body,p['number'])
            self.assertNotIn('네 상품만 비교한',body)
            self.assertNotIn('공개 페이지에 개인정보를 적지 않습니다',body)
            self.assertNotIn('현재 확보된 가격자료만으로 알 수 없습니다',body)
    def test_korean_attached_skus_and_prices_fail_in_assembler(self):
        sample=next(p for p in self.data['pages'] if p.get('purpose')=='budget-entry')
        pool=json.loads(json.dumps(self.plan['purposePools']['budget-entry']))
        invalid={**sample,'purpose':'kor-boundary-test'}
        # Bad SKU is attached to Hangul; strict assembler must not miss it.
        pool['sections'].append({'slot':'unsafe_korean_sku','heading':'가격 비교',
                                 'paragraph':'B201과 B205는 B206의 구성과 다릅니다.'})
        with self.assertRaisesRegex(ConfigError,'off-card SKU'):
            assemble(invalid,{'kor-boundary-test':pool},self.data['products'])
        # No invalid SKU, but a disallowed price is attached to a Korean suffix.
        pool['sections'][-1]['paragraph']='59,000원입니다. 149,000원으로 변경하실 수 있습니다.'
        with self.assertRaisesRegex(ConfigError,'off-card price'):
            assemble(invalid,{'kor-boundary-test':pool},self.data['products'])

    def test_correct_price_difference_stays_allowed(self):
        sample=next(p for p in self.data['pages'] if p.get('purpose')=='budget-upgrade')
        pool=json.loads(json.dumps(self.plan['purposePools']['budget-upgrade']))
        pool['sections'].append({'slot':'valid_difference','heading':'상품 간 가격 차이',
                                 'paragraph':'B201과 B205는 표시가격이 50,000원 차이입니다.'})
        altered={**sample,'purpose':'difference-test'}
        result=assemble(altered,{'difference-test':pool},self.data['products'])
        self.assertIn('50,000원',result['sections'][-1]['paragraph'])

    def test_three_regression_pages(self):
        pages={p['number']:p for p in self.data['pages']}
        for n in (14,38,90):
            self.assertIn(n,pages)
            p=pages[n]
            self.assertEqual(len(p['productSkus']),{14:2,38:2,90:3}[n])
            a=assemble(p,self.plan['purposePools'],self.data['products'])
            body=' '.join([a['intro']]+[x['paragraph'] for x in a['sections']])
            self.assertTrue(product_skus_in_text(body)<=set(p['productSkus']))
    def test_all_eight_previous_offcard_routes_against_actual_rendered_html(self):
        from scripts.build_county_trial_review_only import main as make, OUT
        from scripts.verify_county_independent_html import validate_one
        make()
        expected={
            15:['B201','B205'],
            18:['B201','B202','B205'],
            28:['B054'],
            42:['B201','B206'],
            47:['B202','B206'],
            63:['B205','B206'],
            66:['B201','B206'],
            67:['B202','B205']
        }
        for number,skus in expected.items():
            p=next(x for x in self.data['pages'] if x['number']==number)
            with self.subTest(route='/'+str(number)+'.html'):
                self.assertEqual(p['productSkus'],skus)
                row=validate_one(OUT/(str(number)+'.html'),skus)
                self.assertEqual(row['errors'],[],row)
                self.assertEqual(set(row['visibleProseSKUs'])-set(skus),set())
                self.assertFalse(row['offCardPrices'])

    def test_six_missing_picture_routes_rebuilt_from_pool(self):
        from scripts.build_county_trial_review_only import main as render_review, OUT
        from scripts.verify_county_independent_html import validate_one
        render_review()
        bad_text="아래 도형은 근조화환의 형태를 살펴보기 위한 그림입니다"
        pages={p["number"]:p for p in self.data["pages"]}
        for number in (26,67,69,73,77,86):
            with self.subTest(path=f"/{number}.html"):
                path=OUT/f"{number}.html"
                actual=path.read_text(encoding="utf-8")
                self.assertNotIn(bad_text,actual)
                row=validate_one(path,pages[number]["productSkus"])
                self.assertFalse(row["errors"],row)
                self.assertEqual(row["mainImages"],0)
                self.assertEqual(row["mainSvgs"],0)
                self.assertFalse(row["visualReferences"])

    def test_independent_html_rejects_invented_picture_pointer(self):
        import tempfile
        from scripts.build_county_trial_review_only import main as render_review, OUT
        from scripts.verify_county_independent_html import validate_one
        render_review()
        original=(OUT/"26.html").read_text(encoding="utf-8")
        bad="아래 도형은 근조화환의 형태를 살펴보기 위한 그림입니다."
        with tempfile.TemporaryDirectory() as tmp:
            altered=Path(tmp)/"26.html"
            altered.write_text(original.replace('<section class="recommendations">',
                '<p>'+bad+'</p><section class="recommendations">',1),encoding="utf-8")
            row=validate_one(altered,["B201","B202"])
            self.assertTrue(any("Nonexistent inline visual reference" in e for e in row["errors"]),row)

    def test_factual_customer_tone_and_nonrepeated_faq_in_final_html(self):
        from scripts.build_county_trial_review_only import main as build_review, OUT
        from scripts.verify_county_independent_html import validate_one
        build_review()
        for page in self.data['pages']:
            filename='index.html' if page['number']==1 else str(page['number'])+'.html'
            body=(OUT/filename).read_text(encoding='utf-8')
            with self.subTest(filename=filename):
                for token in ('재확인한 법정동 코드','이 명단은 배송 가능 여부의 확인 자료가 아니라',
                              '현재 보유한 가격 원장','형태 안내 이미지는 판매 상품 실물 사진과 차이가 있을 수 있습니다'):
                    self.assertNotIn(token,body)
                self.assertNotIn('근조화환은 어디에서 주문하고 결제하나요?',body)
                if page['pageType']=='national':
                    self.assertIn('군 지역의 배송료와 주문 합계는 어떻게 확인하나요?',body)
                elif page['pageType']=='province':
                    self.assertIn('선택한 군의 추가 배송비는 어디서 확인하나요?',body)
                self.assertEqual(body.count('<details'),0 if page.get('purpose')=='restricted-basket' else 1)
                self.assertNotIn('지역 안내 페이지에서는 결제정보를 받지 않습니다',body)
                self.assertFalse(validate_one(OUT/filename,page['productSkus'])['errors'])

    def test_refuse_nonselected_fixture(self):
        pool=json.loads(json.dumps(self.plan['purposePools']['budget-entry']))
        pool['sections'].append({'slot':'bad','heading':'잘못된 비교','paragraph':'B201 59,000원, B205 109,000원'})
        p=next(x for x in self.data['pages'] if x.get('purpose')=='budget-entry')
        self.assertNotIn('B205',p['productSkus'])
        altered={**p,'purpose':'bad-test'}
        with self.assertRaisesRegex(ConfigError,'off-card SKU'):
            assemble(altered,{'bad-test':pool},self.data['products'])
        bad_price=json.loads(json.dumps(pool))
        bad_price['sections'][-1]['paragraph']='허용된 상품 이외의 149,000원 표시가'
        with self.assertRaisesRegex(ConfigError,'off-card price'):
            assemble(altered,{'bad-test':bad_price},self.data['products'])


    def test_restricted_fact_ownership_and_semantic_repetition_regression(self):
        from scripts.county_copy_pools import validate_restricted_ownership, RESTRICTED_FACT_OWNER
        from scripts.build_county_trial_review_only import main as make, OUT
        make()
        mapping={'청도군':('restricted-rice',59),
                 '완도군':('restricted-rice-basket',28)}
        ledger=json.loads((Path('docs/evidence/v51-county-restricted-fact-ownership-20261108.json')).read_text(encoding='utf-8'))
        facts={f['fact_id']:f for f in ledger['facts']}
        for county,(purpose,number) in mapping.items():
            with self.subTest(county=county,purpose=purpose):
                page=next(p for p in self.data['pages'] if p['county']==county)
                self.assertEqual(page['number'],number)
                self.assertEqual(page['purpose'],purpose)
                pool=json.loads(json.dumps(self.plan['purposePools'][purpose]))
                validate_restricted_ownership(purpose,pool)
                fact_id=RESTRICTED_FACT_OWNER[purpose]['fact_id']
                self.assertIn(fact_id,page['sellerVenueNotice']['factIds'])
                self.assertEqual(facts[fact_id]['source_url'],page['sellerVenueNotice']['sourceUrl'])
                self.assertEqual(facts[fact_id]['region_scope'],[county])
                self.assertEqual(facts[fact_id]['verification_status'],'confirmed')
                self.assertEqual(facts[fact_id]['facility_scope'],
                    'all funeral venues within named county per seller notice')
                assembled=assemble(page,self.plan['purposePools'],self.data['products'])
                self.assertNotIn('쌀화환',assembled['intro'])
                self.assertNotIn('바구니',assembled['intro'])
                choice=next(x for x in assembled['sections'] if x['slot']=='choice')
                self.assertEqual(listed_prices_in_text(choice['paragraph']),set())
                self.assertEqual(product_skus_in_text(choice['paragraph']),set())
                faq_text=' '.join(x['q']+' '+x['a'] for x in assembled['faq'])
                self.assertNotIn('판매처 공지',faq_text)
                self.assertNotIn('반입 형태',faq_text)
                html=(OUT/(str(number)+'.html')).read_text(encoding='utf-8')
                self.assertEqual(html.count('class="county-venue-notice"'),1)
                self.assertIn('data-product-sku="B054"',html)
                self.assertIn('https://fwith.co.kr/shop/item.php?it_id=B054',html)
                self.assertEqual(html.count('90,000원'),1,
                    'confirmed product price must be printed once in the card')
        # A purpose-scoped regression: the checker rejects a second copy of
        # the acceptance condition even when phrased outside the notice.
        for purpose in mapping.values():
            pool=json.loads(json.dumps(self.plan['purposePools'][purpose[0]]))
            pool['faqs'][0]['a']='판매처 공지에 따른 반입 형태를 다시 확인하세요.'
            with self.assertRaisesRegex(ValueError,'repeated'):
                validate_restricted_ownership(purpose[0],pool)


    def test_all_18_base_buyer_purposes_have_sku_cta_and_heading_contract(self):
        from scripts.county_copy_pools import INTENTS
        from scripts.build_county_trial_review_only import main as make, OUT
        make()
        expected={row[0] for row in INTENTS}
        self.assertEqual(len(expected),18)
        counties=[p for p in self.data['pages'] if p['pageType']=='county']
        self.assertEqual({p['purpose'] for p in counties if p['purpose'] in expected},expected)
        for purpose in sorted(expected):
            page=next(p for p in counties if p['purpose']==purpose)
            with self.subTest(purpose=purpose,page=page['number']):
                result=assemble(page,self.plan['purposePools'],self.data['products'])
                self.assertEqual(set(page['productSkus']),
                    set(self.plan['purposePools'][purpose]['productSkus']))
                self.assertEqual([x['slot'] for x in result['sections']],
                    ['choice','order','ribbon','verified-townships'])
                html=(OUT/(str(page['number'])+'.html')).read_text(encoding='utf-8')
                self.assertIn(page['title'].split(' | ',1)[-1].split('·상품 주문')[0],html)
                for sku in page['productSkus']:
                    self.assertIn('data-product-sku="'+sku+'"',html)
                    self.assertIn('https://fwith.co.kr/shop/item.php?it_id='+sku,html)
                self.assertIn('noindex,nofollow',html)
                self.assertNotIn('rel="canonical"',html)


    def test_all_purpose_fact_registry_faq_question_answer_contract(self):
        from scripts.county_fact_contract import (
            registry, faq_topic, answer_topic, bind_faq, check_page)
        facts=registry()
        pages=self.data['pages']
        self.assertEqual(len(pages),95)
        purposes={p['purpose'] for p in pages}
        self.assertEqual(set(self.plan['purposePools']),purposes | {'budget','venue','ribbon','province'})
        for page in pages:
            with self.subTest(page=page['number'],purpose=page['purpose']):
                pool=self.plan['purposePools'][page['purpose']]
                self.assertTrue(check_page(page,pool if False else self.plan['purposePools'],facts))
                for f in pool['faqs']:
                    self.assertEqual(f['customer_question'],f['q'])
                    self.assertIn(f['answer_kind'],('sourced_fact','buyer_guidance'))
                    self.assertEqual(f['output_slot'],'faq')
                    self.assertIn('answer_fact_ids',f)
                    self.assertEqual(f['answer_topic'],faq_topic(f['q']))
                    if f['answer_kind']=='sourced_fact':
                        self.assertTrue(f['answer_fact_ids'])
                    for fid in f['answer_fact_ids']:
                        self.assertIn(fid,facts)
                        self.assertIn('faq',facts[fid]['allowed_slots'])
        false_answer={'q':'거창군 오브제 리본에는 어떤 이름을 적나요?',
                      'a':'상품 상세에는 선택옵션 0개·추가옵션 0개로 표시됩니다. 고객센터에 문의해 주세요.'}
        with self.assertRaisesRegex(ValueError,'ribbon name question'):
            bind_faq('restricted-obje-거창군',false_answer,facts)
        false_fact={'q':'접수한 주문내역은 어디서 조회하나요?',
                    'a':'판매처 공지에 따르면 거창군에는 상품 배송이 보장됩니다.'}
        with self.assertRaisesRegex(ValueError,'factual claim'):
            bind_faq('restricted-obje-거창군',false_fact,facts)

if __name__=='__main__':
    unittest.main(verbosity=2)
