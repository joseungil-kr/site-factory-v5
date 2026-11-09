"""Evidence gate for worker6 nationwide content. Does not weaken V5 audit."""
from __future__ import annotations
import json
from pathlib import Path

def evidence_ready(pages,ledger):
    errors=[]
    records=ledger.get('records',{}) if isinstance(ledger,dict) else {}
    for p in pages:
        evidence=records.get(p['id'])
        if not isinstance(evidence,dict):
            errors.append(f"{p['id']}: missing factual research record")
            continue
        for key in ('sourceUrl','checkedOn','recipientScenario','productSelectionReason','deliveryScope'):
            if not isinstance(evidence.get(key),str) or not evidence[key].strip():
                errors.append(f"{p['id']}: missing {key}")
        if evidence.get('deliveryScope')=='confirmed' and not evidence.get('deliveryEvidence'):
            errors.append(f"{p['id']}: unsupported delivery coverage")
    return errors

def main():
    import sys
    pages=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    ledger=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
    errors=evidence_ready(pages,ledger)
    print(json.dumps({'ready':not errors,'pages':len(pages),'missingEvidence':len(errors),'examples':errors[:12]},ensure_ascii=False))
    return 0 if not errors else 3
if __name__=='__main__':
    raise SystemExit(main())
