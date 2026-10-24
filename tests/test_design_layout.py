"""The chosen landing/article design must not invent pages, photos or claims."""
import re
import unittest
from pathlib import Path
from v5.config import read_site
from v5.engine import build
from v5 import markup
ROOT=Path(__file__).resolve().parents[1]
SITE='ansan-promotion-plant'
class DesignLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=read_site(SITE)
        build(SITE,mode='preview')
        cls.out=ROOT/'dist'/SITE
    def test_index_is_landing_and_keeps_original_page_one_document(self):
        first=self.data['pages'][0]
        html=(self.out/'index.html').read_text(encoding='utf-8')
        self.assertIn('class="home-hero"',html)
        self.assertIn('data-content-id="'+first['id']+'"',html)
        for section in first['sections']:self.assertIn(section['paragraph'],html)
        self.assertIn('<meta name="robots" content="noindex,nofollow">',html)
        self.assertNotIn('rel="canonical"',html)
    def test_document_layout_does_not_invent_menu_pages(self):
        html=(self.out/'2.html').read_text(encoding='utf-8')
        self.assertIn('class="document-grid"',html)
        self.assertIn('<h2 id="products-heading">관련 식물 선물</h2>',html)
        self.assertNotIn('href="/상품안내.html"',html)
        self.assertNotIn('href="/후기.html"',html)
        self.assertEqual(len(re.findall('class="active"',html)),1)
        for section in self.data['pages'][1]['sections']:self.assertIn(section['paragraph'],html)
    def test_all_illustrations_free_of_location_and_product_names(self):
        for source in (ROOT/'assets/library/promotion-plant').glob('*.svg'):
            svg=source.read_text(encoding='utf-8')
            for term in ('<text','안산','승진화분','1844','꽃이랑','{상품명}'):self.assertNotIn(term,svg)
        for html_path in self.out.glob('*.html'):
            self.assertNotIn('<img src="https://fwith.co.kr/',html_path.read_text(encoding='utf-8'))
    def test_navigation_only_references_real_pages(self):
        site=self.data['site']
        for link in site['navigation']:
            target=link['href'].lstrip('/') or 'index.html'
            self.assertTrue((self.out/target).is_file(),link)
        self.assertEqual(markup.pagination(self.data['pages'],10),list(range(4,11)))
