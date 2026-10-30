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

    def test_monthly_pricing_and_inclusions_confirmed_without_assuming_contract(self):
        spec = load("site-spec.json")
        price = spec["pricing"]
        self.assertEqual(price["headlinePriceKRW"], 1000)
        self.assertEqual(price["billingCycle"], "monthly")
        self.assertTrue(price["baseOfferConfirmed"])
        self.assertTrue(price["creationIncluded"])
        self.assertTrue(price["domainIncluded"])
        self.assertTrue(price["domainRegistrationIncluded"])
        self.assertTrue(price["hostingIncluded"])
        self.assertFalse(price["fullContractTermsConfirmed"])
        for field in ("minimumPages", "vat", "contractTerm", "domainRenewalPolicy",
                      "domainTypeLimit", "maintenanceEdits"):
            self.assertEqual(price[field], "UNCONFIRMED", field)
        self.assertEqual(self.qa["billingCycle"], "monthly")
        self.assertTrue(self.qa["baseOfferApproved"])
        self.assertTrue(self.qa["domainAndHostingIncluded"])
        self.assertFalse(self.qa["pricingApproved"])
        self.assertFalse(self.qa["fullContractTermsConfirmed"])
        self.assertFalse(spec["publishPolicy"]["production"])
        self.assertFalse(spec["publishPolicy"]["indexNow"])
        self.assertFalse(self.qa["domainDeployed"])

    def test_monthly_rate_and_examples_are_visible_without_stale_disclaimers(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        pricing = (self.out / "guide/pricing/index.html").read_text(encoding="utf-8")
        faq = (self.out / "guide/faq/index.html").read_text(encoding="utf-8")
        self.assertIn("페이지당 월 1,000원부터", home)
        self.assertIn("도메인 구입비", home)
        self.assertIn("서버비", home)
        self.assertIn("월 이용료", pricing)
        for pages in (10, 20, 30, 50, 100):
            amount = pages * 1000
            self.assertIn(f"{pages}페이지 × 월 1,000원", pricing)
            self.assertIn(f"월 {amount:,}원", pricing)
        self.assertIn("월 20,000원", home)
        self.assertIn("월 30,000원", home)
        self.assertIn("월 1,000원", faq)
        for stale in ("월 청구액 또는 일회비용으로 확정된 금액이 아닙니다",
                      "1회비와 월 요금 구분", "실제 과금주기",
                      "과금 주기, 도메인·호스팅 포함 범위"):
            self.assertNotIn(stale, home + pricing + faq)
        for path in self.out.rglob("industry/*/index.html"):
            self.assertIn("페이지당 월 1,000원부터", path.read_text(encoding="utf-8"))

    def test_industry_source_is_not_customer_fake_service_ad(self):
        names = [x["id"] for x in load("keyword-pool.json")["industries"] if x["launch"]]
        self.assertEqual(len(names), len(set(names)))
        for sector in names:
            self.assertTrue((self.out / "industry" / sector / "index.html").exists())

if __name__ == "__main__":
    unittest.main()
