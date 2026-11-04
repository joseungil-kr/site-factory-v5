"""Prevent accidentally dropping candidate regions with unmatched parent names."""
import unittest
from v5.region_candidates import select_all_region_names


class RegionCandidatesTest(unittest.TestCase):
    def test_all_rows_including_unmatched_parent(self):
        data = {"regions": [
            {"name": "예시가동", "id": "r1", "parentMatched": True, "parent": "city"},
            {"name": "예시나동", "id": "r2", "parentMatched": False},
            {"name": "예시나동", "id": "r3", "parentMatched": None},
        ]}
        selected = select_all_region_names(data, expected_count=3)
        self.assertEqual((selected["sourceRowCount"], selected["includedRowCount"],
                          selected["excludedRowCount"]), (3, 3, 0))
        self.assertEqual([x["regionName"] for x in selected["records"]],
                         ["예시가동", "예시나동", "예시나동"])
        self.assertEqual(len(set(x["path"] for x in selected["records"])), 3)
        self.assertIsNone(selected["records"][1]["parentCodeAsRecorded"])

    def test_missing_name_is_not_silently_skipped(self):
        with self.assertRaisesRegex(ValueError, "Missing region name"):
            select_all_region_names([{"name": ""}], expected_count=1)

    def test_wrong_source_count_blocks_premature_complete_claim(self):
        with self.assertRaisesRegex(ValueError, "Full source not loaded"):
            select_all_region_names(["예시지역"], expected_count=5034)

    def test_strings_preserve_display_name(self):
        report = select_all_region_names(["안산시", "세종시 나성동"], expected_count=2)
        self.assertEqual([x["regionName"] for x in report["records"]],
                         ["안산시", "세종시 나성동"])


if __name__ == "__main__":
    unittest.main()
