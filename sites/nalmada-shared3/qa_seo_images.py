"""Fail-closed 15,906-page HTML SEO + visible editorial image gate.

No structured-data injection. This checker also ensures that an OG photo is
actually present as an <img> and that the shared Worker has its raw WebP.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha1
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import re

HOSTS = {
    "clinicflower": "clinicflower.nalmada.net",
    "clinicopen": "clinicopen.nalmada.net",
    "clinicpresent": "clinicpresent.nalmada.net",
}
EXPECTED_TYPES = {
    "clinicflower": {"hero.webp", "hospital.webp", "dental.webp", "oriental.webp"},
    "clinicopen": {"hospital.webp", "dental.webp", "oriental.webp"},
    "clinicpresent": {"celebration-wreath.webp"},
}


class HeadInspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.metas = {}
        self.links = []
        self.images = []
        self.scripts = []
        self.h1 = 0
        self.h2 = 0
        self.title = 0
        self.html_lang = None
        self.calls = 0
        self.structured_data = 0

    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        if tag == "html":
            self.html_lang = a.get("lang")
        elif tag == "meta":
            key = a.get("property") or a.get("name")
            if key:
                self.metas.setdefault(key, []).append(a.get("content", ""))
        elif tag == "link":
            self.links.append(a)
        elif tag == "img":
            self.images.append(a)
        elif tag == "script":
            self.scripts.append(a)
            if a.get("type") == "application/ld+json":
                self.structured_data += 1
        elif tag == "title":
            self.title += 1
        elif tag == "h1":
            self.h1 += 1
        elif tag == "h2":
            self.h2 += 1
        elif tag == "a" and a.get("href") == "tel:1844-0644":
            self.calls += 1


def only(a, key):
    values = a.metas.get(key, [])
    assert len(values) == 1 and values[0], (key, values)
    return values[0]


def audit(root: Path) -> dict:
    public = root / "public"
    assert public.is_dir(), public
    result = {"html": {}, "images": {}, "allHTML": 0,
              "missingOG": 0, "missingImages": 0, "missingAlt": 0,
              "jsonLDGenerated": False, "pass": False}
    for site, hostname in HOSTS.items():
        sitebase = public / "sites" / site
        pages = list(sitebase.rglob("*.html"))
        assert len(pages) == 5302, (site, len(pages))
        siteimages = Counter()
        seenurls = set()
        seenTitles = set()
        for file in pages:
            rel = file.relative_to(sitebase).as_posix()
            urlpath = "/" if rel == "index.html" else "/" + rel
            absolute = "https://" + hostname + urlpath
            document = file.read_text(encoding="utf-8")
            page = HeadInspector()
            page.feed(document)
            assert page.html_lang == "ko", (site, rel)
            assert page.title == 1 and page.h1 == 1 and page.calls >= 2, (site, rel, "title/h1/call")
            assert page.structured_data == 0, (site, rel, "JSON-LD is explicitly excluded")
            assert page.h2 > 0, (site, rel, "No content subheading")
            assert only(page, "viewport").startswith("width=device-width")
            assert only(page, "robots") == "index,follow"
            description = only(page, "description")
            assert 25 <= len(description) <= 250, (site, rel, len(description))
            og_title = only(page, "og:title")
            assert og_title not in seenTitles, (site, rel, "duplicate OG title")
            seenTitles.add(og_title)
            assert only(page, "og:description") == description
            assert only(page, "og:type") == "website"
            assert only(page, "og:locale") == "ko_KR"
            assert only(page, "og:url") == absolute
            imageURL = only(page, "og:image")
            imageAlt = only(page, "og:image:alt")
            assert only(page, "twitter:card") == "summary_large_image"
            assert only(page, "twitter:title") == og_title
            assert only(page, "twitter:description") == description
            assert only(page, "twitter:image") == imageURL
            assert imageURL.startswith("https://" + hostname + "/assets/images/")
            parsed = urlsplit(imageURL)
            assert parsed.scheme == "https" and not parsed.query and not parsed.fragment
            imageName = parsed.path.rsplit("/", 1)[-1]
            assert imageName in EXPECTED_TYPES[site], (site, rel, imageName)
            assert imageAlt and ("AI 연출" in imageAlt or "연출" in imageAlt)
            imagePath = public / parsed.path.lstrip("/")
            assert imagePath.is_file() and imagePath.stat().st_size > 5000
            raw = imagePath.read_bytes()
            assert raw[:4] == b"RIFF" and raw[8:12] == b"WEBP"
            if imageName == "celebration-wreath.webp":
                gitsha = sha1((f"blob {len(raw)}" + chr(0)).encode() + raw).hexdigest()
                assert gitsha == "d54ef1dc3cb09e5d974810f6607cd18521e12b91"
            assert int(only(page, "og:image:width")) >= 768
            assert int(only(page, "og:image:height")) >= 500
            assert page.images, (site, rel, "no visible image")
            matches = [pic for pic in page.images if pic.get("src") == parsed.path]
            assert matches, (site, rel, "OG image not actually shown in HTML")
            assert all(pic.get("alt") and pic.get("alt").strip()
                       and pic.get("width") and pic.get("height") for pic in page.images)
            assert any(p.get("loading") == "eager" and p.get("fetchpriority") == "high" for p in matches)
            assert all(not u.get("data-src") for u in matches)
            if site == "clinicpresent":
                assert "화환" in imageAlt and "화분" not in imageAlt
                assert "화분" not in Path(parsed.path).stem and not any("plant" in p.get("src", "") for p in page.images)
            canons = [x.get("href") for x in page.links if x.get("rel") == "canonical"]
            assert canons == [absolute], (site, rel, "canonical")
            rss = [x.get("href") for x in page.links if x.get("type") == "application/rss+xml"]
            assert rss == ["https://" + hostname + "/rss.xml"], (site, rel, "rss auto-discovery")
            assert absolute not in seenurls
            seenurls.add(absolute)
            siteimages[imageName] += 1
        result["html"][site] = len(pages)
        result["images"][site] = dict(siteimages)
        result["allHTML"] += len(pages)
    assert result["allHTML"] == 15906
    result["pass"] = True
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("build", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    opts = parser.parse_args()
    answer = audit(opts.build)
    opts.output.parent.mkdir(parents=True, exist_ok=True)
    opts.output.write_text(json.dumps(answer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("CLINIC_SEO_IMAGE_15906_PASS " + json.dumps(answer, ensure_ascii=False))
