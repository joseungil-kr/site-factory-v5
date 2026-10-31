import unittest
from v5.config import read_site
from v5.service_markup import _head


class RegionalReleaseTests(unittest.TestCase):
    def test_bulk_home_retains_verification_but_regions_and_errors_do_not(self):
        site = dict(read_site('quicksky')['site'])
        site.update(homeIndexingApproved=False, publicIndexingApproved=True,
                    contentQualityApproved=True,
                    publicIndexingScope='quicksky-seoul-gyeonggi-1733-20261027')
        home = _head(site, '빠른스카이', '상담', '/')
        region = _head(site, '빠른스카이', '상담', '/2.html')
        error = _head(site, '빠른스카이', '없음', '/404.html', True)
        self.assertEqual(home.count('naver-site-verification'), 1)
        self.assertNotIn('naver-site-verification', region)
        self.assertNotIn('naver-site-verification', error)
        self.assertIn('index,follow', region)
        self.assertIn('href="https://quicksky.nalmada.net/2.html"', region)
        self.assertIn('noindex,nofollow', error)
        self.assertNotIn('rel="canonical"', error)
