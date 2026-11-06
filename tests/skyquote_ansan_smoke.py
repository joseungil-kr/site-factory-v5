"""QA all 25 Ansan noindex pages for customer usefulness, distinct local questions and original assets."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/skyquote-ansan-preview'
scope=json.loads((ROOT/'sites/skyquote/ansan-expansion-scope.json').read_text(encoding='utf-8'))
m=json.loads((OUT/'expansion-manifest.json').read_text(encoding='utf-8'))
assert m['pages']==25 and m['operatorListedAdministrativeAreas']==22 and m['newPages']==22
assert len(scope['regions'])==22 and len({r['slug'] for r in scope['regions']})==22
assert len(list(OUT.rglob('*.html')))==26
assert (OUT/'robots.txt').read_text()=='User-agent: *\nDisallow: /\n'
assert not (OUT/'sitemap.xml').exists()
images=json.loads((ROOT/'sites/skyquote/assets-manifest.json').read_text(encoding='utf-8'))['assets']
for img in images:
    p=OUT/'assets'/Path(img['path']).name
    assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==img['sha256']
class Visible(HTMLParser):
    def __init__(self):super().__init__();self.skip=0;self.t=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('style','script','head'):self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('style','script','head'):self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip:self.t.append(data)
texts=[]
for p in sorted(OUT.rglob('*.html')):
    if p.name=='404.html':continue
    raw=p.read_text(encoding='utf-8')
    assert raw.count('<img ')==5 and 'AI 생성 설명 이미지' not in raw and '<figcaption>' not in raw,p
    assert 'name="robots" content="noindex,nofollow"' in raw,p
    assert 'href="tel:01053221952"' in raw,p
    assert '영진스카이 공개 이용요금' in raw and '30만 원' in raw and '부가세는 별도' in raw,p
    assert '작업 지점까지 높이(미터)' in raw and '반나절 · 4시간' in raw and '하루 · 8시간' in raw,p
    assert raw.count('loading="eager"')==1 and raw.count('loading="lazy"')==4,p
    for bad in ('업계 최저가를 주장하지 않습니다','AI 생성 설명 이미지 — 실제 시공','차량 톤수만으로 작업 가능성을 보장하지 않습니다','단정하지 마세요','실수를 피할 수 있습니다','기재합니다','실제 환경을 조사한 결과가 아닌 견적용 가정'):
        assert bad not in raw,(p,bad)
    for img in images:assert '/assets/'+Path(img['path']).name in raw
    parser=Visible();parser.feed(raw);texts.append(re.sub(r'\s+',' ',' '.join(parser.t)))
assert len(texts)==25 and len(set(texts))==25
assert len({x['focus'] for x in scope['regions']})==22 and len({x['example'] for x in scope['regions']})==22
for place in scope['regions']:
    if place['slug']=='gojan.html':continue
    raw=(OUT/place['slug']).read_text(encoding='utf-8')
    assert raw.count(place['focus'])==1 and raw.count(place['example'])==1,place['slug']
    assert '견적 상담에 필요한 정보' in raw and '현장 조건을 알려주시면 견적을 안내해 드립니다' in raw
    assert '실제 환경을 조사한 결과가 아닌 견적용 가정' not in raw
print('SKYQUOTE_ANSAN_25_VISITOR_COPY_QA_PASS pages=25 images=5 pricing=true focus/example once noindex=true')
