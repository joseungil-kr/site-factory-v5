import unittest
from scripts.worker6_shipping_render import lookup,evidence_section
class SellerShippingContract(unittest.TestCase):
 def test_exact_locality(self):
  x=lookup('경기도','파주시','적성면')
  self.assertEqual(x['state'],'exact-locality-display')
  self.assertEqual([(r['row'],r['extraKRW']) for r in x['candidates']],[(7,10000)])
 def test_overlap_not_resolved(self):
  x=lookup('경기도','가평군','설악면')
  self.assertEqual(x['state'],'overlap-unknown-priority')
  self.assertEqual({r['extraKRW'] for r in x['candidates']},{10000,20000})
  self.assertIn('최종 적용 요금',evidence_section(x)['paragraph'])
 def test_unlisted_is_not_free(self):
  x=lookup('전라남도','강진군','대구면')
  self.assertEqual(x['state'],'jurisdiction-unresolved')
  self.assertFalse(x['absenceMeansFree'])
  self.assertIn('정확한 배송지',evidence_section(x)['paragraph'])
 def test_alias_not_official_validation(self):
  x=lookup('경기도','파주시','적성면')
  self.assertTrue(x['aliasOnlyNotOfficialAddressValidation'])
  self.assertFalse(x['deliveryAvailabilityKnown'])
  self.assertFalse(x['finalShippingPriceKnown'])
 def test_actual_unlisted_row_with_resolved_province(self):
  x=lookup('경기도','파주시','문산읍')
  self.assertEqual(x['state'],'not-listed-unknown')
  self.assertIn('무료배송으로 확정하지 않습니다',evidence_section(x)['paragraph'])
 def test_unknown_province(self):
  x=lookup('전남광주통합특별시','강진군','마량면')
  self.assertEqual(x['state'],'jurisdiction-unresolved')
  self.assertIn('행정명',evidence_section(x)['paragraph'])
 def test_gunwi_alias_and_parent_uncertain(self):
  x=lookup('대구광역시','군위군','군위읍')
  self.assertEqual(x['state'],'district-display-only')
  self.assertTrue(x['aliasOnlyNotOfficialAddressValidation'])
 def test_yeongjong_district_name_unresolved(self):
  x=lookup('인천광역시','영종구','운서동')
  self.assertEqual(x['state'],'overlap-unknown-priority')
  self.assertFalse(x['deliveryAvailabilityKnown'])
 def test_candidate_flag_zero_not_official_address(self):
  from scripts.worker6_shipping_crosscheck import run
  result=run()
  self.assertFalse(result['deliveryCoverageConfirmed'])
  self.assertIn('unverified',result['candidateFlagZeroMeaning'])
  self.assertTrue(all(x['officialAddressValidated'] is False for x in result['matchedReferences']))
 def test_source_visible(self):
  for region in [('경기도','파주시','적성면'),('경기도','가평군','설악면'),('전라남도','강진군','대구면')]:
   result=lookup(*region)
   p=evidence_section(result)['paragraph']
   self.assertEqual(evidence_section(result)['sourceUrl'],result['sourceUrl'])
   self.assertIn(result['checkedAt'],p)
if __name__=='__main__':unittest.main()
