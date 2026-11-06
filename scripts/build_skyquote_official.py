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
('여러 작업 위치','한 건물에서 앞면과 측면을 모두 작업한다면 차량 정차 위치를 바꿔야 할 수 있습니다. 위치별 예상시간과 장비 재배치 비용을 함께 문의해 보세요.'),
('작업 준비 시간','간판이나 외벽 작업 전에 필요한 자재 준비와 주변 정리에 걸리는 시간을 예상해 보세요. 장비 이용시간을 계산할 때 준비·철수 시간이 어디에 포함되는지도 확인하실 수 있습니다.'),
('사전 출입 협의','건물 관리실이나 시설 담당자의 출입 협의가 필요한 현장이라면 가능한 작업시간을 함께 알려주세요. 일정 조율에 따른 대기시간을 상담하기 좋습니다.'),
('도로와 보행 동선','작업 구역이 차도나 보행로에 걸친다면 필요한 통제 범위와 시간을 먼저 살펴보세요. 관리주체 협의 여부도 견적 상담에서 확인하실 수 있습니다.'),
('장비 대기 시간','다른 작업팀의 작업이 끝난 뒤 장비를 사용한다면 예상 대기시간도 함께 알려주세요. 현장 지연이 생길 때 적용되는 요금 기준을 물어보시면 됩니다.'),
('날씨와 일정 조율','바람이나 비 때문에 일정 변경 가능성이 있다면 변경 가능한 시점과 재출동 비용을 미리 확인해 보세요. 실제 작업 여부는 현장 안전 조건에 따라 협의합니다.'),
('한 장소와 여러 장소','같은 날 작업할 곳이 여러 곳이라면 장소별 주소와 작업순서를 나눠 알려주세요. 이동횟수와 이동시간을 견적에 반영하는 방법을 상담할 수 있습니다.'),
('간판과 외벽 작업','간판 설치와 외벽 보수는 필요한 공구·자재와 작업 시간이 달라질 수 있습니다. 어떤 작업을 먼저 진행할지 알려주시면 장비 일정 상담에 도움이 됩니다.'),
('작업대에 올릴 물품','사람이 탑승하는 작업과 자재를 다루는 작업을 함께 계획했다면 작업방식과 무게를 별도로 말씀해 주세요. 안전한 작업 방법과 장비 조건을 전문가와 상의할 수 있습니다.'),
('정차 위치 조정','차량을 작업 지점 가까이에 세울 수 없다면 대체 정차 위치를 사진에 표시해 주세요. 이동 경로와 작업대 도달거리 조정이 필요한지 상담할 수 있습니다.'),
('예약 변경 기준','업무 일정이 자주 달라지는 현장이라면 예약 변경 가능 시각과 취소 시 적용되는 비용을 문의해 보세요. 확정 전 필요한 준비 사항을 안내받을 수 있습니다.'),
('작업 완료 후 정리','장비를 접고 철수할 공간과 예상 시간을 확보해 두면 작업 일정 잡기가 편합니다. 철수 시간이 이용시간에 포함되는지도 확인해 보세요.')
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
            if len(chosen)==2:break
        assert len(chosen)==2
        # Role-driven questions: province level coordination vs site-level district quote.
        if record['level']==1:
            intro='작업을 계획한 시·군·구와 정확한 주소, 희망 일정을 알려주세요. 현장까지의 이동거리와 작업 조건을 바탕으로 견적을 상담할 수 있습니다.'
            special='작업 지점까지 높이와 차량 정차 위치에서의 수평거리, 탑승 인원과 자재 무게를 알려주시면 장비 상담에 도움이 됩니다.'
        else:
            intro='작업 주소와 희망 시간을 알려주세요. 작업 지점까지 높이와 차량을 세울 자리, 예상 작업시간을 함께 준비하면 견적 상담이 수월합니다.'
            special='예상 작업시간과 한 장소·여러 장소 작업 여부를 알려주세요. 반나절 4시간·하루 8시간 공개 요금과 초과·대기 비용을 함께 확인할 수 있습니다.'
        html=base.render(slug,loc,intro)
        blocks=[]
        for heading,body in chosen:
            blocks.append('<section><h2>'+escape(heading)+'</h2><p>'+escape(body)+'</p></section>')

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
        code_note='<section><h2>관련 지역 안내</h2>'
        if record.get('parent'):
            code_note+='<p><a href="/national/'+escape(record['parent'])+'.html">상위 지역 안내</a></p>'
        if children:
            code_note+='<h3>지역별 견적 안내</h3><ul>'+links_for_children+'</ul>'
        code_note+='<p><a href="/national/index.html">전국 행정구역 목록</a></p></section>'
        target=DEST/'national'/(record['code']+'.html')
        html=target.read_text(encoding='utf-8')
        html=html.replace('</main>',code_note+'</main>',1)
        target.write_text(html,encoding='utf-8')
    root=DEST/'index.html'
    homepage=root.read_text(encoding='utf-8')
    homepage=homepage.replace('</main>','<section><h2>전국 지역명으로 견적 준비하기</h2><p><a href="/national/index.html">다른 지역의 스카이차 견적 안내 보기</a></p></section></main>',1)
    root.write_text(homepage,encoding='utf-8')
    # Group index for information discovery only; do not mislabel as service areas.
    links=''.join('<li><a href="'+x['slug']+'">'+escape(x['region'])+' — 견적 준비 안내</a></li>' for x in indices.values() if x['level']==1)
    page=DEST/'national/index.html'
    page.write_text('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>전국 지역별 스카이차 견적 안내 | 바른견적스카이</title><link rel="stylesheet" href="/assets/style.css"><style>img{max-width:100%;height:auto}main{overflow-wrap:anywhere}figure{margin:12px 0}.national-visuals{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}.national-visuals figure{margin:0}.national-visuals img{width:100%;height:auto;aspect-ratio:3/2;object-fit:cover}</style></head><body><header><strong>바른견적스카이</strong><span>현장에 맞는 장비와 요금 상담</span></header><main><h1>전국 지역별 스카이차 견적 안내</h1><p>작업을 계획한 지역을 선택해 주세요. 정확한 현장 주소와 작업 내용을 알려주시면 이동거리와 이용 조건을 함께 상담할 수 있습니다. 작업 지점까지 높이(미터)와 차량 정차 위치에서의 수평거리도 함께 알려주세요.</p><section><h2>영진스카이 공개 이용요금</h2>'+base.price_table_html()+'</section><section><h2>지역 선택</h2><ul>'+links+'</ul></section><section><h2>작업 장면 이해하기</h2><div class="national-visuals">'+''.join(base.photo(i) for i in range(5))+'</div></section><p><a href="/">안산시 지역 안내</a> · <a href="tel:01053221952">전화 상담 010-5322-1952</a></p></main></body></html>',encoding='utf-8')
    assert not (DEST/'sitemap.xml').exists()
    urls=[p.relative_to(DEST).as_posix() for p in DEST.rglob('*.html') if p.name!='404.html']
    assert len(urls)==310,(len(urls),len(indices))
    (DEST/'national-manifest.json').write_text(json.dumps({'status':'noindex informational preview only','source':d['sourceRepo'],'sourceBlobSha':d['sourceBlobSha'],'sourceArchiveSHA256':d['sourceArchiveSHA256'],'sourceRetrievedOn':d['retrievedOn'],'nationalRecords':len(rows),'nationalInfoPages':284,'nationalDirectoryPages':1,'ansanPreserved':25,'totalContentPages':len(urls),'imageCountPerDetail':5,'serviceCoverageConfirmed':False,'noIndex':True,'noSitemap':True,'paths':urls},ensure_ascii=False,indent=2),encoding='utf-8')
    print('SKYQUOTE_OFFICIAL_NOINDEX_310_PAGES_BUILT provinces=16 upperOthers=268 national_index=1 ansan=25 images=original')
if __name__=='__main__':main()
