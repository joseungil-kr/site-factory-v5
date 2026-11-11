"""Full 5,070-URL Todayflower evidence coverage ledger, offline and nonpublishing.

Classification is an editorial proposal, not a quality pass or service proof.
Exactly-scoped SKU and venue facts must never attach to unrelated URLs.
"""
from __future__ import annotations

from collections import Counter
import csv
from hashlib import sha256
import io
import json
from pathlib import Path

from v5.config import ROOT, read_site
from v5.todayflower_evidence import load_ledger, match_specific_facts
from v5.todayflower_regions import legal_regions

SITE = "todayflower-nalmada"
REPORT_DIR = ROOT / "reports" / SITE / "evidence-coverage"
FIELDS = (
    "number", "urlPath", "pageId", "regionCode", "regionName",
    "regionLevel", "regionSourceId", "regionSourcePath", "regionSourceSha256", "regionSourceUrl", "regionSnapshotDate",
    "listedSkus", "facilityIdentity", "matchedFactIds",
    "contextFactIds", "evidenceScope", "sourceUrls", "sourceObservedAt",
    "sourcePublicationDate", "informationSufficiency", "proposedRole",
    "unmappedReason", "currentServiceVerified", "verifiedRateSku",
    "verifiedFeeKRW", "liveStockVerified",
)
REQUIRED_REGRESSIONS = (186, 3012, 2412, 2852)


def build_rows():
    data = read_site(SITE)
    site = data["site"]
    assert site["id"] == SITE and not site["publishEnabled"]
    assert site["indexNow"]["enabled"] is False
    assert site["todayflowerNational"]["previewOnly"] is True

    pages = data["pages"]
    locations = data["regions"]["regions"]
    assert len(pages) == len(locations) == 5070
    original_regions = json.loads(
        (ROOT / "sites" / SITE / "regions.json").read_text(encoding="utf-8")
    )["regions"]
    assert len(original_regions) == 33
    official = dict(legal_regions(ROOT))
    valid_codes = set(official) | {r["code"] for r in original_regions}
    assert len(official) == 5067
    ledger = load_ledger()
    sources = {s["id"]: s for s in ledger["sources"]}
    assert sources["legal_snapshot"]["sha256"] == "44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd"
    facts = ledger["facts"]
    fact_by_id = {f["id"]: f for f in facts}
    products = {p["sku"] for p in data["products"]}
    assert "B101" not in products and "C030" not in products

    # Any presence at a region code is contextual-only unless this actual
    # URL carries the exact named facility or the exact referenced SKU.
    def contextual(code):
        return sorted(f["id"] for f in facts if code in f["regionCodes"])

    rows = []
    for i, (page, location) in enumerate(zip(pages, locations)):
        n = page["number"]
        code = location["code"]
        assert page["region"] == location["name"], (n, page["region"], location["name"])
        assert code in valid_codes
        assert code == (original_regions[i]["code"] if i < 33 else page["legalCode"])
        assert len(code) == 10 and code.isdecimal()
        assert location["level"] in ("legal-dong", "municipality", "ward")
        if code in official:
            assert official[code] == location["name"]
        assert location["name"].startswith("경기도 안산시") if i < 33 else True

        skus = page["productSkus"]
        assert skus and set(skus) <= products
        # Existing URL is area + general intent, not a named-facility URL.
        facility = None
        effective_facts = {}
        for sku in skus:
            for f in match_specific_facts(
                region_code=code, sku=sku, facility=facility, ledger=ledger
            ):
                effective_facts[f["id"]] = f
        assert not effective_facts  # No current URL has B101 or a facility identity.
        context = contextual(code)
        matched = sorted(effective_facts)
        if matched:
            role = "evidence_detail"
            sufficiency = "scoped_purchase_evidence_available_not_live_verified"
            reason = ""
        elif context:
            role = "regional_navigation"
            sufficiency = "region_identity_and_context_only"
            reason = "regional_source_has_no_matching_page_sku_or_exact_facility"
        else:
            role = "general_buying_guide"
            sufficiency = "region_identity_only"
            reason = "no_page_applicable_facility_or_sku_evidence"

        # Only matched facts appear in applicable evidence columns. Merely
        # contextual seller notices are NOT represented as page-level facts.
        applied_sources = [sources[fact_by_id[fid]["sourceId"]] for fid in matched]
        applicable_fees = [fact_by_id[x] for x in matched
                           if fact_by_id[x]["kind"] == "sku_shipping_fee"]
        assert len(applicable_fees) <= 1
        if applicable_fees:
            fee = applicable_fees[0]
            assert fee["sku"] in skus and code in fee["regionCodes"]
        else:
            fee = None
        record = {
            "number": n,
            "urlPath": "/" if n == 1 else f"/{n}.html",
            "pageId": page["id"],
            "regionCode": code,
            "regionName": location["name"],
            "regionLevel": location["level"],
            "regionSourceId": "legal_snapshot",
            "regionSourcePath": "data/regions/todayflower_official_codes_20261022.zip",
            "regionSourceSha256": sources["legal_snapshot"]["sha256"],
            "regionSourceUrl": None,
            "regionSnapshotDate": "2026-10-22",
            "listedSkus": list(skus),
            "facilityIdentity": facility,
            "matchedFactIds": matched,
            "contextFactIds": context,
            "evidenceScope": (
                [dict(factId=x, regionCode=code,
                      sku=fact_by_id[x]["sku"], facility=fact_by_id[x]["facilityName"])
                 for x in matched]
            ),
            "sourceUrls": sorted({s["url"] for s in applied_sources if s["url"]}),
            "sourceObservedAt": sorted({s["observedAt"] for s in applied_sources}),
            "sourcePublicationDate": sorted({s["publicationDate"] for s in applied_sources
                                              if s["publicationDate"]}),
            "informationSufficiency": sufficiency,
            "proposedRole": role,
            "unmappedReason": reason,
            "currentServiceVerified": False,
            "verifiedRateSku": fee["sku"] if fee else None,
            "verifiedFeeKRW": fee["amountKRW"] if fee else None,
            "liveStockVerified": False,
        }
        rows.append(record)
    verify(rows, pages, ledger, official, original_regions)
    return rows, ledger


