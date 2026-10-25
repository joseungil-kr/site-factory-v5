"""Safety-bounded release of the explicitly approved Daysky domain.

The DNS/Custom Domain changes here are limited to daysky.nalmada.net.
Always read Cloudflare state, verify V4 proof domains, then refuse conflicting
routes/domains/DNS records. No manual DNS-record write or V4 deployment.
"""
from __future__ import annotations

import json
import os
import re
import ssl
import sys
import time
import urllib.parse
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

HOST = "daysky.nalmada.net"
ORIGIN = "https://" + HOST
WORKER = "sfv5-daysky-preview"
PREVIEW = "https://" + WORKER + ".joseungil.workers.dev"
ZONE = "nalmada.net"
V4_PROOF = {
    "flower-a.fwith.kr": "flower-matrix-a-prod",
    "flower-b.fwith.kr": "flower-matrix-b-prod",
}
OUT = Path("reports/daysky/public-launch-readback.json")


def cloudflare(method, path, payload=None):
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not token:
        raise RuntimeError("CLOUDFLARE_API_TOKEN missing")
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    data = json.dumps(payload, separators=(",", ":")).encode() if payload is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = Request("https://api.cloudflare.com/client/v4" + path,
                  headers=headers, data=data, method=method)
    try:
        with urlopen(req, timeout=35) as response:
            result = json.load(response)
    except HTTPError as exc:
        raise RuntimeError("Cloudflare " + method + " " + path.split("?")[0]
                           + " HTTP " + str(exc.code)) from None
    if result.get("success") is not True:
        errors = [(e.get("code"), e.get("message")) for e in result.get("errors", [])]
        raise RuntimeError("Cloudflare " + method + " failed: " + str(errors))
    if (result.get("result_info") or {}).get("total_pages", 1) > 1:
        raise RuntimeError("Unexpected Cloudflare pagination; aborting")
    return result.get("result")


def authorized_account_and_zone():
    configured = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    if configured:
        if not re.fullmatch(r"[0-9a-fA-F]{32}", configured):
            raise RuntimeError("CLOUDFLARE_ACCOUNT_ID malformed")
        candidate_accounts = [configured]
    else:
        candidate_accounts = [x["id"] for x in cloudflare("GET", "/accounts")]
    matches = []
    for account in candidate_accounts:
        if not re.fullmatch(r"[0-9a-fA-F]{32}", account):
            continue
        try:
            domains = cloudflare("GET", "/accounts/" + account + "/workers/domains")
        except RuntimeError:
            continue
        if all(any(d.get("hostname") == hostname and d.get("service") == service
                   for d in domains) for hostname, service in V4_PROOF.items()):
            matches.append((account, domains))
    if len(matches) != 1:
        raise RuntimeError("Could not uniquely prove original Cloudflare account")
    account, domains = matches[0]
    zones = cloudflare("GET", "/zones?name=" + urllib.parse.quote(ZONE) + "&per_page=50")
    exact = [z for z in zones if z.get("name") == ZONE
             and z.get("account", {}).get("id") == account and z.get("status") == "active"]
    if len(exact) != 1:
        raise RuntimeError("Authorized account does not own exactly one active nalmada.net zone")
    conflicting = [d for d in domains if d.get("hostname") == HOST and d.get("service") != WORKER]
    if conflicting:
        raise RuntimeError("daysky.nalmada.net already belongs to a different Worker")
    if sum(d.get("hostname") == HOST for d in domains) > 1:
        raise RuntimeError("Duplicate Cloudflare custom domain records")
    return account, exact[0], domains


def check_empty_hostname(account, zone, existing):
    if existing:
        return "existing-correct-worker"
    try:
        rows = cloudflare("GET", "/zones/" + zone["id"] + "/dns_records?name="
                         + urllib.parse.quote(HOST) + "&per_page=100")
        if rows:
            raise RuntimeError("Existing DNS record blocks new daysky domain attach")
        return "api-empty"
    except RuntimeError as exc:
        if "HTTP 403" not in str(exc):
            raise
    for kind in ("A", "AAAA", "CNAME", "TXT"):
        query = ("https://cloudflare-dns.com/dns-query?name=" + HOST + "&type=" + kind)
        req = Request(query, headers={"Accept": "application/dns-json",
                                     "User-Agent": "Daysky-Official-Domain-Check/1"})
        with urlopen(req, timeout=25) as response:
            answer = json.load(response)
        if answer.get("Status") not in (0, 3) or answer.get("Answer"):
            raise RuntimeError("Public DNS record or lookup problem: " + kind)
    return "public-dns-empty; api-dns-read-unavailable"


def request_url(origin, path, maximum=1_000_000):
    req = Request(origin + path, headers={"User-Agent": "Daysky-Public-Verification/1"})
    try:
        with urlopen(req, timeout=28) as r:
            return r.status, r.headers, r.read(maximum)
    except HTTPError as exc:
        return exc.code, exc.headers, exc.read(maximum)


