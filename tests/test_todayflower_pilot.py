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
        cls.pages = cls.d["pages"][:33]  # preserve reviewed Ansan pilot while national pages extend
        cls.products = cls.d["products"]
        cls.catalog = {p["sku"]: p for p in cls.products}

    def test_plan_scope_and_index_off(self):
        result = check_site(SITE)
        self.assertTrue(result["ready"], result["errors"])
        self.assertEqual(self.site["domain"], "https://todayflower.nalmada.net")
        self.assertFalse(self.site["publishEnabled"])
        self.assertFalse(self.site["indexNow"]["enabled"])
        self.assertFalse(self.site["analytics"]["enabled"])
        self.assertEqual([p["number"] for p in self.pages], list(range(1,34)))
        self.assertEqual([p["region"] for p in self.pages[:3]], [
            "경기도 안산시", "경기도 안산시 단원구",
            "경기도 안산시 단원구 고잔동"
        ])
        self.assertEqual(self.site["todayflowerPilot"]["regionCount"],5070)
        self.assertTrue(self.site["todayflowerPilot"]["previewOnly"])

    def test_original_three_reviewed_content_hashes_are_unchanged(self):
        from v5.engine import stable_hash
        frozen={
            1:"d953d6d3bb9656d38a40b96d72f6f143b7798458584480d47671d06b3426cf46",
            2:"0a009dbb94464ed4a947caa5e57d208cc9730db190192f38a6554f63a7502838",
            3:"a91608f863010dae2cc634125c1f2d8103adaa4a0ffc42a52b8d35e1ba24fb8e",
        }
        for page in self.pages[:3]:
            actual=stable_hash({
                "intro":page["intro"],"sections":page["sections"],
                "faq":page.get("faq",[]),"title":page["title"],
                "region":page["region"],"productSkus":page["productSkus"]
            })
            self.assertEqual(actual,frozen[page["number"]],page["id"])

    def test_30_official_legal_regions_and_no_unverified_admin_dongs(self):
        import json
        root=ROOT/"sites/todayflower-nalmada"
        data=json.loads((root/"ansan-legal-regions-evidence.json").read_text(encoding="utf-8"))
        regions=json.loads((root/"regions.json").read_text(encoding="utf-8"))
        spec=json.loads((root/"site-spec.json").read_text(encoding="utf-8"))
        self.assertEqual(spec["targetPageCount"],5070)
        self.assertEqual(data["archiveHash"],
            "44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd")
        legal=data["legalDongs"]
        self.assertEqual(len(legal),30)
        self.assertEqual(len({r["code"] for r in legal}),30)
        self.assertEqual(len({r["name"] for r in legal}),30)
        self.assertEqual(len(regions["regions"]),33)  # committed 33-row input ledger
        self.assertEqual(len(self.d["regions"]["regions"]),5070)  # runtime expanded inventory
        self.assertEqual(len(self.pages),33)
        by_name={r["name"]:r for r in regions["regions"]}
        for row in legal:
            self.assertEqual(by_name[row["name"]]["code"],row["code"])
            self.assertEqual(by_name[row["name"]]["level"],"legal-dong")
        self.assertEqual(by_name["경기도 안산시 단원구 고잔동"]["code"],"4127310100")
        self.assertEqual(by_name["경기도 안산시 상록구"]["code"],"4127100000")
        actual={p["region"] for p in self.pages}
        self.assertEqual(actual,{r["name"] for r in regions["regions"][:33]})
        self.assertEqual(len(self.pages[3:]),30)

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
        import hashlib
        import json
        spec=json.loads((ROOT/"sites/todayflower-nalmada/site-spec.json").read_text(encoding="utf-8"))
        image_meta=spec["images"]
        self.assertEqual(image_meta["countPerPage"],7)
        self.assertEqual(image_meta["aiEditorialCountPerPage"],5)
        self.assertEqual(image_meta["otherLocalEditorialCountPerPage"],2)
        self.assertEqual(image_meta["libraryAssetCount"],10)
        self.assertEqual(self.site["todayflowerPilot"]["editorialImages"],7)
        proof={v["path"].rsplit("/",1)[-1]:v for v in image_meta["provenance"]}
        for name in generated:
            payload=(ROOT/"assets/library/todayflower"/name).read_bytes()
            self.assertEqual(payload[:4],b"RIFF")
            self.assertEqual(payload[8:12],b"WEBP")
            self.assertEqual(payload[12:16],b"VP8 ")
            self.assertEqual(payload[23:26],b"\x9d\x01\x2a")
            original_width=int.from_bytes(payload[26:28],"little")&0x3fff
            original_height=int.from_bytes(payload[28:30],"little")&0x3fff
            self.assertEqual((original_width,original_height),(1448,1086),name)
            self.assertGreaterEqual(original_width,768)
            self.assertEqual(proof[name]["bytes"],len(payload))
            objhash=hashlib.sha1(b"blob "+str(len(payload)).encode()+b"\x00"+payload).hexdigest()
            self.assertEqual(objhash,proof[name]["gitBlobSHA1"])
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
                self.assertEqual(html.count('width="1448" height="1086"'),5)
                self.assertNotIn('width="96" height="141"',html)
                self.assertNotIn('width:96px',html)
                self.assertIn("grid-template-columns:repeat(6,minmax(0,1fr))",html)
                self.assertIn("grid-template-columns:minmax(0,1fr)",html)
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
            if p["number"]>=4:
                self.assertNotIn("을(를)",body)
                self.assertNotIn("최저가 보장",body)
                self.assertNotIn("당일배송 보장",body)

if __name__=="__main__":
    unittest.main()
