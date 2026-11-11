"""Evidence-bounded Todayflower roles; no new delivery claims or URL changes.

The historical legal ZIP establishes only geographic identity. Seller listings
establish only the specific facility or SKU noted at the observed time.
This module does not generate invented regional claims or production releases.
"""
from __future__ import annotations

import json
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[1] / "sites/todayflower-nalmada/evidence-ledger-sample.json"
ROLES = frozenset(("evidence_detail", "regional_navigation", "general_buying_guide"))


def load_ledger():
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    sources = {s["id"]: s for s in data["sources"]}
    assert len(sources) == len(data["sources"])
    assert all(s["url"].startswith("https://fwith.co.kr/") for s in data["sources"]
               if s["url"] is not None)
    for fact in data["facts"]:
        assert fact["sourceId"] in sources
        assert len(set(fact["regionCodes"])) == len(fact["regionCodes"])
        assert all(name.strip() for name in fact["regionNames"])
        if fact["regionCodes"]:
            assert len(fact["regionCodes"]) == len(fact["regionNames"])
        else:
            # Unmapped seller venues remain unmatchable to any region.
            assert fact["displayPolicy"].endswith("unmapped") or fact["kind"] == "sku_listing"
        assert fact["publicationStatus"] == "seller-listed-undated"
        assert fact["liveStatus"] == "unverified"
        assert fact["regionCodes"] or fact["displayPolicy"].endswith("unmapped") or fact["kind"] == "sku_listing"
        for code in fact["regionCodes"]:
            assert len(code) == 10 and code.isdecimal()
    assert len({f["id"] for f in data["facts"]}) == len(data["facts"])
    return data


def match_specific_facts(*, region_code, sku=None, facility=None, ledger=None):
    """No prefix matching or 'similar SKU' matching is permitted."""
    facts = (ledger or load_ledger())["facts"]
    matched = []
    for f in facts:
        if not region_code or region_code not in f["regionCodes"]:
            continue
        if f["kind"] == "sku_shipping_fee":
            if sku != f["sku"]:
                continue
        elif f["kind"] == "venue_rule":
            if not facility or facility != f["facilityName"]:
                continue
        else:
            continue
        matched.append(f)
    return matched


def decide_role(*, region_code, selected_skus=(), facility=None, ledger=None):
    """Page without verified page-specific facts cannot become evidence detail."""
    data = ledger or load_ledger()
    selected = set(selected_skus)
    for sku in selected:
        if match_specific_facts(region_code=region_code, sku=sku,
                                facility=facility, ledger=data):
            return "evidence_detail"
    if facility and match_specific_facts(region_code=region_code,
                                        facility=facility, ledger=data):
        return "evidence_detail"
    if region_code and any(region_code in f["regionCodes"] for f in data["facts"]):
        return "regional_navigation"
    return "general_buying_guide"


def classify_existing_page(page, *, ledger=None):
    # Region codes are generated from the pinned government ZIP by the caller.
    # Existing historical 33 pages have a separate immutable copy contract.
    assert page["number"] > 33
    return decide_role(region_code=page.get("legalCode"),
                       selected_skus=page["productSkus"],
                       ledger=ledger)


def check_ledger_region_codes(data, legal_codes):
    unknown = sorted({c for f in data["facts"] for c in f["regionCodes"]
                      if c not in legal_codes})
    assert not unknown, "Evidence region codes outside pinned legal inventory: " + str(unknown)


def evidence_detail_payload(*, region_code, facility=None, sku=None, ledger=None):
    """Isolated editorial sample. Never asserts delivery availability or transfers SKU rates."""
    data = ledger or load_ledger()
    facts = match_specific_facts(region_code=region_code, facility=facility,
                                 sku=sku, ledger=data)
    sources = {s["id"]: s for s in data["sources"]}
    return {
        "role": "evidence_detail" if facts else "general_buying_guide",
        "regionCode": region_code,
        "facts": [
            {
                "id": f["id"], "kind": f["kind"], "sku": f["sku"],
                "facility": f["facilityName"], "condition": f.get("condition"),
                "amountKRW": f.get("amountKRW"),
                "sourceURL": sources[f["sourceId"]]["url"],
                "sourceObservedAt": sources[f["sourceId"]]["observedAt"],
                "sourcePublicationDate": sources[f["sourceId"]]["publicationDate"],
                "regionName": f["regionNames"][f["regionCodes"].index(region_code)],
                "sourcePublicationStatus": f["publicationStatus"],
                "verifiedCurrent": False,
                "unknown": f["unknown"],
            }
            for f in facts
        ],
    }
