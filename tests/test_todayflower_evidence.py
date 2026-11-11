"""Evidence-based Todayflower fixtures and 5070 URL identity regression."""
import unittest

from v5.config import read_site
from v5.todayflower_evidence import (
    load_ledger, decide_role, match_specific_facts, evidence_detail_payload, ROLES,
)


class EvidenceScopeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = load_ledger()
        cls.data = read_site("todayflower-nalmada")
        cls.by_number = {p["number"]: p for p in cls.data["pages"]}

    def test_total_url_numbers_original_pilot_and_noindex(self):
        pages=self.data["pages"]
        self.assertEqual(len(pages),5070)
        self.assertEqual(len(self.by_number),5070)
        self.assertNotIn(404,self.by_number)
        self.assertEqual([p["number"] for p in pages[:33]],list(range(1,34)))
        self.assertFalse(self.data["site"]["publishEnabled"])
        self.assertFalse(self.data["site"]["indexNow"]["enabled"])

    def test_exact_sku_prevents_fee_transfer(self):
        facts=match_specific_facts(region_code="4127311200",sku="B101",ledger=self.ledger)
        self.assertEqual([f["id"] for f in facts],["ansan-daebu-b101-fee"])
        for sku in ("B205","C200","C206","D144",None):
            with self.subTest(sku=sku):
                self.assertEqual(match_specific_facts(
                    region_code="4127311200",sku=sku,ledger=self.ledger), [])
        self.assertEqual(match_specific_facts(
            region_code="4127310100",sku="B101",ledger=self.ledger),[])

    def test_exact_facility_not_venue_free_region(self):
        correct=match_specific_facts(region_code="4127000000",
                                    facility="안산 빌라드지디 GD컨벤션 7층 그레이스켈리홀",
                                    ledger=self.ledger)
        self.assertEqual([f["id"] for f in correct],["ansan-gd-venue"])
        self.assertFalse(match_specific_facts(region_code="4127000000",ledger=self.ledger))
        self.assertFalse(match_specific_facts(region_code="4127310100",
                                             facility="안산 빌라드지디 GD컨벤션 7층 그레이스켈리홀",
                                             ledger=self.ledger))

    def test_2852_186_3012_2412_unsourced_and_unchanged_urls(self):
        for n in (186,3012,2412,2852):
            with self.subTest(number=n):
                p=self.by_number[n]
                self.assertEqual(p["pageRole"],"general_buying_guide")
                self.assertEqual(decide_role(region_code=p["legalCode"],
                                             selected_skus=p["productSkus"]),
                                 "general_buying_guide")
                self.assertIn(p["pageRole"], ROLES)
                self.assertTrue(p["id"].startswith("today-national-"))
        p=self.by_number[2852]
        body=" ".join(s["paragraph"] for s in p["sections"])
        self.assertNotIn("수원 호텔리츠컨벤션",body)
        self.assertNotIn("용인 평온의 숲",body)
        self.assertNotIn("30,000원",body)

    def test_detail_fixture_requires_exact_evidence(self):
        valid=evidence_detail_payload(
            region_code="4127000000",
            facility="안산 빌라드지디 GD컨벤션 7층 그레이스켈리홀",
            ledger=self.ledger)
        self.assertEqual(valid["role"],"evidence_detail")
        self.assertEqual(len(valid["facts"]),1)
        self.assertFalse(valid["facts"][0]["verifiedCurrent"])
        missing=evidence_detail_payload(region_code=self.by_number[2852]["legalCode"],
                                        ledger=self.ledger)
        self.assertEqual(missing["role"],"general_buying_guide")
        self.assertFalse(missing["facts"])


if __name__=="__main__":
    unittest.main()
