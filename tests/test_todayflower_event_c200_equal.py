"""Same-event / same-C200 / same-buyer truth-preserving control."""
import json,hashlib,unittest
from v5.config import read_site
from v5.audit import grams
from scripts.audit_todayflower_semantic_gate import article,score,LIMIT
from scripts.audit_todayflower_event_c200_equal import generate,OUT,REGIONS,CASE,SKU

class C200EquivalentTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=generate()
  cls.models=json.loads((OUT/"page-models.json").read_text(encoding="utf-8"))
  cls.trace=json.loads((OUT/"buyer-question-trace.json").read_text(encoding="utf-8"))
 def test_actual_unchanged_pair_and_truthful_gate(self):
  self.assertEqual(self.r["originalPopulationFixed"],333)
  self.assertEqual(self.r["originalExistingViolationsNotChanged"],4503)
  self.assertEqual(self.r["threshold"],LIMIT)
  self.assertGreater(self.r["original186_3012Similarity"],0.93)
  self.assertEqual(self.r["identicalBuyerC200CandidateSimilarity"],1.0)
  self.assertTrue(self.r["identicalBuyerContextStillFails49Percent"])
  self.assertEqual(self.r["independentLocalityHtmlApproved"],0)
  self.assertFalse(self.r["publicationApproved"])
 def test_same_context_and_c200_no_local_claim(self):
  self.assertEqual(len(self.models),2)
  self.assertEqual({p["number"] for p in self.models},set(REGIONS))
  self.assertEqual(self.models[0]["scenario"],self.models[1]["scenario"])
  self.assertEqual(self.models[0]["scenario"],CASE)
  self.assertEqual(self.models[0]["productSkus"],[SKU])
  self.assertEqual(self.models[1]["productSkus"],[SKU])
  self.assertEqual(article(self.models[0]),article(self.models[1]))
  self.assertEqual(score(grams(article(self.models[0])),grams(article(self.models[1]))),1.0)
  self.assertNotEqual(self.models[0]["region"],self.models[1]["region"])
  self.assertFalse(any(p["verifiedRegionalFacts"] for p in self.models))
 def test_question_to_rule_to_literal_html_and_valid_sku_link(self):
  self.assertEqual(len(self.trace),5)
  allowed={"venue_check","recipient_details","product_choice","ribbon_confirmation","checkout_hold"}
  self.assertEqual({q["poolSlot"] for q in self.trace},allowed)
  for q in self.trace:
   self.assertTrue(q["applicableToBothRegions"])
   self.assertFalse(q["verifiedLocalFact"])
   self.assertEqual(q["selectionCondition"],CASE)
   for model in self.models:
    page=(OUT/f'candidate-{model["number"]}.html').read_text(encoding="utf-8")
    self.assertIn(q["exactParagraph"],page)
    self.assertIn('data-article-slot="'+q["poolSlot"]+'"',page)
    self.assertIn('href="https://fwith.co.kr/shop/item.php?it_id=C200"',page)
    self.assertIn('noindex,nofollow',page)
    self.assertNotIn('rel="canonical"',page)
 def test_output_sha_reproducibility(self):
  for x in self.r["candidateControlFiles"]:
   self.assertEqual(hashlib.sha256((OUT/x["candidateHtml"]).read_bytes()).hexdigest(),x["sha256"])
  before={p.name:p.read_bytes() for p in OUT.iterdir() if p.is_file()}
  generate()
  self.assertEqual(before,{p.name:p.read_bytes() for p in OUT.iterdir() if p.is_file()})
 def test_source_limitations(self):
  self.assertEqual(self.r["competitionSourcesDirectlyFullyRead"],0)
  self.assertFalse(self.r["competitionRankVerified"])
  self.assertEqual(self.r["distinctRegionalBuyerDetailEvidence"],0)
  self.assertFalse(self.r["humanEditorialApproved"])

if __name__=="__main__":unittest.main()
