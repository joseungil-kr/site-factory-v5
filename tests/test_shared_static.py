import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from v5.config import ConfigError
from v5.shared_static import assemble, prepare, rewrite_assets
from v5.engine import build


def fixture(root, label):
    root.mkdir()
    (root / 'assets').mkdir()
    (root / 'assets/site.css').write_text('body{color:red}', encoding='utf-8')
    (root / 'assets/photo.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding='utf-8')
    (root / 'index.html').write_text(f'<meta name="robots" content="noindex"><link href="/assets/site.css"><h1>{label}</h1><a href="tel:18440644">전화</a><a href="https://fwith.co.kr/product/1">주문</a>', encoding='utf-8')
    (root / '2.html').write_text(label + ' detail', encoding='utf-8')
    (root / '배송.html').write_text(label + ' shipping', encoding='utf-8')
    (root / '404.html').write_text(label + ' missing', encoding='utf-8')
    (root / 'robots.txt').write_text('User-agent: *\nDisallow: /\n', encoding='utf-8')
    return root


class SharedStaticTests(unittest.TestCase):
    def test_external_order_urls_are_not_asset_rewritten(self):
        value = '<a href="https://fwith.co.kr/assets/order">order</a><img src="https://new.example.test/assets/photo.svg"><link href="/assets/site.css">'
        rewritten = rewrite_assets(value, 'new.example.test', '/_sfv5/assets/hash/')
        self.assertIn('https://fwith.co.kr/assets/order', rewritten)
        self.assertIn('src="/_sfv5/assets/hash/photo.svg"', rewritten)
        self.assertIn('href="/_sfv5/assets/hash/site.css"', rewritten)

    def test_existing_generator_output_survives_packaging_except_asset_prefix(self):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            output = base / 'built'
            result = build('ansan-promotion-plant', output=output, reports=base / 'reports', preserve_previous=False)
            self.assertEqual(result['audit']['errors'], [])
            assemble([('new-demo', 'new.example.test', output)], base / 'bundle')
            public = base / 'bundle/public'
            prefix = '/_sfv5/assets/' + next((public / '_sfv5/assets').iterdir()).name + '/'
            for source in output.glob('*.html'):
                packed = (public / '_sfv5/sites/new-demo' / source.name).read_text(encoding='utf-8')
                self.assertEqual(packed, source.read_text(encoding='utf-8').replace('/assets/', prefix))
                self.assertIn('noindex', packed)
                self.assertNotIn('rel="canonical"', packed)
            self.assertEqual((public / '_sfv5/sites/new-demo/robots.txt').read_bytes(), (output / 'robots.txt').read_bytes())
            self.assertFalse((public / '_sfv5/sites/new-demo/sitemap.xml').exists())

    def test_packs_hosts_without_rewriting_conversion_or_page_urls(self):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            a, b = fixture(base / 'a', 'Ansan'), fixture(base / 'b', 'Seoul')
            report = assemble([('ansan', 'ansanwreath.fwith.kr', a), ('seoul', 'seoulwreath.fwith.kr', b)], base / 'bundle')
            self.assertFalse(report['productionReady'])
            self.assertEqual(report['assetFileCount'], 12)  # Ten private files, two deduplicated public assets.
            config = json.loads((base / 'bundle/wrangler.json').read_text())
            self.assertFalse(config['workers_dev'])
            self.assertNotIn('routes', config)
            html = (base / 'bundle/public/_sfv5/sites/ansan/index.html').read_text(encoding='utf-8')
            self.assertIn('tel:18440644', html)
            self.assertIn('https://fwith.co.kr/product/1', html)
            self.assertIn('/_sfv5/assets/', html)
            self.assertNotIn('/assets/site.css', html)

    def test_rejects_duplicate_hosts_limits_and_output_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            src = fixture(base / 'a', 'A')
            entries = [('ansan', 'ansanwreath.fwith.kr', src)]
            with self.assertRaises(ConfigError):
                assemble(entries * 2, base / 'duplicate')
            with self.assertRaises(ConfigError):
                assemble(entries, base / 'limit', limit=1)
            with self.assertRaises(ConfigError):
                assemble(entries, base / 'hard-limit', limit=20001)
            self.assertFalse((base / 'limit').exists())
            with self.assertRaises(ConfigError):
                assemble(entries, src)

    def test_existing_site_rejected_before_build(self):
        with patch('v5.shared_static.read_site', return_value={'site': {'workerName': 'existing'}}), patch('v5.shared_static.build') as build:
            with self.assertRaises(ConfigError):
                prepare(['existing'], 'unused')
            build.assert_not_called()

    def test_unexpected_public_asset_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            src = fixture(base / 'a', 'A')
            (src / 'assets/private.html').write_text('secret')
            with self.assertRaises(ConfigError):
                assemble([('a', 'a.example.test', src)], base / 'bundle')

    def test_host_specific_css_rewrite_cannot_overwrite_deduplicated_assets(self):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            a, b = fixture(base / 'a', 'A'), fixture(base / 'b', 'B')
            for source in (a, b):
                (source / 'assets/site.css').write_text('body{background:url("https://a.example.test/assets/photo.svg")}', encoding='utf-8')
            assemble([('a', 'a.example.test', a), ('b', 'b.example.test', b)], base / 'bundle')
            css = list((base / 'bundle/public/_sfv5/assets').glob('*/site.css'))
            self.assertEqual(len(css), 2)
            contents = [p.read_text(encoding='utf-8') for p in css]
            self.assertEqual(sum('https://a.example.test/assets/' in text for text in contents), 1)
