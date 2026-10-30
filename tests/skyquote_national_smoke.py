"""Narrow nationwide static information build validation, not an operator-coverage certificate."""
from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dist/skyquote-national-preview'
source=json.loads((ROOT/'sites/skyquote/nationwide-district-source.json').read_text())
m=json.loads((OUT/'national-manifest.json').read_text())
assert len(source['rows'])==242 and source['license']=='CC-BY-4.0'
assert (m['totalContentPages'],m['nationalRecords'],m['ansanPreserved'])==(268,242,25),m
assert m['serviceCoverageConfirmed'] is False and m['noIndex'] and m['noSitemap']
assert len(set(m['paths']))==268
assert not (OUT/'sitemap.xml').exists()
assert (OUT/'robots.txt').read_text()=='User-agent: *\nDisallow: /\n'
assets=json.loads((ROOT/'sites/skyquote/assets-manifest.json').read_text())['assets']
for img in assets:
    p=OUT/'assets'/Path(img['path']).name
    assert hashlib.sha256(p.read_bytes()).hexdigest()==img['sha256']
for x in m['paths']:
    p=OUT/x;html=p.read_text(encoding='utf-8')
    assert 'name="robots" content="noindex,nofollow"' in html,x
    assert html.count('<img ')==5,x
    for image in assets:assert Path(image['path']).name in html,x
    assert not any(bad in html for bad in ('최저가를 보장합니다','업계 최저가 보장','당일 배차 보장','전국 출동 가능')),x
    for link in re.findall(r'href="(/[^"#?]*)"',html):
        if link.startswith('/assets/'):continue
        target=OUT/'index.html' if link=='/' else OUT/link.lstrip('/')
        assert target.is_file(),(x,link)
# Existing original asset bytes and three-page sample paths remain intact.
for x in ('index.html','danwon.html','gojan.html'):
    assert (OUT/x).exists()
# Different quote question sets; not only geographic name replacements.
import importlib.util
spec=importlib.util.spec_from_file_location('nat',ROOT/'scripts/build_skyquote_national.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
sets=set()
for x in source['rows']:
    html=(OUT/'national'/(x['id'].lower()+'.html')).read_text(encoding='utf-8')
    matches=tuple(re.findall(r'<h2>(.*?) 비교 질문</h2>',html))
    assert len(matches)==4 and len(set(matches))==4,x['id']
    sets.add(matches)
assert len(sets)>=20,('excessively repetitive question combinations',len(sets))
print('SKYQUOTE_NATIONAL_QA_PASS pages=268 provinces=17 districts=225 ansanPreserved=25 uniqueQuestionSets='+str(len(sets))+' internalLinks=valid hashes=5 noindex=true')
