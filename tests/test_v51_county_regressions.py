import json,re,unittest
from v5.config import ConfigError
from v5.purpose_render import _text,assemble,regional_index,regional_ancestors,render,schema
from v5.audit import similarity,similarity_violation

class CountyV51Fixes(unittest.TestCase):
 def setUp(self):
  self.site={'id':'county-test','brand':'군 화환','domain':'https://county.example.test',
    'publishEnabled':True,'theme':'classic','phone':'1844-0644',
    'orderBaseUrl':'https://fwith.co.kr','imagePool':['hero.svg'],
    'keyword':'근조화환','region':'전국','analytics':{'enabled':False}}
  self.product={'sku':'B201','name':'근조 3단','referencePrice':59000,
    'orderUrl':'https://fwith.co.kr/shop/item.php?it_id=B201',
    'priceConfirmed':True,'priceEvidence':'seller record','priceCheckedOn':'2026-11-07'}
  self.page={'id':'county','number':3,'region':'충청북도 단양군','county':'단양군','province':'충청북도',
    'parentRegion':'충청북도','parentPageId':'province','purpose':'budget','productSkus':['B201'],
    'intro':'original','title':'단양군 근조화환','sections':[{'heading':'기존','paragraph':'legacy'}]}
  self.pools={'budget':{'productSkus':['B201'],'introductions':['{province} {county} 근조화환'],
    'sections':[{'slot':'choice','heading':'가격','paragraph':'{county}에서 사용 목적에 맞는 실제 근조화환 기준가를 비교합니다.'},
                {'slot':'order','heading':'상담','paragraph':'{province}의 수령 시설과 상세 주소를 입력해 배송 조건을 확인합니다.'},
                {'slot':'ribbon','heading':'리본 문구','paragraph':'{parentRegion} 수령지에 전할 이름과 문구를 작성합니다.'},
                {'slot':'venue','heading':'시설 확인','paragraph':'시설의 반입 조건은 별도 확인합니다.'}],
    'faqs':[{'q':'리본 문구는?','a':'수령지에 전할 이름을 확인합니다.'}]}}
 def test_all_purpose_sections_preserved(self):
  assembled=assemble(self.page,self.pools,[self.product])
  self.assertEqual([p['slot'] for p in assembled['sections']],['choice','order','ribbon','venue'])
  self.assertIn('단양군',assembled['intro'])
  self.assertIn('충청북도',assembled['sections'][1]['paragraph'])
  self.assertEqual(len(assembled['sections']),4)
 def test_unknown_placeholder_rejected(self):
  bad=json.loads(json.dumps(self.pools));bad['budget']['introductions']=['{untrusted} text']
  with self.assertRaises(ConfigError):assemble(self.page,bad,[self.product])
 def test_exact_all_four_placeholders_and_missing_fail_closed(self):
  template='{region} / {county} / {province} / {parentRegion}'
  self.assertEqual(_text(template,self.page),'충청북도 단양군 / 단양군 / 충청북도 / 충청북도')
  for missing in ['region','county','province','parentRegion']:
   broken={k:v for k,v in self.page.items() if k!=missing}
   with self.subTest(missing=missing), self.assertRaisesRegex(ConfigError,'missing purpose placeholder'):
    _text('{'+missing+'} 근조화환',broken)
  with self.assertRaisesRegex(ConfigError,'unknown or missing'):
   _text('{unknown} 근조화환',self.page)
  rendered=render(self.site,self.page,[self.page],[self.product],[],self.pools)
  self.assertNotRegex(rendered,r'\\{(?:region|county|province|parentRegion|unknown)\\}')
  self.assertIn('단양군에서 사용 목적에 맞는',rendered)
 def test_cosine_unicode_whitespace_and_numeric_threshold_boundaries(self):
  for spaced in ['a b c','a\\tb\\tc','a\\nb\\nc','a  \\t b \\n c']:
   with self.subTest(spaced=repr(spaced)):
    self.assertEqual(similarity(spaced,'abc','char-3gram-cosine'),1.0)
  self.assertAlmostEqual(similarity('abcde','abcdf','char-3gram-cosine'),2/3,places=12)
  self.assertEqual(similarity('abcde','xyzuv','char-3gram-cosine'),0)
  self.assertTrue(similarity_violation(2/3,2/3))
  self.assertFalse(similarity_violation(2/3,0.67))
  self.assertTrue(similarity_violation(2/3,0.66))
  with self.assertRaises(ValueError):similarity_violation(0.2,1.0)
 def test_three_level_breadcrumb_matches_schema(self):
  home={**self.page,'id':'nation','number':1,'region':'전국','parentPageId':None}
  prov={**self.page,'id':'province','number':2,'region':'충청북도','parentPageId':'nation'}
  index=regional_index([home,prov,self.page])
  self.assertEqual([x['id'] for x in regional_ancestors(self.page,index)],['nation','province'])
  html=render(self.site,self.page,[home,prov,self.page],[self.product],[],self.pools,index)
  nav=html.split('aria-label="현재 위치"',1)[1].split('</nav>',1)[0]
  self.assertTrue(nav.index('전국')<nav.index('충청북도')<nav.index('단양군'))
  obj=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',html).group(1))
  breadcrumb=next(x for x in obj['@graph'] if x['@type']=='BreadcrumbList')
  self.assertEqual(len(breadcrumb['itemListElement']),3)
  self.assertEqual([x['position'] for x in breadcrumb['itemListElement']],[1,2,3])
 def test_similarity_metric_values(self):
  a='abcabcabcabc';b='abcxabcxabcx'
  jac=similarity(a,b,'char-5gram-jaccard')
  cosine=similarity(a,b,'char-3gram-cosine')
  self.assertTrue(0<=jac<1 and 0<cosine<1)
  self.assertNotEqual(jac,cosine)
  with self.assertRaises(ValueError):similarity(a,b,'fake')
if __name__=='__main__':unittest.main(verbosity=2)
