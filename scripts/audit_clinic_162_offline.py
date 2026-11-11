"""Read-only deterministic 54 x 3 editorial audit of an isolated Clinic build.

Usage: python scripts/audit_clinic_162_offline.py DIST_DIR --output REPORT.json
DIST_DIR should contain public/sites/{clinicflower,clinicopen,clinicpresent}/r/*.html.
This script neither builds nor deploys; scores are rule-based screening, not human approval.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

SITES = ("clinicflower", "clinicopen", "clinicpresent")
FILLERS = (
    "상황에 맞지 않는 선물보다 받는 곳의 실제 여건을 먼저 살펴보는 편이 좋습니다.",
    "받는 분이 편한 날짜와 수령할 위치를 함께 알려주세요.",
)
UNSUPPORTED = ("무료배송 보장", "전국 당일배송 보장", "100% 당일 도착", "배송 완료 사례")
SHOPPING_TERMS = ("화분", "식물", "관엽", "분갈이", "물주기")
class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.links = []
        self.images = []
        self.paragraphs = []
        self._paragraph = None
        self.h1 = 0
        self.phone = 0
        self.seen_text = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            self.meta.setdefault(a.get("property") or a.get("name"), []).append(a.get("content"))
        elif tag == "link":
            self.links.append(a)
        elif tag == "img":
            self.images.append(a)
        elif tag == "h1":
            self.h1 += 1
        elif tag == "a" and a.get("href") == "tel:1844-0644":
            self.phone += 1
        elif tag == "p":
            self._paragraph = []
    def handle_data(self, data):
        self.seen_text.append(data)
        if self._paragraph is not None:
            self._paragraph.append(data)
    def handle_endtag(self, tag):
        if tag == "p" and self._paragraph is not None:
            self.paragraphs.append(" ".join("".join(self._paragraph).split()))
            self._paragraph = None

def sample(paths, count=54):
    assert len(paths) == 5034, ("regional input count", len(paths))
    ranked = sorted(paths, key=lambda p: hashlib.sha256(("clinic-editorial-20261111|" + p.name).encode()).digest())
    return sorted(ranked[:count])

def check(site, path, public):
    doc = Document()
    source = path.read_text(encoding="utf-8")
    doc.feed(source)
    sitebase = public / "sites" / site
    url = "https://" + site + ".nalmada.net/r/" + path.name
    issues = []
    if doc.h1 != 1: issues.append("H1_COUNT")
    if doc.phone < 2: issues.append("PHONE_CTA")
    if any(source.count(x) > 0 for x in UNSUPPORTED): issues.append("UNSUPPORTED_CLAIM")
    if any(source.count(x) > 0 for x in FILLERS): issues.append("EDITORIAL_FILLER")
    substantive = [p for p in doc.paragraphs if len(p) >= 40]
    if len(substantive) != len(set(substantive)): issues.append("DUPLICATE_PARAGRAPH")
    if site == "clinicpresent":
        # '화분' may occur once in an honest wreath-vs-plant comparison, but
        # plant-choice advice cannot be passed off as wreath purchasing guidance.
        if any(x in source for x in ("화분과 화환 중 받는 분에게", "금전수·녹보수의 사진과 가격을 비교", "화분을 골라보세요")):
            issues.append("WREATH_PRODUCT_CONFUSION")
    if doc.meta.get("robots") != ["index,follow"]: issues.append("ROBOTS")
    if doc.meta.get("og:url") != [url]: issues.append("OG_URL")
    if doc.meta.get("og:image") is None: issues.append("OG_IMAGE")
    if not any(a.get("rel") == "canonical" and a.get("href") == url for a in doc.links):
        issues.append("CANONICAL")
    if not doc.images or not all(a.get("alt") and a.get("width") and a.get("height") for a in doc.images):
        issues.append("VISIBLE_IMAGE")
    if site == "clinicpresent" and not any("celebration-wreath.webp" in a.get("src", "") for a in doc.images):
        issues.append("WREATH_IMAGE")
    # Explicit scoring rubric; pass requires no automated failures. Editorial
    # customer usefulness and verified seller product availability remain human review.
    score = max(0, 100 - 15 * len(issues))
    return {"site":site, "path":path.relative_to(sitebase).as_posix(), "score":score,
            "automatedPass":not issues and score >= 90, "issues":issues,
            "paragraphs":len(doc.paragraphs), "images":len(doc.images),
            "phoneLinks":doc.phone, "customerUsefulnessHumanReviewed":False,
            "retailProductPriceAndLinkHumanReviewed":False}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dist", type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    public = args.dist / "public"
    rows = []
    for site in SITES:
        sitebase = public / "sites" / site
        paths = list((sitebase / "r").glob("*.html"))
        for file in sample(paths):
            rows.append(check(site, file, public))
    result = {"scope": "pinned isolated build; not current live byte parity",
              "sampleMethod": "sha256-ranked deterministic IDs, 54 per site",
              "sampleSize":len(rows), "countBySite":{s:sum(x["site"] == s for x in rows) for s in SITES},
              "automatedFailCount":sum(not x["automatedPass"] for x in rows),
              "humanReviewed":False, "releaseApproved":False, "rows":rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="rows"}, ensure_ascii=False))
    if result["automatedFailCount"]: raise SystemExit(1)

if __name__ == "__main__":
    main()
