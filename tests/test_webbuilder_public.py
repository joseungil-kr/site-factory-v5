import hashlib
import unittest
import xml.etree.ElementTree as ET
from scripts import build_webbuilder as b


class PublicModeTest(unittest.TestCase):
    def test_modes_preserve_content_and_assets(self):
        b.build()
        out = b.DEFAULT_OUTPUT
        preview = {p.relative_to(out).as_posix(): p.read_text(encoding="utf-8") for p in out.rglob("*.html")}
        hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (out / "assets/images").glob("*.webp")}
        self.assertEqual(len(preview), 43)
        self.assertEqual(len(hashes), 5)
        self.assertFalse((out / "sitemap.xml").exists())
        self.assertIn("Disallow: /", (out / "robots.txt").read_text())
        b.build(mode="public")
        urls = [x.text for x in ET.parse(out / "sitemap.xml").findall(".//{*}loc")]
        self.assertEqual(len(set(urls)), 42)
        for relative, old in preview.items():
            new = (out / relative).read_text(encoding="utf-8")
            if relative == "404.html":
                self.assertEqual(old, new)
                continue
            path = "/" if relative == "index.html" else "/" + relative.removesuffix("index.html")
            canonical = '<link rel="canonical" href="' + b.DOMAIN + path + '">'
            self.assertEqual(new.count(canonical), 1)
            self.assertIn(b.DOMAIN + path, urls)
            tag = '<meta name="naver-site-verification" content="1992f8e06229005ed7038234611e654b31db4dbf" />'
            self.assertEqual(new.count(tag), 1 if relative == "index.html" else 0)
            self.assertNotIn(tag, old)
            new = new.replace(tag, "")
            self.assertEqual(new.replace(canonical, "").replace('content="index,follow"', 'content="noindex,nofollow,noarchive"'), old)
        self.assertEqual(hashes, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (out / "assets/images").glob("*.webp")})
        self.assertIn("Allow: /", (out / "robots.txt").read_text())
        b.build()
        self.assertFalse((out / "sitemap.xml").exists())


if __name__ == "__main__":
    unittest.main()

