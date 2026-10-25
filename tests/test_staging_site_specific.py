"""Site-specific staging HTTP probes must never invent required pages."""
import unittest
from v5.config import read_site
from v5.markup import filename
from v5.staging import staging_sample_routes

class StagingExpectedRoutes(unittest.TestCase):
    def test_daysky_phone_site(self):
        checks=staging_sample_routes(read_site('daysky'))
        for n in (2,10,1736):
            self.assertEqual(checks[f'/{n}.html'],200)
        self.assertEqual(checks['/1737.html'],404)
        self.assertEqual(checks['/404-auditor-sentinel.html'],404)
        self.assertNotIn('/%EA%B2%AC%EC%A0%81%EA%B3%84%EC%82%B0%EA%B8%B0.html', checks)
    def test_flower_store_keeps_actual_calculator(self):
        checks=staging_sample_routes(read_site('ansan-promotion-plant'))
        self.assertEqual(checks['/10.html'],200)
        self.assertEqual(checks['/11.html'],404)
        self.assertEqual(checks['/%EA%B2%AC%EC%A0%81%EA%B3%84%EC%82%B0%EA%B8%B0.html'],200)
    def test_large_site_samples_real_number_404(self):
        checks=staging_sample_routes({'pages':[{'number':n} for n in range(1,3466)],'special':[]})
        self.assertEqual(checks['/'+filename(404)],200)
        self.assertEqual(checks['/3465.html'],200)
        self.assertEqual(checks['/3466.html'],404)

if __name__=='__main__': unittest.main()
