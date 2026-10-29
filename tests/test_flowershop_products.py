"""Independent QA for the flowershop.nalmada.net representative noindex build."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from v5.config import read_site, ROOT
from v5.site_plan import check_site
from v5.engine import build
from v5.visitor_copy import visible_copy_errors


class FlowershopProductTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = read_site("flowershop-nalmada")
        cls.site = cls.data["site"]
        cls.products = {p["sku"]: p for p in cls.data["products"]}

    def test_domain_plan_and_preview_policy(self):
        plan = check_site("flowershop-nalmada")
        self.assertTrue(plan["ready"], plan["errors"])
        self.assertEqual(self.site["domain"], "https://flowershop.nalmada.net")
        self.assertFalse(self.site["publishEnabled"])
        self.assertFalse(self.site["indexNow"]["enabled"])
        self.assertFalse(self.site["analytics"]["enabled"])
        self.assertEqual(len(self.data["pages"]), 3)

    def test_three_real_catalogue_groups_with_dated_price_photo_and_order(self):
        self.assertEqual(
            {group: sum(p["group"] == group for p in self.products.values())
             for group in ("plant", "celebration", "condolence")},
            {"plant": 2, "celebration": 2, "condolence": 2},
        )
        for sku, p in self.products.items():
            with self.subTest(sku=sku):
                self.assertGreater(p["referencePrice"], 0)
                self.assertRegex(p["referenceDate"], r"^2026-10-\d\d$")
                self.assertEqual(
                    p["orderUrl"], "https://fwith.co.kr/shop/item.php?it_id=" + sku
                )
                self.assertTrue(p["imageUrl"].startswith("https://fwith.co.kr/"))
                self.assertIn("/" + sku + "/", p["imageUrl"])

    def test_pilot_product_selection_matches_page_intent(self):
        pages = {p["number"]: p for p in self.data["pages"]}
        self.assertEqual(len(pages[1]["productSkus"]), 6)
        self.assertIn("D144", pages[2]["productSkus"])
        self.assertIn("C200", pages[2]["productSkus"])
        self.assertIn("C200", pages[3]["productSkus"])
        self.assertIn("C206", pages[3]["productSkus"])
        self.assertIn("B205", pages[3]["productSkus"])

    def test_complete_noindex_html_build_and_visible_product_cards(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, reports = Path(tmp) / "preview", Path(tmp) / "reports"
            result = build(
                "flowershop-nalmada", output=out,
                reports=reports, mode="preview", preserve_previous=False
            )
            self.assertEqual(result["manifest"]["pageCount"], 3)
            self.assertEqual(result["audit"]["errors"], [])
            self.assertFalse((out / "sitemap.xml").exists())
            self.assertEqual(
                (out / "robots.txt").read_text(encoding="utf-8"),
                "User-agent: *\nDisallow: /\n",
            )
            for number, file in ((1, "index.html"), (2, "2.html"), (3, "3.html")):
                html = (out / file).read_text(encoding="utf-8")
                page = next(p for p in self.data["pages"] if p["number"] == number)
                with self.subTest(page=file):
                    self.assertIn('<meta name="robots" content="noindex,nofollow">', html)
                    self.assertNotIn('rel="canonical"', html)
                    self.assertIn("<h1>" + page["title"] + "</h1>", html)
                    self.assertIn("<title>" + page["title"] + " | 꽃이랑</title>", html)
                    self.assertEqual(visible_copy_errors(html), [])
                    self.assertIn('href="tel:18440644"', html)
                    for sku in page["productSkus"]:
                        product = self.products[sku]
                        self.assertIn('src="' + product["imageUrl"] + '"', html)
                        self.assertIn('href="' + product["orderUrl"] + '"', html)
                        self.assertIn(f'{product["referencePrice"]:,}원', html)
                        self.assertIn(
                            "판매처 가격 확인일 " + product["referenceDate"], html
                        )
            for file in ("index.html", "2.html", "3.html"):
                self.assertIn('object-fit:cover', (out / file).read_text(encoding="utf-8"))
            self.assertTrue((out / "배송안내.html").is_file())
            self.assertTrue((out / "404.html").is_file())
            self.assertTrue((reports / "manifest.json").is_file())
            self.assertTrue((reports / "audit.json").is_file())


if __name__ == "__main__":
    unittest.main()
