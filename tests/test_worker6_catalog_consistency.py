import ast
import unittest
from pathlib import Path
class CatalogConsistency(unittest.TestCase):
 def setUp(self):
  self.script=Path('scripts/worker6_core_five_preview.py').read_text(encoding='utf-8')
  tree=ast.parse(self.script)
  fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='product_summary')
  scope={}
  exec(compile(ast.Module(body=[fn],type_ignores=[]),'worker6_summary','exec'),scope)
  self.summarize=scope['product_summary']
 def test_count_price_skus_follow_added_removed_items(self):
  items=[{'sku':'A','name':'가', 'priceKRW':50000},{'sku':'B','name':'나','priceKRW':90000}]
  a=self.summarize(items)
  self.assertEqual(a['count'],2)
  self.assertEqual(a['skus'],['A','B'])
  self.assertIn('90,000원',a['label'])
  b=self.summarize(items[:1])
  self.assertEqual(b['count'],1)
  self.assertNotIn('B',b['skus'])
  self.assertNotIn('90,000원',b['label'])
 def test_cards_and_home_copy_use_same_summary(self):
  self.assertIn("home['productSkus']=summary['skus']",self.script)
  self.assertIn("home['sections'][1]['heading']=f\"판매처에서 확인한 상품 {summary['count']}종\"",self.script)
  self.assertIn("home['faqs'][0]['a']=f\"확인된 상품 {summary['count']}종:",self.script)
  self.assertIn("'productSkus':summary['skus']",self.script)
 def test_no_hardcoded_two_product_title(self):
  self.assertNotIn('판매처에서 확인한 두 상품',self.script)
if __name__=='__main__':unittest.main()
