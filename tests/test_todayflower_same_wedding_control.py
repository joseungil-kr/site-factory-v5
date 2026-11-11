"""Real 186/3012 identical-situation control with no score/gate changes."""
import hashlib,json,unittest
from scripts.audit_todayflower_same_wedding_control import build,OUT
from scripts.audit_todayflower_semantic_gate import article,score,LIMIT
from scripts.build_todayflower_event_49pilot import CASES,make
from v5.config import read_site
from v5.audit import grams

class SameWeddingControlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=build()
    def test_identical_buyer_input_fails_same_original_gate(self):
        r=self.report
        self.assertEqual(r["originalViolationPair"],[186,3012])
        self.assertEqual(r["originalIntent"],"행사장 꽃 반입")
        self.assertEqual(r["sameBuyerContext"],"wedding")
        self.assertGreater(r["originalSameIntentScore"],0.93)
        self.assertAlmostEqual(r["differentSituationCandidateScore"],0.08100558659217877)
        self.assertGreater(r["sameSituationCandidateScore"],r["differentSituationCandidateScore"]+0.30)
        self.assertEqual(r["threshold"],0.49)
        self.assertTrue(r["sameSituationViolates49Percent"])
        self.assertIsNone(r["relativeEffect"]["verifiedRegionalSpecificityEffect"])
        self.assertEqual(r["verifiedLocalEventFacts"],0)
        self.assertFalse(r["editorialApproved"])
        self.assertFalse(r["publishApproved"])
    def test_identical_article_score_and_no_invented_region_fact(self):
        info=read_site("todayflower-nalmada")
        by={p["number"]:p for p in info["pages"]}
        catalog={p["sku"]:p for p in info["products"]}
        a=make(by[186],CASES[186],catalog)
        b=make(by[3012],CASES[186],catalog)
        actual=score(grams(article(a)),grams(article(b)))
        self.assertAlmostEqual(actual,self.report["sameSituationCandidateScore"])
        self.assertEqual(a["scenario"],b["scenario"])
        self.assertEqual(a["sections"],b["sections"])
        self.assertEqual(a["questions"],b["questions"])
        self.assertNotEqual(a["region"],b["region"])
        self.assertTrue(all(x["topic"]=="행사장 꽃 반입" for x in (a,b)))
    def test_html_bytes_links_and_rerun(self):
        for f in self.report["files"]:
            p=OUT/f["html"]
            self.assertTrue(p.exists())
            raw=p.read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),f["sha256"])
            content=raw.decode("utf-8")
            self.assertIn('noindex,nofollow',content)
            self.assertIn('href="'+f["orderUrl"]+'"',content)
            self.assertIn('data-cta-sku="'+f["sku"]+'"',content)
            self.assertNotIn('rel="canonical"',content)
            self.assertIn("해당 지역에 실제 이 행사가 열리거나",content)
        before={p.name:p.read_bytes() for p in OUT.iterdir() if p.is_file()}
        build()
        self.assertEqual(before,{p.name:p.read_bytes() for p in OUT.iterdir() if p.is_file()})

if __name__=="__main__":
    unittest.main()
