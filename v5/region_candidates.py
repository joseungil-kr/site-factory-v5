"""Lossless regional-name selection for national Site Factory pages.

A source record with an unknown or unmatched parent is still a region-name
candidate and must NOT be dropped. This module does not claim the name is
a current legal administrative region or that deliveries are available.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def rows_from_source(source: Any) -> list[Any]:
    if isinstance(source, list):
        return source
    if isinstance(source, dict):
        for key in ("regions", "candidates", "rows", "items"):
            if isinstance(source.get(key), list):
                return source[key]
    raise ValueError("Source must be a list or an object containing a region row list")


def select_all_region_names(source: Any, *, expected_count: int | None = None) -> dict:
    rows = rows_from_source(source)
    if expected_count is not None and len(rows) != expected_count:
        raise ValueError(f"Full source not loaded: {len(rows)} != {expected_count}")
    selected = []
    for index, row in enumerate(rows, start=1):
        if isinstance(row, str):
            region_name = row
            source_id = None
            parent = None
            parent_match = None
        elif isinstance(row, dict):
            region_name = next((row[k] for k in ("displayName", "fullName", "regionName", "name")
                                if isinstance(row.get(k), str) and row[k].strip()), None)
            source_id = row.get("sourceId") or row.get("id") or row.get("code")
            parent = row.get("parent") if "parent" in row else row.get("parentCode")
            parent_match = row.get("parentMatched")
        else:
            raise ValueError(f"Unsupported region row #{index}")
        if not isinstance(region_name, str) or not region_name.strip():
            # Do not silently skip bad rows. Stop and request a corrected source.
            raise ValueError(f"Missing region name in source row #{index}")
        selected.append({
            "sourceOrdinal": index,
            "sourceRecordId": str(source_id) if source_id is not None else f"row-{index:05d}",
            "regionName": region_name,  # exact recorded text; no inferred parent
            "parentCodeAsRecorded": parent,
            "parentMatchedAsRecorded": parent_match,
            "path": f"/r/{index:05d}.html",
        })
    if len(selected) != len(rows):
        raise AssertionError("Lost a source region name")
    if len({x["path"] for x in selected}) != len(rows):
        raise AssertionError("Region URL collisions")
    return {
        "policy": "every recorded region-name row is included; unmatched parents do not filter",
        "sourceRowCount": len(rows),
        "includedRowCount": len(selected),
        "excludedRowCount": 0,
        "records": selected,
        "parentLinkageIndependentlyVerified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Lossless V5 regional name inventory")
    parser.add_argument("--input", required=True, help="Existing CSV/JSON region master")
    parser.add_argument("--output", required=True, help="New JSON report; never deployed directly")
    parser.add_argument("--expected-count", type=int, default=5034)
    a = parser.parse_args()
    source = Path(a.input)
    if source.suffix.lower() == ".csv":
        with source.open(encoding="utf-8-sig", newline="") as stream:
            data = list(csv.DictReader(stream))
    else:
        data = json.loads(source.read_text(encoding="utf-8"))
    report = select_all_region_names(data, expected_count=a.expected_count)
    out = Path(a.output)
    if out.exists():
        parser.error("Output already exists: refusing to overwrite the prior evidence")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"REGION_NAME_LOSSLESS_PASS {report['includedRowCount']} / {report['sourceRowCount']}")


if __name__ == "__main__":
    main()
