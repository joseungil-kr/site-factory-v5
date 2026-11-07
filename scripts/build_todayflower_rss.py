"""Generate a valid, full-content RSS 2.0 feed from actual Todayflower HTML.

No invented publication dates, branch-specific host claims, or unrelated sites.
Production release must execute this after building the pinned Todayflower output.
"""
from __future__ import annotations

from html.parser import HTMLParser
import hashlib
from pathlib import Path
import xml.etree.ElementTree as ET

from v5.config import ROOT, read_site

SITE = "todayflower-nalmada"
DOMAIN = "https://todayflower.nalmada.net"
CONTENT = "http://purl.org/rss/1.0/modules/content/"
ATOM = "http://www.w3.org/2005/Atom"
ET.register_namespace("content", CONTENT)
ET.register_namespace("atom", ATOM)


class Main(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.depth = 0
        self.buffer = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if self.depth == 0 and tag == "main" and attr.get("id") == "main":
            self.depth = 1
        elif self.depth:
            self.depth += 1
        if self.depth:
            raw = self.get_starttag_text()
            self.buffer.append(raw or "<" + tag + ">")

    def handle_startendtag(self, tag, attrs):
        if self.depth:
            self.buffer.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if self.depth:
            self.buffer.append("</" + tag + ">")
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.buffer.append(data)

    def handle_entityref(self, name):
        if self.depth:
            self.buffer.append("&" + name + ";")

    def handle_charref(self, name):
        if self.depth:
            self.buffer.append("&#" + name + ";")


def sample_pages(pages, limit=50):
    # Dates are not established; this is a deterministic geographic / intent
    # selection of actual pages, not an invented "latest articles" feed.
    result = {}
    def add(page):
        result[page["number"]] = page

    bynum = {p["number"]: p for p in pages}
    for n in (1, 2, 3, 28, 29, 34, 403, 405, 2500, 5071):
        add(bynum[n])
    national = pages[33:]
    def order(page):
        return hashlib.sha256(("todayflower-rss-v1:" + page["id"]).encode()).digest()
    for province in sorted({p["region"].split()[0] for p in national}):
        add(min((p for p in national if p["region"].split()[0] == province), key=order))
    for topic in sorted({p["topic"] for p in national}):
        add(min((p for p in national if p["topic"] == topic), key=order))
    for page in sorted(national, key=order):
        if len(result) >= limit:
            break
        add(page)
    if len(result) != limit:
        raise AssertionError(("RSS sample mismatch", len(result), limit))
    return sorted(result.values(), key=lambda p:p["number"])


def generate(root: Path = ROOT):
    d = read_site(SITE)
    pages = d["pages"]
    assert len(pages) == 5070
    output = root / "dist" / SITE
    assert output.is_dir(), "Todayflower output must be built before RSS"
    if (output / "sitemap.xml").exists():
        raise AssertionError("Do not convert preview output to indexable mode")
    chosen = sample_pages(pages)
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    for key, value in (("title", "오늘꽃배달 상품 선택·주문 안내"),
                       ("link", DOMAIN + "/"),
                       ("description", "꽃다발·화분·축하화환·근조화환 상품 선택과 주문 정보"),
                       ("language", "ko-KR")):
        ET.SubElement(channel, key).text = value
    ET.SubElement(channel, f"{{{ATOM}}}link", {
        "href": DOMAIN + "/rss.xml", "rel": "self", "type": "application/rss+xml"
    })
    for page in chosen:
        number = page["number"]
        path = "/" if number == 1 else "/" + str(number) + ".html"
        name = "index.html" if number == 1 else str(number) + ".html"
        source = (output / name).read_text(encoding="utf-8")
        parser = Main()
        parser.feed(source)
        body = "".join(parser.buffer)
        if not body.startswith('<main id="main"') or not body.endswith("</main>"):
            raise AssertionError(("RSS main content missing",name))
        if 'href="https://fwith.co.kr/shop/item.php?it_id=' not in body:
            raise AssertionError(("RSS product path missing",name))
        item = ET.SubElement(channel, "item")
        url = DOMAIN + path
        ET.SubElement(item, "title").text = page["title"]
        ET.SubElement(item, "link").text = url
        ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = url
        ET.SubElement(item, "category").text = page["topic"]
        ET.SubElement(item, "description").text = page["intro"]
        ET.SubElement(item, f"{{{CONTENT}}}encoded").text = body
        # Source does not establish publication dates. No pubDate fabrication.
    data = ET.tostring(rss, encoding="utf-8", xml_declaration=True)
    path = output / "rss.xml"
    path.write_bytes(data)
    check = ET.fromstring(path.read_bytes())
    items = check.find("channel").findall("item")
    assert len(items) == 50
    assert len({i.findtext("link") for i in items}) == 50
    for item in items:
        assert item.find("pubDate") is None
        assert item.findtext("link") == item.findtext("guid")
        assert item.findtext(f"{{{CONTENT}}}encoded").startswith('<main id="main"')
    print("TODAYFLOWER_RSS50_FULL_CONTENT_XML_VALID",len(items),len(data),
          hashlib.sha256(data).hexdigest())
    return path


if __name__ == "__main__":
    generate()
