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
    gitblob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\\0'+b).hexdigest()
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
        # Reuse the existing template, but add independent useful Q&A and conditional scenarios.
        html=base.render(place['slug'],region,place['focus'])
        unique=section('이 지역 문의에서 먼저 분명히 할 조건',place['focus'])
        unique+=section('두 작업 상황을 동일 견적으로 취급하지 않는 이유',place['example'])
        questions=[
          '장비를 이동 없이 고정하는 한 장소 작업과 여러 위치를 옮기는 작업은 총 대기시간과 이동비가 달라질 수 있습니다. 업체별 재배치 비용 포함 여부를 체크합니다.',
          '시간제와 반일·하루 견적의 기준 시각이 다른 경우가 있으므로, 준비·안전점검·철수 시간이 청구시간에 들어가는지 적어 두세요.',
          '작업물의 무게와 작업대에 오르는 인원, 작업점까지의 수평 거리를 미리 전달해야 차량 톤수만 비교하는 실수를 피할 수 있습니다.',
          '작업 시작 전 도로·보행 구획을 확보해야 한다면 허가와 안전 유도 비용을 최종 견적에 포함하는지 분명히 확인하세요.',
          '일정이 변경될 수 있는 작업은 예약 변경·취소 가능 시각과 회차 비용까지 같은 기준으로 문의해야 실제 총액 비교가 됩니다.',
          '비 오는 날 또는 강풍 위험이 있는 날은 작업 가능성을 단정하지 말고 업체의 안전 중지 기준과 일정 변경 비용을 확인하세요.',
          '차량 진입 폭과 아웃트리거를 펼칠 공간을 구분해 제시하면 현장에 도착해서야 장비를 바꾸는 위험을 줄일 수 있습니다.',
          '고정된 장비 사진만으로 안전 가능 여부를 판정하지 말고 실제 작업할 위치와 전선·장애물 정보를 전문가에게 확인받으세요.',
          '자재 인양과 사람 탑승은 같은 가격·안전 조건이 아닐 수 있습니다. 작업 목적과 중량을 분리해 문의해야 합니다.'
        ]
        # This block varies by actual comparison question, not geographic stereotypes.
        unique+=section('견적서에 추가할 구체적인 확인 질문',questions[i%len(questions)])
        unique+=section('견적 요청 예시 — 가격 약속이 아닌 입력 방법',
             '작업지: '+region+' 소재 정확한 도로명주소(별도 확인). 작업 종류와 사진, 최대 높이(미터), 수평 거리(미터), '
             '예상 작업시간, 보행자 통제 및 지지대 설치조건을 함께 전달하고 총금액의 부가세·출동·대기·야간 비용 포함 여부를 확인합니다.')
        html=html.replace('<section><h2>문의 절차</h2>',unique+'<section><h2>문의 절차</h2>',1)
        target=OUT/place['slug']
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(html,encoding='utf-8')
        generated.append(place['slug'])
    # One additional district hub; no unverified promise of immediate dispatch.
    district='상록구'
    district_page='sangnok.html'
    body=base.render(district_page,'안산시 '+district,
        '상록구 상담 대상 지역에 대해서도 현장 주소·하중·도달거리·아웃트리거 공간을 먼저 확인해야 합니다.')
    body=body.replace('<section><h2>문의 절차</h2>',section('상록구 견적 비교 준비',
         '장비가 닿는 실제 거리와 정차 위치를 확인한 뒤 여러 견적서의 최소 이용시간, 추가대기료, 현장 이동비, 세금 포함 총액을 대조합니다. 운영업체의 지역 안내는 상담 가능지역 참고이지 최저가나 당일 배차 보장이 아닙니다.')+'<section><h2>문의 절차</h2>',1)
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
