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


    def test_exact_original_v5_5034_region_master(self):
        from pathlib import Path
        from hashlib import sha1, sha256
        import json
        base = Path(__file__).resolve().parents[1]
        path = base / "data/regions/nationwide_locality_candidates_5034.json"
        raw = path.read_bytes()
        # Original blob from feature/v52-wreath-region, not a reconstructed list.
        self.assertEqual(
            sha1((f"blob {len(raw)}" + chr(0)).encode() + raw).hexdigest(),
            "525eb4b5c9f9f046ce2bcbd96a3dcfb343be399d",
        )
        original = json.loads(raw)
        self.assertEqual(original["counts"], {
            "provinces": 17, "districts": 250, "localities": 5034,
            "parentMatchesV4": 3596, "parentNotMatchedV4": 1438,
            "plannedPages": 10336,
        })
        report = select_all_region_names(original, expected_count=5034)
        self.assertEqual((report["sourceRowCount"], report["includedRowCount"],
                          report["excludedRowCount"]), (5034, 5034, 0))
        self.assertEqual((report["sourceMatchedParentCount"],
                          report["sourceUnmatchedParentCount"]), (3596, 1438))
        self.assertEqual(len({x["regionName"] for x in report["records"]}), 5034)
        self.assertEqual(len({x["path"] for x in report["records"]}), 5034)
        for old, selected in zip(original["records"], report["records"]):
            self.assertEqual(selected["regionName"], " ".join(old[:3]))
            self.assertEqual(selected["sourcePartsAsRecorded"], old[:3])
            self.assertEqual(selected["sourceMatchFlagAsRecorded"], old[3])
            self.assertEqual(selected["parentMatchedAsRecorded"], bool(old[3]))
        self.assertEqual(len({x[0] for x in original["records"]}), 17)
        self.assertEqual(len({(x[0], x[1]) for x in original["records"]}), 250)

    def test_v4_official_reference_is_separate_not_a_replacement(self):
        from pathlib import Path
        from hashlib import sha1, sha256
        import json
        base = Path(__file__).resolve().parents[1] / "data/regions"
        path = base / "v4_official_parent_regions_20261022.json"
        raw = path.read_bytes()
        self.assertEqual(
            sha1((f"blob {len(raw)}" + chr(0)).encode() + raw).hexdigest(),
            "13d43fc3f2492b29b1680858235fe0ac0cd10580",
        )
        self.assertEqual(len(json.loads(raw)["regions"]), 284)
        zip_path = base / "v4_official_legal_codes_20261022.zip"
        zip_bytes = zip_path.read_bytes()
        self.assertEqual(
            sha1((f"blob {len(zip_bytes)}" + chr(0)).encode() + zip_bytes).hexdigest(),
            "105e3084be32a116b7c3c8361edaacd0ea40b110",
        )
        self.assertEqual(sha256(zip_bytes).hexdigest(),
                         "44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd")

    def test_original_unmatched_flag_never_filters_or_changes_names(self):
        src = {"counts": {
            "localities": 2, "parentMatchesV4": 1, "parentNotMatchedV4": 1},
            "records": [
                ["강원도", "강릉시", "강동면", 0],
                ["충청북도", "충주시", "호암동", 1],
            ]}
        result = select_all_region_names(src, expected_count=2)
        self.assertEqual([r["regionName"] for r in result["records"]],
                         ["강원도 강릉시 강동면", "충청북도 충주시 호암동"])
        self.assertEqual(result["excludedRowCount"], 0)
        self.assertFalse(result["records"][0]["parentMatchedAsRecorded"])



if __name__ == "__main__":
    unittest.main()
