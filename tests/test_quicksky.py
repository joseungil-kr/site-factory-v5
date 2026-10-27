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
        self.assertEqual(site["domain"],"https://quicksky.nalmada.net")
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

    def test_consult_only_page_does_not_promise_rate_table(self):
        from v5.service_markup import home,detail
        site=self.data["site"]
        front=home(site,self.pages[0],self.pages,self.data["services"],self.data["rates"])
        page=detail(site,self.pages[1],self.pages,self.data["services"],self.data["rates"])
        for text in (front,page):
            self.assertIn("비용 상담",text)
            self.assertNotIn("작업 요금표 보기",text)
            self.assertNotIn("기본 요금</h2>",text)
            self.assertNotIn("300,000원",text)
        self.assertIn("비용 상담 안내",front)

    def test_owner_approved_plan_for_preview(self):
        result=check_site("quicksky")
        self.assertTrue(result["ready"],result)
        self.assertTrue(result["approved"])
        self.assertFalse(self.data["site"]["publicIndexingApproved"])

    def test_indexing_requires_domain_image_rights_and_quality(self):
        from copy import deepcopy
        from v5.config import ConfigError
        from v5.service_model import read_service_site
        from v5.service_markup import _head
        from v5.indexnow import submission
        root=ROOT/"sites"/"quicksky"
        plan=deepcopy(self.data["site"])
        plan["publicIndexingApproved"]=True
        plan["publicIndexingScope"]="quicksky-seoul-gyeonggi-1733-20261027"
        with self.assertRaises(ConfigError):
            read_service_site("quicksky",plan,root)
        preview=_head(self.data["site"],"빠른스카이 스카이차","설명","/2.html")
        self.assertIn('name="robots" content="noindex,nofollow"',preview)
        self.assertNotIn('rel="canonical"',preview)
        candidate=deepcopy(plan)
        candidate["domain"]="https://quicksky.nalmada.com"
        candidate["imageAssetsApproved"]=True
        candidate["contentQualityApproved"]=True
        candidate["domainOwnershipVerified"]=True
        with self.assertRaises(ConfigError):
            read_service_site("quicksky",candidate,root)
        # Simulated all-positive flags demonstrate exact-host gating only;
        # actual published site keeps these flags FALSE until external proof.
        candidate["domain"]="https://quicksky.nalmada.net"
        idx=_head(candidate,"빠른스카이 스카이차","설명","/2.html")
        self.assertIn('name="robots" content="index,follow"',idx)
        self.assertIn('href="https://quicksky.nalmada.net/2.html"',idx)
        candidate["domain"]="https://quicksky.nalmada.com"
        denied=_head(candidate,"빠른스카이 스카이차","설명","/2.html")
        self.assertIn('name="robots" content="noindex,nofollow"',denied)
        with self.assertRaises(ConfigError):
            submission("quicksky","0"*32,submit=False)

    def test_one_percent_sample_against_every_page(self):
        report=audit_one_percent(self.pages)
        self.assertEqual(report["population"],TARGET_COUNT)
        self.assertGreaterEqual(report["sample"],17)
        self.assertEqual(report["exactDuplicates"],0)
        self.assertTrue(report["passes"],report)

    def test_cross_brand_sample_vs_existing_daysky_articles(self):
        """Check independent page text against all 1736 other-brand documents."""
        from math import ceil
        from random import Random
        from v5.skycar_pool import candidates as daysky_candidates, body as daysky_body
        from v5.quicksky_pages import grams, text_body, THRESHOLD
        original, generated, _=daysky_candidates()
        daysky=original+generated
        self.assertEqual(len(daysky),1736)
        other_fingerprints=[grams(daysky_body(p)) for p in daysky]
        provinces={
            "seoul":[p for p in self.pages[1:] if p["region"].startswith("서울특별시 ")],
            "gyeonggi":[p for p in self.pages[1:] if p["region"].startswith("경기도 ")]
        }
        random=Random(20261027)
        sample=[]
        for label,pages in provinces.items():
            sample += random.sample(pages,max(1,ceil(len(pages)*0.01)))
        worst=(0.0,"","")
        for p in sample:
            ours=grams(text_body(p))
            for j,other in enumerate(other_fingerprints):
                score=len(ours & other)/len(ours | other) if (ours | other) else 1.0
                if score>worst[0]:
                    worst=(score,p["region"],daysky[j]["region"])
        print("QUICKSKY_CROSS_BRAND_AUDIT",{
            "quickskySamples":len(sample),"dayskyPopulation":len(daysky),
            "thresholdExclusive":THRESHOLD,"maximumSimilarity":round(worst[0],6),
            "closestRegions":list(worst[1:])
        })
        self.assertLess(worst[0],THRESHOLD,worst)

if __name__=="__main__":
    unittest.main()
