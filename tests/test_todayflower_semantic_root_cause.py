"""Source-exact semantic cause checks; no quality gate or threshold relaxation."""
import json
import unittest
from pathlib import Path

from scripts.audit_todayflower_semantic_root_cause import main,OUT,REGRESSIONS,LIMIT
from scripts.audit_todayflower_semantic_gate import article,score
from v5.audit import grams
from v5.config import read_site


class RootCauseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=main()
        cls.by={p["number"]:p for p in read_site("todayflower-nalmada")["pages"]}

    def test_same_original_population_and_failures(self):
        method=self.report["method"]
        self.assertEqual(method["populationPages"],333)
        self.assertEqual(method["pairs"],55278)
        self.assertEqual(method["unmodifiedOriginalViolations"],4503)
        self.assertEqual(method["nGram"],5)
        self.assertEqual(method["threshold"],0.49)
        self.assertEqual(method["maximum"][1:],[186,3012])
        for sample in self.report["representative"]:
            a,b=sample["left"],sample["right"]
            raw=score(grams(article(self.by[a])),grams(article(self.by[b])))
            self.assertAlmostEqual(raw,sample["original"]["score"])
        self.assertGreaterEqual(self.report["representative"][0]["original"]["score"],LIMIT)
        self.assertLess(self.report["representative"][1]["original"]["score"],LIMIT)

    def test_pool_attribution_is_not_fake_success(self):
        worst=self.report["representative"][0]
        self.assertGreater(worst["leftPoolSentencesFound"],0)
        self.assertGreater(worst["rightPoolSentencesFound"],0)
        self.assertIn("counterfactualAfterRemovingKnownPoolSentences",worst)
        self.assertTrue(worst["removedPoolSentencesForAnalysisOnly"])
        self.assertFalse(self.report["seoSeok"]["editorialApproved"])
        self.assertFalse(self.report["seoSeok"]["publishApproved"])

    def test_real_SeoSeok_html_and_claim_sources(self):
        block=self.report["seoSeok"]
        self.assertEqual(block["number"],4582)
        self.assertEqual(block["candidateClaimCount"],4)
        self.assertEqual(set(block["candidateSourceIds"]),{"S1","S2","S3","S4"})
        self.assertIn("서석장례식장",block["candidateBuyerSections"])
        self.assertIn("20,000원",block["candidateBuyerSections"])
        self.assertEqual(len(block["missingToCompleteBuyerDecision"]),5)
        self.assertIn("seller current checkout",block["sourceStatus"])
        self.assertFalse(block["editorialApproved"])
        p=OUT/"candidate-seoseok-4582.html"
        self.assertTrue(p.is_file())
        self.assertIn("noindex,nofollow",p.read_text(encoding="utf-8"))
        for n in REGRESSIONS:
            self.assertTrue((OUT/f"original-{n}.html").is_file())

    def test_candidate_only_rule_no_new_page_fabrication(self):
        rules=self.report["candidateRule"]
        self.assertEqual(rules["independentBuyerPagePublishable"],0)
        self.assertTrue(rules["noNationwideGeneratorModification"])
        self.assertEqual({r["number"] for r in rules["evaluated"]},{1039,4360,4582})
        self.assertEqual(set(p.name for p in OUT.glob("*.html")),
                         {f"original-{n}.html" for n in REGRESSIONS}|{"candidate-seoseok-4582.html"})
        gate=json.loads((OUT/"candidate-333-eligibility.json").read_text(encoding="utf-8"))
        self.assertEqual(gate["recordCount"],333)
        self.assertFalse(gate["qualityGatePassed"])
        self.assertEqual(len(gate["records"]),333)
        self.assertEqual(len({x["number"] for x in gate["records"]}),333)
        self.assertFalse(any(x["allowIndependentBuyerHtml"] for x in gate["records"]))
        self.assertFalse(any(x["mappedFactIds"] for x in gate["records"]))
        self.assertEqual(self.report["candidateRule"]["sameIntentStandaloneHtmlApproved"],0)
        saved={p.name:p.read_bytes() for p in OUT.iterdir() if p.is_file()}
        main()
        self.assertEqual(saved,{p.name:p.read_bytes() for p in OUT.iterdir() if p.is_file()})

if __name__=="__main__":
    unittest.main()
