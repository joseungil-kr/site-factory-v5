"""Separate candidate structure assertions from unchanged official QA."""
from __future__ import annotations
import hashlib,json,re,unittest
from pathlib import Path
from v5.config import ROOT
from scripts.build_todayflower_role_candidate import build,OUT,REGRESSIONS

class TodayflowerCandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=build()
        cls.root=OUT/"candidate"

    def test_comparison_population_and_actual_html_are_preserved(self):
        r=self.report
        self.assertEqual(r["eventSameIntentPageCount"],333)
        self.assertEqual(r["original333ArticleSimilarity"]["pairs"],55278)
        self.assertEqual(r["original333ArticleSimilarity"]["overStrict49Percent"],4503)
        self.assertEqual(r["original333ActualVisibleHtmlSimilarity"]["pairs"],55278)
        self.assertEqual(r["candidate333ActualVisibleHtmlSimilarity"]["pairs"],55278)
        self.assertTrue(r["comparisonPopulationIdentical"])
        for n in REGRESSIONS:
            self.assertTrue((OUT/"original-actual-html"/f"{n}.html").is_file())
            self.assertTrue((self.root/"regional"/f"{n}.html").is_file())
        self.assertFalse(r["candidateEditorialApproved"])
        self.assertFalse(r["legacy5070QualityPassed"])

    def test_every_candidate_link_exists_and_source_files_unchanged(self):
        self.assertGreater(self.report["linksChecked"],333)
        for entry in self.report["sourceToCandidate"]:
            candidate=OUT/entry["htmlPath"]
            original=OUT/"original-actual-html"/f'{entry["number"]}.html'
            self.assertTrue(candidate.is_file())
            self.assertTrue(original.is_file())
            self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(),
                             entry["baselineSHA256"])
            txt=candidate.read_text(encoding="utf-8")
            self.assertIn("noindex,nofollow",txt)
            self.assertNotIn("rel=\"canonical\"",txt)
            self.assertIn("지역",txt)
            self.assertIn("공통 구매 안내",txt)

    def test_intent_guide_owns_advice_not_333_locality_pages(self):
        event=[r for r in self.report["sourceToCandidate"] if r["intent"]=="행사장 꽃 반입"]
        self.assertEqual(len(event),333)
        guide_href=event[0]["guide"]
        page=(OUT/event[0]["htmlPath"]).read_text(encoding="utf-8")
        self.assertIn(guide_href,page)
        guide=(self.root/"guides"/Path(guide_href).name).read_text(encoding="utf-8")
        self.assertIn("행사장 꽃 반입",guide)
        self.assertIn("수령",guide)
        for row in event:
            s=(OUT/row["htmlPath"]).read_text(encoding="utf-8")
            self.assertNotIn("행사장 꽃 반입은 설치 위치와 반입 가능 시간",s)
            self.assertIn(guide_href,s)

    def test_evidence_limited_no_fabricated_availability(self):
        matched=[r for r in self.report["sourceToCandidate"] if r["matchedFacts"]]
        self.assertEqual(len(matched),3)
        for r in matched:
            p=(OUT/r["htmlPath"]).read_text(encoding="utf-8")
            self.assertIn('data-evidence="B205-only"',p)
            self.assertIn("현재 주문 적용 및 배송 가능 여부 미확인",p)
            self.assertNotIn("C030·다른 SKU 요율에 대한 주장 아님.",p.replace("C030·다른 SKU 요율에 대한 주장 아님.",""))
        for n in REGRESSIONS:
            p=(self.root/"regional"/f"{n}.html").read_text(encoding="utf-8")
            self.assertNotIn("30,000원",p)
            self.assertIn("구체적인 시설 반입 조건",p)

if __name__=="__main__":
    unittest.main()
