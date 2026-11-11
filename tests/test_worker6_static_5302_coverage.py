import unittest
from scripts.worker6_static_5302_coverage import summarize
class StaticCoverage(unittest.TestCase):
 def test_5302_inventory_not_mistaken_for_verified_pages(self):
  x=summarize()
  self.assertEqual(x['target'],5302)
  self.assertEqual(x['localityCandidates'],5034)
  self.assertIsNone(x['verifiedIndependentLocalityBodies'])
  self.assertFalse(x['similarityBelow49Verified'])
  self.assertFalse(x['editorial85Verified'])
if __name__=='__main__':unittest.main()
