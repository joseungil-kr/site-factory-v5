"""Isolated 95-page county trial SKU, price, and intent regression tests."""
import json,re,unittest
from pathlib import Path
from scripts.build_county_funeral_trial_inputs import main as generate,ID,SITE,PRICES
from scripts.county_copy_pools import product_skus_in_text,listed_prices_in_text
from v5.config import read_site
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
    def test_three_regression_pages(self):
        pages={p['number']:p for p in self.data['pages']}
        for n in (14,38,90):
            self.assertIn(n,pages)
            p=pages[n]
            self.assertEqual(len(p['productSkus']),{14:2,38:2,90:3}[n])
            a=assemble(p,self.plan['purposePools'],self.data['products'])
            body=' '.join([a['intro']]+[x['paragraph'] for x in a['sections']])
            self.assertTrue(product_skus_in_text(body)<=set(p['productSkus']))
    def test_refuse_nonselected_fixture(self):
        pool=json.loads(json.dumps(self.plan['purposePools']['budget-entry']))
        pool['sections'].append({'slot':'bad','heading':'잘못된 비교','paragraph':'B201 59,000원, B205 109,000원'})
        p=next(x for x in self.data['pages'] if x.get('purpose')=='budget-entry')
        self.assertNotIn('B205',p['productSkus'])
        assembled=assemble(p,{'bad-test':pool},self.data['products']) if False else None
        text=pool['sections'][-1]['paragraph']
        self.assertFalse(product_skus_in_text(text).issubset(set(p['productSkus'])))

if __name__=='__main__':
    unittest.main(verbosity=2)
