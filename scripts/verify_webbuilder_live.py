"""Read-only verification of the published Webbuilder pages against the regenerated copy."""
from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from scripts.build_webbuilder import DOMAIN, ROOT, SITE, visible_copy

BASE = DOMAIN.rstrip("/")
DIST = ROOT / "dist" / "webbuilder"
REPORT = ROOT / "reports" / "webbuilder" / "live-verification.json"
USER_AGENT = "WebbuilderReadOnlyCopyAudit/1.0"


def get(url: str, timeout: int = 15):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers.items()), response.read(), None
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers.items()) if exc.headers else {}, exc.read(), "HTTPError"
    except Exception as exc:
        return None, {}, b"", type(exc).__name__ + ": " + str(exc)


def local_path(url_path: str) -> Path:
    relative = "index.html" if url_path == "/" else url_path.strip("/") + "/index.html"
    return DIST / relative


def main() -> int:
    policy = json.loads((SITE / "copy-review-policy.json").read_text(encoding="utf-8"))
    page_results = []
    all_images = set()
    forbidden_phrases = policy.get("forbiddenPhrases", [])
    forbidden_regex = policy.get("forbiddenRegex", [])

    for path in policy["samplePaths"]:
        url = BASE + path
        status, headers, body, error = get(url)
        live_html = body.decode("utf-8", errors="replace")
        live_text = visible_copy(live_html) if body else ""
        generated_file = local_path(path)
        generated_html = generated_file.read_text(encoding="utf-8") if generated_file.is_file() else ""
        generated_text = visible_copy(generated_html) if generated_html else ""
        canonical_match = re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', live_html, re.I)
        if not canonical_match:
            canonical_match = re.search(r'<link\b[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', live_html, re.I)
        robots_match = re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)["\']', live_html, re.I)
        if not robots_match:
            robots_match = re.search(r'<meta\b[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']robots["\']', live_html, re.I)
        robots_meta = robots_match.group(1).lower() if robots_match else ""
        x_robots = headers.get("X-Robots-Tag", headers.get("x-robots-tag", "")).lower()
        legacy = [x for x in forbidden_phrases if x in live_text]
        legacy.extend("regex:" + x for x in forbidden_regex if re.search(x, live_text, re.I))
        for src in re.findall(r'<img\b[^>]*src=["\']([^"\']+\.webp(?:\?[^"\']*)?)["\']', live_html, re.I):
            all_images.add(urljoin(url, src))
        page_results.append({
            "path": path,
            "url": url,
            "httpStatus": status,
            "contentType": headers.get("Content-Type", headers.get("content-type", "")),
            "bytes": len(body),
            "liveTextSha256": hashlib.sha256(live_text.encode("utf-8")).hexdigest() if live_text else None,
            "generatedTextSha256": hashlib.sha256(generated_text.encode("utf-8")).hexdigest() if generated_text else None,
            "matchesRegeneratedCopy": bool(live_text) and live_text == generated_text,
            "canonical": canonical_match.group(1) if canonical_match else None,
            "canonicalMatchesRequestedUrl": bool(canonical_match and canonical_match.group(1) == url),
            "robotsMeta": robots_meta or None,
            "indexableResponse": bool(robots_meta and "noindex" not in robots_meta and "noindex" not in x_robots),
            "phoneLinkPresent": "tel:01024900555" in live_html,
            "legacyCopyHits": legacy,
            "error": error
        })

    image_results = []
    for url in sorted(all_images):
        status, headers, body, error = get(url)
        image_results.append({
            "url": url, "httpStatus": status, "bytes": len(body),
            "contentType": headers.get("Content-Type", headers.get("content-type", "")),
            "sha256": hashlib.sha256(body).hexdigest() if body else None,
            "error": error
        })

    robots_status, robots_headers, robots_body, robots_error = get(BASE + "/robots.txt")
    robots_text = robots_body.decode("utf-8", errors="replace")
    sitemap_status, sitemap_headers, sitemap_body, sitemap_error = get(BASE + "/sitemap.xml")
    sitemap_text = sitemap_body.decode("utf-8", errors="replace")
    try:
        root = ET.fromstring(sitemap_body)
        sitemap_urls = [x.text for x in root.iter() if x.tag.endswith("loc") and x.text]
    except Exception:
        sitemap_urls = []

    all_200 = len(page_results) == len(policy["samplePaths"]) and all(x["httpStatus"] == 200 for x in page_results)
    all_match = all_200 and all(x["matchesRegeneratedCopy"] for x in page_results)
    no_legacy = all_200 and all(not x["legacyCopyHits"] for x in page_results)
    all_indexable = all_200 and all(x["indexableResponse"] and x["canonicalMatchesRequestedUrl"] for x in page_results)
    images_ok = bool(image_results) and all(x["httpStatus"] == 200 for x in image_results)
    robots_ok = robots_status == 200 and "Allow: /" in robots_text and (BASE + "/sitemap.xml") in robots_text
    sitemap_ok = sitemap_status == 200 and len(sitemap_urls) == 42 and all(BASE + p in sitemap_urls for p in policy["samplePaths"])
    if all_match and no_legacy and all_indexable and images_ok and robots_ok and sitemap_ok:
        overall = "PASS"
    elif all_200 and (not all_match or not no_legacy):
        overall = "LIVE_COPY_MISMATCH"
    elif any(x["httpStatus"] is not None for x in page_results):
        overall = "PARTIAL"
    else:
        overall = "UNVERIFIED"

    report = {
        "checkedAtUtc": datetime.now(timezone.utc).isoformat(),
        "workflowCommit": os.environ.get("GITHUB_SHA"),
        "scope": BASE,
        "readOnly": True,
        "reportOnly": True,
        "sampleCount": len(page_results),
        "overall": overall,
        "pagesAllHttp200": all_200,
        "pagesMatchRegeneratedCopy": all_match,
        "legacyCopyAbsent": no_legacy,
        "samplePagesIndexableAndCanonical": all_indexable,
        "sampleImagesAllHttp200": images_ok,
        "robotsTxt": {"httpStatus": robots_status, "allowsRoot": "Allow: /" in robots_text, "referencesSitemap": (BASE + "/sitemap.xml") in robots_text, "error": robots_error},
        "sitemap": {"httpStatus": sitemap_status, "urlCount": len(sitemap_urls), "sampleUrlsPresent": all(BASE + p in sitemap_urls for p in policy["samplePaths"]), "error": sitemap_error},
        "pages": page_results,
        "images": image_results
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
