"""Onehour Sky real V5 build/input regression tests; never touch other sites."""
import json
import unittest
from pathlib import Path
from v5.config import ROOT, read_site
from v5.onehour_sky_pages import _rows, _pool, EXPECTED_PAGES
from v5.site_plan import check_site
from v5.service_markup import home, detail
from v5.markup import filename


class OneHourSky(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = read_site("onehour-sky")

    def test_preview_plan_is_buildable_but_not_indexable(self):
        self.assertTrue(check_site("onehour-sky")["ready"])
        site = self.data["site"]
        self.assertEqual(site["domain"], "https://1hrsky.nalmada.net")
        self.assertFalse(site["publicIndexingApproved"])
        self.assertFalse(site["publishEnabled"])
        self.assertFalse(site["indexNow"]["enabled"])
        self.assertFalse(site["imageAssetsApproved"])
        self.assertEqual(site["pricingPolicy"], "half-day-minimum-consult")

    def test_pinned_national_ledger_and_pool(self):
        self.assertEqual(len(_rows()), 284)
        shared, topics = _pool()
        self.assertEqual(sum(map(len, shared.values())), 72)
        self.assertEqual(len(topics), 8)

    def test_regional_pages_are_real_v5_page_models(self):
        pages = self.data["pages"]
        self.assertEqual(len(pages), EXPECTED_PAGES)
        self.assertEqual([p["number"] for p in pages], list(range(1, 286)))
        self.assertEqual(len({p["id"] for p in pages}), EXPECTED_PAGES)
        self.assertEqual(len({p["region"] for p in pages}), EXPECTED_PAGES)
        for p in pages:
            self.assertEqual(p["title"],
                             f"{p['region']} 스카이차 1시간 작업, 반일작업 전문 '한시간스카이'")
            self.assertGreaterEqual(len(p["sections"]), 3)
            self.assertTrue(all(len(s["paragraph"]) >= 80 for s in p["sections"]))

    def test_renderer_displays_exact_h1_and_half_day_terms(self):
        data = self.data
        site = data["site"]
        pages = data["pages"]
        home_html = home(site, pages[0], pages, data["services"], data["rates"])
        detail_html = detail(site, pages[1], pages, data["services"], data["rates"])
        for content, page in ((home_html, pages[0]), (detail_html, pages[1])):
            self.assertIn("<h1>" + page["title"] + "</h1>", content)
            self.assertIn("1시간 작업도 반나절 요금 기준", content)
            self.assertIn('content="noindex,nofollow"', content)
            self.assertNotIn('rel="canonical"', content)
            self.assertNotIn("30만원", content)
            self.assertNotIn("400,000원", content)
            self.assertNotIn("부가세 별도", content)
        self.assertIn('href="/285.html"', home_html)

    def test_existing_daysky_numeric_rate_renderer_still_available(self):
        from v5.service_markup import _prices
        site={"id":"daysky","serviceLabel":"스카이차"}
        sample=[{"id":"sky-1t","name":"1톤 스카이차"}]
        rates={"plans":[{"serviceId":"sky-1t","hour":300000,"halfDay":400000,"fullDay":600000}]}
        self.assertIn("300,000원", _prices(site, rates, sample))

    def test_foreign_customer_and_service_status(self):
        all_content=json.dumps(self.data["pages"],ensure_ascii=False)
        for name in ("당일스카이","빠른스카이","영진"):
            self.assertNotIn(name,all_content)
        self.assertIn("한시간스카이",all_content)


if __name__=="__main__":
    unittest.main()
