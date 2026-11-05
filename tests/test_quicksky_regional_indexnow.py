import unittest
import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from scripts.quicksky_regional_indexnow import submit
from scripts.quicksky_regional_indexnow import PUBLIC, regional_urls, validate_page
from v5.markup import url_path


class RegionalIndexNowTests(unittest.TestCase):
    def test_existing_or_uncertain_receipt_prevents_post(self):
        proof = Mock()
        key = 'a' * 32
        proof.read_text.return_value = json.dumps({'verifiedAt': datetime.now(timezone.utc).isoformat(),
            'urlList': [PUBLIC + url_path(n) for n in range(2, 1734)],
            'allPagesHttpCanonicalIndexVerified': True, 'homepageExcluded': True,
            'keyLocation': PUBLIC + '/' + key + '.txt'})
        receipt = Mock()
        receipt.open.side_effect = FileExistsError('Prior attempt receipt')
        with patch('scripts.quicksky_regional_indexnow.key_and_scope', return_value=key), \
             patch('scripts.quicksky_regional_indexnow.read', return_value=(200, {}, key.encode())), \
             patch('scripts.quicksky_regional_indexnow.urlopen') as post:
            with self.assertRaises(FileExistsError):
                submit(proof, receipt)
            post.assert_not_called()

    def test_scope_excludes_home_and_preserves_reserved_path(self):
        urls = [PUBLIC + url_path(n) for n in range(1, 1734)]
        def xml(items):
            return ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
                    ''.join('<url><loc>' + url + '</loc></url>' for url in items) + '</urlset>').encode()
        result = regional_urls(xml(urls))
        self.assertEqual(len(result), 1732)
        self.assertNotIn(PUBLIC + '/', result)
        self.assertIn(PUBLIC + '/page-404.html', result)
        for invalid in (urls + [urls[1]], urls[:-1], ['https://other.example/'] + urls[1:]):
            with self.assertRaises(AssertionError):
                regional_urls(xml(invalid))

    def test_blocks_noindex_and_wrong_canonical(self):
        url = PUBLIC + '/2.html'
        body = ('<link rel="canonical" href="' + url + '"><meta name="robots" content="index,follow">').encode()
        validate_page(url, 200, {}, body)
        for status, headers, content in ((404, {}, body), (200, {'X-Robots-Tag': 'noindex'}, body),
                                         (200, {}, body.replace(b'index,follow', b'noindex,follow')),
                                         (200, {}, body.replace(b'/2.html', b'/3.html'))):
            with self.assertRaises(AssertionError):
                validate_page(url, status, headers, content)
