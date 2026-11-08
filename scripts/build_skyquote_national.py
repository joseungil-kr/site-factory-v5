"""Generate a national *informational* noindex quote preview using frozen province/district records.
Reuses existing 25 Ansan pages, 5 original images, template and assets. Never infers service coverage.
"""
from pathlib import Path
from html import escape
import json,hashlib,importlib.util,shutil,re
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'sites/skyquote'
DEST=ROOT/'dist/skyquote-national-preview'
INFO=SITE/'nationwide-district-source.json'
PROMPTS=[
('높이와 수평거리','작업점의 실제 높이와 차량 정차 위치에서의 수평거리를 각각 측정했나요? 층수만으로 장비를 확정하지 마세요.'),
('진입 공간','차량의 진입 폭·회전 공간과 아웃트리거 전개 폭을 따로 확인했나요? 현장 사진과 계측값이 필요합니다.'),
('시간과 대기','작업 시작·종료 예상 시각 외에 안전점검과 정리 시간을 포함했나요? 최소 청구시간과 대기료 적용 시점을 질문하세요.'),
('이동과 회차','차량 출발지와 정확한 현장 주소가 확인됐나요? 이동·회차·통행료가 총액에 포함됐는지 확인하세요.'),
('자재와 작업인원','작업대에 오를 인원과 장비·자재 중량을 따로 기재했나요? 차량 톤수만으로 안전조건을 단정하지 마세요.'),
('야간·휴일','예정된 실제 작업시간에 야간·휴일 할증이 적용되나요? 포함·별도 청구 항목을 문의하세요.'),
('안전 통제','보행자·차량 동선 통제와 주변 전선·장애물 점검이 필요한지 전문가에게 확인했나요? 허가 비용도 분리해 확인하세요.'),
('변경과 취소','작업일 변경이나 현장 사정으로 중단할 경우 취소·대기·재출동비가 발생하는지 서면으로 문의하세요.'),
('가격 총액','반일·하루·시간제 각 견적에 부가세와 작업 준비·철수 시간이 어떻게 포함되는지 동일 조건으로 대조하세요.'),
]
def main():
    d=json.loads(INFO.read_text(encoding='utf-8'));rows=d['rows']
    assert d['license']=='CC-BY-4.0' and len(rows)==242
    assert sum(x['level']==1 for x in rows)==17 and sum(x['level']==2 for x in rows)==225
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
        loc=record['region'] if record['level']==1 else record['region']+' '+record['name']
        key=hashlib.sha256(record['id'].encode()).digest()
        chosen=[]
        for digit in key:
            prompt=PROMPTS[digit%len(PROMPTS)]
            if prompt not in chosen:chosen.append(prompt)
            if len(chosen)==4:break
        assert len(chosen)==4
        # Role-driven questions: province level coordination vs site-level district quote.
        if record['level']==1:
            intro='광역 행정명만으로 차량 출동이나 가격을 정할 수 없습니다. 구체적인 시·군·구와 작업지 주소가 필요합니다.'
            special='시·도 단위 문의에서는 실제 작업할 시·군·구, 도로명주소, 출발지·현장 이동비를 확인한 뒤 세부 견적을 받아야 합니다.'
        else:
            intro='시·군·구 이름은 현장정보가 아닙니다. 정확한 주소와 건물 작업면·정차 가능 위치를 먼저 확인하세요.'
            special='시·군·구 단위 문의에서는 정차 위치, 실제 작업 높이와 수평 거리, 지지대 설치 조건을 한 견적 요청서에 같이 적습니다.'
        html=base.render(slug,loc,intro)
        blocks=['<section><h2>견적 산정 전 공통으로 확인할 실제 정보</h2><p>'+escape(special)+'</p><p>행정구역 표기는 지역 식별용이며 실제 출동 가능 여부와 요금은 확인되지 않았습니다. 이 페이지는 업체별 동일 조건 비교를 위한 정보 문서입니다.</p></section>']
        for heading,body in chosen:
            blocks.append('<section><h2>'+escape(heading)+' 비교 질문</h2><p>'+escape(body)+'</p></section>')
        blocks.append('<section><h2>동일 조건 견적 요청 문장 예시</h2><p>'+escape(
          '작업 예정지 '+loc+'의 정확한 현장 주소는 별도로 전달합니다. 장비 도달 높이·수평거리·하중·정차면·예상 작업시간·준비 및 철수 시간에 대해 차량/기사/이동/대기/야간/부가세 포함 여부를 구분한 견적을 요청합니다.')+'</p><p>어느 업체가 최저가인지는 실제 동조건 견적을 확보하기 전에는 알 수 없습니다.</p></section>')
        html=html.replace('<section><h2>문의 절차</h2>',''.join(blocks)+'<section><h2>문의 절차</h2>',1)
        # Images remain original 5, links point to already verified operator.
        p=DEST/slug;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(html,encoding='utf-8')
        indices[record['id']]={'slug':'/'+slug,'region':loc,'level':record['level'],'questions':[x[0] for x in chosen]}
    # Group index for information discovery only; do not mislabel as service areas.
    links=''.join('<li><a href="'+x['slug']+'">'+escape(x['region'])+' — 견적 준비 안내</a></li>' for x in indices.values() if x['level']==1)
    page=DEST/'national/index.html'
    page.write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><title>전국 행정구역별 스카이차 견적 확인사항 | 바른견적스카이</title><link rel="stylesheet" href="/assets/style.css"><style>img{max-width:100%;height:auto}main{overflow-wrap:anywhere}figure{margin:12px 0}</style><main><h1>전국 행정구역별 견적 비교 준비</h1><p>이 목록은 CC-BY 행정구역 정보로, 스카이차 업체의 전국 출동 범위·현장 작업사례 또는 가격 보장 목록이 아닙니다.</p><p>아래 다섯 이미지는 AI 생성 견적 설명용으로 실제 현장의 증거가 아닙니다.</p>'+''.join(base.photo(i) for i in range(5))+'<ul>'+links+'</ul><a href="/">안산시 검수 페이지</a></main></html>',encoding='utf-8')
    assert not (DEST/'sitemap.xml').exists()
    urls=[p.relative_to(DEST).as_posix() for p in DEST.rglob('*.html') if p.name!='404.html']
    assert len(urls)==268,(len(urls),len(indices))
    (DEST/'national-manifest.json').write_text(json.dumps({'status':'noindex informational preview only','source':d['source'],'sourceBlobDistrict':d['sourceBlobDistrict'],'sourceBlobProvince':d['sourceBlobProvince'],'license':d['license'],'sourceDate':d['sourceDate'],'nationalRecords':len(rows),'nationalInfoPages':242,'nationalDirectoryPages':1,'ansanPreserved':25,'totalContentPages':len(urls),'imageCountPerDetail':5,'serviceCoverageConfirmed':False,'noIndex':True,'noSitemap':True,'paths':urls},ensure_ascii=False,indent=2),encoding='utf-8')
    print('SKYQUOTE_NATIONAL_NOINDEX_268_PAGES_BUILT provinces=17 districts=225 national_index=1 ansan=25 images=original')
if __name__=='__main__':main()
