"""3 intent-consistent ribbon page examples, same original article extraction."""
import json,hashlib,re,unittest
from pathlib import Path
from scripts.build_todayflower_ribbon_intent_pilot import audit,ROOTOUT,INTENT,ROLES,choose,BUYER_SITUATIONS,select_role
from scripts.audit_todayflower_semantic_gate import article,score,LIMIT
from v5.audit import grams

class RibbonIntentPilotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit()
        cls.rows=json.loads((ROOTOUT/"pilot-candidate-page-models.json").read_text(encoding="utf-8"))
        cls.ledger=json.loads((ROOTOUT/"research-evidence-copy.json").read_text(encoding="utf-8"))
        cls.source,cls.population,cls.originals=choose()

    def test_intent_and_non_cherrypicked_population(self):
        self.assertEqual(len(self.rows),3)
        self.assertEqual(self.report["chosenNumbers"][0],4582)
        self.assertEqual(self.report["chosenNumbers"][1:],sorted(self.report["chosenNumbers"][1:]))
        self.assertEqual([x["role"] for x in self.rows],list(ROLES))
        self.assertEqual([x["buyerSituation"] for x in self.rows],list(BUYER_SITUATIONS))
        self.assertEqual([select_role(x["buyerSituation"]) for x in self.rows],list(ROLES))
        for row in self.rows:
            rendered=(ROOTOUT/f'candidate-{row["number"]}.html').read_text(encoding="utf-8")
            self.assertIn(row["roleLabel"],rendered)
            self.assertNotIn("<strong>"+row["role"]+"</strong>",rendered)
            self.assertNotIn("search_index_excerpt;",rendered)
        with self.assertRaises(AssertionError):
            select_role({"senderType":"company","approvalOwner":"self","eventPurpose":"formal_event"})
        self.assertTrue(all(x["topic"]==INTENT for x in self.rows))
        self.assertEqual(self.report["crossPopulationPairs"],3*len(self.population))
        self.assertFalse(self.report["competitionRankingVerified"])
        self.assertFalse(self.report["notNationwideSolution"] is False)

    def test_exact_same_5gram_no_score_tampering(self):
        original_by_num={p["number"]:p for p in self.originals}
        for row,record in zip(self.rows,self.report["sourceToQuestionToHTML"]):
            o=original_by_num[row["number"]]
            real=score(grams(article(o)),grams(article(row)))
            self.assertAlmostEqual(real,record["originalToCandidateSimilarity"])
            self.assertEqual(record["intent"],INTENT)
            self.assertEqual(len(record["sourceQuestionsToHtmlSections"]),5)
        for pair in self.report["pairwise"]:
            a,b=pair["left"],pair["right"]
            src_a=original_by_num[a];src_b=original_by_num[b]
            self.assertAlmostEqual(pair["originalOriginal"],score(grams(article(src_a)),grams(article(src_b))))
            candidate={x["number"]:x for x in self.rows}
            self.assertAlmostEqual(pair["candidateCandidate"],score(grams(article(candidate[a])),grams(article(candidate[b]))))
        self.assertEqual(self.report["threshold"],LIMIT)

    def test_each_seller_cta_is_product_specific_and_honest(self):
        products={p["sku"]:p for p in self.source["products"]}
        for row in self.rows:
            sku=row["productSkus"][0]
            self.assertTrue(sku.startswith("C"))
            self.assertEqual(row["orderUrl"],products[sku]["orderUrl"])
            html=(ROOTOUT/f'candidate-{row["number"]}.html').read_text(encoding="utf-8")
            self.assertIn('data-cta-sku="'+sku+'"',html)
            self.assertIn('href="'+row["orderUrl"]+'"',html)
            self.assertEqual(html.count('data-copy="section-'),4)
            self.assertIn("현재 가격·재고·리본 길이",html)
            self.assertIn("noindex,nofollow",html)
            self.assertNotIn('rel="canonical"',html)
            original=ROOTOUT/f'original-{row["number"]}.html'
            self.assertTrue(original.is_file())
            self.assertIn("noindex,nofollow",original.read_text(encoding="utf-8"))
        self.assertEqual(len(list(ROOTOUT.glob("candidate-*.html"))),3)

    def test_source_to_questions_and_outcome_distinct(self):
        qs=self.ledger["questionToRules"]
        sources={x["id"] for x in self.ledger["sources"]}
        self.assertEqual(len(qs),5)
        self.assertTrue(all(set(q["basis"])<=sources for q in qs))
        self.assertEqual({x["role"] for x in self.rows},set(ROLES))
        self.assertEqual(self.report["utilityGates"]["manualEditorialApproved"],0)
        self.assertEqual(self.report["utilityGates"]["regionalSpecificFactsVerified"],0)
        a,b,c=self.rows
        self.assertNotEqual([x["heading"] for x in a["sections"]],[x["heading"] for x in b["sections"]])
        self.assertNotEqual([x["heading"] for x in b["sections"]],[x["heading"] for x in c["sections"]])

if __name__=="__main__":
    unittest.main()
