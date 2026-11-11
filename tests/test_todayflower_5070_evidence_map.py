"""Coverage map regression: all 5070 URLs, exact source scope, reversible CSV."""
import csv
import json
import unittest

from scripts.audit_todayflower_5070_evidence_map import (
    FIELDS, REPORT_DIR, REQUIRED_REGRESSIONS, build_rows, write_outputs
)


class Todayflower5070CoverageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.ledger = build_rows()
        cls.report = write_outputs(cls.rows, cls.ledger)

    def test_complete_population_and_no_duplicate(self):
        rows=self.rows
        self.assertEqual(len(rows), 5070)
        self.assertEqual(len({r["number"] for r in rows}), 5070)
        self.assertEqual(len({r["urlPath"] for r in rows}), 5070)
        self.assertEqual(len({r["regionCode"] for r in rows}), 5070)
        self.assertEqual(rows[0]["urlPath"], "/")
        self.assertNotIn("/404.html", {r["urlPath"] for r in rows})
        self.assertEqual(self.report["verification"]["missingRows"],0)
        self.assertEqual(self.report["verification"]["duplicatedRows"],0)

    def test_role_scope_counts_are_only_candidates(self):
        self.assertEqual(sum(self.report["roles"].values()),5070)
        self.assertEqual(self.report["roles"]["evidence_detail"],0)
        self.assertEqual(self.report["eligibleDetailCountNotQualityPass"],0)
        self.assertFalse(self.report["qualityApproved"])
        for row in self.rows:
            self.assertFalse(row["currentServiceVerified"])
            self.assertFalse(row["liveStockVerified"])
            if row["proposedRole"]!="evidence_detail":
                self.assertEqual(row["matchedFactIds"],[])
                self.assertEqual(row["evidenceScope"],[])
                self.assertEqual(row["sourceUrls"],[])
                self.assertIsNone(row["verifiedFeeKRW"])
                self.assertIsNone(row["verifiedRateSku"])

    def test_regressions_and_no_sku_fee_transfer(self):
        nums={x["number"]:x for x in self.rows}
        for n in REQUIRED_REGRESSIONS:
            self.assertEqual(nums[n]["proposedRole"],"general_buying_guide")
            self.assertEqual(nums[n]["matchedFactIds"],[])
            self.assertEqual(nums[n]["contextFactIds"],[])
        related=[r for r in self.rows if "ansan-daebu-b101-fee" in r["contextFactIds"]]
        self.assertTrue(related)
        for row in related:
            self.assertNotIn("B101",row["listedSkus"])
            self.assertEqual(row["matchedFactIds"],[])
            self.assertIsNone(row["verifiedFeeKRW"])

    def test_csv_json_round_trip_and_stable_output(self):
        jpath=REPORT_DIR/"todayflower-5070-evidence-map.json"
        cpath=REPORT_DIR/"todayflower-5070-evidence-map.csv"
        data=json.loads(jpath.read_text(encoding="utf-8"))
        self.assertEqual(data["rows"],self.rows)
        with cpath.open(encoding="utf-8",newline="") as fh:
            csv_rows=list(csv.DictReader(fh))
        self.assertEqual(len(csv_rows),5070)
        self.assertEqual(set(csv_rows[0]),set(FIELDS))
        for row,csv_row in zip(self.rows,csv_rows):
            self.assertEqual(int(csv_row["number"]),row["number"])
            self.assertEqual(csv_row["urlPath"],row["urlPath"])
            self.assertEqual(csv_row["regionCode"],row["regionCode"])
            for name in ("matchedFactIds","contextFactIds","listedSkus","evidenceScope",
                         "sourceUrls","sourceObservedAt","sourcePublicationDate"):
                self.assertEqual(json.loads(csv_row[name]),row[name])
        original=jpath.read_bytes(),cpath.read_bytes()
        write_outputs(self.rows,self.ledger)
        self.assertEqual(original,(jpath.read_bytes(),cpath.read_bytes()))


if __name__=="__main__":
    unittest.main()
