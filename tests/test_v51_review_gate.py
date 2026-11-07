import unittest
from v5.config import ConfigError
from v5.review_gate import assert_review, review_digest, sample_ids

class V51ReviewTests(unittest.TestCase):
 def setUp(self):
  self.data={'site':{'id':'demo'},'pages':[{'id':str(i),'purpose':'one' if i<150 else 'two'} for i in range(200)],'products':[]}
  self.plan={'version':2,'purposePools':{'one':{},'two':{}}}
 def review(self):
  return {'approved':True,'reviewer':'reviewer','reviewedOn':'2026-11-07','evidence':'report.md',
          'inputDigest':review_digest(self.data,self.plan),'samples':[{'id':i,'score':90} for i in sample_ids(self.data['pages'])]}
 def test_stratified_one_percent_is_pinned(self):
  self.assertEqual(len(sample_ids(self.data['pages'])),3)
  self.assertEqual(sample_ids(self.data['pages']),sample_ids(list(reversed(self.data['pages']))))
 def test_review_accepted_and_bound_to_inputs(self):
  plan={**self.plan,'qualityReview':self.review()};assert_review(self.data,plan)
  with self.assertRaisesRegex(ConfigError,'current inputs'):
   assert_review({**self.data,'products':[{'sku':'changed'}]},plan)
 def test_missing_sample_below_90_and_duplicate_fail(self):
  r=self.review();r['samples']=r['samples'][:-1]
  with self.assertRaisesRegex(ConfigError,'pinned'):assert_review(self.data,{**self.plan,'qualityReview':r})
  r=self.review();r['samples'][0]['score']=89
  with self.assertRaisesRegex(ConfigError,'below 90'):assert_review(self.data,{**self.plan,'qualityReview':r})
  r=self.review();r['samples'].append(r['samples'][0])
  with self.assertRaisesRegex(ConfigError,'duplicate'):assert_review(self.data,{**self.plan,'qualityReview':r})
 def test_missing_review_fails(self):
  with self.assertRaisesRegex(ConfigError,'approved'):assert_review(self.data,self.plan)

if __name__=='__main__':unittest.main()
