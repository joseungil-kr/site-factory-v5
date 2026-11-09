import unittest
from pathlib import Path
class CoreGuideRoles(unittest.TestCase):
 def test_three_distinct_roles_not_append(self):
  s=Path('scripts/worker6_core_five_preview.py').read_text(encoding='utf-8')
  self.assertIn("pool['sections']=[",s)
  self.assertIn("modules['choice']",s)
  self.assertIn("modules['message']",s)
  self.assertIn("modules['order']",s)
 def test_sameday_confirmation_not_repeated(self):
  s=Path('scripts/worker6_core_five_preview.py').read_text(encoding='utf-8')
  for phrase in ('문의할 정보:','판매처에 확인할 항목:','결제 판단'):
   self.assertIn(phrase,s)
  self.assertIn("pool['sections']=[",s)
  self.assertIn("returns_copy",s)
 def test_reference_is_not_service_promise(self):
  s=Path('scripts/worker6_core_five_preview.py').read_text(encoding='utf-8')
  self.assertIn('리본 포함·문구 입력·무료 제공 여부는 확인되지 않았습니다',s)
  self.assertIn('식물관리 조건을 추정하지 말고',s)
if __name__=='__main__':unittest.main()
