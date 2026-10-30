"""Bounded nationwide preview QA; retains the 33 independently reviewed pages.

All legal codes are from a 2026-10-22 fixed ZIP snapshot, not a fresh
government query. The existence of a legal code never proves fulfillment.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import re
import unittest

from v5.config import ROOT, read_json, read_site
from v5.audit import grams, similarity
from v5 import todayflower_regions as national
from v5 import markup

SITE="todayflower-nalmada"
BAD_SEMANTICS=re.compile(
    r"관련 꽃을 주문하실 계획|관련 꽃을 오늘 받을 수|"
    r"상황에서 꽃 종류와 상품을 어떻게 비교|"
    r"에 관한 선택이라면 필수 조건|"
    r"부재 관련 꽃|주소 비교 관련 꽃|배송비 관련 꽃"
)
BAD_GRAMMAR=re.compile(
    r"동라는|동로(?=\s|[,.!?]|$)|화분(?:와|를)(?=\s|[,.!?]|$)"
    r"|꽃다발(?:와|를)(?=\s|[,.!?]|$)|을\(를\)"
)
PROMISES=re.compile(
    r"무조건\s*당일배송|당일배송\s*보장|최저가\s*보장"
    r"|배송비\s*무료\s*확정|전국\s*3시간\s*이내"
)
SAMPLES=(1,2,3,4,28,29,33,34,35,100,403,405,730,2500,4060,5071)


class TodayflowerNationalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=read_site(SITE)
        cls.pages=cls.d["pages"]
        cls.original=read_json(ROOT/"sites"/SITE/"pages.json")
        cls.regions=cls.d["regions"]["regions"]
        cls.products={p["sku"]:p for p in cls.d["products"]}

    def test_pinned_legal_source_and_complete_numbering(self):
        self.assertEqual(len(self.original),33)
        self.assertEqual(len(self.pages),5070)
        self.assertEqual(len(self.regions),5070)
        self.assertEqual([p["number"] for p in self.pages],[*range(1,404),*range(405,5072)])
        self.assertNotIn(404,{p["number"] for p in self.pages})
        self.assertEqual(self.pages[:33],self.original)
        self.assertEqual(national.EXPECTED_DONG_COUNT,5067)
        archive=ROOT/national.ARCHIVE
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),national.ZIP_SHA256)
        legal=national.legal_regions(ROOT)
        self.assertEqual(len(legal),5067)
        self.assertEqual(len({code for code,_ in legal}),5067)
        self.assertEqual(len(self.pages[33:]),5037)
        self.assertEqual(self.pages[369]["number"],370)
        self.assertEqual(self.pages[369+34]["number"],405)
        original_codes={row["code"] for row in self.regions[:33] if row.get("level")=="legal-dong"}
        self.assertEqual(len(original_codes),30)
        self.assertEqual(len(set(self.regions[i]["name"] for i in range(5070))),5070)
        legal_codes={row["code"] for row in self.regions if row.get("level")=="legal-dong"}
        self.assertEqual(legal_codes,{code for code,_ in legal})
        self.assertFalse(self.d["site"]["publishEnabled"])
        self.assertFalse(self.d["site"]["indexNow"]["enabled"])
        self.assertTrue(self.d["site"]["todayflowerNational"]["previewOnly"])
        self.assertEqual(self.d["site"]["todayflowerNational"]["sourceAsOf"],"2026-10-22")

    def test_full_generated_pages_no_guarantees_or_unverified_local_shops(self):
        seen_ids=set()
        seen_articles=set()
        checked=0
        for page in self.pages:
            self.assertNotIn(page["id"],seen_ids)
            seen_ids.add(page["id"])
            self.assertEqual(len(page["sections"]),4)
            self.assertEqual(len(page["faq"]),3)
            self.assertTrue(page["productSkus"])
            for sku in page["productSkus"]:
                self.assertIn(sku,self.products)
            text=" ".join(
                [page["title"],page["intro"],page.get("sectionLead","")]
                +[s["heading"]+" "+s["paragraph"] for s in page["sections"]]
                +[f["q"]+" "+f["a"] for f in page["faq"]]
            )
            with self.subTest(n=page["number"]):
                self.assertNotRegex(text,BAD_SEMANTICS)
                self.assertNotRegex(text,BAD_GRAMMAR)
                self.assertNotRegex(text,PROMISES)
                self.assertNotIn("매장이 실제로",text)
                self.assertNotIn("지점 위치",text)
                self.assertIn("꽃배달 당일배송",page["title"])
                for section in page["sections"]:
                    self.assertTrue(section["paragraph"].endswith("."))
                for question in page["faq"]:
                    self.assertTrue(question["q"].endswith("?"))
                    self.assertTrue(question["a"].endswith("."))
            main=" ".join([page["intro"]]+[s["paragraph"] for s in page["sections"]])
            digest=hashlib.sha256(main.encode("utf-8")).hexdigest()
            self.assertNotIn(digest,seen_articles,page["number"])
            seen_articles.add(digest)
            checked+=1
        self.assertEqual(checked,5070)
        self.assertEqual(len(seen_articles),5070)

    def test_fixed_stratified_similarity_and_rendered_samples(self):
        # Same deterministic sample strategy as v5.audit; full-population
        # duplicate hashes are checked above but semantic review is limited.
        selected=sorted(self.pages,key=lambda p:hashlib.sha256(
            ("v5-dong-similarity-v1:"+p["id"]).encode("utf-8")).digest())[:51]
        self.assertEqual(len(selected),51)
        maximum=(0.0,None,None)
        count=0
        for i,a in enumerate(selected):
            body_a=" ".join([a["intro"]]+[s["paragraph"] for s in a["sections"]])
            for b in selected[i+1:]:
                body_b=" ".join([b["intro"]]+[s["paragraph"] for s in b["sections"]])
                score=similarity(body_a,body_b)
                maximum=max(maximum,(score,a["number"],b["number"]))
                self.assertLess(score,0.49,("sample",a["number"],b["number"],score))
                count+=1
        self.assertEqual(count,1275)
        for n in SAMPLES:
            p=next(p for p in self.pages if p["number"]==n)
            html=(markup.home if n==1 else markup.detail)(
                self.d["site"],p,self.pages,self.d["products"],self.d["links"])
            self.assertIn('<meta name="robots" content="noindex,nofollow">',html)
            self.assertNotIn('rel="canonical"',html)
            self.assertIn('word-break:keep-all',html)
            self.assertEqual(html.count('src="/assets/images/'),7)
            self.assertEqual(html.count('width="1448" height="1086"'),5)
            self.assertIn("fwith.co.kr/shop/item.php?it_id=",html)
            self.assertEqual(html.count('<h1>'),1)
            self.assertNotRegex(html,BAD_SEMANTICS)
            self.assertNotRegex(html,PROMISES)
            self.assertLess(html.count('class="tf-related"'),2)
            if n>33:
                self.assertIn(p["region"],html)


if __name__=="__main__":
    unittest.main()
