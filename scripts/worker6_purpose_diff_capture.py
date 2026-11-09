"""Preserve real V5.1 assembled bodies and HTML before similarity gate, no bypass."""
from pathlib import Path
import json
from v5.purpose_render import assemble,render
from v5.audit import similarity
root=Path('sites/promotion-gift-plants')
spec=json.loads((root/'site-spec.json').read_text())
site=json.loads((root/'site.json').read_text())
pages=json.loads((root/'pages.json').read_text())
products=json.loads((root/'products.json').read_text())
out=Path('reports/promotion-gift-plants/purpose-diff')
out.mkdir(parents=True,exist_ok=True)
bodies={}
for page in pages:
 if page['purpose'] not in ('promotion','transfer'):continue
 assembled=assemble(page,spec['purposePools'],products)
 body=assembled['intro']+'\n'+'\n'.join(x['heading']+' '+x['paragraph'] for x in assembled['sections'])
 bodies[page['purpose']]=body
 (out/(page['purpose']+'.txt')).write_text(body,encoding='utf-8')
 html=render(site,page,pages,products,[],spec['purposePools'])
 (out/(page['purpose']+'.html')).write_text(html,encoding='utf-8')
assert set(bodies)=={'promotion','transfer'}
score=similarity(bodies['promotion'],bodies['transfer'])
(out/'diagnostic.json').write_text(json.dumps({'pair':['promotion','transfer'],'similarity':score,'thresholdExclusive':0.49,'passed':score<0.49,'notAQualityApproval':True},indent=2)+'\n')
print('PURPOSE_REAL_BODY_SIMILARITY',score,'passed',score<0.49)
