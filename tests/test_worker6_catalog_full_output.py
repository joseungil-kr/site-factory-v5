"""Exercise the real worker6 input generator and V5.1 HTML renderer, not hand-built cards."""
import copy
import json
import unittest
from pathlib import Path
from scripts.worker6_core_five_preview import generate_inputs
from v5.purpose_render import render
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'sites/promotion-gift-plants'
class CatalogFullOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=json.loads((SITE/'site-spec.json').read_text(encoding='utf-8'))
        cls.site=json.loads((SITE/'site.json').read_text(encoding='utf-8'))
        cls.seller=json.loads((SITE/'core-five-seller-evidence.json').read_text(encoding='utf-8'))
        cls.catalog=json.loads((SITE/'products.json').read_text(encoding='utf-8'))
    def _real_render(self,skus):
        selected=[copy.deepcopy(next(x for x in self.seller['sources'] if x['sku']==sku)) for sku in skus]
        spec,pages,regions,site=generate_inputs({'sources':selected},self.spec,self.site)
        products=[copy.deepcopy(next(x for x in self.catalog if x['sku']==sku)) for sku in skus]
        outputs={}
        for page in pages:
            outputs[page['number']]=render(site,page,pages,products,[],spec['purposePools'])
        return spec,pages,outputs
    def test_catalog_1_to_2_to_1_real_html(self):
        for skus in (['D144'],['D144','D026'],['D144']):
            with self.subTest(skus=skus):
                spec,pages,outputs=self._real_render(skus)
                count=len(skus)
                for number,html in outputs.items():
                    self.assertIn(f'상품 {count}종',html)
                    self.assertEqual(html.count('data-product-sku='),count)
                    for sku in skus:
                        product=next(x for x in self.catalog if x['sku']==sku)
                        self.assertIn(product['name'],html)
                        self.assertIn(f"{product['referencePrice']:,}원",html)
                        self.assertIn('it_id='+sku,html)
                    for sku in {'D144','D026'}-set(skus):
                        self.assertNotIn('it_id='+sku,html)
                        self.assertNotIn('data-product-sku="'+sku+'"',html)
                home=outputs[1]
                self.assertIn(f'판매처에서 확인한 상품 {count}종',home)
                self.assertIn(f'확인된 상품 {count}종',home)
                self.assertEqual(pages[0]['productSkus'],spec['purposePools']['home']['productSkus'])
    def test_no_source_section_render_is_unchanged(self):
        from v5 import markup
        page={'id':'legacy','sections':[{'heading':'안내','paragraph':'내용'}]}
        self.assertEqual(markup.article_body(page),'<article class="article-content" data-content-id="legacy"><section class="document-section" id="section-1"><span class="section-index">01</span><h2>안내</h2><p>내용</p></section></article>')
    def test_policy_link_and_legal_caveat_present(self):
        _,_,outputs=self._real_render(['D144'])
        for html in outputs.values():
            self.assertIn('de_change_content.jpg',html)
            self.assertIn('참고 원문 보기',html)
            self.assertIn('법정 권리',html)
if __name__=='__main__':
    unittest.main()
