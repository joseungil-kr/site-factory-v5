"""Strict originally failing 186/3012 event-intent experiment tests."""
import json,hashlib,unittest
from scripts.build_todayflower_event_49pilot import run,OUT,REGRESSIONS,INTENT,CASES
from scripts.audit_todayflower_semantic_gate import article,score,LIMIT
from v5.audit import grams
from v5.config import read_site

class EqualIntentTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.report=run()
  cls.models=json.loads((OUT/"candidate-models.json").read_text(encoding="utf-8"))
  cls.original={p["number"]:p for p in read_site("todayflower-nalmada")["pages"]}
 def test_unmodified_original_critical_failures(self):
  self.assertEqual(self.report["populationPreserved"],333)
  self.assertEqual(self.report["originalFullCorpusFailCountUnchanged"],4503)
  self.assertEqual(self.report["originalThreshold"],LIMIT)
  self.assertGreater(self.report["originalWorst186_3012"],0.93)
  self.assertEqual(self.report["crossCorpusPairs"],999)
  self.assertEqual({p["number"] for p in self.models},set(REGRESSIONS))
  self.assertEqual({p["scenario"] for p in self.models},{"wedding","performance","conference"})
  self.assertFalse(self.report["humanEditorialApproved"])
 def test_same_intent_qa_no_substitution(self):
  for p in self.models:
   self.assertEqual(self.original[p["number"]]["topic"],INTENT)
   self.assertEqual(p["topic"],INTENT)
   self.assertTrue(p["scenarioExplicitInput"])
   self.assertEqual(len(p["sections"]),4)
   self.assertFalse(p["currentInboundVerified"])
  for pair in self.report["candidatePairMetrics"]:
   n,m=pair["left"],pair["right"]
   a=self.original[n];b=self.original[m]
   self.assertAlmostEqual(pair["baselineSimilarity"],score(grams(article(a)),grams(article(b))))
   c=next(x for x in self.models if x["number"]==n)
   d=next(x for x in self.models if x["number"]==m)
   self.assertAlmostEqual(pair["candidateSimilarity"],score(grams(article(c)),grams(article(d))))
 def test_actual_html_sku_and_product_scope(self):
  site=read_site("todayflower-nalmada")
  products={p["sku"]:p for p in site["products"]}
  for p in self.models:
   sku=p["productSkus"][0]
   self.assertTrue(sku.startswith("C"))
   self.assertIn(sku,self.original[p["number"]]["productSkus"])
   self.assertEqual(p["orderUrl"],products[sku]["orderUrl"])
   html=(OUT/f'candidate-{p["number"]}.html').read_text(encoding="utf-8")
   self.assertIn('noindex,nofollow',html)
   self.assertNotIn('rel="canonical"',html)
   self.assertIn('data-cta-sku="'+sku+'"',html)
   self.assertIn('href="'+p["orderUrl"]+'"',html)
   self.assertIn("배송 가능성·재고",html)
   self.assertEqual(html.count('data-article-slot='),4)
   orig=OUT/f'original-{p["number"]}.html'
   self.assertTrue(orig.is_file())
   rec=next(r for r in self.report["candidateMapping"] if r["number"]==p["number"])
   self.assertEqual(hashlib.sha256(orig.read_bytes()).hexdigest(),rec["originalHtmlSHA256"])
   self.assertEqual(hashlib.sha256(html.encode()).hexdigest(),rec["candidateSHA256"])
 def test_source_constraints_and_reproducibility(self):
  self.assertFalse(self.report["sourceRankingVerified"])
  self.assertFalse(self.report["sourceDirectOpened"])
  self.assertFalse(self.report["publicReleaseApproved"])
  self.assertTrue(self.report["noUniqueRegionalServiceFacts"])
  orig={p.name:p.read_bytes() for p in OUT.iterdir() if p.is_file()}
  run()
  self.assertEqual(orig,{p.name:p.read_bytes() for p in OUT.iterdir() if p.is_file()})

if __name__=="__main__":unittest.main()
