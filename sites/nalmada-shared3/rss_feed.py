"""Build RSS 2.0 with the actual full public page body, not URL-only entries.

Naver Search Advisor feed guidance requires usable article content, and Google
Search Central accepts RSS 2.0 as a *recent-URL* sitemap alternative.

Dates are intentionally omitted when page-level publication/update timestamps
are not verifiable. The ordered 50-entry legacy selection is preserved as-is.
This tool never claims the list is chronological.
"""
from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
from typing import Mapping, Sequence
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

RSS_CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"
ET.register_namespace("content", RSS_CONTENT_NS)

TITLE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
MAIN = re.compile(r"<main\b[^>]*>.*?</main\s*>", re.IGNORECASE | re.DOTALL)
WHITESPACE = re.compile(r"\s+")


class ReadableMain(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip_depth += 1
        elif not self.skip_depth and tag in (
            "h1", "h2", "h3", "h4", "p", "li", "section", "article",
            "summary", "details", "figcaption", "br"
        ):
            self.parts.append("\n")

    def handle_endtag(self, tag: str):
        if tag in ("script", "style", "noscript") and self.skip_depth:
            self.skip_depth -= 1
        elif not self.skip_depth and tag in (
            "h1", "h2", "h3", "h4", "p", "li", "section", "article",
            "summary", "details", "figcaption"
        ):
            self.parts.append("\n")

    def handle_data(self, data: str):
        if not self.skip_depth and data.strip():
            self.parts.append(data)


def full_body_from_html(html_doc: str, host: str) -> tuple[str, str]:
    """Return human-readable full text and equivalent full HTML.

    Relative internal links/images are made absolute for a feed reader. The HTML
    is stored in content:encoded as XML-escaped text, which RSS clients decode.
    """
    matched = MAIN.search(html_doc)
    if not matched:
        raise ValueError("A real <main> body is required for every feed item")
    html_main = matched.group(0)
    body = ReadableMain()
    body.feed(html_main)
    lines = [WHITESPACE.sub(" ", section).strip()
             for section in "".join(body.parts).splitlines()]
    text = "\n".join(t for t in lines if t)
    if len(text) < 120:
        raise ValueError("RSS full-body text is unreasonably short")
    site = "https://" + host
    html_main = html_main.replace('href="/', 'href="' + site + '/')
    html_main = html_main.replace("href='/", "href='" + site + "/")
    html_main = html_main.replace('src="/', 'src="' + site + '/')
    html_main = html_main.replace("src='/", "src='" + site + "/")
    return text, html_main


def create_rss(
    *,
    host: str,
    channel_title: str,
    channel_description: str,
    paths: Sequence[str],
    page_files: Mapping[str, Path],
    require_public_canonical: bool = True,
    max_bytes: int = 9_950_000,
) -> tuple[bytes, dict]:
    if not re.fullmatch(r"(?:clinicflower|clinicopen|clinicpresent)\.nalmada\.net", host):
        raise ValueError("Unapproved Clinic feed host")
    if not paths or len(paths) > 50 or len(set(paths)) != len(paths):
        raise ValueError("RSS must have between 1 and 50 unique content URLs")
    if not channel_title or not channel_description:
        raise ValueError("RSS channel title and description are required")

    root = ET.Element("rss", {"version": "2.0"})
    chan = ET.SubElement(root, "channel")
    for key, value in (
        ("title", channel_title),
        ("link", "https://" + host + "/"),
        ("description", channel_description),
        ("language", "ko-KR"),
    ):
        ET.SubElement(chan, key).text = value
    text_lengths = []
    for path in paths:
        if (not path.startswith("/r/") or not re.fullmatch(r"/r/\d{5}\.html", path)
                or path not in page_files):
            raise ValueError("RSS path is not an existing regional HTML: " + path)
        raw_html = page_files[path].read_text(encoding="utf-8")
        expected_canonical = "https://" + host + path
        if require_public_canonical and (
            '<link rel="canonical" href="' + expected_canonical + '">' not in raw_html
            or '<meta name="robots" content="index,follow">' not in raw_html
        ):
            raise ValueError("RSS URL is not its public self-canonical: " + path)
        title_match = TITLE.search(raw_html)
        if not title_match:
            raise ValueError("Missing page <title> on RSS target")
        title = unescape(title_match.group(1)).strip()
        if not title:
            raise ValueError("Empty RSS item title")
        description, html_body = full_body_from_html(raw_html, host)
        if not (description and html_body):
            raise ValueError("Missing RSS full content")

        item = ET.SubElement(chan, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link").text = expected_canonical
        ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = expected_canonical
        ET.SubElement(item, "description").text = description
        ET.SubElement(item, "{" + RSS_CONTENT_NS + "}encoded").text = html_body
        # No pubDate: there is no independently verified publication timestamp
        # for these locality pages. Fabricating freshness would be misleading.
        text_lengths.append(len(description))

    output = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    if len(output) >= max_bytes:
        raise ValueError(f"RSS exceeds safe Naver 10 MB budget: {len(output)} bytes")
    xml = ET.fromstring(output)
    entries = xml.find("channel").findall("item")
    if len(entries) != len(paths):
        raise AssertionError("RSS item count changed during serialization")
    for entry in entries:
        if entry.findtext("link") != entry.findtext("guid"):
            raise AssertionError("RSS guid/link mismatch")
        if not entry.findtext("description") or not entry.findtext("{" + RSS_CONTENT_NS + "}encoded"):
            raise AssertionError("RSS body not serialized")
        if entry.find("pubDate") is not None:
            raise AssertionError("Unverified feed publication date must not be emitted")
        if urlsplit(entry.findtext("link")).hostname != host:
            raise AssertionError("RSS item crosses the verified site hostname")
    evidence = {
        "host": host,
        "itemCount": len(entries),
        "bytes": len(output),
        "allItemsHaveDescription": True,
        "allItemsHaveContentEncoded": True,
        "feedHasFabricatedDate": False,
        "rssItemOrderPolicy": "legacy_stable_50; not claimed as latest chronological updates",
        "minimumBodyLength": min(text_lengths),
        "maximumBodyLength": max(text_lengths),
        "sameHostAbsoluteGuid": True,
    }
    return output, evidence
