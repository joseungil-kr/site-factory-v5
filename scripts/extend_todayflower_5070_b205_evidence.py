"""Expand the verified 5,070-row QA map with pinned WreathPrice B205 evidence.

Never update production HTML. A single historic seller fee is not enough to
qualify an independent regional detail page.
"""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
from html import escape
import io
import json
from pathlib import Path

from v5.config import ROOT
from v5.todayflower_wreathprice_evidence import (
    load_pinned, map_posted_fee, SOURCE_COMMIT, SOURCE_PATH, SOURCE_GIT_BLOB_SHA
)
from scripts.audit_todayflower_5070_evidence_map import build_rows, REPORT_DIR, REQUIRED_REGRESSIONS

NAMESPACE = "wreathprice-b205-strict-v1"
EXTRA_FIELDS = (
    "wreathpriceContextIds", "wreathpriceMatchedIds", "wreathpriceScopeKind",
    "wreathpriceScopeReason", "sellerPostedFeeKRW", "sellerPostedFeeSku",
    "sellerPostedFeeSourceURL", "sellerPostedFeeSourceObservedAt",
    "sellerPostedFeePublishedAt", "sellerPostedFeeCurrentEffective",
    "sellerPostedFeeRowScope",
)
EXTRA = REPORT_DIR / "b205-pinned-extension"
ROLE_ORDER = ("evidence_detail", "regional_navigation", "general_buying_guide")


def extend_rows():
    original, _ledger = build_rows()
    evidence = load_pinned()
    result = []
    for row in original:
        mapped = map_posted_fee(
            region_code=row["regionCode"], region_name=row["regionName"],
            selected_skus=row["listedSkus"], source=evidence
        )
        out = row.copy()
        out["wreathpriceContextIds"] = mapped["contextIds"]
        out["wreathpriceMatchedIds"] = mapped["matchedIds"]
        out["wreathpriceScopeKind"] = mapped.get("scopeKind")
        out["wreathpriceScopeReason"] = mapped["reason"]
        out["sellerPostedFeeKRW"] = mapped.get("postedFeeKRW")
        out["sellerPostedFeeSku"] = mapped.get("sku")
        out["sellerPostedFeeSourceURL"] = mapped.get("sourceURL")
        out["sellerPostedFeeSourceObservedAt"] = mapped.get("sellerObservedAt")
        out["sellerPostedFeePublishedAt"] = mapped.get("sellerPublishedAt")
        out["sellerPostedFeeCurrentEffective"] = False
        out["sellerPostedFeeRowScope"] = mapped.get("sourceRowScope")
        # A seller rate alone does NOT establish locality-specific service
        # facts, independent editorial value, availability, or eligibility.
        if mapped["contextIds"]:
            out["proposedRole"] = "regional_navigation"
            if mapped["matchedIds"]:
                out["informationSufficiency"] = "exact_B205_seller_posted_fee_only_not_live"
                out["unmappedReason"] = "fee_only_insufficient_for_independent_detail"
            else:
                out["informationSufficiency"] = "historical_seller_fee_context_not_page_applicable"
                out["unmappedReason"] = mapped["reason"]
        out["currentServiceVerified"] = False
        out["liveStockVerified"] = False
        out["verifiedFeeKRW"] = None
        out["verifiedRateSku"] = None
        out["matchedFactIds"] = sorted(set(out["matchedFactIds"] + mapped["matchedIds"]))
        out["contextFactIds"] = sorted(set(out["contextFactIds"] + mapped["contextIds"]))
        if mapped["matchedIds"]:
            # A specifically scoped, non-live seller posting may be recorded
            # with its exact B205 reference in separate QA-only columns.
            assert out["sellerPostedFeeSku"] == "B205"
            assert "B205" in out["listedSkus"]
            assert out["wreathpriceScopeKind"] == "explicit_locality_row"
            assert out["sellerPostedFeeSourceURL"] == evidence["skuEvidence"]["B205"]["sourceUrl"]
            assert out["sellerPostedFeeSourceObservedAt"] == evidence["retrievedOn"]
            assert out["sellerPostedFeeCurrentEffective"] is False
        else:
            assert out["sellerPostedFeeKRW"] is None
            assert out["sellerPostedFeeSku"] is None
        result.append(out)
    validate(result, evidence)
    return result, evidence


