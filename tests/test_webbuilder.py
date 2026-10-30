"""Independent noindex-only webbuilder preview checks."""
from __future__ import annotations
import csv
import unittest
from scripts.build_webbuilder import ROOT, build, load

class WebbuilderPreviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qa = build()
        cls.out = ROOT / "dist" / "webbuilder"
        cls.report = ROOT / "reports" / "webbuilder"
        cls.html = sorted(cls.out.rglob("*.html"))

    def test_preflight_and_counts(self):
        from v5.site_plan import check_site
        self.assertTrue(check_site("webbuilder")["ready"])
        self.assertEqual(self.qa["pages"], 14)
        self.assertEqual(self.qa["launchIndustries"], 10)
        self.assertEqual(self.qa["researchIndustries"], 28)
        self.assertEqual(len(self.html), 15)

    def test_same_phone_and_footer_every_page(self):
        for path in self.html:
            data = path.read_text(encoding="utf-8")
            with self.subTest(file=str(path)):
                self.assertIn("010-2490-0555", data)
                self.assertIn("사업자 : 인터피아드", data)
                self.assertIn("https://interpiad.com", data)
                self.assertIn("tel:01024900555", data)

    def test_noindex_is_immutable(self):
        self.assertFalse((self.out / "sitemap.xml").exists())
        self.assertEqual((self.out / "robots.txt").read_text(), "User-agent: *\nDisallow: /\n")
        for path in self.html:
            text = path.read_text(encoding="utf-8")
            self.assertIn('content="noindex,nofollow,noarchive"', text)
            self.assertNotIn('rel="canonical"', text)

    def test_preview_not_unsupported_advertisement(self):
        forbidden = ("전국 최저가", "상위노출 100%", "검색 1위 보장",
                     "모든 시 전체 동 월 2~3만원 확정")
        for path in self.html:
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, (path, token))

    def test_industry_distinctness(self):
        self.assertEqual(self.qa["narrativePairsChecked"], 45)
        self.assertLess(self.qa["narrativeMaxChar5GramJaccard"], .49)
        self.assertEqual(self.qa["titleUnique"], 14)

    def test_links_and_copy(self):
        self.assertGreater(self.qa["linksChecked"], 100)
        self.assertEqual(self.qa["brokenLinks"], 0)
        self.assertGreaterEqual(len(load("copy-pool.json")["faq"]), 12)
        self.assertIn("사이트", (self.out/"guide/faq/index.html").read_text())

    def test_keyword_pool_export(self):
        with (self.report / "keyword-candidates.csv").open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(self.qa["keywordCandidates"], 494)
        self.assertEqual(len(rows), 494)
        self.assertEqual(sum(x["type"] == "buyer" for x in rows), 380)
        self.assertEqual(sum(x["type"] == "customer_example" for x in rows), 114)
        self.assertTrue(all(x["priority"] in ("launch", "research_only") for x in rows))
        self.assertTrue(all("{동}" not in x["keyword"] for x in rows if x["type"] == "buyer"))

    def test_commercial_terms_not_assumed(self):
        spec = load("site-spec.json")
        self.assertEqual(spec["pricing"]["billingCycle"], "UNCONFIRMED")
        self.assertFalse(spec["publishPolicy"]["production"])
        self.assertFalse(spec["publishPolicy"]["indexNow"])
        self.assertFalse(self.qa["domainDeployed"])
        self.assertFalse(self.qa["pricingApproved"])

    def test_industry_source_is_not_customer_fake_service_ad(self):
        names = [x["id"] for x in load("keyword-pool.json")["industries"] if x["launch"]]
        self.assertEqual(len(names), len(set(names)))
        for sector in names:
            self.assertTrue((self.out / "industry" / sector / "index.html").exists())

if __name__ == "__main__":
    unittest.main()
