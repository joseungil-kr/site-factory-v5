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
            html=(home if p["number"]==1 else detail)({**site,"homeIndexingApproved":False},p,self.pages,self.data["services"],self.data["rates"])
            self.assertIn("noindex,nofollow",html)
            self.assertIn("빠른스카이",html)
            self.assertNotIn("<td>300,000원",html)
            self.assertIn("전화",html)
            self.assertNotIn("공사 중",html)
            self.assertNotIn("보유 상품 사진",html)

    def test_consult_only_page_does_not_promise_rate_table(self):
        from v5.service_markup import home,detail
        site=self.data["site"]
        front=home({**site,"homeIndexingApproved":False},self.pages[0],self.pages,self.data["services"],self.data["rates"])
        page=detail({**site,"homeIndexingApproved":False},self.pages[1],self.pages,self.data["services"],self.data["rates"])
        for text in (front,page):
            self.assertIn("비용 상담",text)
            self.assertNotIn("작업 요금표 보기",text)
            self.assertNotIn("기본 요금</h2>",text)
            self.assertNotIn("300,000원",text)
        self.assertIn("비용 상담 안내 보기",front)
        # Licensed photos are generic skycar worksites; no photo is represented
        # as a particular 1t/3.5t/5t model or as directly owned equipment.
        self.assertNotIn('class="equip-art"',front)
        self.assertIn('class="hero-art"',front)
        self.assertIn("스카이차 비용 상담 안내</h2>",front)
        self.assertIn("스카이차 비용 상담 안내</h2>",page)
        self.assertNotIn("<table",front)
        self.assertNotIn("<table",page)

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
        preview=_head({**self.data["site"],"homeIndexingApproved":False},"빠른스카이 스카이차","설명","/2.html")
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

    def test_all_twelve_topics_natural_intro_and_region_ledger(self):
        from v5.quicksky_pages import TOPICS
        seen={}
        for p in self.pages[1:]:
            seen.setdefault(p["poolTopicId"],p)
            self.assertIn(p["topic"]+" 관련 작업을 계획한다면",p["intro"],p["id"])
            self.assertNotIn(p["topic"]+"을 계획한다면",p["intro"],p["id"])
        self.assertEqual(set(seen),set(TOPICS))
        spec=json.loads((ROOT/"sites/quicksky/site-spec.json").read_text())
        self.assertIn("지역명 원장",spec["serviceScope"]["granularity"])
        self.assertEqual(spec["targetPageCount"],1733)
        self.assertEqual([p["number"] for p in self.pages],list(range(1,1734)))

    def test_daysky_existing_rates_unchanged_by_quicksky_consult_ui(self):
        daysky=read_site("daysky")
        site=daysky["site"]
        page=daysky["pages"][0]
        rendered=home(site,page,daysky["pages"],daysky["services"],daysky["rates"])
        self.assertIn("작업 요금표 보기",rendered)
        self.assertIn('class="equip-art"',rendered)
        self.assertIn("스카이차 기본 요금",rendered)
        self.assertIn("<table",rendered)
        self.assertIn("300,000원",rendered)
        self.assertNotIn("비용 상담 안내 보기",rendered)

    def test_independent_release_rights_quality_and_ownership_gates(self):
        from copy import deepcopy
        from v5.service_model import read_service_site
        from v5.config import ConfigError
        from v5.engine import build
        target=ROOT/"sites/quicksky"
        candidate=deepcopy(self.data["site"])
        candidate["homeIndexingApproved"]=False  # bulk-mode negative control is independent of approved home-only mode
        candidate.update(publicIndexingApproved=True,
                         publicIndexingScope="quicksky-seoul-gyeonggi-1733-20261027",
                         imageAssetsApproved=True,
                         contentQualityApproved=True,
                         domainOwnershipVerified=True)
        for gate in ("imageAssetsApproved","contentQualityApproved","domainOwnershipVerified"):
            without=deepcopy(candidate)
            without[gate]=False
            with self.subTest(gate=gate):
                with self.assertRaises(ConfigError):
                    read_service_site("quicksky",without,target)
        self.assertIs(read_service_site("quicksky",candidate,target)["site"]["publishEnabled"],False)
        with self.assertRaises(ConfigError):
            build("quicksky",mode="public-indexing")
        from v5.service_markup import _head
        actual=_head({**self.data["site"],"homeIndexingApproved":False},"빠른스카이 스카이차","정보","/2.html")
        self.assertIn('name="robots" content="noindex,nofollow"',actual)
        self.assertNotIn('rel="canonical"',actual)

    def test_image_owner_permission_exact_source_scope_and_local_hashes(self):
        import hashlib
        record=json.loads((ROOT/"docs/QUICKSKY_PHOTO_PERMISSION_20261027.json").read_text())
        provenance=json.loads((ROOT/"docs/DAYSKY_PHOTO_PROVENANCE.json").read_text())
        site=self.data["site"]
        self.assertEqual(record["ownerStatementOriginal"],"직접 받은 사진이다. 사용권 허락받음")
        self.assertEqual({s["sourceUrl"] for s in record["sources"]},{
            "https://skycar1day.com/images/yjsky_01.jpg",
            "https://skycar1day.com/images/yjsky_02.jpg"})
        self.assertEqual(len(record["sources"]),2)
        flattened={d["file"]:{"original":s["sourceUrl"],
              "sha":d["outputSHA256"],"crop":d["cropTopFraction"]}
              for s in record["sources"] for d in s["derived"]}
        self.assertEqual(set(flattened),set(site["imagePool"]))
        self.assertEqual(set(flattened),{p["file"] for p in provenance})
        for p in provenance:
            name=p["file"];q=flattened[name]
            self.assertEqual(q["original"],p["original"])
            self.assertEqual(q["sha"],p["output_sha256"])
            self.assertEqual(q["crop"],p["cropTopFraction"])
            actual=(ROOT/"assets/library/daysky"/name).read_bytes()
            self.assertEqual(hashlib.sha256(actual).hexdigest(),q["sha"])
        self.assertTrue(site["imageAssetsApproved"])
        self.assertFalse(site["publicIndexingApproved"])
        self.assertFalse(site.get("contentQualityApproved",False))

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