def validate(rows, source):
    assert len(rows) == 5070
    for k in ("number", "pageId", "urlPath", "regionCode"):
        assert len({r[k] for r in rows}) == 5070, k
    assert [r["number"] for r in rows] == [*range(1,404), *range(405,5072)]
    assert len({r["pageId"] for r in rows}) == 5070
    assert sum(r["proposedRole"] == "evidence_detail" for r in rows) == 0
    assert not any(r["currentServiceVerified"] or r["liveStockVerified"] for r in rows)
    assert all(r["verifiedFeeKRW"] is None and r["verifiedRateSku"] is None for r in rows)
    indexed = {x["regionCode"]:x for x in source["postedFees"]}
    attached = set()
    for r in rows:
        code = r["regionCode"]
        m = r["wreathpriceMatchedIds"]
        contextual = r["wreathpriceContextIds"]
        assert len(contextual) <= 1 and len(m) <= 1
        if m:
            assert m == contextual
            source_row = indexed[code]
            assert source_row["regionName"] == r["regionName"]
            assert "B205" in r["listedSkus"] and r["sellerPostedFeeSku"] == "B205"
            assert r["wreathpriceScopeKind"] == "explicit_locality_row"
            assert r["sellerPostedFeeKRW"] == source_row["postedAdditionalFeeKRW"]
            assert r["sellerPostedFeeSourceURL"] == "https://fwith.co.kr/shop/item.php?it_id=B205"
            assert r["sellerPostedFeeSourceObservedAt"] == "2026-11-11"
            assert r["sellerPostedFeePublishedAt"] is None
            assert r["sellerPostedFeeCurrentEffective"] is False
            assert r["proposedRole"] == "regional_navigation"
            attached.add(code)
        else:
            assert r["sellerPostedFeeKRW"] is None
            assert r["sellerPostedFeeSku"] is None
            assert r["sellerPostedFeeSourceURL"] is None
        if contextual:
            assert code in indexed
        assert "C030" not in r["listedSkus"]
    for n in REQUIRED_REGRESSIONS:
        row = next(r for r in rows if r["number"] == n)
        assert not row["wreathpriceMatchedIds"]
        assert row["sellerPostedFeeKRW"] is None
    assert attached.issubset(set(indexed))
    assert not any(r["proposedRole"] == "evidence_detail" for r in rows)


def write_outputs(rows, source):
    EXTRA.mkdir(parents=True, exist_ok=True)
    roles = {role:sum(r["proposedRole"]==role for r in rows) for role in ROLE_ORDER}
    matches = [r for r in rows if r["wreathpriceMatchedIds"]]
    contextual = [r for r in rows if r["wreathpriceContextIds"]]
    broadened = [r for r in contextual if r["wreathpriceScopeKind"] == "broader_or_ambiguous_seller_row"]
    sku_missing = [r for r in contextual if r["wreathpriceScopeReason"] == "page_has_no_exact_b205_sku"]
    summary = {
        "status": "research-only; not quality approval",
        "totalUrls": 5070,
        "roles": roles,
        "b205MatchedLocalityRows": len(matches),
        "wreathpriceContextRows": len(contextual),
        "broadOrAmbiguousRowsBlocked": len(broadened),
        "exactLocalRowsMissingB205": len(sku_missing),
        "source": {"repo": "joseungil-kr/site-factory-v5",
                   "commit": SOURCE_COMMIT, "path": SOURCE_PATH,
                   "gitBlobSHA": SOURCE_GIT_BLOB_SHA,
                   "retrievedOn": source["retrievedOn"],
                   "publisherLastUpdated": source["sellerPageLastUpdated"],
                   "B205": source["skuEvidence"]["B205"]["sourceUrl"],
                   "C030": source["skuEvidence"]["C030"]["sourceUrl"],
                   "currentCheckoutVerified": False},
        "unmappedReasons": dict(Counter(r["unmappedReason"] for r in rows)),
        "regressions": [
            {k:r[k] for k in ("number","urlPath","regionName","proposedRole",
                               "wreathpriceMatchedIds","sellerPostedFeeKRW")}
            for r in rows if r["number"] in REQUIRED_REGRESSIONS
        ],
        "validations": {"urlDuplicates":0, "urlMissing":0, "wrongSkuFeeTransfers":0,
                        "broadRowsUsedAsLocal":0, "unknownLiveStatusInferred":0,
                        "indexApproved":False, "qualityApproved":False},
        "examples": [
            {k:r[k] for k in ("number","urlPath","regionName","listedSkus",
                               "sellerPostedFeeKRW","sellerPostedFeeSku",
                               "wreathpriceScopeKind","wreathpriceMatchedIds",
                               "wreathpriceScopeReason")}
            for r in (matches[:5]+broadened[:3]+sku_missing[:3])
        ]
    }
    result = json.dumps({"summary":summary,"rows":rows},ensure_ascii=False,indent=2)+"\n"
    json_path=EXTRA/"todayflower-5070-b205-extended.json"
    json_path.write_text(result,encoding="utf-8")
    fields=list(rows[0])
    buf=io.StringIO(newline="")
    wr=csv.DictWriter(buf,fieldnames=fields,lineterminator="\n")
    wr.writeheader()
    for row in rows:
        wr.writerow({k:(json.dumps(v,ensure_ascii=False,separators=(",",":"))
                        if isinstance(v,(list,dict)) else
                        ("true" if v is True else "false" if v is False else
                         "" if v is None else str(v))) for k,v in row.items()})
    csv_data=buf.getvalue()
    csv_path=EXTRA/"todayflower-5070-b205-extended.csv"
    csv_path.write_text(csv_data,encoding="utf-8")
    sha={"json":hashlib.sha256(result.encode()).hexdigest(),
         "csv":hashlib.sha256(csv_data.encode()).hexdigest()}
    summary["outputSHA256"]=sha
    (EXTRA/"b205-coverage-summary.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TODAYFLOWER_B205_EXTENDED_5070 "+json.dumps({
        "rows":len(rows),"roles":roles,"matches":len(matches),
        "context":len(contextual),"broadBlocked":len(broadened),
        "skuMissing":len(sku_missing),"sha256":sha
    },ensure_ascii=False),flush=True)
    return summary


def main():
    rows,source=extend_rows()
    write_outputs(rows,source)


if __name__=="__main__":
    main()
