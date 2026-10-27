"""Home-only indexing is a dormant, evidence-gated release, not authorization.

These tests simulate positive evidence solely in memory. They never update
site.json, DNS, Cloudflare, IndexNow, Google, or Naver.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

from v5.config import ConfigError, ROOT, read_site
from v5.engine import build
from v5.audit import audit
from v5.service_model import read_service_site
from v5.service_markup import _head

class QuickskyHomeOnlyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual=read_site("quicksky")
        cls.site=cls.actual["site"]
        cls.source=ROOT/"sites"/"quicksky"

    @staticmethod
    def simulated_approved(site):
        permitted=deepcopy(site)
        permitted.update(
            homeIndexingApproved=True,
            homeIndexingScope="quicksky-home-1-20261027",
            homeBusinessFactsVerified=True,
            homeContentQualityApproved=True,
        )
        return permitted

    def test_real_source_stays_noindex_and_both_index_release_modes_blocked(self):
        self.assertFalse(self.site.get("homeIndexingApproved",False))
        self.assertFalse(self.site.get("homeBusinessFactsVerified",False))
        self.assertFalse(self.site.get("homeContentQualityApproved",False))
        self.assertFalse(self.site["publicIndexingApproved"])
        self.assertFalse(self.site["publishEnabled"])
        actual=_head(self.site,"빠른스카이 스카이차","미리보기","/")
        self.assertIn('name="robots" content="noindex,nofollow"',actual)
        self.assertNotIn('rel="canonical"',actual)
        with self.assertRaises(ConfigError):
            build("quicksky",mode="home-indexing")
        with self.assertRaises(ConfigError):
            build("quicksky",mode="public-indexing")

    def test_scope_fails_closed_when_any_essential_proof_is_missing(self):
        permitted=self.simulated_approved(self.site)
        self.assertEqual(len(read_service_site("quicksky",permitted,self.source)["pages"]),1733)
        for field in ("imageAssetsApproved","domainOwnershipVerified",
                      "homeIndexingApproved","homeBusinessFactsVerified",
                      "homeContentQualityApproved"):
            x=deepcopy(permitted);x[field]=False
            with self.subTest(field=field):
                with self.assertRaises(ConfigError):
                    read_service_site("quicksky",x,self.source)
        for field,value in (
            ("domain","https://quicksky.nalmada.com"),
            ("homeIndexingScope","quicksky-all-regions"),
            ("publicIndexingApproved",True),
            ("publishEnabled",True),
        ):
            x=deepcopy(permitted);x[field]=value
            with self.subTest(field=field):
                with self.assertRaises(ConfigError):
                    read_service_site("quicksky",x,self.source)

    def test_only_home_receives_index_canonical_when_evidence_is_simulated(self):
        site=self.simulated_approved(self.site)
        rendered_home=_head(site,"빠른스카이 스카이차","홈","/")
        rendered_region=_head(site,"서울 스카이차","지역","/2.html")
        rendered_404=_head(site,"찾을 수 없습니다","오류","/404.html",True)
        self.assertIn('<meta name="robots" content="index,follow">',rendered_home)
        self.assertIn('<link rel="canonical" href="https://quicksky.nalmada.net/">',rendered_home)
        for html in (rendered_region,rendered_404):
            self.assertIn('<meta name="robots" content="noindex,nofollow">',html)
            self.assertNotIn('rel="canonical"',html)

    def test_simulated_home_release_retains_every_regional_page_noindex(self):
        simulated_site=self.simulated_approved(self.site)
        data={**self.actual,"site":simulated_site}
        with tempfile.TemporaryDirectory(prefix="quicksky-home-qa-") as tmp:
            root=Path(tmp)
            with patch("v5.engine.read_site",return_value=data):
                result=build("quicksky",mode="home-indexing",
                             output=root/"dist",reports=root/"reports",
                             preserve_previous=False)
            dist=root/"dist"
            self.assertEqual(result["manifest"]["pageCount"],1733)
            self.assertEqual(result["manifest"]["mode"],"home-indexing")
            self.assertEqual(list((dist).glob("*.html")).__len__(),1734)
            self.assertFalse((dist/"indexnow-key.txt").exists())
            self.assertEqual((dist/"robots.txt").read_text().splitlines(),[
                "User-agent: *","Allow: /",
                "Sitemap: https://quicksky.nalmada.net/sitemap.xml"
            ])
            tree=ET.parse(dist/"sitemap.xml")
            ns="{http://www.sitemaps.org/schemas/sitemap/0.9}"
            locs=[x.text for x in tree.findall(".//"+ns+"loc")]
            self.assertEqual(locs,["https://quicksky.nalmada.net/"])
            all_pages=sorted(dist.glob("*.html"))
            for p in all_pages:
                html=p.read_text(encoding="utf-8")
                expected="index,follow" if p.name=="index.html" else "noindex,nofollow"
                self.assertIn('<meta name="robots" content="'+expected+'">',html,p.name)
                if p.name=="index.html":
                    self.assertEqual(html.count('<link rel="canonical" href="https://quicksky.nalmada.net/">'),1)
                else:
                    self.assertNotIn('rel="canonical"',html,p.name)
            self.assertEqual(result["audit"]["errors"],[])
            # A wrong sitemap must fail independent direct audit as well.
            (dist/"sitemap.xml").write_text(
                (dist/"sitemap.xml").read_text().replace(
                    "</urlset>","<url><loc>https://quicksky.nalmada.net/2.html</loc></url></urlset>"))
            # audit mode is deliberately explicit; this never touches live site.
            after=audit("quicksky",output=dist,write_report=False,release_mode="home-indexing")
            self.assertTrue(any("Home-only sitemap" in x for x in after["errors"]),after)

if __name__=="__main__":
    unittest.main()
