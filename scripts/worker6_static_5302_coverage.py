"""Static coverage preflight only; never count candidate locality as verified copy."""
from collections import Counter
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def summarize():
    source=json.loads((ROOT/'data/regions/nationwide_locality_candidates_5034.json').read_text(encoding='utf-8'))
    rows=source['records']
    spec=json.loads((ROOT/'sites/promotion-gift-plants/site-spec.json').read_text(encoding='utf-8'))
    assert len(rows)==5034
    assert spec['targetPageCount']==5302
    assert 1+17+250+len(rows)==5302
    flags=Counter(str(row[3]) for row in rows)
    return {'target':5302,'localityCandidates':len(rows),'candidateFlags':dict(sorted(flags.items())),
      'verifiedIndependentLocalityBodies':None,
      'similarityBelow49Verified':False,'editorial85Verified':False,
      'explanation':'Candidate counts and source flags are not proof of locality-specific buyer decisions or publication readiness.'}
if __name__=='__main__':
 print(json.dumps(summarize(),ensure_ascii=False,indent=2))
