"""Quicksky can be validated without approving release or touching Daysky."""
import json
import unittest
from pathlib import Path

from v5.config import read_site
from v5.quicksky_pages import TARGET_COUNT, audit_one_percent
from v5.site_plan import check_site
from v5.service_markup import home, detail

ROOT=Path(__file__).resolve().parents[1]

class QuickskyIsolatedSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=read_site("quicksky")
        cls.pages=cls.data["pages"]

    def test_proposed_complete_seoul_gyeonggi_inventory(self):
        self.assertEqual(len(self.pages),TARGET_COUNT)
        self.assertEqual([p["number"] for p in self.pages],list(range(1,TARGET_COUNT+1)))
        self.assertEqual(len({p["id"] for p in self.pages}),TARGET_COUNT)
        self.assertEqual(len({p["region"] for p in self.pages}),TARGET_COUNT)
        self.assertEqual(self.pages[-1]["number"],1733)

    def test_no_price_claim_or_cross_brand_leak(self):
        site=self.data["site"]
        self.assertEqual(site["domain"],"https://quicksky.nalmada.com")
        self.assertEqual(site["brand"],"빠른스카이")
        self.assertEqual(site["pricingPolicy"],"consult-only")
        self.assertFalse(site["publishEnabled"])
        self.assertFalse(site["publicIndexingApproved"])
        self.assertEqual(self.data["rates"]["plans"],[])
        self.assertEqual(site["imageLibrary"],"daysky")
        sample=[self.pages[0],self.pages[1],self.pages[245],self.pages[-1]]
        for p in sample:
            txt=json.dumps(p,ensure_ascii=False)
            self.assertNotIn("당일스카이",txt)
            self.assertNotIn("영진",txt)
            self.assertNotIn("1844-0644",txt)
            html=(home if p["number"]==1 else detail)(site,p,self.pages,self.data["services"],self.data["rates"])
            self.assertIn("noindex,nofollow",html)
            self.assertIn("빠른스카이",html)
            self.assertNotIn("<td>300,000원",html)
            self.assertIn("전화",html)
            self.assertNotIn("공사 중",html)
            self.assertNotIn("보유 상품 사진",html)

    def test_planning_gate_not_bypassed(self):
        result=check_site("quicksky")
        self.assertFalse(result["ready"])
        self.assertIn("plan not approved",result["errors"])

    def test_one_percent_sample_against_every_page(self):
        report=audit_one_percent(self.pages)
        self.assertEqual(report["population"],TARGET_COUNT)
        self.assertGreaterEqual(report["sample"],17)
        self.assertEqual(report["exactDuplicates"],0)
        self.assertTrue(report["passes"],report)

if __name__=="__main__":
    unittest.main()
