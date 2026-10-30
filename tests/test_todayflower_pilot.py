"""Narrow pilot QA: excludes V4, Flowershop and every other site."""
import unittest
from v5.config import read_site, ROOT
from v5.site_plan import check_site
from v5 import markup
from v5.audit import similarity
from v5.visitor_copy import visible_copy_errors

SITE = "todayflower-nalmada"
KINDS = {"bouquet", "plant", "celebration", "condolence"}

class TodayflowerPilotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = read_site(SITE)
        cls.site = cls.d["site"]
        cls.pages = cls.d["pages"]
        cls.products = cls.d["products"]
        cls.catalog = {p["sku"]: p for p in cls.products}

    def test_plan_scope_and_index_off(self):
        result = check_site(SITE)
        self.assertTrue(result["ready"], result["errors"])
        self.assertEqual(self.site["domain"], "https://todayflower.nalmada.net")
        self.assertFalse(self.site["publishEnabled"])
        self.assertFalse(self.site["indexNow"]["enabled"])
        self.assertFalse(self.site["analytics"]["enabled"])
        self.assertEqual([p["number"] for p in self.pages], [1,2,3])
        self.assertEqual([p["region"] for p in self.pages], [
            "경기도 안산시", "경기도 안산시 단원구",
            "경기도 안산시 단원구 고잔동"
        ])

    def test_seller_products_all_four_intents(self):
        self.assertEqual(len(self.products), 8)
        self.assertEqual({p["group"] for p in self.products}, KINDS)
        for p in self.products:
            with self.subTest(sku=p["sku"]):
                self.assertTrue(p["verifiedLive"])
                self.assertEqual(p["referenceDate"], "2026-10-30")
                self.assertGreater(p["referencePrice"], 0)
                self.assertEqual(
                    p["orderUrl"], "https://fwith.co.kr/shop/item.php?it_id="+p["sku"]
                )
                self.assertTrue(p["imageUrl"].startswith(
                    "https://fwith.co.kr/data/item/flower379/"+p["sku"]+"/"
                ))

    def test_ten_editorial_images_including_five_created_webps_each(self):
        self.assertEqual(len(self.site["imagePool"]), 10)
        generated=self.site["imagePool"][5:]
        self.assertEqual(generated,[
            "gift-bouquet.webp","opening-plant.webp","celebration-wreath.webp",
            "condolence-wreath.webp","flower-wrapping.webp"
        ])
        for name in generated:
            payload=(ROOT/"assets/library/todayflower"/name).read_bytes()
            self.assertTrue(payload.startswith(b"RIFF") and payload[8:12]==b"WEBP")
        for page in self.pages:
            with self.subTest(page=page["number"]):
                html=(markup.home if page["number"]==1 else markup.detail)(
                    self.site,page,self.pages,self.products,self.d["links"]
                )
                self.assertIn('<meta name="robots" content="noindex,nofollow">',html)
                self.assertNotIn('rel="canonical"',html)
                self.assertEqual(html.count('<h1>'),1)
                self.assertEqual(html.count('src="/assets/images/'),7)
                for name in generated:
                    self.assertEqual(html.count('src="/assets/images/'+name+'"'),1)
                self.assertIn("AI 연출 이미지",html)
                self.assertEqual(visible_copy_errors(html),[])
                self.assertIn('href="tel:18440644"',html)
                self.assertIn('object-fit:cover',html)
                self.assertEqual(len([s for s in page["sections"] if s["paragraph"]]),4)
                groups={self.catalog[sku]["group"] for sku in page["productSkus"]}
                self.assertTrue({"bouquet","plant","celebration","condolence"} <= groups)
                for sku in page["productSkus"]:
                    product=self.catalog[sku]
                    self.assertIn('href="'+product["orderUrl"]+'"',html)
                    self.assertIn(f'{product["referencePrice"]:,}원',html)
                    self.assertIn('src="'+product["imageUrl"]+'"',html)

    def test_distinct_region_copy_not_keyword_swaps(self):
        for i,a in enumerate(self.pages):
            text_a=" ".join([a["intro"]]+[s["paragraph"] for s in a["sections"]])
            for b in self.pages[i+1:]:
                text_b=" ".join([b["intro"]]+[s["paragraph"] for s in b["sections"]])
                with self.subTest(a=a["id"],b=b["id"]):
                    self.assertLess(similarity(text_a,text_b),0.49)

    def test_no_unsupported_delivery_guarantees(self):
        for p in self.pages:
            body=" ".join([p["intro"]]+[s["paragraph"] for s in p["sections"]])
            for forbidden in ("전국 3시간", "당일배송 보장", "무료 배송 확정","무조건 당일"):
                self.assertNotIn(forbidden,body)
            self.assertGreater(len(body),350)

if __name__=="__main__":
    unittest.main()
