"""Exact Naver verification, host restriction, and preview isolation."""
import unittest
import json
from v5 import markup
from v5.config import ROOT

SITE='seoul-gyeonggi-plants'
TOKEN='7e7acc99a89fa45de0dd0c5c454568ccca2e495b'
URL='https://plants.nalmada.net'

class PublicIndexingContract(unittest.TestCase):
    def setUp(self):
        self.site=json.loads((ROOT/'sites'/SITE/'site.json').read_text(encoding='utf-8'))

    def test_homepage_naver_meta_only_and_canonical(self):
        page=markup.head(self.site,'test','description','/','/assets/images/hero-florist.webp')
        self.assertIn('<meta name="naver-site-verification" content="'+TOKEN+'">',page)
        self.assertIn('<meta name="robots" content="index,follow">',page)
        self.assertIn('<link rel="canonical" href="'+URL+'/">',page)
        detail=markup.head(self.site,'test','description','/2.html','/assets/images/hero-florist.webp')
        self.assertNotIn('naver-site-verification',detail)
        self.assertIn('<link rel="canonical" href="'+URL+'/2.html">',detail)

    def test_404_still_noindex(self):
        page=markup.error_page(self.site,[])
        self.assertIn('<meta name="robots" content="noindex,nofollow">',page)
        self.assertNotIn('naver-site-verification',page)

    def test_preview_does_not_inherit_public_indexing(self):
        site={**self.site,'publicIndexingApproved':False}
        self.assertIn('noindex,nofollow',markup.head(site,'t','d','/','/assets/images/hero-florist.webp'))
        self.assertFalse(self.site['publishEnabled'])
        self.assertTrue(self.site['publicIndexingApproved'])
        self.assertEqual(self.site['domain'],URL)
