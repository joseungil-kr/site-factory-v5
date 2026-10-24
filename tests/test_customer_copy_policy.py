"""Keep customer-facing V5 pages free of safety boilerplate and sales caveats.

Quality/safety checks remain internal; this test concerns rendered prose only.
"""
import unittest
from v5.config import read_site
from v5 import markup

TARGET = 'seoul-gyeonggi-plants'
DISALLOWED = (
    '상품 정보 확인 안내',
    '상품 사진·가격·재고',
    '판매처 참고사진',
    '지난 가격 기록',
    '실제 결제 금액이 아닙니다',
    '실제 가격·배송 일정·구성',
    '확인해 주세요',
    '확인하세요',
    '주의해야',
    '보장되는 것은 아닙니다',
    '확약하는 문구는 아닙니다',
    '최종 금액은 판매처',
    '반드시 확인',
    '배송비·추가 선택 사항은 미포함',
)
class CleanCopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=read_site(TARGET)

    def assert_clean(self, rendered, where):
        for text in DISALLOWED:
            self.assertNotIn(text, rendered, where+': '+text)

    def test_global_header_footer_and_calculator_are_free_of_caveats(self):
        data=self.data
        site=data['site']
        self.assertNotIn('preview-banner',markup.header(site))
        self.assert_clean(markup.header(site), 'header')
        self.assert_clean(markup.footer(site,data['links']), 'footer')
        for item in data['special']:
            html=markup.special_page(site,item,data['products'],data['links'])
            self.assert_clean(html, 'special '+item['path'])
        home=markup.home(site,data['pages'][0],data['pages'],data['products'],data['links'])
        self.assert_clean(home, 'home')
        for number in (2,404,3465):
            page=data['pages'][number-1]
            self.assertEqual(page['number'],number)
            self.assert_clean(markup.detail(site,page,data['pages'],data['products'],data['links']),str(number))

    def test_every_generated_dong_page_has_no_cautionary_copy(self):
        data=self.data
        self.assertEqual(len(data['pages']),3465)
        self.assertEqual(len(set(p['id'] for p in data['pages'])),3465)
        for page in data['pages']:
            fields=[page['title'],page['intro'],page['topic']]
            fields += [x['heading']+' '+x['paragraph'] for x in page['sections']]
            fields += [x['q']+' '+x['a'] for x in page.get('faq',[])]
            self.assert_clean(' '.join(fields),str(page['number']))

    def test_preserve_naver_indexing_and_links(self):
        html=markup.home(self.data['site'],self.data['pages'][0],
                         self.data['pages'],self.data['products'],self.data['links'])
        self.assertIn('naver-site-verification',html)
        self.assertIn('<meta name="robots" content="index,follow">',html)
        self.assertIn('<link rel="canonical" href="https://plants.nalmada.net/">',html)
        self.assertIn('1844-0644',html)
