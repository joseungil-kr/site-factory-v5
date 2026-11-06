"""Independently validate frozen Skyquote WebP bytes and three local noindex pages."""
from pathlib import Path
import hashlib,json,re,sys
from html.parser import HTMLParser
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'sites/skyquote'
OUT=ROOT/'dist/skyquote-preview'
manifest=json.loads((SITE/'assets-manifest.json').read_text(encoding='utf-8'))
assert len(manifest['assets'])==5
for item in manifest['assets']:
    p=ROOT/item['path']
    assert p.is_file(),f'Missing GitHub-bundled image: {p}'
    raw=p.read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    assert digest==item['sha256'],f'WebP hash mismatch: {p} {digest} != {item["sha256"]}'
    with Image.open(p) as im:
        assert im.format=='WEBP' and im.size==(1536,1024),(p,im.format,im.size)
    target=OUT/'assets'/p.name
    assert target.read_bytes()==raw,f'Generated asset differs: {p.name}'
    print('IMAGE_ASSET_PASS',p.name,'1536x1024',len(raw),digest)
pages=['index.html','danwon.html','gojan.html']
for name in pages:
    path=OUT/name
    raw=path.read_text(encoding='utf-8')
    assert raw.count('<img ')==5,(name,raw.count('<img '))
    assert 'AI 생성 설명 이미지' not in raw
    assert '<figcaption>' not in raw
    assert raw.count('loading="lazy"')==4 and 'loading="eager"' in raw
    assert '스카이차 견적, 최저가 비교 전 확인사항 | 바른견적스카이' in raw
    assert '영진스카이 공개 이용요금' in raw
    assert '반나절 · 4시간' in raw and '하루 · 8시간' in raw
    assert '30만 원' in raw and '50만 원' in raw and '부가세는 별도' in raw
    assert '작업 지점까지 높이(미터)' in raw and '수평거리' in raw
    assert '초과·대기 시간 요금은 상담 시 확인' in raw
    for unsupported_claim in ('AI 생성 설명 이미지 — 실제 시공','실제 현장 작업사례가 아닙니다','업계 최저가를 주장하지 않습니다','차량 톤수만으로 작업 가능성을 보장하지 않습니다','단정하지 마세요','실수를 피할 수 있습니다','보장하지 않습니다'):
        assert unsupported_claim not in raw, (name, unsupported_claim)
    assert '<meta name="robots" content="noindex,nofollow">' in raw
    assert 'href="tel:01053221952"' in raw
    for image in manifest['assets']:
        assert 'src="/assets/'+Path(image['path']).name+'"' in raw,(name,image['path'])
    assert '<html lang="ko">' in raw
    print('PAGE_PASS',name,'images=5 noindex=true')
robots=(OUT/'robots.txt').read_text()
assert robots=='User-agent: *\nDisallow: /\n'
assert not (OUT/'sitemap.xml').exists()
assert len(list(OUT.glob('*.html')))==4, '3 pages plus 404 only'
print('SKYQUOTE_ASSETS_AND_THREE_PAGES_PASS')
