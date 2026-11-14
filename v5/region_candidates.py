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
        for key in ("records", "regions", "candidates", "rows", "items"):
            if isinstance(source.get(key), list):
                return source[key]
    raise ValueError("Source must be a list or an object containing a region row list")


def select_all_region_names(source: Any, *, expected_count: int | None = None) -> dict:
    rows = rows_from_source(source)
    if expected_count is not None and len(rows) != expected_count:
        raise ValueError(f"Full source not loaded: {len(rows)} != {expected_count}")
    selected = []
    for index, row in enumerate(rows, start=1):
        parent_names = None
        source_parts = None
        source_match_flag = None
        if isinstance(row, str):
            region_name = row
            source_id = None
            parent = None
            parent_match = None
        elif isinstance(row, (list, tuple)) and len(row) == 4:
            # Historical V5 Wreath source format: [province, district, locality, v4ParentMatchFlag].
            # A flag of 0 is NOT an exclusion instruction. Preserve all original components.
            province, district, locality, flag = row
            if (not all(isinstance(p, str) and p.strip() and p == p.strip()
                        for p in (province, district, locality))
                    or type(flag) is not int or flag not in (0, 1)):
                raise ValueError(f"Invalid 4-field region source row #{index}")
            region_name = " ".join((province, district, locality))
            source_id = None
            parent = None  # the source includes names, but no official parent code
            parent_match = bool(flag)
            parent_names = province + " " + district
            source_parts = [province, district, locality]
            source_match_flag = flag
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
            "parentNamesAsRecorded": parent_names,
            "parentMatchedAsRecorded": parent_match,
            "sourceMatchFlagAsRecorded": source_match_flag,
            "sourcePartsAsRecorded": source_parts,
            "path": f"/r/{index:05d}.html",
        })
    if len(selected) != len(rows):
        raise AssertionError("Lost a source region name")
    if len({x["path"] for x in selected}) != len(rows):
        raise AssertionError("Region URL collisions")
    flags = [x["sourceMatchFlagAsRecorded"] for x in selected
             if x["sourceMatchFlagAsRecorded"] is not None]
    if isinstance(source, dict) and "counts" in source:
        declared = source["counts"]
        if declared.get("localities") != len(rows):
            raise ValueError("Region count does not agree with original metadata")
        if flags and (declared.get("parentMatchesV4") != sum(flags)
                      or declared.get("parentNotMatchedV4") != len(flags) - sum(flags)):
            raise ValueError("Parent match flags disagree with source metadata")
    return {
        "policy": "every recorded region-name row is included; unmatched parents do not filter",
        "sourceRowCount": len(rows),
        "includedRowCount": len(selected),
        "excludedRowCount": 0,
        "sourceMatchedParentCount": sum(flags) if flags else None,
        "sourceUnmatchedParentCount": len(flags) - sum(flags) if flags else None,
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
