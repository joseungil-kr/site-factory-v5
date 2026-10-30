"""Focused noindex pilot gate; never falls back to placeholder assets."""
import ast, hashlib, json, subprocess, sys, unittest
from pathlib import Path

BASE=Path(__file__).resolve().parent
IMAGES=['funeral-wreath.webp','celebration-wreath.webp','flower-detail.webp','ribbon-guide.webp','florist-preparation.webp']
PAGES=['ansan/index.html','ansan/sangnok/index.html','ansan/sangnok/bono/index.html']

class PilotQA(unittest.TestCase):
    def test_python_compiles(self):
        ast.parse((BASE/'build.py').read_text(encoding='utf-8'),filename='build.py')
    def test_real_images_exist(self):
        missing=[name for name in IMAGES if not (BASE/'assets'/name).is_file()]
        self.assertFalse(missing,'BINARY_ASSETS_MISSING: '+', '.join(missing))
        from PIL import Image
        manifest=json.loads((BASE/'image-manifest.json').read_text(encoding='utf-8'))
        files={x['filename']:x for x in manifest['images']}
        for name in IMAGES:
            image=BASE/'assets'/name
            with Image.open(image) as im:
                self.assertEqual(im.format,'WEBP')
                self.assertGreaterEqual(im.width,768)
                self.assertEqual((im.width,im.height),(files[name]['width'],files[name]['height']))
            self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(),files[name]['sha256'])
    def test_actual_build(self):
        subprocess.run([sys.executable,str(BASE/'build.py')],check=True)
        out=BASE/'dist'
        for path in PAGES:
            data=(out/path).read_text(encoding='utf-8')
            self.assertEqual(data.count('<img '),5)
            self.assertIn('noindex,nofollow',data)
            self.assertEqual(data.count('shop/item.php?it_id='),5)
        self.assertFalse((out/'sitemap.xml').exists())
        self.assertEqual((out/'robots.txt').read_text(),'User-agent: *\\nDisallow: /\\n')

if __name__=='__main__':unittest.main()
