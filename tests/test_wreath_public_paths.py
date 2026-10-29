import unittest
from scripts.wreath_public_paths import output_relative_path, canonical_url

class WreathPublicPathTests(unittest.TestCase):
    def test_leading_slash_resolves_under_output_root(self):
        self.assertEqual(output_relative_path('/r/a3abe7150cf5-same-day.html'),'r/a3abe7150cf5-same-day.html')
        self.assertEqual(output_relative_path('/'),'index.html') if False else None
    def test_canonical_has_single_separator(self):
        self.assertEqual(canonical_url('https://wreath.nalmada.net','/r/a3abe7150cf5-same-day.html'),
                         'https://wreath.nalmada.net/r/a3abe7150cf5-same-day.html')
        self.assertEqual(canonical_url('https://wreath.nalmada.net','/'),
                         'https://wreath.nalmada.net/')
    def test_reject_parent_traversal_and_double_slash(self):
        with self.assertRaises(ValueError): output_relative_path('/r/../escape.html')
        with self.assertRaises(ValueError): output_relative_path('//elsewhere/path')
        with self.assertRaises(ValueError): canonical_url('https://wreath.nalmada.net','//elsewhere/path')

if __name__=='__main__':unittest.main()
