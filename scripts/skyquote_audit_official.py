"""Cross-check every official upper region with original authenticated V4 legal-code ZIP.
This does not authorize service/dispatch claims or infer administrative-dong counts.
"""
from pathlib import Path
import csv,hashlib,io,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
SHA="44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd"
def audit(archive):
    archive=Path(archive)
    blob=archive.read_bytes()
    assert hashlib.sha256(blob).hexdigest()==SHA,"Unexpected official archive; stop"
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names=z.namelist()
        assert len(names)==1
        records=list(csv.reader(io.StringIO(z.read(names[0]).decode("cp949")),delimiter="\t"))
    assert records[0]==["법정동코드","법정동명","폐지여부"]
    active={r[0]:r[1].strip() for r in records[1:] if len(r)==3 and r[2].strip()=="존재"}
    active_names=[r for r in records[1:] if len(r)==3 and r[2].strip()=="존재"]
    lower=[r for r in active_names if r[1].split()[-1].endswith(("읍","면","동"))]
    assert len(records)-1==53403 and len(active)==20560,(len(records),len(active))
    assert len(lower)==4632,len(lower)
    data=json.loads((ROOT/"sites/skyquote/official-upper-regions-20261022.json").read_text())
    entries=data["entries"]
    assert len(entries)==284
    assert len({x["code"] for x in entries})==284
    mismatches=[]
    for item in entries:
        assert item["sourceStatus"]=="존재"
        official=active.get(item["code"])
        if official!=item["fullName"]:
            mismatches.append({"code":item["code"],"cachedName":item["fullName"],"officialActiveName":official,
                               "status":"active" if official else "notActive"})
    if mismatches:
        print("SKYQUOTE_UPPER_CODE_MISMATCH_REPORT",json.dumps(mismatches,ensure_ascii=False))
        raise AssertionError("Cached upper-region rows do not match the official ZIP; update the reviewed ledger before release")
    upper_names=sorted(entries,key=lambda x:len(x["fullName"]),reverse=True)
    unmatched=[]
    for code,name,_ in lower:
        parent=next((x for x in upper_names if name.startswith(x["fullName"]+" ")),None)
        if parent is None: unmatched.append([code,name])
    assert not unmatched,unmatched[:5]
    names={x["fullName"] for x in entries}
    required={"서울특별시 강서구","인천광역시 제물포구","인천광역시 영종구",
              "인천광역시 서해구","인천광역시 검단구","전남광주통합특별시",
              "강원특별자치도","전북특별자치도"}
    assert required.issubset(names),sorted(required-names)
    obsolete={"광주광역시","전라남도","강원도","전라북도","인천광역시 중구","인천광역시 동구","인천광역시 서구"}
    assert not obsolete.intersection(names),sorted(obsolete.intersection(names))
    assert sum(x["level"]=="province" for x in entries)==16
    assert sum(x["level"]=="municipality" for x in entries)==229
    assert sum(x["level"]=="ward" for x in entries)==39
    evidence={"archiveSHA256":SHA,"sourceRows":len(records)-1,"activeLegalCodeRows":len(active),
        "eupMyeonDongLegalCodeRecords":len(lower),"matchedParents":len(lower),
        "upperCodeEntries":len(entries),"province":16,"municipality":229,"ward":39,
        "sourceAcquired":"2026-10-22","verifiedServiceAreas":0,
        "rawRecordsAreNotAllAdministrativeDong":True}
    print("SKYQUOTE_OFFICIAL_CODE_AUDIT_PASS",json.dumps(evidence,ensure_ascii=False))
    return evidence
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--archive",required=True)
    audit(p.parse_args().archive)
