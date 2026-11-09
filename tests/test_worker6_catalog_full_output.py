import ast,json,unittest
from pathlib import Path
from v5.purpose_render import assemble
from v5 import markup
class CatalogFullOutput(unittest.TestCase):
 def setUp(self):
  s=Path('scripts/worker6_core_five_preview.py').read_text(encoding='utf-8')
  fn=next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name=='product_summary')
  scope={}
  exec(compile(ast.Module(body=[fn],type_ignores=[]),'summary','exec'),scope)
  self.summary=scope['product_summary']
 def _render(self,items):
  summary=self.summary(items)
  catalog=[{'sku':p['sku'],'name':p['name'],'referencePrice':p['priceKRW'],
   'priceConfirmed':True,'priceEvidence':'https://seller.example/item',
   'priceCheckedOn':'2026-11-09','orderUrl':'https://seller.example/'+p['sku']} for p in items]
  pool={'promotion':{'productSkus':summary['skus'],
   'introductions':[f"판매처에서 확인한 상품 {summary['count']}종"],
   'sections':[{'slot':'choice','heading':f"판매처에서 확인한 상품 {summary['count']}종",
     'paragraph':summary['label']},{'slot':'order','heading':'주문','paragraph':'결제 확인'}],
   'faqs':[{'q':'가격?','a':summary['label']}]}}
  page={'id':'x','pageType':'purpose-guide','purpose':'promotion','region':'안내',
    'productSkus':summary['skus']}
  a=assemble(page,pool,catalog)
  html=markup.article_body(a)+markup.faq_markup(a)+''.join(
    f'<article data-product-sku="{sku}">{sku}</article>' for sku in a['productSkus'])
  return html
 def test_add_remove_changes_entire_rendered_copy_and_cards(self):
  one=[{'sku':'D144','name':'금전수 탁상용','priceKRW':53000}]
  two=one+[{'sku':'D026','name':'아로우카리아 대형','priceKRW':90000}]
  a=self._render(one);b=self._render(two)
  self.assertIn('상품 1종',a);self.assertNotIn('D026',a)
  self.assertIn('상품 2종',b);self.assertIn('D026',b)
  self.assertIn('90,000원',b);self.assertNotIn('90,000원',a)
  self.assertEqual(a.count('data-product-sku='),1)
  self.assertEqual(b.count('data-product-sku='),2)
if __name__=='__main__':unittest.main()
