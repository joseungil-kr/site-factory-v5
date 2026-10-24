import unittest
from v5.region_pages import _page,TOPICS
from v5 import markup

class RegionalScaleTests(unittest.TestCase):
    def test_two_intents_and_named_district(self):
        a=_page(['서울특별시 강남구','역삼동'],10,0,22)
        b=_page(['서울특별시 강남구','역삼동'],10,1,23)
        self.assertEqual(TOPICS,('축하화분','승진화분'))
        self.assertIn('서울 강남구 역삼동 축하화분',a['title'])
        self.assertIn('서울 강남구 역삼동 승진화분',b['title'])
        self.assertEqual(len(a['sections']),5)
        self.assertNotEqual(a['id'],b['id'])
        self.assertGreater(sum(len(s['paragraph']) for s in a['sections']),900)
    def test_number_404_is_not_error_asset(self):
        self.assertEqual(markup.filename(404),'page-404.html')
        self.assertEqual(markup.url_path(404),'/page-404.html')
        self.assertEqual(markup.filename(405),'405.html')
        pages=[{'number':n} for n in range(400,410)]
        self.assertIn('href="/page-404.html"',markup.render_pagination(pages,403))
