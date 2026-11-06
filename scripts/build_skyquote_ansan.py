"""Expand only the 22 operator-listed Ansan administrative areas intersecting the frozen V5 ledger.
No nationwide or availability claims. Original three sample pages and image bytes stay unchanged in source.
"""
from pathlib import Path
from html import escape
import hashlib,importlib.util,json,shutil
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'sites/skyquote'
OUT=ROOT/'dist/skyquote-ansan-preview'
DOMAIN_CANDIDATE='skyquote.nalmada.net'
def main():
    spec=importlib.util.spec_from_file_location('skyquote_base',ROOT/'scripts/build_skyquote.py')
    base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
    source=ROOT/'data/regions/seoul_gyeonggi_current_dong.json'
    b=source.read_bytes()
    gitblob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    scope=json.loads((SITE/'ansan-expansion-scope.json').read_text(encoding='utf-8'))
    assert gitblob==scope['sourceBlobSha'], 'Source region ledger changed; stop instead of generating guessed places'
    ledger=json.loads(b.decode('utf-8'))
    rows=ledger['rows']
    assert len(rows)==1732 and ledger.get('asOf')==scope['sourceAsOf']
    allow=scope['regions']
    assert len(allow)==22 and len({x['slug'] for x in allow})==22
    assert sum(x['district']=='단원구' for x in allow)==9 and sum(x['district']=='상록구' for x in allow)==13
    for region in allow:
        assert ['경기도 안산시 '+region['district'],region['dong']] in rows,region
    # Build only the proven existing three-page source and copy its verified static assets.
    base.build()
    if OUT.exists():shutil.rmtree(OUT)
    shutil.copytree(base.OUT,OUT)
    (OUT/'ansan').mkdir()
    generated=[]
    def section(title,body):
        return '<section><h2>'+escape(title)+'</h2><p>'+escape(body)+'</p></section>'
    for i,place in enumerate(allow):
        if place['dong']=='고잔동':
            assert place['slug']=='gojan.html'
            continue
        district,dong=place['district'],place['dong']
        region='안산시 '+district+' '+dong
        # Reuse the visitor-first base template and add only the two useful
        # questions selected for this named area; never infer local geography.
        html=base.render(place['slug'],region,'')
        unique=section('견적 상담 전에 알려주세요',place['focus'])
        unique+=section('현장 사진과 일정도 함께 준비해 주세요',place['example'])
        html=html.replace('<section><h2>현장 조건을 알려주시면 견적을 안내해 드립니다</h2>',
                          unique+'<section><h2>현장 조건을 알려주시면 견적을 안내해 드립니다</h2>',1)
        target=OUT/place['slug']
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(html,encoding='utf-8')
        generated.append(place['slug'])
    # One additional district hub; no unverified promise of immediate dispatch.
    district='상록구'
    district_page='sangnok.html'
    body=base.render(district_page,'안산시 '+district,'')
    body=body.replace('<section><h2>현장 조건을 알려주시면 견적을 안내해 드립니다</h2>',
         section('상록구 현장 상담에 필요한 정보','작업 주소와 일정, 실제 높이와 차량 정차 위치에서의 수평거리, 탑승 인원과 자재 무게를 알려주세요.')+
         '<section><h2>현장 조건을 알려주시면 견적을 안내해 드립니다</h2>',1)
    (OUT/district_page).write_text(body,encoding='utf-8')
    generated.append(district_page)
    # Add navigable links to all original sample and newly generated pages.
    links=''.join('<li><a href="/'+escape(x['slug'])+'">안산시 '+escape(x['district']+' '+x['dong'])+' 스카이차 견적 비교 안내</a></li>' for x in allow)
    link_section='<section><h2>안산시 행정동 견적 비교 안내</h2><p>기존 사업자 지역 안내와 서울·경기 원장 두 자료에 함께 나타난 22개 행정동만 수록했습니다. 상담 가능 여부·가격은 현장별 확인이 필요합니다.</p><ul>'+links+'</ul><p><a href="/danwon.html">단원구 비교 안내</a> · <a href="/sangnok.html">상록구 비교 안내</a></p></section>'
    for path in ('index.html','danwon.html','gojan.html',district_page):
        target=OUT/path
        text=target.read_text(encoding='utf-8')
        text=text.replace('</main>',link_section+'</main>',1)
        target.write_text(text,encoding='utf-8')
    # Additional pages already link to siblings; explicitly connect them to city and district hubs.
    for path in generated:
        if path==district_page:continue
        target=OUT/path
        text=target.read_text(encoding='utf-8')
        district_hub='/danwon.html' if '/danwon-' in '/'+path else '/sangnok.html'
        text=text.replace('</main>','<section><h2>지역 안내로 이동</h2><p><a href="/">안산시 전체</a> · <a href="'+district_hub+'">해당 구 안내</a></p></section></main>',1)
        target.write_text(text,encoding='utf-8')
    # 1 city + 2 districts + 22 distinct administrative-dong pages = 25.
    all_pages=[p for p in OUT.rglob('*.html') if p.name!='404.html']
    assert len(all_pages)==25,(len(all_pages),[str(x) for x in all_pages])
    assert len(generated)==22 and (OUT/'gojan.html').is_file()
    report={'status':'noindex-preview-only','region':'안산시','source':scope['sourceLedger'],'sourceGitBlob':gitblob,
       'operatorDirectory':scope['providerSource'],'operatorListedAdministrativeAreas':22,
       'ledgerAnsanPlaceRows':sum('안산시' in x[0] for x in rows),
       'pages':25,'originalReviewedPages':3,'newPages':len(generated),'generated':[p.relative_to(OUT).as_posix() for p in all_pages],
       'noSitemap':True,'noServiceGuarantee':True,'noLowestPriceGuarantee':True}
    assert not (OUT/'sitemap.xml').exists()
    (OUT/'expansion-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('SKYQUOTE_ANSAN_NOINDEX_EXPANSION_BUILT',json.dumps({k:v for k,v in report.items() if k not in ('generated',)},ensure_ascii=False))
if __name__=='__main__':main()
