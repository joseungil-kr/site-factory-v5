import unittest,tempfile
from pathlib import Path
from scripts.worker6_illustration_integrity import verify_illustrations,require_rendered_illustrations,EXPECTED,LABEL
class IllustrationIntegrityTests(unittest.TestCase):
 def test_missing_files_fail_closed(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(ValueError,'missing='):verify_illustrations(d)
 def test_wrong_bytes_fail_closed(self):
  with tempfile.TemporaryDirectory() as d:
   for name in EXPECTED:(Path(d)/name).write_bytes(b'not an approved raster')
   with self.assertRaisesRegex(ValueError,'sha256 mismatch'):verify_illustrations(d)
 def test_zero_images_do_not_pass(self):
  with self.assertRaises(ValueError):require_rendered_illustrations('<html><body>no images</body></html>')
 def test_disclosure_without_both_images_fails(self):
  with self.assertRaises(ValueError):require_rendered_illustrations('<img src="a.webp"><p>'+LABEL+'</p>')
 def test_valid_markup_structure(self):
  h=''.join('<img src="/assets/images/'+name+'">' for name in EXPECTED)+'<p>'+LABEL+'</p>'
  self.assertTrue(require_rendered_illustrations(h))
if __name__=='__main__':unittest.main()
