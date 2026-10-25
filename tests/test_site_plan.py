import unittest
from v5.site_plan import initial_spec,validate_plan,check_site
from v5.config import ConfigError

class SiteCreationPlanningGate(unittest.TestCase):
    def test_incomplete_new_site_cannot_pass(self):
        spec=initial_spec("new-flower","꽃이랑","꽃배달","전국","1844-0644")
        self.assertFalse(validate_plan(spec,"new-flower")["ready"])
    def test_approved_complete_plan_passes(self):
        spec=initial_spec("new-flower","꽃이랑","꽃배달","전국","1844-0644")
        spec.update(domain="https://flower.example.org",businessModel="service-lead",
                    serviceScope={"region":"전국","granularity":"city","facilities":False},
                    pageTypes=["city","category"],targetPageCount=300,
                    titlePattern="{region} {keyword} 주문",urlPattern="/{number}.html",
                    copyPoolPlan={"industry":"flower","source":"new","sentenceTarget":600},
                    conversion={"mode":"phone","phone":"1844-0644"},
                    images={"source":"owner","approved":True},
                    publishPolicy={"mode":"review","indexNow":False},approved=True)
        self.assertTrue(validate_plan(spec,"new-flower")["ready"])
    def test_legacy_site_unaffected(self):
        self.assertTrue(check_site("daysky")["legacy"])

if __name__=="__main__":unittest.main()
