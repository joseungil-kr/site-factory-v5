"""Generate a national *informational* noindex quote preview using frozen province/district records.
Reuses existing 25 Ansan pages, 5 original images, template and assets. Never infers service coverage.
"""
from pathlib import Path
from html import escape
import json,hashlib,importlib.util,shutil,re
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'sites/skyquote'
DEST=ROOT/'dist/skyquote-official-preview'
INFO=SITE/'official-upper-regions-20261022.json'
PROMPTS=[
('작업 높이와 거리','건물 층수와 함께 작업 지점까지 높이(미터), 차량을 세울 자리에서 작업 지점까지 수평거리를 알려주세요.'),
('차량 진입과 정차','진입로 폭과 회전 공간, 차량 정차 위치가 보이도록 현장 사진을 준비해 주세요.'),
('이용 시간','시작·종료 예정 시각과 작업시간을 알려주세요. 반나절 4시간·하루 8시간 기준과 초과·대기 요금을 함께 확인할 수 있습니다.'),
('이동과 회차','정확한 작업 주소와 출발 위치를 알려주세요. 이동·회차 비용이 견적에 포함되는지 확인해 드립니다.'),
('인원과 자재','작업대에 오를 인원과 공구·자재 무게, 작업 내용을 알려주세요. 장비 선택 상담에 도움이 됩니다.'),
('야간과 휴일','18시 이후 또는 휴일 작업이라면 희망 일정을 알려주세요. 추가 비용 여부를 미리 확인할 수 있습니다.'),
('현장 사진','주변 전선·장애물과 보행자 이동 경로가 보이는 사진을 보내주세요. 현장 준비 사항을 함께 살펴봅니다.'),
('일정 조율','일정 변경 가능성이 있다면 예약 전에 변경·취소 조건과 대기료 기준을 확인해 주세요.'),
('요금 비교','부가세와 기사·유류비·기본 보험료 포함 여부를 확인하고 같은 조건의 총액으로 비교해 보세요.')
]
def main():
    d=json.loads(INFO.read_text(encoding='utf-8'))
    assert d['sourceArchiveSHA256']=='44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd'
    rows=[{'id':e['code'],'level':1 if e['level']=='province' else 2,'region':e['fullName'].rsplit(' ',1)[0] if e['level']!='province' else e['fullName'],'name':e['name'],'fullName':e['fullName'],'parent':e['parent']} for e in d['entries']]
    assert len(rows)==284 and sum(x['level']==1 for x in rows)==16 and sum(x['level']==2 for x in rows)==268
    assert len({x['id'] for x in rows})==len(rows)
    spec=importlib.util.spec_from_file_location('ansan',ROOT/'scripts/build_skyquote_ansan.py')
    ansan=importlib.util.module_from_spec(spec);spec.loader.exec_module(ansan)
    ansan.main()
    if DEST.exists():shutil.rmtree(DEST)
    shutil.copytree(ansan.OUT,DEST)
    spec2=importlib.util.spec_from_file_location('base',ROOT/'scripts/build_skyquote.py')
    base=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(base)
    indices={}
    for record in rows:
        slug='national/'+record['id'].lower()+'.html'
        loc=record['fullName']
        key=hashlib.sha256(record['id'].encode()).digest()
        chosen=[]
        for digit in key:
            prompt=PROMPTS[digit%len(PROMPTS)]
            if prompt not in chosen:chosen.append(prompt)
            if len(chosen)==4:break
        assert len(chosen)==4
        # Role-driven questions: province level coordination vs site-level district quote.
        if record['level']==1:
            intro='작업을 계획한 시·군·구와 정확한 주소, 희망 일정을 알려주세요. 현장까지의 이동거리와 작업 조건을 바탕으로 견적을 상담할 수 있습니다.'
            special='작업 지점까지 높이와 차량 정차 위치에서의 수평거리, 탑승 인원과 자재 무게를 알려주시면 장비 상담에 도움이 됩니다.'
        else:
            intro='작업 주소와 희망 시간을 알려주세요. 작업 지점까지 높이와 차량을 세울 자리, 예상 작업시간을 함께 준비하면 견적 상담이 수월합니다.'
            special='예상 작업시간과 한 장소·여러 장소 작업 여부를 알려주세요. 반나절 4시간·하루 8시간 공개 요금과 초과·대기 비용을 함께 확인할 수 있습니다.'
        html=base.render(slug,loc,intro)
        blocks=['<section><h2>견적 상담에 필요한 정보</h2><p>'+escape(special)+'</p></section>']
        for heading,body in chosen:
            blocks.append('<section><h2>'+escape(heading)+'</h2><p>'+escape(body)+'</p></section>')
        blocks.append('<section><h2>견적 문의 예시</h2><p>'+escape(
          '작업 예정 주소와 날짜, 작업 지점 높이와 차량 정차 위치에서의 수평거리, 탑승 인원과 자재 무게, 예상 작업시간을 알려주세요. 공개 단가의 4시간·8시간 기준과 부가세, 야간·휴일·원거리 추가 비용을 함께 확인할 수 있습니다.')+'</p></section>')
        html=html.replace('<section><h2>현장 조건을 알려주시면 견적을 안내해 드립니다</h2>',''.join(blocks)+'<section><h2>현장 조건을 알려주시면 견적을 안내해 드립니다</h2>',1)
        # Images remain original 5, links point to already verified operator.
        p=DEST/slug;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(html,encoding='utf-8')
        indices[record['id']]={'slug':'/'+slug,'region':loc,'level':record['level'],'questions':[x[0] for x in chosen]}
    # Navigable official-code hierarchy: national directory -> province -> municipality -> ward.
    # No claim that any node is an available dispatch location.
    by_parent={}
    for record in d['entries']:
        if record.get('parent'):
            by_parent.setdefault(record['parent'],[]).append(record)
    for record in d['entries']:
        children=sorted(by_parent.get(record['code'],[]),key=lambda x:x['fullName'])
        links_for_children=''.join('<li><a href="/national/'+escape(ch['code'])+'.html">'+escape(ch['fullName'])+' — 견적 확인 질문</a></li>' for ch in children)
        code_note='<section><h2>공식 지역 코드와 연결</h2><p>2026년 10월 22일 확보한 법정동 코드 원장에 존재하는 지역입니다. 코드 '+escape(record['code'])+'는 행정구역 식별용이며 장비 출동·가격이나 영업지점을 증명하지 않습니다.</p>'
        if record.get('parent'):
            code_note+='<p><a href="/national/'+escape(record['parent'])+'.html">상위 지역 안내</a></p>'
        if children:
            code_note+='<h3>하위 지역의 비교 질문</h3><ul>'+links_for_children+'</ul>'
        code_note+='<p><a href="/national/index.html">전국 행정구역 목록</a></p></section>'
        target=DEST/'national'/(record['code']+'.html')
        html=target.read_text(encoding='utf-8')
        html=html.replace('</main>',code_note+'</main>',1)
        target.write_text(html,encoding='utf-8')
    root=DEST/'index.html'
    homepage=root.read_text(encoding='utf-8')
    homepage=homepage.replace('</main>','<section><h2>전국 지역명으로 견적 준비하기</h2><p>공식 행정구역명 안내이며 전국 출동 가능을 뜻하지 않습니다.</p><a href="/national/index.html">전국 행정구역별 견적 비교 질문 보기</a></section></main>',1)
    root.write_text(homepage,encoding='utf-8')
    # Group index for information discovery only; do not mislabel as service areas.
    links=''.join('<li><a href="'+x['slug']+'">'+escape(x['region'])+' — 견적 준비 안내</a></li>' for x in indices.values() if x['level']==1)
    page=DEST/'national/index.html'
    page.write_text('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>전국 지역별 스카이차 견적 안내 | 바른견적스카이</title><link rel="stylesheet" href="/assets/style.css"><style>img{max-width:100%;height:auto}main{overflow-wrap:anywhere}figure{margin:12px 0}</style></head><body><header><strong>바른견적스카이</strong><span>현장에 맞는 장비와 요금 상담</span></header><main><h1>전국 지역별 스카이차 견적 안내</h1><p>작업을 계획한 지역을 선택해 주세요. 정확한 현장 주소와 작업 내용을 알려주시면 이동거리와 이용 조건을 함께 상담할 수 있습니다.</p>'+''.join(base.photo(i) for i in range(5))+base.price_table_html()+'<ul>'+links+'</ul><p><a href="/">안산시 지역 안내</a> · <a href="tel:01053221952">전화 상담 010-5322-1952</a></p></main></body></html>',encoding='utf-8')
    assert not (DEST/'sitemap.xml').exists()
    urls=[p.relative_to(DEST).as_posix() for p in DEST.rglob('*.html') if p.name!='404.html']
    assert len(urls)==310,(len(urls),len(indices))
    (DEST/'national-manifest.json').write_text(json.dumps({'status':'noindex informational preview only','source':d['sourceRepo'],'sourceBlobSha':d['sourceBlobSha'],'sourceArchiveSHA256':d['sourceArchiveSHA256'],'sourceRetrievedOn':d['retrievedOn'],'nationalRecords':len(rows),'nationalInfoPages':284,'nationalDirectoryPages':1,'ansanPreserved':25,'totalContentPages':len(urls),'imageCountPerDetail':5,'serviceCoverageConfirmed':False,'noIndex':True,'noSitemap':True,'paths':urls},ensure_ascii=False,indent=2),encoding='utf-8')
    print('SKYQUOTE_OFFICIAL_NOINDEX_310_PAGES_BUILT provinces=16 upperOthers=268 national_index=1 ansan=25 images=original')
if __name__=='__main__':main()
