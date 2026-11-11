"""Strict, historical WreathPrice fee evidence reuse for Todayflower mapping.

Read-only, pinned copied source. Seller-listed B205 and C030 evidence is NOT
a confirmed checkout fee, availability, or evidence about other SKUs.
A city/county-wide source row is never promoted to a locality-specific fee.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .config import ROOT

PINNED = ROOT / "sites/todayflower-nalmada/wreathprice-shipping-evidence-pinned.json"
SOURCE_GIT_BLOB_SHA = "04ec10b3715dd1bfcc44c06b1445de68808a3a05"
SOURCE_COMMIT = "791c0cd5f4313e48efbde8f712d3c91f40931fce"
SOURCE_PATH = "sites/wreathprice/posted-shipping-evidence-50.json"
SOURCE_REPO = "joseungil-kr/site-factory-v5"
EXPECTED_URL = "https://fwith.co.kr/shop/item.php?it_id=B205"
SEPARATE_ROW_SUFFIX = "별도행"


def load_pinned():
    raw = PINNED.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\\0" + raw).hexdigest()
    assert blob == SOURCE_GIT_BLOB_SHA, ("WreathPrice source blob drift", blob)
    data = json.loads(raw)
    assert data["ledgerId"] == "wreathprice-50-posted-shipping-only"
    assert data["retrievedOn"] == "2026-11-11"
    assert data["sellerPageLastUpdated"] is None
    assert data["skuEvidence"]["B205"]["sourceUrl"] == EXPECTED_URL
    assert data["skuEvidence"]["B205"]["verifiedCheckout"] is False
    assert data["skuEvidence"]["C030"]["verifiedCheckout"] is False
    assert data["regionalFactsProven"] == data["indexEligibleRegions"] == 0
    assert len(data["postedFees"]) == 20
    assert len({r["regionCode"] for r in data["postedFees"]}) == 20
    assert all(set(x["sourceSkuIds"]) == {"B205", "C030"} for x in data["postedFees"])
    assert all(x["appliesToLiveOrder"] == x["actualDeliveryAvailable"] == "unverified"
               for x in data["postedFees"])
    return data


def scope_class(record):
    """Conservative distinction between a dedicated locality row and a broad table row."""
    name = record["regionName"]
    last = name.split()[-1]
    scope = record["sourceRowScope"]
    # An explicit separate row must name the exact locality; no prefix or
    # matching by parent city is allowed. Broad/exception rows stay unresolved.
    if SEPARATE_ROW_SUFFIX in scope and last in scope and not (
        "전체" in scope or "기본행" in scope or "단위 행" in scope
    ):
        return "explicit_locality_row"
    return "broader_or_ambiguous_seller_row"


def map_posted_fee(*, region_code, region_name, selected_skus, source=None):
    data = source or load_pinned()
    candidates = [r for r in data["postedFees"] if r["regionCode"] == region_code]
    assert len(candidates) <= 1
    if not candidates:
        return {"contextIds": [], "matchedIds": [], "reason": "no_pinned_b205_fee_row"}
    row = candidates[0]
    assert row["regionName"] == region_name, ("WreathPrice exact region name mismatch", region_code)
    assert set(row["sourceSkuIds"]) == {"B205", "C030"}
    assert row["retrievedOn"] == "2026-11-11" and row["sellerUpdatedOn"] is None
    context_id = "wreathprice-posted-b205-c030-" + region_code
    kind = scope_class(row)
    if kind != "explicit_locality_row":
        return {"contextIds":[context_id], "matchedIds": [],
                "reason":"seller_fee_row_is_broader_or_ambiguous",
                "scopeKind":kind, "postedFeeKRW":None}
    if "B205" not in selected_skus:
        return {"contextIds":[context_id], "matchedIds": [],
                "reason":"page_has_no_exact_b205_sku",
                "scopeKind":kind, "postedFeeKRW":None}
    return {"contextIds":[context_id], "matchedIds":[context_id],
            "reason":"seller_posted_fee_only_current_applicability_unverified",
            "scopeKind":kind, "postedFeeKRW":row["postedAdditionalFeeKRW"],
            "sku":"B205", "sourceURL":EXPECTED_URL,
            "sellerObservedAt":row["retrievedOn"], "sellerPublishedAt":None,
            "sourceRowScope":row["sourceRowScope"], "liveCheckoutVerified":False,
            "currentAvailabilityVerified":False}
