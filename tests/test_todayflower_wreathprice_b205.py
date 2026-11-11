"""Pinned B205/C030 WreathPrice evidence must not leak across SKUs or regions."""
import csv
import json
import unittest

from scripts.extend_todayflower_5070_b205_evidence import (
    extend_rows, write_outputs, EXTRA
)
from v5.todayflower_wreathprice_evidence import load_pinned, map_posted_fee, scope_class
from scripts.build_todayflower_b205_samples import main as build_samples


class PinnedB205MapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.source = extend_rows()
        cls.summary = write_outputs(cls.rows, cls.source)

    def test_exact_pinned_original_and_scope(self):
        self.assertEqual(len(self.source["postedFees"]),20)
        self.assertEqual(self.source["retrievedOn"],"2026-11-11")
        self.assertIsNone(self.source["sellerPageLastUpdated"])
        by_code={r["regionCode"]:r for r in self.source["postedFees"]}
        self.assertEqual(scope_class(by_code["5172034000"]),"explicit_locality_row")
        self.assertEqual(scope_class(by_code["5123012500"]),"broader_or_ambiguous_seller_row")
        x=map_posted_fee(region_code="5172034000",
                         region_name=by_code["5172034000"]["regionName"],
                         selected_skus=["B205"],source=self.source)
        self.assertEqual(x["sku"],"B205")
        self.assertEqual(x["postedFeeKRW"],20000)
        self.assertIs(x["currentAvailabilityVerified"],False)
        self.assertFalse(map_posted_fee(region_code="5172034000",
                         region_name=by_code["5172034000"]["regionName"],
                         selected_skus=["C030"],source=self.source)["matchedIds"])
        self.assertFalse(map_posted_fee(region_code="5123012500",
                         region_name=by_code["5123012500"]["regionName"],
                         selected_skus=["B205"],source=self.source)["matchedIds"])
        with self.assertRaises(AssertionError):
            map_posted_fee(region_code="5172034000",
                           region_name="강원특별자치도 홍천군 다른면",
                           selected_skus=["B205"],source=self.source)

    def test_all_5070_unique_unknown_fields_and_no_other_sku(self):
        self.assertEqual(len(self.rows),5070)
        self.assertEqual(len({r["urlPath"] for r in self.rows}),5070)
        self.assertEqual(len({r["regionCode"] for r in self.rows}),5070)
        self.assertEqual(sum(self.summary["roles"].values()),5070)
        self.assertEqual(self.summary["roles"]["evidence_detail"],0)
        for row in self.rows:
            self.assertFalse(row["currentServiceVerified"])
            self.assertFalse(row["sellerPostedFeeCurrentEffective"])
            self.assertIsNone(row["verifiedFeeKRW"])
            self.assertIsNone(row["verifiedRateSku"])
            if row["wreathpriceMatchedIds"]:
                self.assertEqual(row["sellerPostedFeeSku"],"B205")
                self.assertIn("B205",row["listedSkus"])
                self.assertEqual(row["wreathpriceScopeKind"],"explicit_locality_row")
                self.assertEqual(row["sellerPostedFeeSourceObservedAt"],"2026-11-11")
                self.assertIsNone(row["sellerPostedFeePublishedAt"])
                self.assertEqual(row["proposedRole"],"regional_navigation")
            else:
                self.assertIsNone(row["sellerPostedFeeKRW"])
                self.assertIsNone(row["sellerPostedFeeSku"])

    def test_reproducible_json_csv_and_stable_hash(self):
        jp=EXTRA/"todayflower-5070-b205-extended.json"
        cp=EXTRA/"todayflower-5070-b205-extended.csv"
        parsed=json.loads(jp.read_text(encoding="utf-8"))
        self.assertEqual(len(parsed["rows"]),5070)
        with cp.open(encoding="utf-8",newline="") as f:
            csv_rows=list(csv.DictReader(f))
        self.assertEqual(len(csv_rows),5070)
        for j,c in zip(parsed["rows"],csv_rows):
            self.assertEqual(j["regionCode"],c["regionCode"])
            self.assertEqual(j["urlPath"],c["urlPath"])
            self.assertEqual(json.loads(c["wreathpriceMatchedIds"]),j["wreathpriceMatchedIds"])
        before=jp.read_bytes(),cp.read_bytes()
        write_outputs(self.rows,self.source)
        self.assertEqual(before,(jp.read_bytes(),cp.read_bytes()))

    def test_bounded_sample_html_never_asserts_delivery(self):
        build_samples()
        manifest=json.loads((EXTRA/"sample-html-manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest)
        for row in manifest:
            html=(EXTRA/row["file"]).read_text(encoding="utf-8")
            self.assertIn("noindex,nofollow",html)
            self.assertNotIn("배송이 가능합니다",html)
            if row["matched"]:
                self.assertIn("B205",html)
                self.assertIn("게시일 미상",html)
                self.assertIn(row["regionName"],html)
            else:
                self.assertNotIn("판매처가 게시한 금액",html)


if __name__=="__main__":
    unittest.main()
