"""Site-specific regression QA for the flowershop national noindex preview."""
from __future__ import annotations

import unittest

from v5.config import ROOT, read_site
from v5.site_plan import check_site
from v5.flowershop_regions import current_regions, EXPECTED_TOTAL
from v5 import markup
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
        self.assertEqual(len(self.data["pages"]), 10137)
        self.assertEqual(self.data["pages"][-1]["number"], 10137)

    def test_nationwide_official_coverage_is_pinned(self):
        rows = current_regions(ROOT)
        self.assertEqual(len(rows), EXPECTED_TOTAL)
        self.assertEqual(len(set(r[0] for r in rows)), EXPECTED_TOTAL)
        self.assertEqual(len(set(r[1] for r in rows)), EXPECTED_TOTAL)
        self.assertEqual(self.data["regions"]["nationwideLegalDongCount"], EXPECTED_TOTAL)
        self.assertEqual(len(self.data["pages"]), 3 + EXPECTED_TOTAL * 2)
        self.assertEqual(self.data["pages"][3]["number"], 4)
        self.assertIn("꽃집 개업화분", self.data["pages"][3]["title"])
        self.assertIn("화환전문 꽃집", self.data["pages"][4]["title"])

    def test_product_groups_price_photo_and_order_sources(self):
        self.assertEqual(
            {g: sum(p["group"] == g for p in self.products.values())
             for g in ("plant", "celebration", "condolence")},
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
                self.assertTrue((ROOT / "assets/library/promotion-plant" / (sku.lower()+".jpg")).is_file())
                self.assertEqual(p["localImagePath"], "/assets/images/"+sku.lower()+".jpg")

    def test_representative_and_national_pages_render_real_cards(self):
        pages = self.data["pages"]
        self.assertEqual(len(pages[0]["productSkus"]), 6)
        self.assertEqual(pages[1]["productSkus"], ["D144", "D149", "C200"])
        self.assertEqual(pages[2]["productSkus"], ["C200", "C206", "B205"])
        for page in [pages[0],pages[1],pages[2],pages[3],pages[4],
                     pages[len(pages)//2],pages[-1]]:
            with self.subTest(number=page["number"]):
                renderer=markup.home if page["number"]==1 else markup.detail
                html=renderer(self.site,page,pages,self.data["products"],self.data["links"])
                self.assertIn('<meta name="robots" content="noindex,nofollow">',html)
                self.assertNotIn('rel="canonical"',html)
                self.assertIn("<h1>"+page["title"]+"</h1>",html)
                self.assertIn("<title>"+page["title"]+" | 꽃이랑</title>",html)
                self.assertEqual(visible_copy_errors(html),[])
                self.assertIn('object-fit:cover',html)
                self.assertIn('href="tel:18440644"',html)
                for sku in page["productSkus"]:
                    p=self.products[sku]
                    self.assertIn('src="'+p["localImagePath"]+'"',html)
                    self.assertIn('href="'+p["orderUrl"]+'"',html)
                    self.assertIn(f'{p["referencePrice"]:,}원',html)
                    self.assertIn('판매처 가격 확인일 '+p["referenceDate"],html)

    def test_national_pagination_has_seven_or_fewer_reachable_pages(self):
        pages=self.data["pages"]
        for idx in [0,1,2,3,4,143,2025,len(pages)//2,len(pages)-1]:
            page=pages[idx]
            html=markup.detail(self.site,page,pages,self.data["products"],self.data["links"]) if idx else markup.home(
                self.site,page,pages,self.data["products"],self.data["links"])
            self.assertIn('aria-current="page"',html)
            self.assertIn('class="fs-related-grid"',html)
            self.assertLessEqual(html.count('aria-label="번 페이지"'),7)
            self.assertEqual(visible_copy_errors(html),[])


if __name__ == "__main__":
    unittest.main()
