"""Skyquote isolated three-region site; real .webp binaries required before deployment."""
from pathlib import Path
from html import escape
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'sites/skyquote'
OUT=ROOT/'dist/skyquote-preview'
IMG=['city-crane','facade-safety','sign-work','work-height','outrigger-access']
ALT=['도시 스카이차 전경','안전구획을 갖춘 외벽 작업대','안전한 간판 작업 설명','작업 높이와 도달거리 설명','아웃트리거 지반과 진입공간 확인']
ROWS=[('index.html','안산시','시 수준에서는 작업 주소와 장비 이동거리를 먼저 비교합니다.'),('danwon.html','안산시 단원구','구 수준에서는 높이와 차량 정차·진입 조건을 구체화합니다.'),('gojan.html','안산시 단원구 고잔동','동명만으로 현장 접근성이나 최저가가 결정되지 않습니다. 정확한 주소와 사진이 필요합니다.')]
CSS='''*{box-sizing:border-box}body{margin:0;background:#f7f8f6;color:#1b3028;font:16px/1.7 system-ui,sans-serif}header,footer{background:#103c31;color:#fff;padding:24px}header a,footer a{color:inherit}main{max-width:1100px;margin:auto;padding:24px}h1{font-size:clamp(28px,4vw,48px);line-height:1.3}h2{font-size:24px}section{padding:24px;border:1px solid #e1e8e3;border-radius:16px;margin:24px 0;background:#fff}.cta{display:inline-block;background:#096349;color:#fff;padding:14px 18px;border-radius:10px;text-decoration:none}.media{display:flex;gap:24px;align-items:center}.media div{flex:1;min-width:0}.media figure{flex:1;margin:0}.media img{width:100%;height:270px;object-fit:cover;border-radius:12px}.media figcaption{font-size:12px;color:#5b7066}.table{overflow-x:auto;max-width:100%}table{min-width:620px;width:100%;border-collapse:collapse}td,th{text-align:left;border-bottom:1px solid #ddd;padding:10px}@media(max-width:700px){.media{display:block}.media img{height:240px}section{padding:18px}main{padding:14px}}'''
def photo(i):
    return f'<figure><img src="/assets/{IMG[i]}.webp" loading="lazy" width="768" height="640" alt="{escape(ALT[i])}"><figcaption>AI 생성 설명 이미지 — 실제 시공·장비 보유 증명이 아닙니다.</figcaption></figure>'
def block(n,head,text):
    return f'<section class="media"><div><small>견적 안내 {n:02d}</small><h2>{head}</h2>{text}</div>{photo(n-1)}</section>'
