from __future__ import annotations
import unittest
from scripts import build_baekse_cities as b

class BaekseCityTests(unittest.TestCase):
    def test_only_valid_85_cities(self):
        data=b.read(b.SITE/"cities.json")
        rows=data["cities"]
        self.assertEqual(len(rows),85)
        self.assertEqual(len({b.city_title(c) for c in rows}),85)
        self.assertEqual(sum(c["level"]=="metropolitan-city" for c in rows),8)
        self.assertEqual(sum(c["level"]!="metropolitan-city" for c in rows),77)
        self.assertTrue(all(c["city"].endswith("시") for c in rows))
        self.assertFalse(any(c["city"].endswith(("군","구","동","읍","면")) for c in rows))
        self.assertEqual(sum(c["city"]=="전남광주통합특별시" for c in rows),1)
        self.assertEqual(sum(c["city"]=="광주광역시" for c in rows),0)

    def test_four_menus_and_page_count(self):
        self.assertEqual(len(b.MENUS),4)
        self.assertEqual(85*4+85+4+1,430)
        self.assertEqual(b.read(b.SITE/"site-spec.json")["targetPageCount"],430)
        self.assertIn("닭한마리",b.MENUS["dakhanmari"]["name"])
        self.assertEqual(b.PHONE,"031-407-0103")

    def test_104_original_copy_blocks_and_unique_decisions(self):
        pool=b.read(b.SITE/"copy-pool.json")
        self.assertEqual(pool["copyCount"],104)
        self.assertEqual(set(pool["families"]),set(b.GROUPS))
        self.assertTrue(all(len(v)==8 for v in pool["families"].values()))
        self.assertTrue(all(len(v)==8 for v in pool["menus"].values()))
        city=b.read(b.SITE/"cities.json")["cities"][0]
        text1=b.select_copy(pool,city,"dakhanmari")
        self.assertEqual(text1,b.select_copy(pool,city,"dakhanmari"))
        self.assertEqual(len(text1),10)
        self.assertEqual(len({text for _,text in text1}),10)

    def test_city_and_menu_url_stability(self):
        cities=b.read(b.SITE/"cities.json")["cities"]
        paths=[b.city_path(c) for c in cities]
        details=[b.city_menu_path(c,key) for c in cities for key in b.MENUS]
        self.assertEqual(len(set(paths)),85)
        self.assertEqual(len(set(details)),340)
        self.assertEqual(len(set(paths+details+list(b.MENUS))),429)
        self.assertTrue(all(path.endswith(".html") for path in paths+details))

    def test_preview_is_noindex_and_business_accurate(self):
        city=b.read(b.SITE/"cities.json")["cities"][0]
        pool=b.read(b.SITE/"copy-pool.json")
        doc,narr=b.render_city_menu(city,"sundaeguk",pool)
        self.assertIn('noindex,nofollow',doc)
        self.assertIn('tel:0314070103',doc)
        self.assertNotIn('rel="canonical"',doc)
        self.assertNotIn("현지 직영 매장",doc)
        self.assertIn("상담",doc)
        self.assertTrue(len(narr)>300)

if __name__=="__main__":unittest.main()
