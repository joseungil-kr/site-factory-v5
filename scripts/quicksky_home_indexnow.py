"""Explicit Quicksky homepage-only IndexNow release; bulk configuration stays disabled."""
import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from xml.etree import ElementTree as ET
from scripts.verify_quicksky_home_release import verify, read, PUBLIC

ROOT = Path(__file__).resolve().parents[1]

def key_and_scope():
    site = json.loads((ROOT / "sites/quicksky/site.json").read_text(encoding="utf-8"))
    if not (site["domain"] == PUBLIC and site["homeIndexingApproved"] is True
            and site["homeIndexingScope"] == "quicksky-home-1-20261027"
            and site["publishEnabled"] is False and site["publicIndexingApproved"] is False
            and site["indexNow"] == {"enabled": False, "key": None}):
        raise ValueError("Exact homepage-only approval required; bulk IndexNow must remain disabled")
    key = (ROOT / "sites/quicksky/home-indexnow-key.txt").read_text().strip()
    if not re.fullmatch(r"[a-f0-9]{32}", key):
        raise ValueError("Invalid public verification key")
    return key

def prepare():
    key = key_and_scope()
    root = ROOT / "dist/quicksky"
    urls = [x.text for x in ET.parse(root / "sitemap.xml").findall(
        ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    if urls != [PUBLIC + "/"]:
        raise ValueError("Only homepage sitemap permitted")
    (root / (key + ".txt")).write_text(key + "\n", encoding="utf-8")
    return {"keyFilePrepared": True, "urlCount": 1, "submitted": False}

def submit(receipt):
    if receipt.exists():
        raise ValueError("Receipt already exists; inspect it instead of resubmitting")
    if os.environ.get("GITHUB_RUN_ATTEMPT", "1") != "1":
        raise ValueError("Automatic rerun submission forbidden; inspect previous receipt")
    key = key_and_scope()
    proof = verify()
    if proof["publicSitemapUrls"] != 1 or proof["regionsIndexable"]:
        raise ValueError("Live homepage-only verification failed")
    status, _, body = read(PUBLIC, "/" + key + ".txt")
    if status != 200 or body.decode("utf-8").strip() != key:
        raise ValueError("Public key file verification failed")
    payload = {"host": "quicksky.nalmada.net", "key": key,
               "keyLocation": PUBLIC + "/" + key + ".txt", "urlList": [PUBLIC + "/"]}
    report = {"urlList": payload["urlList"], "keyLocation": payload["keyLocation"],
              "attemptedAt": datetime.now(timezone.utc).isoformat(),
              "runId": os.environ.get("GITHUB_RUN_ID"), "outcome": "uncertain",
              "indexingProven": False, "liveProof": proof}
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    request = Request("https://api.indexnow.org/indexnow",
                      data=json.dumps(payload).encode(),
                      headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try:
        with urlopen(request, timeout=90) as response:
            code = response.status
            response_body = response.read(1000).decode("utf-8", "replace")
    except HTTPError as error:
        code = error.code
        response_body = error.read(1000).decode("utf-8", "replace")
    # Transport errors deliberately leave an uncertain receipt and are never retried.
    report.update(http=code, response=response_body,
                  outcome={200: "received", 202: "received-key-validation-pending"}.get(code, "rejected"))
    receipt.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if code not in (200, 202):
        raise RuntimeError(f"IndexNow HTTP {code}; receipt saved, no retry")
    return {"http": code, "outcome": report["outcome"], "urlCount": 1, "indexingProven": False}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "submit"])
    parser.add_argument("--receipt", type=Path, default=Path("quicksky-home-indexnow-receipt.json"))
    args = parser.parse_args()
    print(json.dumps(prepare() if args.action == "prepare" else submit(args.receipt)))
