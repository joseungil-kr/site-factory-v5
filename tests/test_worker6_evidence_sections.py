import unittest
from v5.purpose_render import assemble
from v5.config import ConfigError
P={'id':'test-one','region':'전국','purpose':'promotion','productSkus':['D144']}
POOL={'promotion':{'productSkus':['D144'],'introductions':['소개'],'sections':[{'slot':'choice','heading':'선택','paragraph':'선택 근거'},{'slot':'order','heading':'주문','paragraph':'주문 방법'}],'faqs':[{'q':'문의?','a':'전화'}]}}
PRODUCTS=[{'sku':'D144'}]
def evidence(**changes):
    data={'heading':'확인 사항','paragraph':'배송비를 주소별로 확인','sourceUrl':'https://fwith.co.kr/shop/item.php?it_id=D144','checkedOn':'2026-11-09'}
    data.update(changes)
    return data
class EvidenceSectionsContract(unittest.TestCase):
    def test_valid_evidence_preserves_text(self):
        result=assemble({**P,'evidenceSections':[evidence()]},POOL,PRODUCTS)
        self.assertEqual(len(result['sections']),3)
        self.assertEqual(result['sections'][-1]['paragraph'],'배송비를 주소별로 확인')
    def test_without_evidence_backward_compatible(self):
        result=assemble(P,POOL,PRODUCTS)
        self.assertEqual(len(result['sections']),2)
    def test_required_fields(self):
        for field in ('heading','paragraph','sourceUrl','checkedOn'):
            with self.subTest(field=field):
                with self.assertRaises(ConfigError):
                    assemble({**P,'evidenceSections':[evidence(**{field:''})]},POOL,PRODUCTS)
    def test_invalid_url(self):
        for url in ('http://example.com','javascript:alert(1)','/relative',''):
            with self.subTest(url=url),self.assertRaises(ConfigError):
                assemble({**P,'evidenceSections':[evidence(sourceUrl=url)]},POOL,PRODUCTS)
    def test_invalid_date(self):
        for date in ('20261109','2026-11-9','unknown',''):
            with self.subTest(date=date),self.assertRaises(ConfigError):
                assemble({**P,'evidenceSections':[evidence(checkedOn=date)]},POOL,PRODUCTS)
    def test_invalid_collection(self):
        with self.assertRaises(ConfigError):
            assemble({**P,'evidenceSections':'not-a-list'},POOL,PRODUCTS)
if __name__=='__main__':unittest.main()
