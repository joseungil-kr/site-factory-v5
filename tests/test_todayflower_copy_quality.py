"""Proofread every Todayflower page, not just representative samples.

The 2026-10-22 region archive is a *pinned snapshot*, never a claim that an
official agency was queried again today. Tests check Korean surface copy,
not local fulfillment certainty or independently sourced regional features.
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import json
import re
import unittest

from v5.config import read_site, ROOT
from v5.audit import similarity
from v5.visitor_copy import visible_copy_errors
from v5 import markup


SITE = "todayflower-nalmada"
BAD_PARTICLES = re.compile(
    r"동라는|동로(?=\s|[.,!?]|$)|화분(?:와|를)(?=\s|[.,!?]|$)"
    r"|화환(?:와|를)(?=\s|[.,!?]|$)|꽃다발(?:와|를)(?=\s|[.,!?]|$)"
    r"|선물를(?=\s|[.,!?]|$)|주문를(?=\s|[.,!?]|$)"
    r"|상담를(?=\s|[.,!?]|$)|을\(를\)"
)
BROKEN_BOUNDARY = re.compile(
    r"(?:습니다|합니다|됩니다|있습니다|없습니다|세요|봐요|좋습니다)"
    r"\s+(?=[가-힣])"
)
BAD_PROMISES = re.compile(
    r"무조건\s*당일배송|당일배송\s*보장|최저가\s*보장"
    r"|무료배송\s*확정|[0-9]+\s*시간\s*이내\s*도착\s*보장"
)
FRAGMENT_END = re.compile(r"(?:는 경우|하려는 상황|하려는 주문)\.$")


def fields(page):
    yield "title", page["title"]
    yield "topic", page["topic"]
    yield "heroTag", page["heroTag"]
    yield "sectionLead", page["sectionLead"]
    yield "intro", page["intro"]
    for i, section in enumerate(page["sections"], 1):
        yield f"section{i}:heading", section["heading"]
        yield f"section{i}:body", section["paragraph"]
    for i, faq in enumerate(page["faq"], 1):
        yield f"faq{i}:question", faq["q"]
        yield f"faq{i}:answer", faq["a"]


def body_blocks(page):
    return [
        ("intro", page["intro"]),
        *((f"section{i}", s["paragraph"]) for i, s in enumerate(page["sections"], 1)),
        *((f"faq{i}", f["a"]) for i, f in enumerate(page["faq"], 1)),
    ]


class VisibleParts(HTMLParser):
    """Inspect visitor-visible HTML, not only page.json data fields."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ("script","style","noscript","template"):
            self.skip += 1
        if not self.skip:
            for key,value in attrs:
                if key in ("alt","title","aria-label","placeholder") and value:
                    self.parts.append(value)
    def handle_endtag(self, tag):
        if tag in ("script","style","noscript","template") and self.skip:
            self.skip -= 1
    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(data.strip())


class TodayflowerWholeCopyAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site_data = read_site(SITE)
        cls.pages = cls.site_data["pages"]
        cls.site = cls.site_data["site"]

    def test_33_pages_all_text_fields_have_complete_korean_sentences(self):
        self.assertEqual(len(self.pages), 33)
        total = 0
        for page in self.pages:
            self.assertEqual(len(page["sections"]), 4, page["number"])
            self.assertEqual(len(page["faq"]), 3, page["number"])
            for field, value in fields(page):
                total += 1
                with self.subTest(page=page["number"], field=field):
                    self.assertEqual(value, value.strip())
                    self.assertNotRegex(value, BAD_PARTICLES)
                    self.assertNotRegex(value, BAD_PROMISES)
                    self.assertNotRegex(value, BROKEN_BOUNDARY)
                    self.assertNotRegex(value, FRAGMENT_END)
                    self.assertNotIn("을(를)", value)
                    self.assertNotIn("화정동라는", value)
                    self.assertNotIn("화분와", value)
                    if field.endswith(":question"):
                        self.assertTrue(value.endswith("?"), value)
                    elif field == "intro" or field.endswith(":body") or field.endswith(":answer"):
                        self.assertTrue(value.endswith("."), value)
                        for sentence in re.split(r"(?<=[.!?])\s+", value):
                            self.assertGreaterEqual(len(sentence), 12, (page["number"], field, sentence))
        self.assertEqual(total, 33 * (5 + 4*2 + 3*2))  # 19 fields/page = 627

    def test_all_33_rendered_html_visible_strings_not_only_article_bodies(self):
        for p in self.pages:
            html = (markup.home if p["number"]==1 else markup.detail)(
                self.site,p,self.pages,self.site_data["products"],self.site_data["links"]
            )
            parse=VisibleParts()
            parse.feed(html)
            self.assertGreater(len(parse.parts),40,p["number"])
            for text in parse.parts:
                with self.subTest(page=p["number"],text=text[:48]):
                    self.assertNotRegex(text,BAD_PARTICLES)
                    self.assertNotRegex(text,BAD_PROMISES)
                    self.assertNotIn("화분와",text)
                    self.assertNotIn("화분를",text)
                    self.assertNotIn("화환와",text)
                    self.assertNotIn("꽃다발와",text)
                    self.assertNotIn("화정동라는",text)
        # Raw source metadata remains historical: not an official government refresh.

    def test_no_repeated_full_paragraphs_across_33_pages(self):
        seen = {}
        for page in self.pages:
            for field, text in body_blocks(page):
                with self.subTest(page=page["number"], field=field):
                    self.assertNotIn(text, seen, (page["number"], field, seen.get(text)))
                    seen[text] = (page["number"], field)
        self.assertEqual(len(seen), 33*8)

    def test_all_528_pairs_and_sku_or_image_integrity(self):
        count = 0
        maximum = (0.0, None, None)
        for i, a in enumerate(self.pages):
            body_a = " ".join([a["intro"]] + [s["paragraph"] for s in a["sections"]])
            for b in self.pages[i+1:]:
                body_b = " ".join([b["intro"]] + [s["paragraph"] for s in b["sections"]])
                score = similarity(body_a, body_b)
                maximum = max(maximum, (score, a["number"], b["number"]))
                self.assertLess(score, 0.49, (a["number"], b["number"], score))
                count += 1
        self.assertEqual(count, 528)
        for p in self.pages:
            html = (markup.home if p["number"] == 1 else markup.detail)(
                self.site, p, self.pages,
                self.site_data["products"], self.site_data["links"]
            )
            with self.subTest(page=p["number"]):
                self.assertEqual(visible_copy_errors(html), [])
                self.assertEqual(html.count('<h1>'), 1)
                self.assertEqual(html.count('src="/assets/images/'), 7)
                self.assertEqual(html.count('width="1448" height="1086"'), 5)
                self.assertIn('<meta name="robots" content="noindex,nofollow">', html)
                self.assertNotIn('rel="canonical"', html)
                for sku in p["productSkus"]:
                    self.assertIn('href="https://fwith.co.kr/shop/item.php?it_id=' + sku + '"', html)
        self.assertFalse(self.site["publishEnabled"])
        self.assertFalse(self.site["indexNow"]["enabled"])

    def test_evidence_is_historical_not_a_live_government_query(self):
        evidence = json.loads(
            (ROOT/"sites"/SITE/"ansan-legal-regions-evidence.json").read_text(encoding="utf-8")
        )
        self.assertEqual(evidence["archiveHash"],
            "44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd")
        self.assertEqual(len(evidence["legalDongs"]), 30)
        self.assertIn("2026-10-22", evidence["source"])
        self.assertEqual(len(self.site_data["regions"]["regions"]), 33)


if __name__ == "__main__":
    unittest.main()
