"""Guard region gap exports against mistakenly asserting dispatch or official codes."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from scripts.export_quicksky_region_evidence_gaps import export

class QuickskyRegionGapTest(unittest.TestCase):
    def test_export_only_unknown_verified_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)
            report=export(path)
            self.assertEqual(report["regionNameEntries"],1732)
            self.assertEqual(report["sourcePageCount"],1733)
            self.assertEqual(report["operatorAvailabilityEvidenceRecordsPresentInCurrentSource"],0)
            self.assertEqual(report["publicIndexingEligibleEstablishedByThisEvidenceExport"],0)
            with (path/"region-evidence-gaps.csv").open(encoding="utf-8-sig",newline="") as handle:
                rows=list(csv.DictReader(handle))
            self.assertEqual(len(rows),1732)
            self.assertEqual(rows[0]["pageNumber"],"2")
            self.assertEqual(rows[-1]["pageNumber"],"1733")
            self.assertEqual(len({x["pageId"] for x in rows}),1732)
            for x in rows:
                self.assertEqual(x["officialRegionType"],"UNVERIFIED")
                self.assertEqual(x["operatorServiceStatus"],"UNVERIFIED")
                self.assertEqual(x["bookingPolicy"],"UNVERIFIED")
                self.assertEqual(x["verifiedEquipmentModels"],"UNVERIFIED")
                self.assertEqual(x["publishedIndexingState"],"noindex")
            self.assertEqual(json.loads((path/"region-evidence-gaps-summary.json").read_text())["regionNameEntries"],1732)

if __name__=="__main__":
    unittest.main()
