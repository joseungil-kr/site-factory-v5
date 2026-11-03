import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from v5.rss import generate


class RSSTest(unittest.TestCase):
    def test_full_content_escaping_links_dates_and_private_filter(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "nested").mkdir()
            (root / "nested/index.html").write_text('<html><head><meta property="article:published_time" content="2026-01-02T03:00:00+09:00"></head><main><h1>A &amp; B</h1><p>Complete article end.</p><a href="../contact/">Call</a><img src="/x.png"></main></html>', encoding="utf-8")
            (root / "index.html").write_text('<html><head></head><main><h1>Undated</h1><p>Full undated content.</p></main></html>', encoding="utf-8")
            (root / "private.html").write_text('<meta name="robots" content="noindex"><main>Private</main>', encoding="utf-8")
            (root / "sitemap.xml").write_text('<urlset>' + ''.join('<url><loc>https://example.com' + p + '</loc></url>' for p in ('/', '/nested/', '/private.html')) + '</urlset>', encoding="utf-8")
            report = generate(root, 'https://example.com', 'A & B')
            self.assertEqual(report['items'], 2)
            self.assertEqual(report['datesOmitted'], 1)
            items = ET.parse(root / 'rss.xml').findall('./channel/item')
            self.assertEqual(items[0].findtext('title'), 'A & B')
            self.assertIn('https://example.com/contact/', items[0].findtext('description'))
            self.assertIn('https://example.com/x.png', items[0].findtext('description'))
            self.assertIn('Complete article end.', items[0].findtext('description'))
            self.assertIsNone(items[1].find('pubDate'))
            self.assertEqual(items[0].findtext('guid'), items[0].findtext('link'))
            self.assertEqual(items[0].findtext('description'), items[0].findtext('{http://purl.org/rss/1.0/modules/content/}encoded'))
            self.assertIn('application/rss+xml', (root / 'index.html').read_text())

    def test_body_scope_preserves_hero_title_and_intro_before_main(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'index.html').write_text('<html><head></head><body><section><h1>Actual article title</h1><p>Hero introduction.</p></section><main><p>Complete lower article.</p></main></body></html>',encoding='utf-8')
            (root/'sitemap.xml').write_text('<urlset><url><loc>https://example.com/</loc></url></urlset>',encoding='utf-8')
            generate(root,'https://example.com','Site',body_tag='body')
            item=ET.parse(root/'rss.xml').find('./channel/item')
            self.assertEqual(item.findtext('title'),'Actual article title')
            self.assertIn('Hero introduction.',item.findtext('description'))
            self.assertIn('Complete lower article.',item.findtext('description'))
