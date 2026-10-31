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
        self.assertEqual(self.qa["pages"], 42)
        self.assertEqual(self.qa["launchIndustries"], 38)
        self.assertEqual(self.qa["researchIndustries"], 0)
        self.assertEqual(len(self.html), 43)

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
        self.assertEqual(self.qa["narrativePairsChecked"], 703)
        self.assertLess(self.qa["narrativeMaxChar5GramJaccard"], .49)
        self.assertEqual(self.qa["titleUnique"], 42)

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
        self.assertTrue(all(x["priority"] == "launch" for x in rows))
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
        self.assertEqual(price["minimumPages"], 10)
        self.assertEqual(price["minimumMonthlyKRW"], 10000)
        self.assertTrue(price["providerOwnedSubdomainIncluded"])
        self.assertTrue(price["providerPurchasedIndustryDomainCostsIncluded"])
        self.assertFalse(price["customerDomainRegistrationIncluded"])
        self.assertFalse(price["fullContractTermsConfirmed"])
        for field in ("vat", "contractTerm", "maintenanceEdits"):
            self.assertEqual(price[field], "UNCONFIRMED", field)
        dp = load("domain-policy.json")
        self.assertEqual(dp["offer"]["minPages"], 10)
        self.assertEqual(dp["offer"]["minMonthlyKRW"], 10000)
        self.assertTrue(dp["expansionPolicy"]["rootDomains"].startswith("add as many"))
        self.assertFalse(spec["domainProvision"]["rootDomainWhitelistFixed"])
        self.assertFalse(spec["domainProvision"]["domainRegistrationOrPurchaseExecuted"])
        self.assertEqual(spec["domainProvision"]["type"], "provider-managed-multi-domain-pool")
        roots = {x["root"]:x["status"] for x in dp["domainInventory"]}
        self.assertIn("nalmada.net", roots)
        self.assertEqual(roots["leak119.net"], "candidate_example_not_purchased_or_verified")
        self.assertEqual(roots["skycar24hr.com"], "candidate_example_not_purchased_or_verified")
        self.assertEqual(self.qa["billingCycle"], "monthly")
        self.assertTrue(self.qa["baseOfferApproved"])
        self.assertTrue(self.qa["domainAndHostingIncluded"])
        self.assertFalse(self.qa["pricingApproved"])
        self.assertEqual(self.qa["minimumPages"], 10)
        self.assertEqual(self.qa["minimumMonthlyKRW"], 10000)
        self.assertEqual(self.qa["domainModel"], "provider-managed-multi-industry-domains")
        self.assertFalse(self.qa["candidateIndustryDomainsPurchased"])
        self.assertFalse(self.qa["fullContractTermsConfirmed"])
        self.assertFalse(spec["publishPolicy"]["production"])
        self.assertFalse(spec["publishPolicy"]["indexNow"])
        self.assertFalse(self.qa["domainDeployed"])

    def test_monthly_rate_and_examples_are_visible_without_stale_disclaimers(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        pricing = (self.out / "guide/pricing/index.html").read_text(encoding="utf-8")
        faq = (self.out / "guide/faq/index.html").read_text(encoding="utf-8")
        self.assertIn("페이지당 월 1,000원부터", home)
        self.assertIn("월 10,000원", home)
        self.assertIn("최소 10페이지", home)
        self.assertIn("업종별 도메인 확보·관리", home)
        self.assertIn("서버비", home)
        self.assertIn("월 이용료", pricing)
        for pages in (10, 20, 30, 50, 100):
            amount = pages * 1000
            self.assertIn(f"{pages}페이지 × 월 1,000원", pricing)
            self.assertIn(f"월 {amount:,}원", pricing)
        self.assertIn("월 20,000원", home)
        self.assertIn("월 30,000원", home)
        self.assertIn("월 1,000원", faq)
        self.assertIn("최소 10페이지", faq)
        self.assertIn("도메인을 확보하고 관리해 드립니다", pricing)
        self.assertIn("도메인을 확보하고 관리해 드립니다", faq)
        for html_page in self.html:
            self.assertNotIn("한 장부터, 필요한 정보부터", html_page.read_text(encoding="utf-8"))
        for html_page in self.html:
            visible = html_page.read_text(encoding="utf-8")
            for internal in ("*.leak119.net", "*.skycar24hr.com",
                             "leak119.nalmada.net", "구매·배정 전",
                             "미배정", "Cloudflare", "worker.preview.js"):
                self.assertNotIn(internal, visible, (html_page, internal))
        for stale in ("월 청구액 또는 일회비용으로 확정된 금액이 아닙니다",
                      "1회비와 월 요금 구분", "실제 과금주기",
                      "과금 주기, 도메인·호스팅 포함 범위",
                      "최소 수량·부가세", "도메인 구입비·서버비 포함"):
            self.assertNotIn(stale, home + pricing + faq)
        for path in self.out.rglob("industry/*/index.html"):
            self.assertIn("페이지당 월 1,000원부터", path.read_text(encoding="utf-8"))

    def test_industry_extension_originality_and_preservation(self):
        source = load("copy-pool.json")["industry"]
        a = load("industry-expansion-a.json")["industry"]
        b = load("industry-expansion-b.json")["industry"]
        self.assertEqual(len(source), 10)
        self.assertEqual(len(a), 14)
        self.assertEqual(len(b), 14)
        self.assertEqual(len(set(source) | set(a) | set(b)), 38)
        self.assertEqual(self.qa["extensionIndustries"], 28)
        self.assertEqual(self.qa["originalIndustriesPreserved"], 10)
        for ident, article in {**a, **b}.items():
            with self.subTest(industry=ident):
                narrative = "".join(article[k] for k in
                     ("intro", "problem", "structure", "conversion", "difference"))
                self.assertGreaterEqual(len(narrative), 360)
                self.assertEqual(len(article["checklist"]), 4)
                self.assertNotIn("추가 수요/실제 업종 자료 검증 후", narrative)
                self.assertIn("홈페이지", article["title"])

    def test_generated_webp_files_match_source_and_provenance(self):
        import hashlib
        from scripts.build_webbuilder import webp_dimensions
        source = ROOT / "sites" / "webbuilder" / "illustrations" / "generated"
        dest = self.out / "assets" / "images"
        meta = __import__("json").loads((source / "provenance.json").read_text(encoding="utf-8"))
        records = {x["fileName"]: x for x in meta["assetRefs"]}
        self.assertEqual(len(records), 5)
        self.assertEqual({x.name for x in dest.glob("*.webp")}, set(records))
        self.assertEqual(list(dest.glob("*.svg")), [])
        self.assertEqual(self.qa["imageFiles"], 5)
        self.assertGreater(self.qa["imageReferences"], 50)
        self.assertIn("generated-raster-WebP", self.qa["imagesSource"])
        all_html = "\\n".join(x.read_text(encoding="utf-8") for x in self.html)
        for name, info in records.items():
            with self.subTest(filename=name):
                b = (dest / name).read_bytes()
                self.assertEqual((source / name).read_bytes(), b)
                self.assertEqual(hashlib.sha256(b).hexdigest(), info["sha256"])
                self.assertEqual(len(b), info["bytes"])
                self.assertEqual(webp_dimensions(b), (info["width"], info["height"]))
                self.assertGreaterEqual(info["width"], 768)
                self.assertIn("/assets/images/" + name, all_html)

    def test_virtual_example_disclosure_and_image_review_ledger(self):
        data = (self.out / "guide" / "pricing" / "index.html").read_text(encoding="utf-8")
        self.assertIn("가상 홈페이지 화면 예시이며 실제 고객 작업 사례가 아닙니다", data)
        source = ROOT / "sites" / "webbuilder" / "illustrations" / "generated"
        import json
        manifest = json.loads((source / "provenance.json").read_text(encoding="utf-8"))
        fix = manifest["visualCorrection"]
        self.assertEqual(set(fix["editedFiles"]),
                         {"industry-services.webp","mobile-contact.webp","managed-domain.webp"})
        self.assertEqual(len(fix["sourcePaths"]),3)
        self.assertIn("not independently verified",fix["rightsEvidenceStatus"])
        self.assertTrue(fix["noRelease"])

    def test_all_38_sectors_are_discoverable_and_related(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertEqual(home.count('class="industry-card"'), 38)
        self.assertEqual(home.count('class="industry-group"'), 7)
        for id in ("waterproof", "skycar", "watertank", "quick", "doorlock"):
            self.assertIn('/industry/' + id + '/', home)
            doc = (self.out / "industry" / id / "index.html").read_text(encoding="utf-8")
            self.assertIn('class="related-links"', doc)
            self.assertIn("페이지당 월 1,000원부터", doc)
        self.assertIn("webbuilder-hero.webp", home)

    def test_original_body_paragraph_is_not_repeated_as_hero(self):
        corpus = {**load("copy-pool.json")["industry"],
                  **load("industry-expansion-a.json")["industry"],
                  **load("industry-expansion-b.json")["industry"]}
        for ident, article in corpus.items():
            with self.subTest(industry=ident):
                page = (self.out / "industry" / ident / "index.html").read_text(encoding="utf-8")
                self.assertEqual(page.count(article["intro"][:35]), 1,
                                 "Full section introduction must appear exactly once")

    def test_industry_source_is_not_customer_fake_service_ad(self):
        names = [x["id"] for x in load("keyword-pool.json")["industries"] if x["launch"]]
        self.assertEqual(len(names), len(set(names)))
        for sector in names:
            self.assertTrue((self.out / "industry" / sector / "index.html").exists())

if __name__ == "__main__":
    unittest.main()
