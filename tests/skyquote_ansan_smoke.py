"""Local QA of the Ansan-only noindex regional expansion."""
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
texts=[];all_paths=[]
for p in OUT.rglob('*.html'):
    if p.name=='404.html':continue
    t=p.read_text(encoding='utf-8')
    assert t.count('<img ')==5 and t.count('AI 생성 설명 이미지')==5,p
    assert 'name="robots" content="noindex,nofollow"' in t,p
    assert 'href="tel:01053221952"' in t,p
    assert '최저가를 보장하지' in t and '업계 최저가를 주장하지 않습니다' in t,p
    for banned in ('업계 최저가 보장','무조건 최저가','최저가를 보장합니다','타사보다 무조건 저렴','지점 운영','시공 완료 사례'):
        assert banned not in t,(p,banned)
    for img in images:assert '/assets/'+Path(img['path']).name in t
    parser=Visible();parser.feed(t);texts.append(re.sub(r'\s+',' ',' '.join(parser.t)));all_paths.append(p.relative_to(OUT).as_posix())
    for href in re.findall(r'href="(/[^"#?]*)"',t):
        target=(OUT/'index.html') if href=='/' else OUT/href.lstrip('/')
        assert target.is_file(),(p,href)
assert len(all_paths)==25 and len(set(texts))==25
assert len({p['focus'] for p in scope['regions']})==22
assert len({p['example'] for p in scope['regions']})==22
assert all((OUT/p['slug']).is_file() for p in scope['regions'])
assert len(set(all_paths))==25
print('SKYQUOTE_ANSAN_25_PAGE_QA_PASS pages=25 original=3 added=22 images_per_page=5 links=valid noindex=true')
