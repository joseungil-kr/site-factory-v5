"""Coverage of the isolated Daysky skycar phrase pool and 1% randomized QA.

This suite must never mutate the published Daysky 29 URLs.
"""
from __future__ import annotations
import json
import math
import unittest
from pathlib import Path

from v5.skycar_pool import (
    TARGET_SCORE, QA_SEED, ROOT, REGION_LEDGER, EXISTING_SITE,
    _page, audit_random_one_percent, body, candidates, load_pool
)

class DayskyDedicatedPoolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old, cls.generated, cls.pool = candidates()

    def test_pool_is_industry_specific_and_substantially_expanded(self):
        self.assertEqual(len(self.pool["topics"]), 8)
        self.assertEqual(len(self.pool["shared"]), 10)
        self.assertGreaterEqual(self.pool["sentenceCount"], 440)
        self.assertTrue(set(self.pool["topics"]) >= {
            "facade","signage","glass","painting","facility",
            "communication","hvac","advertising"})

    def test_preserves_29_existing_pages_and_previews_1707_regions_only(self):
        original=json.loads((EXISTING_SITE/"pages.json").read_text(encoding="utf-8"))
        self.assertEqual(self.old,original)
        self.assertEqual(len(self.old),29)
        self.assertEqual(len(self.generated),1707)
        self.assertEqual([p["number"] for p in self.generated],list(range(30,1737)))
        self.assertEqual(len({p["id"] for p in self.generated}),1707)
        self.assertEqual(len({p["region"] for p in self.generated}),1707)
        self.assertEqual(len({p["title"] for p in self.generated}),1707)
        self.assertEqual(len({body(p) for p in self.generated}),1707)
        self.assertEqual({len(p["sections"]) for p in self.generated},{5})
        self.assertEqual(set(p["searchKeyword"] for p in self.generated),{"스카이차"})
        self.assertEqual({len(p["serviceIds"]) for p in self.generated},{3})
        self.assertEqual(len({p["poolTopicId"] for p in self.generated}),8)
        self.assertTrue(all(len(body(p))>=1300 for p in self.generated))

    def test_no_fabricated_local_claims_or_customer_brand_leaks(self):
        forbidden=("영진","1844-0644","fwith","출동 보장",
                   "실제 완료한 작업","실제 시공한 현장")
        for page in self.generated:
            text=json.dumps(page,ensure_ascii=False)
            self.assertTrue("당일스카이" in text,page["id"])
            self.assertTrue("스카이차" in page["title"])
            for phrase in forbidden:
                self.assertNotIn(phrase,text,page["id"])

    def test_stable_regeneration_and_safe_counter_examples(self):
        first=self.generated[113]
        parent,dong=first["region"].rsplit(" ",1)
        regenerate=_page(parent,dong,first["number"],113,self.pool)
        self.assertEqual(first,regenerate)
        self.assertNotEqual(first,_page(parent,dong,first["number"],113,self.pool,variant=1))

    def test_seeded_random_one_percent_against_full_population(self):
        report=audit_random_one_percent(seed=QA_SEED)
        self.assertEqual(report["newUnpublishedCandidates"],1707)
        self.assertEqual(report["evaluatedTotalDocuments"],1736)
        self.assertEqual(report["sampleSize"],18)
        self.assertEqual(report["pairsCompared"],18*1735)
        self.assertEqual(report["exactDuplicateBodiesInPopulation"],0)
        self.assertEqual(report["provincePopulations"],{"서울":807,"경기":900})
        self.assertEqual(len(report["failingSamples"]),0,report["failingSamples"][:3])
        self.assertLess(report["worstSampleToPopulationScore"],TARGET_SCORE,report)
        self.assertTrue(report["passesSample"],report)

if __name__ == "__main__":
    unittest.main()
