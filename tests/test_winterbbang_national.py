from __future__ import annotations
import unittest
from scripts import build_winterbbang_national as w

class WinterbbangNationalTests(unittest.TestCase):
    def test_region_inventory_pinned(self):
        rows, plan=w.source_data()
        self.assertEqual(len(rows),1732)
        self.assertEqual(plan["targetPageCount"],1804)
        self.assertEqual(len({r[0] for r in rows}),69)
        self.assertEqual(sum(r[1].endswith("동") for r in rows),1588)

    def test_pools_are_independent_and_sufficient(self):
        seed, ext, seed_by_family=w.pools()
        self.assertEqual(len(seed["blocks"]),64)
        self.assertEqual(sum(len(v) for v in ext.values()),96)
        self.assertEqual(len(w.GROUPS),8)
        for g in w.GROUPS:self.assertEqual(len(ext[g]),12)

    def test_url_uniqueness_and_deterministic_selection(self):
        rows,_=w.source_data()
        paths={w.region_url(*r) for r in rows}
        self.assertEqual(len(paths),1732)
        seed,ext,fam=w.pools()
        chosen1=w.make_selection(*rows[0],ext,fam)
        chosen2=w.make_selection(*rows[0],ext,fam)
        self.assertEqual(chosen1,chosen2)
        self.assertEqual(len(chosen1[1]),9)

    def test_noindex_sample_and_claim_safety(self):
        base=w.sample.load_pool(w.sample.POOL_DEFAULT)
        result=w.sample.render(base)
        self.assertIn('noindex,nofollow',result)
        self.assertIn('tel:0314070103',result)
        self.assertIn('매출총이익률',result)
        self.assertIn('순이익률',result)
        self.assertNotIn('월 100만 원',result)

    def test_locality_navigation_escapes(self):
        page=w.more_content("서울특별시 강남구","역삼동",["안전한 안내"]*9,[], "서울특별시 강남구")
        self.assertIn(w.district_url("서울특별시 강남구"),page)
        self.assertIn("서울특별시 강남구 역삼동 창업 체크리스트",page)

if __name__=="__main__":unittest.main()
