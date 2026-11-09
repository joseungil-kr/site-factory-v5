"""Controlled comparison: same purpose, products, V5.1 renderer and page IDs."""
from __future__ import annotations
import json
from pathlib import Path
from v5.purpose_render import assemble
from v5.audit import similarity
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'sites/promotion-gift-plants'
def run():
    records=json.loads((SITE/'gangjin-two-page-experiment.json').read_text(encoding='utf-8'))['pages']
    spec=json.loads((SITE/'site-spec.json').read_text(encoding='utf-8'))
    products=json.loads((SITE/'products.json').read_text(encoding='utf-8'))
    # Fix the exact same purpose, product order and copy selection for both
    # regions. Only the optional evidenceSections differ between conditions.
    pages=[]
    for record in records:
        pages.append({'id':record['id'],'region':record['region'],'purpose':'promotion',
            'productSkus':['D144','D156'],'evidenceSections':record['evidenceSections']})
    def body(page):
        assembled=assemble(page,spec['purposePools'],products)
        return ' '.join([assembled['intro']]+[s['paragraph'] for s in assembled['sections']])
    before=[body({**p,'evidenceSections':[]}) for p in pages]
    after=[body(p) for p in pages]
    before_sim=similarity(*before)
    after_sim=similarity(*after)
    return {'experiment':'same-purpose-same-products-evidence-only',
        'purpose':'promotion','productSkus':['D144','D156'],
        'regions':[p['region'] for p in pages],
        'beforeSimilarity':before_sim,'afterSimilarity':after_sim,
        'delta':after_sim-before_sim,'threshold':0.49,
        'afterBelowThreshold':after_sim<0.49,
        'caveat':'Effect measures added text, not commercial usefulness. Administrative/facility facts are not evidence of delivery or customer need.',
        'conditions':[{'id':p['id'],'beforeChars':len(before[i]),'afterChars':len(after[i]),
          'beforeBody':before[i],'afterBody':after[i]} for i,p in enumerate(pages)]}
if __name__=='__main__':
    result=run()
    out=ROOT/'reports/promotion-gift-plants/controlled'
    out.mkdir(parents=True,exist_ok=True)
    (out/'same-purpose-before-after.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='conditions'},ensure_ascii=False))
