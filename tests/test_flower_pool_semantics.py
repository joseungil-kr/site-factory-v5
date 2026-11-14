"""Regression checks for group-safe prose and actual final rendered document scope."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_flower_funeral_national as flower


class FuneralHallContentGroups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.facilities, cls.assignments, cls.curated, cls.support, cls.allowed=flower.load_sources()
        cls.index={f["id"]:i for i,f in enumerate(cls.facilities)}

    def test_all_1080_facilities_all_selected_indices_respect_group(self):
        visited_groups=set()
        excluded=set(range(120))-set.union(*(set(v) for v in self.allowed.values()))
        self.assertEqual(len(excluded),8)
        for f,a in zip(self.facilities,self.assignments):
            c=flower.create_content(f,a,self.curated,self.support,self.allowed)
            g=a["group"]
            visited_groups.add(g)
            self.assertEqual(c["group"],g)
            for field in flower.CORE_FIELDS:
                ids=c["selectedIndices"][field]
                self.assertEqual(ids[0],a[field])
                self.assertEqual(len(ids),4)
                self.assertEqual(len(set(ids)),4)
                self.assertTrue(set(ids).issubset(self.allowed[g]),(f["id"],g,field,ids))
                self.assertFalse(set(ids)&excluded)
        self.assertEqual(visited_groups,set(flower.GROUP_LABELS))

    def test_real_optimized_1080_selection_stays_within_assigned_groups(self):
        contents=flower.create_population(self.facilities,self.assignments,
                                          self.curated,self.support,self.allowed)
        self.assertEqual(len(contents),1080)
        for c,a,f in zip(contents,self.assignments,self.facilities):
            self.assertEqual(c["group"],a["group"])
            self.assertEqual(c["sections"][1][0],flower.BODY_HEADINGS[a["group"]])
            for field in flower.CORE_FIELDS:
                selected=c["selectedIndices"][field]
                self.assertEqual(selected[0],a[field])
                self.assertEqual(len(selected),4)
                self.assertTrue(set(selected).issubset(self.allowed[a["group"]]),(f["id"],field))
            for field in flower.SUPPORT_FIELDS:
                selected=c["supportSelectedIndices"][field]
                self.assertEqual(len(selected),2 if field=="order" else 1)
                self.assertTrue(all(i<len(self.support[field]) for i in selected))

    def test_all_eight_group_representatives_have_matching_section_headings(self):
        representatives={}
        for i,assignment in enumerate(self.assignments):
            representatives.setdefault(assignment["group"],i)
        self.assertEqual(set(representatives),set(flower.GROUP_LABELS))
        for group,i in representatives.items():
            f=self.facilities[i];a=self.assignments[i]
            c=flower.create_content(f,a,self.curated,self.support,self.allowed)
            self.assertEqual(c["sections"][1][0],flower.BODY_HEADINGS[group])
            self.assertIn(flower.GROUP_LABELS[group],c["sections"][4][0])
            self.assertIn(flower.GROUP_LABELS[group],c["sections"][6][0])
            self.assertEqual(len(c["sections"]),7)
            expected=[flower._fill(self.curated["body"][t],f)
                      for t in c["selectedIndices"]["body"]]
            self.assertEqual(c["sections"][1][1],expected)
            self.assertTrue(c["sections"][2][0].startswith("장례식장 명칭"))
            self.assertFalse(any(t in c["sections"][1][1] for t in c["sections"][2][1]))

    def test_two_reported_problem_hall_pages_are_correctly_scoped(self):
        for hall_id in ("fh-0003dfe99ba37467302b","fh-0010364f5b79fa1bfa07"):
            with self.subTest(id=hall_id):
                i=self.index[hall_id]
                f=self.facilities[i]
                c=flower.create_content(f,self.assignments[i],self.curated,self.support,self.allowed)
                self.assertEqual(c["sections"][1][0],flower.BODY_HEADINGS[c["group"]])
                rendered=flower.render(f,c)
                body=flower._rendered_main_text(f,c)
                self.assertIn(c["sections"][1][0],body)
                self.assertIn("59,000원",body)
                self.assertNotIn("현재 확정된 가격표가 없으므로",body)
                self.assertNotIn("원장 기재 주소",rendered)
                self.assertNotIn("현행 정보 미검증",rendered)
                self.assertIn("<main",rendered)
                self.assertIn("noindex,nofollow",rendered)

    def test_rendered_main_body_matches_parser_exactly_not_fake_unrendered_text(self):
        i=0;f=self.facilities[i]
        c=flower.create_content(f,self.assignments[i],self.curated,self.support,self.allowed)
        text=flower._rendered_main_text(f,c)
        self.assertIn("근조 3단 화환",text)
        self.assertIn("79,000원",text)
        self.assertIn("109,000원",text)
        self.assertIn("자주 묻는 질문",text)
        self.assertNotIn("현재 확정된 가격표가 없으므로",text)
        self.assertNotIn("2026-10-22",text)
        self.assertIn("2026.10.27",text)


if __name__=="__main__":
    unittest.main()