def live_checks():
    report = {"host": HOST, "worker": WORKER, "origin": ORIGIN,
              "verified": False, "pages": [], "indexing": False}
    probes = ("/", "/2.html", "/19.html", "/29.html")
    for path in probes:
        status, headers, raw = request_url(ORIGIN, path)
        html = raw.decode("utf-8", "replace")
        assert status == 200, (path, status)
        assert "noindex" not in headers.get("X-Robots-Tag", "").lower(), ("X-robots", path)
        assert '<meta name="robots" content="index,follow">' in html, ("meta index", path)
        assert '<link rel="canonical" href="' + ORIGIN + path + '">' in html, ("canonical", path)
        assert "당일스카이" in html and "010-5322-1952" in html, ("brand and phone", path)
        assert "영진" not in html and "1844-0644" not in html and "fwith.co.kr" not in html
        report["pages"].append({"path": path, "http": status, "indexable": True})
    status, headers, body = request_url(ORIGIN, "/404-daysky-public-check.html", 200_000)
    assert status == 404, ("missing URL", status)
    assert '<meta name="robots" content="noindex,nofollow">' in body.decode("utf-8","replace")
    assert "noindex" in headers.get("X-Robots-Tag", "").lower()
    status, headers, body = request_url(ORIGIN, "/robots.txt", 100_000)
    assert status == 200
    robots = body.decode("utf-8", "replace")
    assert "Allow: /" in robots and "Disallow: /" not in robots
    assert "Sitemap: " + ORIGIN + "/sitemap.xml" in robots
    status, headers, body = request_url(ORIGIN, "/sitemap.xml")
    assert status == 200
    xml = ET.fromstring(body)
    urls = [e.text for e in xml.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    assert len(urls) == 29 and len(set(urls)) == 29
    assert urls[0] == ORIGIN + "/" and urls[-1] == ORIGIN + "/29.html"
    for name in ("skycar-hero.webp", "skycar-facade.webp", "skycar-truck.webp"):
        status, headers, raw = request_url(ORIGIN, "/assets/images/" + name, 200_000)
        assert status == 200 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP", name
    status, headers, _ = request_url(PREVIEW, "/")
    assert status == 200 and "noindex" in headers.get("X-Robots-Tag", "").lower()
    status, _, body = request_url(PREVIEW, "/robots.txt", 100_000)
    assert status == 200 and "Disallow: /" in body.decode("utf-8","replace")
    report.update({"verified": True, "indexing": True, "sitemapUrls": len(urls),
                   "previewNoindex": True, "ownerPhotos": 3,
                   "v4WorkersUntouched": True})
    return report


def save(data):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "preflight"
    account, zone, domains = authorized_account_and_zone()
    existing = [d for d in domains if d.get("hostname") == HOST]
    dns = check_empty_hostname(account, zone, existing)
    if command == "preflight":
        result = {"host": HOST, "worker": WORKER, "dnsCheck": dns,
                  "zoneActive": True, "existingBindingCorrect": bool(existing),
                  "v4WorkersUntouched": True}
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
                f.write("account=" + account + "\n")
        save({"preflight": result})
        print("DAYSKY_SAFE_PREFLIGHT=" + json.dumps(result, ensure_ascii=False))
        return
    if command != "attach-and-verify":
        raise RuntimeError("Unknown command")
    # Exact V5 Worker must already contain tested indexable assets.
    if not existing:
        result = cloudflare("PUT", "/accounts/" + account + "/workers/domains",
                            {"hostname": HOST, "service": WORKER,
                             "zone_id": zone["id"], "enabled": True})
        if result.get("hostname") != HOST or result.get("service") != WORKER:
            raise RuntimeError("Cloudflare bound unexpected Worker")
    after = cloudflare("GET", "/accounts/" + account + "/workers/domains")
    matched = [d for d in after if d.get("hostname") == HOST]
    if len(matched) != 1 or matched[0].get("service") != WORKER:
        raise RuntimeError("Cloudflare domain binding readback mismatch")
    if not all(any(d.get("hostname") == host and d.get("service") == svc for d in after)
               for host, svc in V4_PROOF.items()):
        raise RuntimeError("Unexpected V4 production Worker binding changes")
    last = None
    for attempt in range(1, 21):
        try:
            report = live_checks()
            report.update({"checkAttempt": attempt,
                           "boundToExpectedWorker": True})
            save(report)
            print("DAYSKY_PUBLIC_SITE_VERIFIED=" + json.dumps(report, ensure_ascii=False))
            return
        except (AssertionError, URLError, HTTPError, ssl.SSLError,
                ValueError, ET.ParseError, OSError) as error:
            last = str(error)[:220]
            print("Public HTTPS/asset propagation check " + str(attempt)
                  + "/20: " + last, flush=True)
            if attempt < 20:
                time.sleep(12)
    save({"host": HOST, "worker": WORKER, "domainBindingConfirmed": True,
          "liveVerified": False, "lastError": last,
          "v4WorkersUntouched": True})
    raise RuntimeError("Daysky public HTTP readback failed after 20 bounded retries")


if __name__ == "__main__":
    main()
