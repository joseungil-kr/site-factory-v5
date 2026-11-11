"""Fail-closed Todayflower isolated editorial evidence; never deploy.

Evidence is generated from the current branch's original V5 site loader.
The full 333-page same-intent comparison and 51+51 actual HTML checks are
separate from the pre-existing official QA and manual editorial approval.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

from v5.config import ROOT, read_site
from v5.audit import grams
from scripts.audit_todayflower_customer import pick_sample

SITE = "todayflower-nalmada"
REPORT = ROOT / "reports" / SITE / "semantic-isolated-qa.json"
DIST = ROOT / "dist" / SITE
LIMIT = 0.49


def article(page):
    return " ".join([page["intro"]] + [s["paragraph"] for s in page["sections"]])


def score(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def main():
    source = read_site(SITE)
    pages = source["pages"]
    assert len(pages) == 5070
    assert not source["site"]["publishEnabled"]
    assert not source["site"]["indexNow"]["enabled"]
    by_number = {p["number"]: p for p in pages}
    assert len(by_number) == 5070 and 404 not in by_number
    event = [p for p in pages[33:] if p["topic"] == "행사장 꽃 반입"]
    assert len(event) == 333, len(event)
    population = [(p, grams(article(p))) for p in event]
    violations = []
    maximum = (0.0, None, None)
    for i, (pa, ga) in enumerate(population):
        for pb, gb in population[i + 1:]:
            value = score(ga, gb)
            if value > maximum[0]:
                maximum = (value, pa["number"], pb["number"])
            if value >= LIMIT:
                violations.append({"left": pa["number"], "right": pb["number"],
                                   "similarity": round(value, 7)})
    target = score(grams(article(by_number[2412])), grams(article(by_number[2852])))
    fixed = pick_sample(pages)
    assert len(fixed) == 51
    salt = "todayflower-extra-20261111:"
    exclude = {p["id"] for p in fixed}
    extras = sorted((p for p in pages if p["id"] not in exclude),
                    key=lambda p: hashlib.sha256((salt + p["id"]).encode()).digest())[:51]
    assert len(extras) == 51 and all(x["id"] not in exclude for x in extras)
    samples = []
    for group, selected in (("fixed", fixed), ("additional", extras)):
        for p in selected:
            file = DIST / ("index.html" if p["number"] == 1 else f'{p["number"]}.html')
            html = file.read_text(encoding="utf-8")
            assert '<meta name="robots" content="noindex,nofollow">' in html, p["number"]
            assert 'rel="canonical"' not in html, p["number"]
            assert '<h1>' in html, p["number"]
            assert "fwith.co.kr/shop/item.php?it_id=" in html, p["number"]
            samples.append({"group": group, "number": p["number"], "region": p["region"],
                            "intent": p["topic"], "htmlFile": file.name,
                            "sha256": hashlib.sha256(html.encode()).hexdigest(),
                            "intro": p["intro"], "sections": p["sections"],
                            "faq": p["faq"]})
    report = {
        "source": "Current branch's generated V5 pages, not older deployed ZIP",
        "publishAllowed": False, "population": len(pages),
        "sameIntent": "행사장 꽃 반입", "sameIntentPages": len(event),
        "sameIntentPairs": len(event) * (len(event)-1) // 2,
        "limitExclusive": LIMIT, "aboveLimitCount": len(violations),
        "maximum": maximum, "reproducedTarget2412_2852": target,
        "fixedSample": len(fixed), "additionalSample": len(extras),
        "samples": samples, "firstViolations": violations[:100],
        "fullPass": not violations and target < LIMIT,
        "humanEditorialApproved": False,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("TODAYFLOWER_SEMANTIC_SUMMARY " + json.dumps({
        "total":len(pages), "sameIntentPages": len(event), "pairs": report["sameIntentPairs"],
        "violations": len(violations), "max": maximum,
        "pair2412_2852": target, "fixed":len(fixed), "additional":len(extras)
    }, ensure_ascii=False), flush=True)
    if not report["fullPass"]:
        raise SystemExit("FAIL: semantic 49% strict gate failed (report saved)")


if __name__ == "__main__":
    main()
