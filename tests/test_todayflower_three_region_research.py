"""Strict three-region official fact grounding and no-deploy output QA."""
from __future__ import annotations
from html.parser import HTMLParser
import hashlib
import json
import re
import unittest

from scripts.build_todayflower_three_region_research import main,BASE,TARGET

class ThreeRegionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=main()
        cls.index=(BASE/"index.html").read_text(encoding="utf-8")
        cls.seoseok=(BASE/"seoseok-4582.html").read_text(encoding="utf-8")
        cls.ledger=json.loads((BASE/"claim-ledger.json").read_text(encoding="utf-8"))

    def test_just_one_real_detail_and_two_visible_holds(self):
        self.assertEqual(self.report["evidenceLedDetailCandidates"],1)
        self.assertEqual(self.report["heldForMissingFacilityEvidence"],2)
        self.assertEqual(set(map(int,self.report["originalHtml"])),set(TARGET))
        self.assertEqual(len(list(BASE.glob("*.html"))),2)
        self.assertIn('data-hold-region="1039"',self.index)
        self.assertIn('data-hold-region="4360"',self.index)
        self.assertNotIn('data-hold-region="4582"',self.index)
        self.assertFalse(self.report["editorialApproved"])
        self.assertEqual(self.report["currentDeliveryVerified"],0)
        self.assertEqual(self.report["merchantRatesCurrentVerified"],0)

    def test_each_fact_clause_has_source_and_only_one_sku_rate(self):
        claims={c["id"]:c for c in self.ledger["claims"]}
        sources={s["id"]:s for s in self.ledger["sources"]}
        self.assertEqual(set(claims),{"S1","S2","S3","S4"})
        self.assertEqual(set(re.findall(r'data-evidence-ids="(S[0-9]+)"',self.seoseok)),set(claims))
        for c in claims.values():
            self.assertIn(c["claim"],self.seoseok)
            self.assertTrue(all(src in sources for src in c["sources"]))
        self.assertIn("서석장례식장",self.seoseok)
        self.assertIn("풍암길2길 30",self.seoseok)
        self.assertIn("본관",self.seoseok)
        self.assertIn("별관",self.seoseok)
        self.assertIn("033-430-4558",self.seoseok)
        self.assertIn("20,000원",self.seoseok)
        self.assertIn("근조 특대 3단 화환 B205",self.seoseok)
        self.assertIn("판매처 게시일·변경일 미상",self.seoseok)
        self.assertNotIn("배송 확정",self.seoseok)
        self.assertNotIn("현재 배송 가능합니다",self.seoseok)

    def test_urls_and_exact_seller_venue_scope(self):
        refs=self.report["linksVerified"]
        self.assertTrue(refs)
        self.assertTrue(all(x["kind"] in ("local_exists","registered_official_source") for x in refs))
        self.assertTrue(any("hongcheon.go.kr" in x["href"] for x in refs))
        self.assertTrue(any("it_id=B205" in x["href"] for x in refs))
        self.assertIn('noindex,nofollow',self.seoseok)
        self.assertIn('noindex,nofollow',self.index)
        for name,digest in self.report["candidateFiles"].items():
            self.assertEqual(hashlib.sha256((BASE/name).read_bytes()).hexdigest(),digest)
        for n in TARGET:
            before=BASE/"original-html"/f"{n}.html"
            self.assertTrue(before.is_file())
            self.assertEqual(hashlib.sha256(before.read_bytes()).hexdigest(),
                             self.report["originalHtml"][n]["sha256"])

    def test_limited_official_munae_location_and_namwon_held(self):
        followup={x["id"]:x for x in self.ledger["followupClaimMap"]}
        self.assertEqual(set(followup),{"M1","M2"})
        self.assertEqual(followup["M1"]["regionNumber"],1039)
        self.assertEqual(followup["M2"]["regionNumber"],1039)
        official=next(s for s in self.ledger["sources"]
                      if s["id"]=="KFCPI_FUNERAL_FACILITIES_PDF_2025")
        self.assertIn("kfcpi.or.kr",official["url"])
        self.assertEqual(official["checkedOn"],"2026-11-11")
        self.assertIsNone(official["publicationDate"])
        self.assertFalse(official["currentOperationChecked"])
        self.assertTrue(self.report["officialFacilityProofDoesNotGrantDelivery"])
        self.assertTrue(self.report["namwonStillHeldForExactFacilityAddress"])
        self.assertEqual(self.report["additionalOfficialFacilityLocationFindings"],1)
        self.assertEqual(self.report["additionalOfficialFacilityClaims"],2)
        self.assertEqual(self.index.count('data-facility-location-only="true"'),1)
        for item in ("우수영장례식장","관광레저로 534-5","061-533-4440",
                     "현재 영업·인수 위치·외부화환 반입·B205 배송 가능 여부는 확인되지 않았습니다",
                     "URL 디렉터리 날짜는 2025-09-29"):
            self.assertIn(item,self.index)
        self.assertIn('data-evidence-ids="M1"',self.index)
        self.assertIn('data-evidence-ids="M2"',self.index)
        self.assertIn('data-hold-region="1039"',self.index)
        self.assertIn('data-hold-region="4360"',self.index)
        self.assertIn("본문 발행·갱신일은 확인되지 않았습니다",self.index)
        self.assertNotIn("우수영장례식장",self.seoseok)
        self.assertNotIn("우수영장례식장으로 배송 가능합니다",self.index)
        attempts=self.ledger["followupResearch"]["attempts"]
        self.assertEqual(len(attempts),5)
        self.assertEqual(self.ledger["followupResearch"]["publicationCandidateCount"],0)
        self.assertIn("no_exact_official_facility_row",
                      self.ledger["followupResearch"]["findings"][1]["editorialDecision"])

    def test_distinct_workflow_and_rerun_reproducibility(self):
        for x in ("1. 수령 시설부터 정확히 지정",
                  "2. 상품 선택과 비용을 구분",
                  "3. 현장 인계 조건은 별도로 확인"):
            self.assertIn(x,self.seoseok)
        self.assertNotIn("서석장례식장",self.index.replace(
            "서석면은 공식 시설 주소와 본관·별관 정보를 확인", ""))
        before={f:(BASE/f).read_bytes() for f in ("index.html","seoseok-4582.html","claim-ledger.json")}
        main()
        self.assertEqual(before,{f:(BASE/f).read_bytes() for f in before})

if __name__=="__main__":
    unittest.main()
