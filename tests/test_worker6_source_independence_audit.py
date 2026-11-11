import unittest
from scripts.worker6_source_independence_audit import analyze
class SourceIndependenceAudit(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.report=analyze()
 def test_target_is_candidate_not_publication(self):
  r=self.report
  self.assertEqual(r['totalTarget'],5302)
  self.assertEqual(r['candidateCount'],5034)
  self.assertFalse(r['releaseAllowed'])
 def test_no_fake_locality_coverage_from_seller_rows(self):
  r=self.report
  self.assertEqual(len(r['catalog']),6)
  for p in r['catalog'].values():
   self.assertFalse(p['stockConfirmed'])
   self.assertFalse(p['localAvailabilityConfirmed'])
   self.assertTrue(p['orderUrl'].startswith('https://fwith.co.kr/shop/item.php?it_id='))
  for p in r['sellerRowExamples']:
   self.assertFalse(p['finalShippingConfirmed'])
 def test_repetition_not_misrepresented_as_unique_evidence(self):
  r=self.report
  self.assertGreater(r['largestBucketCount'],1)
  self.assertGreater(sum(x['count'] for x in r['topRepeatedBuckets']),20)
  self.assertEqual(r['fieldMapping']['actualLocalStock'],'unknown')
  self.assertEqual(r['fieldMapping']['deliveryArrivalCutoff'],'unknown')
  self.assertEqual(r['fieldMapping']['facilityAdmission'],'unknown unless separate current venue evidence passes gate')
 def test_policy_is_not_waived(self):
  self.assertEqual(self.report['similarityThreshold'],0.49)
  self.assertEqual(self.report['editorialThreshold'],85)
if __name__=='__main__':unittest.main()
