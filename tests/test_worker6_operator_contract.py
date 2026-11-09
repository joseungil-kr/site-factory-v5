import json,unittest
from pathlib import Path
class OperatorContract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads(Path('sites/promotion-gift-plants/operator-service-confirmation-20261109.json').read_text())
 def test_phone_order_not_delivery_hours(self):
  self.assertEqual((self.d['phoneOrderHours']['start'],self.d['phoneOrderHours']['end']),('08:00','23:00'))
  self.assertEqual((self.d['deliveryWindow']['earliestPossible'],self.d['deliveryWindow']['latestPossible']),('06:00','20:00'))
  self.assertFalse(self.d['individualSameDayArrivalGuaranteed'])
  self.assertFalse(self.d['deliveryWindow']['guaranteed'])
 def test_source_not_external_and_no_guaranteed_cutoff(self):
  self.assertEqual(self.d['sourceType'],'user-provided seller operational confirmation relayed by supervisor')
  self.assertFalse(self.d['sourceVerifiedExternally'])
  self.assertEqual(self.d['individualCutoff'],'phone-confirm')
  self.assertEqual(self.d['regionalSurcharge'],'phone-confirm')
  self.assertFalse(self.d['branchAddressesVerified'])
 def test_empty_operational_handoff_untouched(self):
  x=json.loads(Path('sites/promotion-gift-plants/operations-shipping-handoff-template.json').read_text())
  self.assertEqual(x['records'],[])
if __name__=='__main__':unittest.main()
