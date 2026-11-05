"""Patch ONLY three RSS feeds in an exact restored Clinic active-version build.

Must be used with the national builder pinned to the live deployed source
commit 32484f02e3c12e6bfcf057702041b70f66fdafe5. Any other assets
are preserved byte-for-byte and independently checked before deployment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

from rss_feed import RSS_CONTENT_NS, create_rss

HOSTS = {
    "clinicflower": "clinicflower.nalmada.net",
    "clinicopen": "clinicopen.nalmada.net",
    "clinicpresent": "clinicpresent.nalmada.net",
}


def patch(public: Path) -> dict:
    if not public.is_dir():
        raise ValueError("Public static asset directory does not exist")
    report = {"sites": {}, "onlyExpectedRSSModified": True, "rssTargets": []}
    for site, host in HOSTS.items():
        base = public / "sites" / site
        rss_file = base / "rss.xml"
        if not rss_file.is_file():
            raise ValueError("Existing RSS is not present: " + str(rss_file))
        original_bytes = rss_file.read_bytes()
        root = ET.fromstring(original_bytes)
        channel = root.find("channel")
        if channel is None or root.attrib.get("version") != "2.0":
            raise ValueError("Existing source feed is not RSS 2.0")
        if channel.findtext("link") != "https://" + host + "/":
            raise ValueError("Existing RSS is not for the target host")
        old_items = channel.findall("item")
        if len(old_items) != 50 or any(
            i.find("description") is not None or i.find(
                "{" + RSS_CONTENT_NS + "}encoded"
            ) is not None for i in old_items
        ):
            raise ValueError("Expected exactly 50 legacy RSS URL-only entries, abort")
        item_paths = []
        files: dict[str, Path] = {}
        for entry in old_items:
            url = entry.findtext("link")
            parsed = urlsplit(url or "")
            if (parsed.scheme != "https" or parsed.hostname != host or parsed.query
                    or parsed.fragment or entry.findtext("guid") != url):
                raise ValueError("RSS legacy item is missing a valid self-hosted URL")
            path = parsed.path
            file = base / path.lstrip("/")
            if not file.is_file():
                raise ValueError("RSS references nonexistent public article " + path)
            item_paths.append(path)
            files[path] = file
        result, stats = create_rss(
            host=host,
            channel_title=channel.findtext("title") or "",
            channel_description=channel.findtext("description") or "",
            paths=item_paths,
            page_files=files,
            require_public_canonical=True,
        )
        newitems = ET.fromstring(result).find("channel").findall("item")
        if [i.findtext("link") for i in old_items] != [i.findtext("link") for i in newitems]:
            raise ValueError("RSS source URL membership changed")
        if len(result) >= 10_000_000:
            raise ValueError("RSS exceeds Naver feed submission limit")
        rss_file.write_bytes(result)
        report["sites"][site] = {
            **stats,
            "oldBytes": len(original_bytes),
            "oldSHA256": hashlib.sha256(original_bytes).hexdigest(),
            "newSHA256": hashlib.sha256(result).hexdigest(),
            "canonicalURLsPreserved": True,
            "sourceItemsAlreadyHadFullBodies": False,
        }
        report["rssTargets"].append(f"sites/{site}/rss.xml")
        print("CLINIC_RSS_UPDATED_ONLY=" + json.dumps(report["sites"][site], ensure_ascii=False))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    data = patch(args.public.resolve())
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    if args.receipt.exists():
        raise RuntimeError("Refusing to overwrite existing patch evidence")
    args.receipt.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("CLINIC_RSS_THREE_FEEDS_UPDATED_NO_HTML_WRITES")