def verify(rows, pages, ledger, official, original_regions):
    assert len(rows) == len(pages) == 5070
    assert len({r["pageId"] for r in rows}) == 5070
    assert len({r["urlPath"] for r in rows}) == 5070
    assert len({r["number"] for r in rows}) == 5070
    expected = [*range(1, 404), *range(405, 5072)]
    assert [r["number"] for r in rows] == expected
    assert rows[0]["urlPath"] == "/" and "/404.html" not in {x["urlPath"] for x in rows}
    assert [x["regionCode"] for x in rows[:33]] == [r["code"] for r in original_regions]
    assert len({x["regionCode"] for x in rows}) == 5070

    facts = {f["id"]: f for f in ledger["facts"]}
    source_ids = {s["id"]: s for s in ledger["sources"]}
    for row in rows:
        code = row["regionCode"]
        assert code in official or code in {r["code"] for r in original_regions}
        assert row["regionSnapshotDate"] == "2026-10-22"
        assert row["regionSourceId"] == "legal_snapshot"
        assert row["regionSourceUrl"] is None
        assert row["regionSourceSha256"] == "44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd"
        assert row["currentServiceVerified"] is False
        assert row["liveStockVerified"] is False
        assert row["facilityIdentity"] is None
        assert len(row["matchedFactIds"]) == len(set(row["matchedFactIds"]))
        if row["proposedRole"] == "evidence_detail":
            assert row["matchedFactIds"] and row["informationSufficiency"].startswith("scoped_")
        else:
            assert not row["matchedFactIds"]
            assert not row["sourceUrls"] and not row["sourceObservedAt"]
            assert not row["sourcePublicationDate"]
            assert not row["evidenceScope"]
            assert row["verifiedRateSku"] is None and row["verifiedFeeKRW"] is None
            assert row["unmappedReason"]
        for fid in row["matchedFactIds"]:
            fact = facts[fid]
            assert code in fact["regionCodes"]
            if fact["kind"] == "sku_shipping_fee":
                assert fact["sku"] in row["listedSkus"]
            if fact["kind"] == "venue_rule":
                assert fact["facilityName"] == row["facilityIdentity"]
            assert source_ids[fact["sourceId"]]["url"] in row["sourceUrls"]
        assert not ({"ansan-daebu-b101-fee", "c030-listing"} & set(row["matchedFactIds"]))
    for n in REQUIRED_REGRESSIONS:
        row = next(r for r in rows if r["number"] == n)
        assert row["proposedRole"] == "general_buying_guide", (n, row)
        assert not row["matchedFactIds"] and not row["contextFactIds"], n
        assert row["verifiedFeeKRW"] is None
    assert Counter(x["proposedRole"] for x in rows)["evidence_detail"] == 0


