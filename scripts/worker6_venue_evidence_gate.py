"""Fail-closed provenance validation for venue-specific customer claims.

This validates evidence structure, not the truth of an external source.
"""
from urllib.parse import urlparse

READ_MODES = frozenset(("full-text", "excerpt", "metadata", "unavailable"))
REQUIRED = ("readMode", "exactQuote", "pageOrSection", "documentVenue",
            "eventYear", "targetVenue", "checkedAt", "sourceUpdatedAt")
def normalize(record):
    """Normalize older source records without silently upgrading read coverage."""
    raw = dict(record)
    read_mode = raw.get("readMode")
    if read_mode is None:
        if raw.get("documentFullTextRead") is True and raw.get("exactQuoteVerified"):
            read_mode = "full-text"
        elif raw.get("quoteEvidenceLevel", "").startswith("indexed search excerpt"):
            read_mode = "excerpt"
        elif raw.get("accessResult", "").startswith(("HTTP 502", "HTTP 403")):
            read_mode = "unavailable"
        else:
            read_mode = "metadata"
    result = dict(raw)
    result.update({
        "readMode": read_mode,
        "exactQuote": raw.get("exactQuote", raw.get("exactQuoteVerified")
                       if isinstance(raw.get("exactQuoteVerified"), str) else
                       raw.get("exactQuoteFromIndexedExcerpt")),
        "pageOrSection": raw.get("pageOrSection", raw.get("pageNumberVerified")),
        "documentVenue": raw.get("documentVenue", raw.get("eventVenue")),
        "eventYear": raw.get("eventYear"),
        "targetVenue": raw.get("targetVenue"),
        "checkedAt": raw.get("checkedAt", raw.get("accessAttemptedAt")),
        "sourceUpdatedAt": raw.get("sourceUpdatedAt"),
    })
    return result

def validate(record):
    item = normalize(record)
    missing = [key for key in REQUIRED if key not in item]
    if missing:
        raise ValueError("missing provenance fields: " + ",".join(missing))
    if item["readMode"] not in READ_MODES:
        raise ValueError("invalid readMode")
    if not isinstance(item["checkedAt"], str) or len(item["checkedAt"]) < 10:
        raise ValueError("checkedAt required")
    if item["sourceUpdatedAt"] is not None and not isinstance(item["sourceUpdatedAt"], str):
        raise ValueError("invalid sourceUpdatedAt")
    return item

def may_make_confirmed_customer_claim(record):
    """Conservative gate; full text is necessary but never proves truth by itself."""
    x = validate(record)
    if x["readMode"] != "full-text":
        return False
    if not isinstance(x["exactQuote"], str) or not x["exactQuote"].strip():
        return False
    if not x["pageOrSection"]:
        return False
    if not x["documentVenue"] or not x["targetVenue"]:
        return False
    if x["documentVenue"].strip() != x["targetVenue"].strip():
        return False
    if not isinstance(x["eventYear"], int):
        return False
    if not x.get("currentRuleIndependentlyVerified", False):
        return False
    if x.get("contradictionUnresolved", False):
        return False
    if x.get("sellerReportedOnly", False):
        return False
    return True
