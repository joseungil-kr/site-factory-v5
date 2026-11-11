"""Regression tests for the noindex nationwide price-card mobile styling.

No internet, binary upload, deployment, or official regional archive needed.
"""
import re
import unittest
import build

class MobileCards(unittest.TestCase):
    def test_mobile_order_action_and_price_visibility(self):
        css=build.CSS
        self.assertIn('@media(max-width:700px)',css)
        for declaration in [
            '.overflow tbody{display:grid',
            '.overflow table{min-width:0;display:block',
            '.overflow td:last-child a{display:block;min-height:44px;width:100%',
            'background:#275e3d;color:#fff',
            '.overflow td:last-child a:focus-visible{outline:3px',
            '.overflow td:nth-last-child(2){white-space:nowrap',
        ]:
            self.assertIn(declaration,css)
        self.assertIn('noindex,nofollow',build.build.__code__.co_consts.__str__())
    def test_catalogue_links_untouched(self):
        expected={'B201':59000,'B203':79000,'B205':109000,
                  'C205':149000,'C030':200000}
        self.assertEqual({p['sku']:p['referenceKRW']
                          for p in build.SPEC['catalog']},expected)
        self.assertTrue(all(p['orderUrl']==
            'https://fwith.co.kr/shop/item.php?it_id='+p['sku']
            for p in build.SPEC['catalog']))
if __name__ == '__main__': unittest.main()
