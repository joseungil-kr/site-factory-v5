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
        assert im.format=='WEBP' and im.size==(768,640),(p,im.format,im.size)
    target=OUT/'assets'/p.name
    assert target.read_bytes()==raw,f'Generated asset differs: {p.name}'
    print('IMAGE_ASSET_PASS',p.name,'768x640',len(raw),digest)
pages=['index.html','danwon.html','gojan.html']
for name in pages:
    path=OUT/name
    raw=path.read_text(encoding='utf-8')
    assert raw.count('<img ')==5,(name,raw.count('<img '))
    assert raw.count('AI 생성 설명 이미지')==5
    assert raw.count('loading="lazy"')==5
    assert '스카이차 견적, 최저가 비교 전 확인사항 | 바른견적스카이' in raw
    assert '업계 최저가를 주장하지 않습니다' in raw, f'Missing truthful price-comparison disclosure: {name}'
    for unsupported_claim in ('업계 최저가 보장','무조건 최저가','최저가를 보장합니다','타사보다 무조건 저렴'):
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