def render(path,loc,note):
    title=f'{loc} 스카이차 견적, 최저가 비교 전 확인사항 | 바른견적스카이'
    sections=[
      block(1,'지역 견적 비교의 핵심',f'<p>{escape(note)} 실제 동일한 조건의 복수 업체 견적이 확보되지 않았으므로 최저가 또는 최저가 보장을 주장하지 않습니다.</p><p>현장 주소, 희망 시간, 높이, 수평 도달거리, 대기·이동·부가세 포함 여부가 같은 경우에만 총액을 비교합니다.</p>'),
      block(2,'차량·높이·시간을 같은 기준으로','<p>몇 층인지뿐 아니라 실제 미터 높이, 차량 정차점에서 작업점까지 거리와 탑승 인원·자재 중량을 기재합니다. 차량 톤수만으로 작업 가능성을 보장하지 않습니다.</p><p>반일인지 하루인지, 최소 시간과 초과 요금 기준이 무엇인지 비교합니다.</p>'),
      block(3,'비용 포함·별도 항목','<div class="table"><table><tr><th>항목</th><th>꼭 확인할 내용</th></tr><tr><td>기본료</td><td>장비·기사·연료 포함 여부</td></tr><tr><td>이동·출동</td><td>거리, 톨비, 회차비</td></tr><tr><td>대기</td><td>현장 지연·취소 산정 방식</td></tr><tr><td>야간·휴일</td><td>시간대 할증과 적용 시작</td></tr><tr><td>세금</td><td>부가세 포함 최종금액</td></tr></table></div>'),
      block(4,'안전 및 접근성 확인','<p>진입로 폭·경사, 지지대 설치면의 지반, 보행자 안전 구획, 인접 전선과 장애물을 점검합니다. 작업 허가 및 통행 통제 여부도 사전 확인이 필요합니다.</p><p>사진만으로 안전하게 작업 가능하다고 단정하지 않으며 현장 전문가의 확인이 우선입니다.</p>'),
      block(5,'같은 조건 견적 요청 체크리스트','<ul><li>주소 및 작업일·시작/종료 시간</li><li>작업 종류, 실제 높이, 도달거리</li><li>진입로·지반·전선·아웃트리거 공간</li><li>탑승 인원과 자재 하중</li><li>대기·야간·이동·부가세 포함 총액</li><li>견적 기준일과 유효기간</li></ul><p>가격은 비교할 원문 실견적이 확보될 때 동일 조건·기준일을 함께 밝혀야 합니다.</p>')]
    faq='<section><h2>FAQ</h2><details><summary>최저가를 보장하나요?</summary><p>아닙니다. 실제 비교 가능한 견적이 없으므로 보장하지 않으며 견적 비교 기준을 설명합니다.</p></details><details><summary>몇 층이면 어떤 차를 쓰나요?</summary><p>수평거리·하중·접근 조건을 확인한 뒤 장비를 정합니다.</p></details><details><summary>야간 비용은 같은가요?</summary><p>작업 시각과 업체별 조건에 따라 달라집니다. 별도 비용을 확인하세요.</p></details><details><summary>어디로 문의하나요?</summary><p>확인된 기존 영진스카이 운영 전화 010-5322-1952로 문의합니다.</p></details></section>'
    links=' · '.join(f'<a href="/{"" if p=="index.html" else p}">{escape(locname)} 견적</a>' for p,locname,_ in ROWS if p!=path)
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(loc)} 스카이차 견적 최저가 비교 전 높이·시간·차량·이동비·대기료 확인사항"><meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="/assets/style.css"></head><body><header><strong>바른견적스카이</strong> · 숫자보다 정확한 조건 비교</header><main><h1>{escape(title)}</h1><p>스카이차 견적의 최저가를 찾는다면 조건과 추가비용을 먼저 맞춰 보세요. 업계 최저가를 주장하지 않습니다.</p><a class="cta" href="tel:01053221952">견적 상담 010-5322-1952</a><p><a href="https://www.skycar1day.com/">확인된 영진스카이 운영 사이트</a></p>{"".join(sections)}<section><h2>문의 절차</h2><p>현장정보 확인 → 적합 장비·일정 상담 → 이동·대기·야간비 포함 총액 확인 → 작업 조건과 안전 확인 → 예약 여부 결정</p><a class="cta" href="tel:01053221952">확인된 연락처로 문의</a></section>{faq}<section><h2>관련 지역 안내</h2>{links}</section></main><footer>AI 설명 이미지 사용 · 실제 현장 작업사례가 아닙니다. 실제 지역 지점·배차·최저가 보장 없음.</footer></body></html>'
def build():
    if OUT.exists():shutil.rmtree(OUT)
    (OUT/'assets').mkdir(parents=True)
    for name in IMG:
        path=SITE/'assets'/f'{name}.webp'
        if not path.is_file(): raise RuntimeError(f'Missing REAL AI image file (not placeholder): {path}')
        shutil.copy2(path,OUT/'assets'/path.name)
    (OUT/'assets/style.css').write_text(CSS,encoding='utf-8')
    manifest=[]
    for path,loc,note in ROWS:
        t=render(path,loc,note)
        assert t.count('<img ')==5 and t.count('AI 생성 설명 이미지')==5
        (OUT/path).write_text(t,encoding='utf-8')
        manifest.append({'file':path,'title':loc+' 스카이차 견적, 최저가 비교 전 확인사항 | 바른견적스카이','images':5})
    (OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
    (OUT/'404.html').write_text('<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><h1>페이지 없음</h1>',encoding='utf-8')
    (OUT/'manifest.json').write_text(json.dumps({'status':'preview-only','pages':manifest,'imageHashes':{x:hashlib.sha256((OUT/'assets'/f'{x}.webp').read_bytes()).hexdigest() for x in IMG}},ensure_ascii=False,indent=2),encoding='utf-8')
    print('SKYQUOTE_THREE_PAGES_READY',len(manifest))
if __name__=='__main__':build()
