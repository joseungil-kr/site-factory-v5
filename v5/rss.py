"""Generate RSS from an existing public sitemap and its rendered article bodies."""
from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


class Metadata(HTMLParser):
    def __init__(self, source: str):
        super().__init__()
        self.values = {}
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            self.values[attrs.get("property", attrs.get("name", ""))] = attrs.get("content", "")


def generate(out: Path, origin: str, title: str, limit: int = 50, *, body_tag: str = "main") -> dict:
    if body_tag not in ("main", "body"):
        raise ValueError("Unsupported RSS body tag")
    origin = origin.rstrip("/")
    out = out.resolve()
    urls = [n.text for n in ET.parse(out / "sitemap.xml").findall(".//{*}loc")]
    entries = []
    for url in urls:
        if urlsplit(url).netloc != urlsplit(origin).netloc:
            raise ValueError("RSS sitemap contains an external host")
        parsed = urlsplit(url)
        if re.search(r"/(admin|privacy|terms)(/|\.)", parsed.path, re.I):
            continue
        file = out / unquote(parsed.path).lstrip("/")
        if parsed.path.endswith("/"):
            file /= "index.html"
        file.resolve().relative_to(out)
        source = file.read_text(encoding="utf-8")
        metadata = Metadata(source).values
        if "noindex" in metadata.get("robots", "").lower():
            continue
        main = re.search(r"<" + body_tag + r"\b[^>]*>(.*?)</" + body_tag + ">", source, re.I | re.S)
        if not main and body_tag == "body":
            main = re.search(r"<main\b[^>]*>(.*?)</main>", source, re.I | re.S)
        if not main:
            main = re.search(r"<article\b[^>]*>(.*?)</article>", source, re.I | re.S)
        if not main:
            raise ValueError("RSS article body not found: " + url)
        body = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", main.group(1), flags=re.I | re.S)
        if not re.sub(r"<[^>]+>", "", body).strip():
            continue
        body = re.sub(r'''\b(href|src|poster)=(["'])(.*?)\2''',
                      lambda m: m[1] + '="' + html.escape(urljoin(url, html.unescape(m[3])), quote=True) + '"',
                      body, flags=re.I | re.S)
        heading = re.search(r"<h1\b[^>]*>(.*?)</h1>", source, re.I | re.S)
        heading = html.unescape(re.sub(r"<[^>]+>", "", heading[1])).strip() if heading else title
        date = metadata.get("article:published_time", "")
        published = None
        if date:
            published = datetime.fromisoformat(date.replace("Z", "+00:00"))
            if published.tzinfo is None:
                published = None
            elif published > datetime.now(timezone.utc):
                continue
        entries.append((url, heading, body, published))
        link = '<link rel="alternate" type="application/rss+xml" title="' + html.escape(title, quote=True) + '" href="' + origin + '/rss.xml">'
        if 'type="application/rss+xml"' not in source:
            if "</head>" in source:
                updated = source.replace("</head>", link + "</head>", 1)
            else:
                # HTML permits omitted head/body tags; metadata ends at the first flow element.
                updated, count = re.subn(r"<(body|main|article)\b", lambda m: link + m[0], source, count=1, flags=re.I)
                if count != 1:
                    raise ValueError("RSS discovery insertion point not found: " + url)
            file.write_text(updated, encoding="utf-8")
    entries.sort(key=lambda x: (x[3] is not None, x[3] or datetime.min.replace(tzinfo=timezone.utc)), reverse=True)
    ET.register_namespace("content", "http://purl.org/rss/1.0/modules/content/")
    root = ET.Element("rss", version="2.0")
    channel = ET.SubElement(root, "channel")
    for name, value in (("title", title), ("link", origin + "/"), ("description", title)):
        ET.SubElement(channel, name).text = value
    for url, heading, body, published in entries[:limit]:
        item = ET.SubElement(channel, "item")
        for name, value in (("title", heading), ("link", url), ("description", body), ("{http://purl.org/rss/1.0/modules/content/}encoded", body)):
            ET.SubElement(item, name).text = value
        ET.SubElement(item, "guid", isPermaLink="true").text = url
        if published:
            ET.SubElement(item, "pubDate").text = format_datetime(published)
    data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    if len(data) >= 10 * 1024 * 1024:
        raise ValueError("RSS exceeds 10MB")
    (out / "rss.xml").write_bytes(data)
    return {"items": min(len(entries), limit), "bytes": len(data), "datesOmitted": sum(x[3] is None for x in entries[:limit])}
