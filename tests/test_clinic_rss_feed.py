"""Visitor-readable RSS 2.0 from actual Clinic HTML, with source/scope guards."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sites/nalmada-shared3"))
from rss_feed import create_rss, full_body_from_html, RSS_CONTENT_NS

HOST = "clinicflower.nalmada.net"


def page_html(url, content):
    return (
        '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<title>진짜 꽃 &amp; 화분 · 병원 개원 | 꽃이랑</title>'
        '<link rel="canonical" href="' + url + '">'
        '<meta name="robots" content="index,follow"></head>'
        '<body><header>내비게이션은 본문 아님</header><main><h1>개원축하화분</h1>'
        '<p>' + content + '</p><p>받으실 날짜와 주소를 알려주시면 배송 조건을 안내해 드립니다.</p>'
        '<p>축하화분을 고르실 때는 상품별 사진과 표시가격을 함께 비교하실 수 있습니다. '
        '접수대 주변에 놓는 작은 화분과 로비에 두는 화분은 사용할 공간이 다르므로 '
        '실제 받을 위치와 관리하는 분의 상황에 맞춰 고르시면 편리합니다.</p>'
        '<a href="/r/00003.html">지역 더 보기</a>'
        '<img src="/assets/images/hospital.webp" alt="화분 연출">'
        '<details><summary>배송비</summary><p>주소에 따른 추가 배송비는 주문 단계에서 안내됩니다.</p></details>'
        '</main><footer>이것은 상품 설명이 아님</footer></body></html>'
    )


class ClinicRSSFeedTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.paths = [f"/r/{i:05d}.html" for i in range(1, 51)]
        self.files = {}
        for n, path in enumerate(self.paths):
            file = self.directory / (str(n) + ".html")
            file.write_text(page_html("https://" + HOST + path,
                            f"상품 정보 & 실제 주문 안내 {n}번. <판매 옵션>"), encoding="utf-8")
            self.files[path] = file

    def tearDown(self):
        self.temp.cleanup()

    def test_all_fifty_items_include_actual_full_body_and_absolute_media(self):
        feed, evidence = create_rss(host=HOST, channel_title="꽃이랑 의료기관 개원화분",
                                    channel_description="병원 개원 축하화분 안내",
                                    paths=self.paths, page_files=self.files)
        root = ET.fromstring(feed)
        self.assertEqual(root.tag, "rss")
        self.assertEqual(root.attrib["version"], "2.0")
        ch = root.find("channel")
        self.assertEqual(ch.findtext("language"), "ko-KR")
        items = ch.findall("item")
        self.assertEqual(len(items), 50)
        self.assertEqual(evidence["itemCount"], 50)
        self.assertTrue(evidence["allItemsHaveDescription"])
        self.assertTrue(evidence["allItemsHaveContentEncoded"])
        self.assertEqual(evidence["minimumBodyLength"] > 120, True)
        self.assertLess(evidence["bytes"], 9_950_000)
        for i, item in enumerate(items):
            self.assertEqual(item.findtext("link"), "https://" + HOST + self.paths[i])
            self.assertEqual(item.findtext("guid"), item.findtext("link"))
            self.assertEqual(item.find("guid").attrib["isPermaLink"], "true")
            self.assertEqual(item.findtext("title"), "진짜 꽃 & 화분 · 병원 개원 | 꽃이랑")
            self.assertIn("받으실 날짜와 주소", item.findtext("description"))
            self.assertIn("배송비", item.findtext("description"))
            self.assertNotIn("이것은 상품 설명이 아님", item.findtext("description"))
            rich = item.findtext("{" + RSS_CONTENT_NS + "}encoded")
            self.assertIn("<main>", rich)
            self.assertIn('href="https://' + HOST + '/r/00003.html"', rich)
            self.assertIn('src="https://' + HOST + '/assets/images/hospital.webp"', rich)
            self.assertNotIn("<footer>", rich)
            self.assertIsNone(item.find("pubDate"), "Cannot invent historical publication dates")
        self.assertIn(b"xmlns:content=", feed)
        self.assertEqual(feed, create_rss(host=HOST, channel_title="꽃이랑 의료기관 개원화분",
                                          channel_description="병원 개원 축하화분 안내",
                                          paths=self.paths, page_files=self.files)[0])

    def test_malformed_missing_or_foreign_urls_fail_closed(self):
        with self.assertRaises(ValueError):
            create_rss(host="evil.example", channel_title="t", channel_description="d",
                       paths=self.paths, page_files=self.files)
        with self.assertRaises(ValueError):
            create_rss(host=HOST, channel_title="t", channel_description="d",
                       paths=self.paths + ["/r/00051.html"], page_files=self.files)
        with self.assertRaises(ValueError):
            create_rss(host=HOST, channel_title="t", channel_description="d",
                       paths=self.paths[:-1] + ["/r/99999.html"], page_files=self.files)
        with self.assertRaises(ValueError):
            create_rss(host=HOST, channel_title="t", channel_description="d",
                       paths=[self.paths[0]] * 2, page_files=self.files)

    def test_canonical_missing_or_noindex_rejected_for_public_feed(self):
        selected = self.paths[0]
        self.files[selected].write_text(page_html("https://evil.example/r/00001.html",
                                                "안산시의 다양한 개원 축하화분을 보여드립니다."),
                                        encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "canonical"):
            create_rss(host=HOST, channel_title="t", channel_description="d",
                       paths=self.paths, page_files=self.files)
        self.files[selected].write_text(page_html("https://" + HOST + selected,
                                                 "안산시의 다양한 개원 축하화분을 보여드립니다.").replace(
            "index,follow", "noindex,nofollow"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "canonical"):
            create_rss(host=HOST, channel_title="t", channel_description="d",
                       paths=self.paths, page_files=self.files)

    def test_no_main_is_never_a_feed_item(self):
        with self.assertRaisesRegex(ValueError, "main"):
            full_body_from_html("<html><p>상단 메뉴만 있음</p></html>", HOST)

    def test_feed_size_budget_fails_before_upload(self):
        with self.assertRaisesRegex(ValueError, "budget"):
            create_rss(host=HOST, channel_title="t", channel_description="d",
                       paths=self.paths, page_files=self.files, max_bytes=100)

if __name__ == "__main__":
    unittest.main()
