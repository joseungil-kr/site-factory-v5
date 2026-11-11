"""Offline fixed 50-page editorial audit of *generated HTML*, never a deploy job.

Requires the pinned official ZIP; expand_lower.main verifies its SHA-256.
Reports and snapshots are written outside the live deploy path.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict, Counter
from html.parser import HTMLParser
from pathlib import Path
import expand_lower

SEED = "wreathprice-qa-20261111"
PRODUCTS = dict(B201="59,000원", B203="79,000원", B205="109,000원",
                C205="149,000원", C030="200,000원")

class HTMLFacts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.meta = []
        self.images = []
        self.text = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a": self.links.append(d.get("href", ""))
        if tag == "img": self.images.append(d.get("src", ""))
        if tag == "meta" and d.get("name") == "robots":
            self.meta.append(d.get("content", ""))
    def handle_data(self, data):
        self.text.append(data)

def rank(row):
    return hashlib.sha256((SEED + "|" + row["code"]).encode()).hexdigest()

def fixed_sample(records):
    groups = defaultdict(list)
    for r in records:
        groups[r["province"]].append(r)
    chosen = {}
    for province, group in sorted(groups.items()):
        for suffix in ("동", "읍", "면"):
            eligible = [r for r in group if r["suffix"] == suffix]
            if eligible:
                r = min(eligible, key=rank)
                chosen[r["code"]] = r
    for r in sorted(records, key=rank):
        if len(chosen) >= 50: break
        chosen.setdefault(r["code"], r)
    assert len(chosen) == 50
    return sorted(chosen.values(), key=lambda r: (r["province"],r["suffix"],r["code"]))

def audit(archive, evidence):
    report = expand_lower.main(archive)
    assert report["grandTotalHTML"] == 4935
    assert report["verifiedDeliveryAreas"] == 0
    root = expand_lower.OUT
    selected = fixed_sample(report["localities"])
    evidence.mkdir(parents=True, exist_ok=True)
    snapshots = evidence / "html"
    snapshots.mkdir(exist_ok=True)
    rows, signatures = [], []
    for r in selected:
        path = root / "locality" / (r["code"] + ".html")
        body = path.read_text(encoding="utf-8")  # actual generator output
        (snapshots / path.name).write_text(body,encoding="utf-8")
        facts = HTMLFacts()
        facts.feed(body)
        rendered = " ".join(facts.text)
        # Remove only identifying administrative names; does not imply semantic uniqueness.
        signature = rendered.replace(r["name"], "[지역명]").replace(r["parentName"], "[상위지역]")
        signatures.append(signature)
        sku_links = {s: sum("shop/item.php?it_id=" + s in u for u in facts.links)
                     for s in PRODUCTS}
        correct = (all(count == 1 for count in sku_links.values())
                   and all(p in rendered for p in PRODUCTS.values()))
        guarded = (facts.meta == ["noindex,nofollow"]
                   and "배송 가능 여부" in rendered
                   and "최종" in rendered)
        usable = ("수령 시설" in rendered and "주소" in rendered
                  and "리본" in rendered and "주문" in rendered)
        # Evidence-sensitive gate: a shared template cannot pass as a local editorial page.
        utility = 20 if usable else 0
        accuracy = 20 if guarded else 0
        commerce = 25 if correct else 0
        rows.append(dict(code=r["code"],name=r["name"],province=r["province"],
                         suffix=r["suffix"],html_path="html/"+path.name,
                         html_sha256=hashlib.sha256(body.encode()).hexdigest(),
                         utility=utility,accuracy=accuracy,semantic_uniqueness=0,
                         product_price_links=commerce,score=utility+accuracy+commerce,
                         disposition="FAIL: no verified regional service evidence",
                         reason="Common price/FAQ template; shipping coverage and fees unverified"))
    # Same-purpose locality repetition is a source property, not a hash uniqueness test.
    normalized_repeats = len(signatures)-len(set(signatures))
    with (evidence/"scores.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys())
        writer.writeheader();writer.writerows(rows)
    summary = dict(source_archive_sha256=report["archiveSHA256"],
                   total_generated_html=report["grandTotalHTML"],
                   fixed_sample_seed=SEED, sample_count=len(rows),
                   provinces=len({r["province"] for r in rows}),
                   suffix_counts=dict(Counter(r["suffix"] for r in rows)),
                   sampled_actual_html_read=50, normalized_repeated_count=normalized_repeats,
                   pass_count=0, index_eligible=0, noindex=True,
                   sources="Pinned official region ZIP + local generator output",
                   note="Prices are historical reference values, not live checkout validation")
    (evidence/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False))
    return summary

if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive",type=Path,required=True)
    ap.add_argument("--evidence",type=Path,required=True)
    args=ap.parse_args()
    audit(args.archive,args.evidence)