def write_outputs(rows, ledger):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    counts = dict(Counter(r["proposedRole"] for r in rows))
    for role in ("evidence_detail", "regional_navigation", "general_buying_guide"):
        counts.setdefault(role, 0)
    status = Counter(r["informationSufficiency"] for r in rows)
    report = {
        "site": SITE,
        "sourceCommitNotRelease": True,
        "indexable": False,
        "qualityApproved": False,
        "eligibleDetailCountNotQualityPass": counts["evidence_detail"],
        "population": len(rows),
        "roles": counts,
        "informationSufficiency": dict(status),
        "unmappedReasons": dict(Counter(r["unmappedReason"] for r in rows)),
        "sampleChecks": [
            {k:r[k] for k in ("number", "urlPath", "regionCode",
                              "matchedFactIds", "contextFactIds", "proposedRole",
                              "unmappedReason", "verifiedFeeKRW")}
            for r in rows if r["number"] in REQUIRED_REGRESSIONS
        ],
        "sellerFactsOutsidePageScope": [
            {"id": f["id"], "scope": f["displayPolicy"], "sku": f["sku"],
             "facility": f["facilityName"], "regionCodes": f["regionCodes"]}
            for f in ledger["facts"]
        ],
        "verification": {
            "uniqueUrlPaths": len({r["urlPath"] for r in rows}),
            "uniquePageIds": len({r["pageId"] for r in rows}),
            "uniqueRegionCodes": len({r["regionCode"] for r in rows}),
            "missingRows": 0,
            "duplicatedRows": 0,
            "skuFeeTransferred": 0,
            "facilityRuleBroadcasts": 0,
            "unverifiedFactsShownAsCurrent": 0,
        },
    }
    data = json.dumps({"schemaVersion": 1, "summary": report, "rows": rows},
                      ensure_ascii=False, indent=2) + "\n"
    jpath = REPORT_DIR / "todayflower-5070-evidence-map.json"
    jpath.write_text(data, encoding="utf-8")
    # Flatten list values as JSON in CSV cells: reversible without quoting ambiguity.
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: (json.dumps(row[k], ensure_ascii=False,
                                        separators=(",", ":"))
                            if isinstance(row[k], (list, dict)) else
                            ("" if row[k] is None else
                             "false" if row[k] is False else
                             "true" if row[k] is True else str(row[k])))
                         for k in FIELDS})
    csv_text = buf.getvalue()
    cpath = REPORT_DIR / "todayflower-5070-evidence-map.csv"
    cpath.write_text(csv_text, encoding="utf-8")
    report["sha256"] = {
        "json": sha256(data.encode()).hexdigest(),
        "csv": sha256(csv_text.encode()).hexdigest()
    }
    (REPORT_DIR/"verification-summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("TODAYFLOWER_5070_COVERAGE " + json.dumps({
        "rows":len(rows),"roles":counts,"info":dict(status),
        "verification":report["verification"],"sha256":report["sha256"]
    }, ensure_ascii=False), flush=True)
    return report


def main():
    rows, ledger = build_rows()
    write_outputs(rows, ledger)


if __name__ == "__main__":
    main()
