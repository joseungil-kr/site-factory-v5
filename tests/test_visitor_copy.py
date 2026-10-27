import tempfile
import unittest
from pathlib import Path

from v5.visitor_copy import audit_html_tree, visible_copy_errors, require_clean_html


class VisitorCopyGateTest(unittest.TestCase):
    def test_internal_status_and_mockup_phrases_are_rejected(self):
        cases = ("보유 상품 사진 · 실제 상품 구성은 달라질 수 있습니다",
                 "축하화환 상품 정보 준비 중", "날마다꽃 디자인 검수용 페이지",
                 "원장 기재 주소(현행 정보 미검증)", "59,000원 참고가")
        for case in cases:
            with self.subTest(case=case):
                self.assertTrue(visible_copy_errors("<p>"+case+"</p>"))

    def test_accessibility_text_is_included(self):
        self.assertTrue(visible_copy_errors('<img alt="공통 상품 사진">'))

    def test_technical_seo_directives_are_preserved(self):
        page = ('<!doctype html><html><head>'
                '<meta name="robots" content="noindex,nofollow">'
                '<style>.notice:before{content:"검수용"}</style></head><body>'
                '<h1>근조화환 주문 가격안내</h1>'
                '<script>const message="상품 정보 준비 중";</script>'
                '<img alt="근조 3단 화환" src="/assets/images/B201.jpg">'
                '<a href="tel:18440644">전화 상담</a>'
                '</body></html>')
        self.assertEqual(visible_copy_errors(page), [])

    def test_full_tree_blocks_any_visible_status(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"index.html").write_text("<h1>날마다꽃</h1>",encoding="utf-8")
            (root/"2.html").write_text("<p>공사 중</p>",encoding="utf-8")
            self.assertIn("2.html",audit_html_tree(root))
            with self.assertRaises(ValueError):
                require_clean_html(root)
            (root/"2.html").write_text("<p>근조화환 주문 안내</p>",encoding="utf-8")
            require_clean_html(root)


if __name__ == "__main__":
    unittest.main()
