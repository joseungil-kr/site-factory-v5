"""Isolated 95-page county trial SKU, price, and intent regression tests."""
import json,re,unittest
from pathlib import Path
from scripts.build_county_funeral_trial_inputs import main as generate,ID,SITE,PRICES
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
                product_prices={PRICES[x] for x in selected}
                permitted={format(x,',')+'원' for x in product_prices}
                permitted|={format(abs(x-y),',')+'원' for x in product_prices for y in product_prices if x!=y}
                self.assertTrue(listed_prices_in_text(text)<=permitted,
                    f"{p['number']}: prose contains prices of products absent from cards")
                self.assertNotIn(a['intro'],[x['paragraph'] for x in a['sections']])
                self.assertNotIn('{townships}',text)
                self.assertIn(p['townships'],text)
                self.assertEqual(p['siteVariantPolicy'],'county-v51')
                self.assertGreater(int(p['townshipCount']),0)
                if len(selected)<4:
                    self.assertFalse(any(x in text for x in ('네 상품만 비교한','같은 등급으로 간주하지 않습니다')))
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
                expected=format(PRICES[sku],',')+'원'
                self.assertIn('data-product-sku="'+sku+'"',body,p['number'])
                self.assertIn(expected,body,p['number'])
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
            28:['B201','B205'],
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

if __name__=='__main__':
    unittest.main(verbosity=2)
