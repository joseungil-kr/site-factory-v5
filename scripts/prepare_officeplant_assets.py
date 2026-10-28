"""Restore the three frozen seller photos by exact hash; fail closed if source bytes changed."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"EXPORT-MANIFEST.json"
SOURCE="https://fwith.co.kr/data/item/flower379/{sku}/thumb-1_500x500.jpg"

def main():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries={x["path"]:x for x in manifest["files"]}
    for sku in ("D144","D149","D158"):
        rel=f"sites/officeplant/assets/{sku}.jpg"
        expected=entries[rel]["sha256"]
        target=ROOT/rel
        if target.exists():
            actual=hashlib.sha256(target.read_bytes()).hexdigest()
            if actual!=expected:
                raise SystemExit(f"Existing product photo differs from frozen handoff: {rel}")
            print(f"PHOTO_HASH_OK {rel} existing")
            continue
        request=Request(SOURCE.format(sku=sku),headers={"User-Agent":"Officeplant-V5-build/1.0"})
        with urlopen(request,timeout=30) as response:
            if response.status!=200:
                raise SystemExit(f"Photo source HTTP {response.status}: {sku}")
            data=response.read()
        actual=hashlib.sha256(data).hexdigest()
        if actual!=expected:
            raise SystemExit(f"Product photo source changed: {sku}; expected {expected}; got {actual}")
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
        print(f"PHOTO_HASH_OK {rel} downloaded bytes={len(data)} sha256={actual}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
