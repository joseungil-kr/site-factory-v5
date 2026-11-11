"""Validate the two-document alternative without claiming 49% content pass."""
import json, unittest
from pathlib import Path
from html.parser import HTMLParser
from scripts.build_todayflower_hub_prototype import generate, OUT

class HubArchitectureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=generate()
        cls.rows=json.loads((OUT/"regions-333.json").read_text(encoding="utf-8"))
        cls.hub=(OUT/"index.html").read_text(encoding="utf-8")
        cls.guide=(OUT/"buying-guide.html").read_text(encoding="utf-8")

    def test_real_333_data_rows_but_only_two_html_documents(self):
        self.assertEqual(len(self.rows),333)
        self.assertEqual(len({r["number"] for r in self.rows}),333)
        self.assertEqual(len({r["code"] for r in self.rows}),333)
        self.assertEqual(self.report["candidateHtmlDocuments"],2)
        self.assertEqual(len(list(OUT.glob("*.html"))),2)
        self.assertEqual(self.report["originalRegionalHtmlDocuments"],333)
        self.assertTrue(self.report["similarity49PercentNotApplicableToOneHub"])
        self.assertTrue(self.report["existingOriginalQualityStillFailed"])
        self.assertNotIn('<link rel="canonical"',self.hub)
        self.assertIn('noindex,nofollow',self.hub)

    def test_actual_facility_region_codes_and_regressions(self):
        for n in (186,3012,2412,2852):
            self.assertIn(n,{r["number"] for r in self.rows})
        for r in self.rows:
            self.assertEqual(r["intent"],"행사장 꽃 반입")
            self.assertFalse(r["currentAvailabilityVerified"])
            self.assertEqual(r["parent"]," ".join(r["name"].split()[:-1]))
            self.assertTrue(r["name"].startswith(r["province"]+" "))
            self.assertEqual(r["guideAnchor"],"intent-13")
            if r["verifiedPostedFee"]:
                fee=r["verifiedPostedFee"]
                self.assertEqual(fee["sku"],"B205")
                self.assertEqual(fee["observedAt"],"2026-11-11")
                self.assertFalse(fee["currentEffective"])
                self.assertEqual(fee["sourceURL"],"https://fwith.co.kr/shop/item.php?it_id=B205")
        self.assertEqual(self.report["unmappedRegionCount"]+self.report["withMatchingSkuFee"],333)

    def test_one_guide_owns_buyer_advice_and_links_resolve(self):
        self.assertIn('href="./buying-guide.html#intent-13"',self.hub)
        self.assertIn('id="intent-13"',self.guide)
        self.assertIn('행사장 꽃 반입',self.guide)
        self.assertNotIn("행사장 꽃 반입은 설치 위치와 반입 가능 시간",self.hub)
        self.assertEqual(self.guide.count('id="intent-'),16)
        self.assertTrue((OUT/"buying-guide.html").is_file())
        self.assertIn('id="region-search"',self.hub)
        self.assertIn('id="province"',self.hub)
        self.assertIn('id="results"',self.hub)
        self.assertIn('aria-live="polite"',self.hub)

    def test_deterministic_output_bytes(self):
        old={n:(OUT/n).read_bytes() for n in
             ("index.html","buying-guide.html","regions-333.json","prototype-report.json")}
        generate()
        self.assertEqual(old,{n:(OUT/n).read_bytes() for n in old})
if __name__=="__main__":unittest.main()
