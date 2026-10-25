"""Regression guard for customer-facing Daysky page content."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class DayskyCopyQuality(unittest.TestCase):
    def test_dong_urls_and_customer_facing_wording(self):
        pages = json.loads((ROOT / "sites/daysky/pages.json").read_text(encoding="utf-8"))
        self.assertEqual(len(pages), 29)
        self.assertEqual([page["number"] for page in pages], list(range(1, 30)))
        text = "\\n".join(json.dumps(page, ensure_ascii=False) for page in pages)
        for phrase in (
            "간판 설치·교체을 상담",
            "통신·전기설비 보조을 상담",
            "안전작업 조건를",
            "가상 상황",
            "영진",
            "1844-0644",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)
        self.assertIn("010-5322-1952", text)

if __name__ == "__main__":
    unittest.main()
