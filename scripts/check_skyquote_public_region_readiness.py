"""Fail closed unless original authenticated ZIP and reviewed upper-level codes agree.

The deprecated third-party 242-region source is never accepted for publication.
Runtime Cloudflare verification must still be checked independently.
"""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from skyquote_audit_official import audit

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path)
    args=p.parse_args()
    if not args.archive or not args.archive.is_file():
        print("SKYQUOTE_PUBLIC_OFFICIAL_SOURCE_BLOCKED original ZIP not present in this checkout; use authorized V4 archive")
        return 2
    result=audit(args.archive)
    review=json.loads((ROOT/"sites/skyquote/official-region-reconciliation.json").read_text())
    verified=review["fullOfficialSnapshot"]
    assert result["archiveSHA256"]==verified["sha256"]
    assert result["activeLegalCodeRows"]==verified["validatedRowCount"]==20560
    assert result["eupMyeonDongLegalCodeRecords"]==verified["activeEupMyeonDongLegalRecords"]==4632
    assert result["matchedParents"]==4632
    assert result["upperCodeEntries"]==284
    assert verified["matchedCurrentCodeSystem"] is True
    print("SKYQUOTE_OFFICIAL_SOURCE_READY source=V4-archive upper=284 lowerLegalRows=4632 notServiceAreas=true")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
