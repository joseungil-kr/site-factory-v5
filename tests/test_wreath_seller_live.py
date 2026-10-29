import hashlib, unittest
from scripts.qa_wreath_seller_live import check, live_price

class SellerLiveTests(unittest.TestCase):
    def setUp(self):
        self.img=b'\xff\xd8\xff'+b'fixture-image'
        self.p={'id':'B201','referencePriceKRW':59000,
                'orderUrl':'https://fwith.co.kr/shop/item.php?it_id=B201',
                'imageUrl':'https://fwith.co.kr/data/item/B201/test.jpg',
                'imageSHA256':hashlib.sha256(self.img).hexdigest()}
    def get(self,url):
        if 'item.php' in url:
            return (b'<html>B201 <div id="it_price">59,000</div><button>바로구매</button></html>','text/html')
        return (self.img,'image/jpeg')
    def test_live_extraction_not_catalog_copy(self):
        self.assertEqual(live_price('<span id="it_price">59,000</span>'),59000)
        self.assertEqual(live_price('<meta property="product:price:amount" content="79000">'),79000)
        with self.assertRaises(ValueError):live_price('<div>price unknown</div>')
    def test_success_for_six(self):
        self.assertTrue(check([self.p]*6,self.get)['passes'])
    def test_price_mismatch_fails(self):
        p={**self.p,'referencePriceKRW':79000}
        self.assertFalse(check([p]*6,self.get)['passes'])
    def test_hash_mismatch_fails(self):
        p={**self.p,'imageSHA256':'0'*64}
        self.assertFalse(check([p]*6,self.get)['passes'])
    def test_http_error_fails(self):
        def bad(url):
            raise RuntimeError('HTTP_503')
        self.assertFalse(check([self.p]*6,bad)['passes'])
    def test_missing_price_fails(self):
        def no_price(url):
            if 'item.php' in url:return (b'<html>B201 <button>바로구매</button></html>','text/html')
            return (self.img,'image/jpeg')
        self.assertFalse(check([self.p]*6,no_price)['passes'])

if __name__=='__main__':unittest.main()
