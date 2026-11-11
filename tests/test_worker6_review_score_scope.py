import unittest
from v5.review_gate import minimum_review_score
class SiteSpecificReviewThreshold(unittest.TestCase):
 def test_worker6_explicit_target_85(self):
  self.assertEqual(minimum_review_score({'site':{'id':'promotion-gift-plants'}},{'targetPageCount':5302}),85)
 def test_other_sites_remain_90(self):
  for name in ('county-funeral','wreath','hallflower','flowershop'):
   self.assertEqual(minimum_review_score({'site':{'id':name}},{'targetPageCount':5302}),90)
 def test_worker6_wrong_target_fails_closed_to_90(self):
  self.assertEqual(minimum_review_score({'site':{'id':'promotion-gift-plants'}},{'targetPageCount':5}),90)
 def test_score_boundaries(self):
  def valid(score,threshold):
   return type(score) in (int,float) and threshold<=score<=100
  self.assertTrue(valid(85,minimum_review_score({'site':{'id':'promotion-gift-plants'}},{'targetPageCount':5302})))
  self.assertFalse(valid(84.99,85))
  self.assertFalse(valid(True,85))
  self.assertFalse(valid(89.99,90))
  self.assertTrue(valid(90,90))
if __name__=='__main__':unittest.main()
