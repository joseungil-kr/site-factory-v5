"""Isolated same-intent event-wreath experiment on real 49%-failed pages.

No region-specific event inferred from locality. All event contexts are
explicit buyer test inputs, NOT facts about 186/3012/2852 districts.
"""
from __future__ import annotations
import hashlib,json,re
from html import escape
from html.parser import HTMLParser
from itertools import combinations
from pathlib import Path
from v5.config import ROOT,read_site
from v5.audit import grams
from scripts.audit_todayflower_semantic_gate import article,score,LIMIT
from scripts.build_todayflower_ribbon_intent_pilot import STYLE

OUT=ROOT/"reports/todayflower-nalmada/event-intent-49pilot"
REGRESSIONS=(186,3012,2852)
INTENT="행사장 꽃 반입"
CASES={
 186:{"scenario":"wedding","title":"예식장 화환 반입 사전 승인형",
      "questions":["해당 예식장에서 외부 화환을 받을 수 있나요?","홀명·예식 시각과 설치 담당자를 누구에게 확인하나요?","주문 전 무엇을 기록해야 하나요?"],
      "sections":[
       ("결제 전 반입 결정","예식장 안내를 확인하지 않았다면 축하화환부터 결제하지 않습니다. 예식장 측에 외부 업체가 보내는 화환을 받는지, 특정 홀이나 시간에 별도 제한이 있는지를 질문하고 답변 확인 시각을 남기는 구매 흐름입니다."),
       ("예식 홀과 수령 담당자","웨딩홀 이름이 같아도 실제 예식 홀과 시작 시각, 현장에서 통화 가능한 담당자는 주문마다 다릅니다. 예식장명·홀명·예식일과 신랑·신부 측 구분이 필요한지 확인해 입력 메모를 작성합니다."),
       ("상품 선택 조건","해당 판매처의 축하화환 중 이 페이지에 실제 등록된 SKU 한 개를 비교 대상으로 삼습니다. 현장 반입 가능 형태와 제품 크기는 확정돼 있지 않아 행사장 답변과 상품 실측을 받은 다음 구매 여부를 결정합니다."),
       ("결제 직전 순서","판매처 상품번호, 리본 축하문구·발신 명의, 홀명·희망 시각, 허용 여부 확인 담당자를 별개 항목으로 확인합니다. 현장 반입·추가요금·현재 접수 가능 여부는 확인되지 않았습니다.")],
      "sourceIds":["EVENT_WEDDING_INDEX","EVENT_VENUE_INDEX"]},
 3012:{"scenario":"performance","title":"공연·전시 주최측 수령 조정형",
      "questions":["주최 측의 설치 승인을 받았나요?","공연·전시 회차와 실제 로비 위치를 확인했나요?","설치 뒤 확인과 회수 책임을 누가 맡나요?"],
      "sections":[
       ("공연장 담당 부서로 확인","공연·전시 축하 목적이라면 받는 사람과 시설 관리자가 다를 수 있습니다. 공연장 또는 주최 측 담당자에게 반입 가능 여부와 실제 수령 위치를 먼저 물어보고 확정되지 않은 설치 약속을 주문서에 쓰지 않습니다."),
       ("회차와 공간을 구분","공연명 또는 전시명, 행사 날짜, 상영·공연 회차, 층·홀과 현장 연락 가능한 사람을 서로 다른 항목으로 정리합니다. 같은 장소에서도 여러 행사가 있을 가능성을 주문서 작성 단계에서 점검하는 편집 절차입니다."),
       ("제품·설치 형태 선택","축하화환이 행사장에 들어갈 수 있는지는 아직 검증되지 않았습니다. 판매처의 등록된 SKU와 실제 규격을 확인하고 주최 측이 허용한 설치 방법이 확인된 이후에만 화환 또는 다른 유형을 비교합니다."),
       ("설치 확인과 후속 책임","행사 담당자에게 설치 완료 확인 방법과 행사 종료 후 회수 책임을 문의합니다. 판매처가 실물 사진을 제공하는지, 언제까지 리본을 변경할 수 있는지는 주문별로 확인해야 합니다.")],
      "sourceIds":["EVENT_PERFORMANCE_INDEX","EVENT_VENUE_INDEX"]},
 2852:{"scenario":"conference","title":"학회·세미나 사무국 조율형",
      "questions":["주최 사무국과 건물 관리자 중 누구에게 승인 받나요?","행사·홀·등록데스크 인수 담당자가 일치하나요?","단체 발신과 복수 주문을 어떻게 대조하나요?"],
      "sections":[
       ("학회 사무국에 먼저 문의","학회·세미나 축하화환은 행사명만으로 배달 지시를 확정할 수 없습니다. 주최 사무국에 외부 화환 수령·전시가 가능한지와 건물 관리 부서의 별도 승인이 필요한지를 구분해 질문합니다."),
       ("등록데스크와 행사장 위치 대조","같은 건물의 다른 회의실을 혼동하지 않도록 행사 날짜, 층·회의실명, 실제로 인수할 사무국 담당자와 전화번호를 한 화면에서 점검합니다. 사무국 답변이 없으면 ‘수령 가능’이라고 기록하지 않습니다."),
       ("단체 발신 SKU 선택","학회 주최 또는 후원 단체가 보내는 화환이라면 승인된 기관명·직함·발신 명의를 정리합니다. 축하화환 상품의 실제 크기와 승인된 반입 형태가 맞는지는 판매처와 건물 담당자에게 재확인합니다."),
       ("복수 주문과 주문 확인","여러 기관이 비슷한 명의로 주문한다면 상품번호, 발신 단체명, 행사명, 인수 담당자, 주문별 요청사항을 분리합니다. 현장 반입 시간·배송 가능성·실제 금액을 임의로 채우지 않습니다.")],
      "sourceIds":["EVENT_CONFERENCE_INDEX","EVENT_VENUE_INDEX"]}
}
SOURCES=[
{"id":"EVENT_WEDDING_INDEX","url":"https://pladaum.com/guide/celebration/wedding-wreath-order-guide","checkedOn":"2026-11-11","access":"search result extended source text; direct open cache miss","scope":"venue/ceremony/ribbon verification outline, other seller"},
{"id":"EVENT_PERFORMANCE_INDEX","url":"https://kkotjeonbo.kr/guide/전시회-공연-축하화환/","checkedOn":"2026-11-11","access":"search result indexed article body; direct open cache miss","scope":"performance/event handoff and confirmation, other seller"},
{"id":"EVENT_CONFERENCE_INDEX","url":"https://flowername.co.kr/blog/post.php?slug=hakhoe-semin나-hwahwan","checkedOn":"2026-11-11","access":"search result indexed body; slug to verify; URL NOT proven","scope":"conference/organizer checklist, NO link use"},
{"id":"EVENT_VENUE_INDEX","url":"https://flowername.co.kr/blog/post.php?slug=yesikjang-hwahwan-banip","checkedOn":"2026-11-11","access":"search result extended body; direct open cache miss","scope":"questions about recipient venue; not live policy"}
]
# Correction: use only URLs genuinely verified in search results.
SOURCES[2]["url"]="https://flowername.co.kr/blog/post.php?slug=hakhoe-seminar-hwahwan"

def H(x):return escape(str(x),quote=True)
def digest(s):return hashlib.sha256(s.encode("utf-8")).hexdigest()

def make(page,case,product):
    sku=sorted(x for x in page["productSkus"] if x.startswith("C"))[0]
    item=product[sku]
    assert item["orderUrl"]==f"https://fwith.co.kr/shop/item.php?it_id={sku}"
    return {"number":page["number"],"id":page["id"],"region":page["region"],
            "topic":INTENT,"scenario":case["scenario"],"scenarioExplicitInput":True,
            "intro":"이 격리 예시는 "+case["title"]+" 구매 상황을 가정한 시나리오입니다. "+
                    "해당 지역에 실제 이 행사가 열리거나 화환 반입이 허용된다는 뜻은 아닙니다.",
            "sections":[{"heading":h,"paragraph":p} for h,p in case["sections"]],
            "questions":case["questions"],"sourceIds":case["sourceIds"],
            "productSkus":[sku],"productName":item["name"],"orderUrl":item["orderUrl"],
            "editorialApproved":False,"currentInboundVerified":False}

def html(p):
    content="".join('<section data-article-slot="'+str(i)+'"><h2>'+H(s["heading"])+
                   '</h2><p data-article-text="section-'+str(i)+'">'+H(s["paragraph"])+
                   '</p></section>' for i,s in enumerate(p["sections"]))
    qs='<ol>'+''.join('<li>'+H(q)+'</li>' for q in p["questions"])+'</ol>'
    body=('<article class="article-content"><p data-article-text="intro">'+H(p["intro"])+'</p>'+
          content+'</article><section><h2>구매자가 실제로 답해야 할 질문</h2>'+qs+'</section>'+
          '<section><h2>선택 SKU·주문 원문</h2><p>'+H(p["productName"])+' ('+H(p["productSkus"][0])+')</p>'+
          '<p>행사장 반입·리본 길이·현재 배송 가능성·재고·최종 추가배송비는 미확인입니다.</p>'+
          '<a data-cta-sku="'+H(p["productSkus"][0])+'" href="'+H(p["orderUrl"])+'">해당 상품 주문페이지 열기</a></section>')
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'+
            '<meta name="viewport" content="width=device-width,initial-scale=1">'+
            '<meta name="robots" content="noindex,nofollow"><title>'+H(p["region"])+' '+INTENT+
            ' · '+H(p["scenario"])+'</title><style>'+STYLE+'</style></head>'+
            '<body><main><header><p>격리 시나리오 실험 · 운영 미반영</p><h1>'+H(INTENT)+
            ' — '+H(p["region"])+'</h1><p>지명만으로 구매 상황이 확정되는 것은 아닙니다.</p></header>'+
            body+'</main></body></html>')

class Text(HTMLParser):
    def __init__(self):
        super().__init__();self.key=None;self.found={}
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=="p" and d.get("data-article-text"):self.key=d["data-article-text"];self.found[self.key]=""
    def handle_data(self,text):
        if self.key:self.found[self.key]+=text
    def handle_endtag(self,tag):
        if tag=="p":self.key=None

def run():
    site=read_site("todayflower-nalmada")
    assert len(site["pages"])==5070
    assert site["site"]["publishEnabled"] is False and site["site"]["indexNow"]["enabled"] is False
    bynumber={p["number"]:p for p in site["pages"]}
    assert all(bynumber[n]["topic"]==INTENT for n in REGRESSIONS)
    assert all(any(s.startswith("C") for s in bynumber[n]["productSkus"]) for n in REGRESSIONS)
    originalWorst=score(grams(article(bynumber[186])),grams(article(bynumber[3012])))
    assert originalWorst>0.93
    products={p["sku"]:p for p in site["products"]}
    OUT.mkdir(parents=True,exist_ok=True)
    records=[]; candidates=[]
    for n in REGRESSIONS:
        p=make(bynumber[n],CASES[n],products);raw=html(p)
        parser=Text();parser.feed(raw)
        expect={"intro":p["intro"],**{f"section-{i}":s["paragraph"] for i,s in enumerate(p["sections"])}}
        assert parser.found==expect,(n,parser.found,expect)
        assert raw.count('data-cta-sku=')==1
        candidate=OUT/f"candidate-{n}.html"
        original=ROOT/"dist/todayflower-nalmada"/f"{n}.html"
        assert original.is_file()
        candidate.write_text(raw,encoding="utf-8")
        (OUT/f"original-{n}.html").write_bytes(original.read_bytes())
        candidates.append(p)
        records.append({"number":n,"originalIntent":bynumber[n]["topic"],"candidateIntent":p["topic"],
                        "scenarioInput":p["scenario"],"scenarioNotRegionalFact":True,
                        "sourceIds":p["sourceIds"],"customerQuestions":p["questions"],
                        "articleSlots":[{"section":i,"heading":s["heading"],"text":s["paragraph"]}
                                        for i,s in enumerate(p["sections"])],
                        "sku":p["productSkus"][0],"cta":p["orderUrl"],"candidateSHA256":digest(raw),
                        "originalHtmlSHA256":hashlib.sha256(original.read_bytes()).hexdigest(),
                        "originalToCandidate":score(grams(article(bynumber[n])),grams(article(p)))})
    pairs=[]
    for n,m in combinations(REGRESSIONS,2):
        a=next(x for x in candidates if x["number"]==n)
        b=next(x for x in candidates if x["number"]==m)
        pairs.append({"left":n,"right":m,
                      "baselineSimilarity":score(grams(article(bynumber[n])),grams(article(bynumber[m]))),
                      "candidateSimilarity":score(grams(article(a)),grams(article(b)))})
    base=[p for p in site["pages"][33:] if p["topic"]==INTENT]
    assert len(base)==333
    across=[{"candidate":p["number"],"original":b["number"],
             "similarity":score(grams(article(p)),grams(article(b)))}
             for p in candidates for b in base]
    assert len(across)==999
    report={"populationPreserved":333,"originalFullCorpusFailCountUnchanged":4503,
            "originalWorst186_3012":originalWorst,
            "originalThreshold":LIMIT,"method":"scripts.audit_todayflower_semantic_gate.article,score and v5.audit.grams",
            "candidateNumbers":list(REGRESSIONS),"candidatePairMetrics":pairs,
            "crossCorpusPairs":len(across),"crossCorpusViolations":sum(x["similarity"]>=LIMIT for x in across),
            "crossCorpusMaximum":max(across,key=lambda x:x["similarity"]),
            "sourceEvidence":SOURCES,"sourceRankingVerified":False,
            "sourceDirectOpened":False,"candidateMapping":records,
            "buyerChoices":[c["scenario"] for c in candidates],
            "noUniqueRegionalServiceFacts":True,
            "currentInboundVerified":False,"sellerStockVerified":False,
            "humanEditorialApproved":False,"publicReleaseApproved":False,
            "notNationwideSolution":True}
    (OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"candidate-models.json").write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TODAYFLOWER_EVENT_EQUAL_INTENT "+json.dumps({"pairs":pairs,"crossPairs":len(across),
          "crossViolations":report["crossCorpusViolations"],"baselineWorst":originalWorst},ensure_ascii=False))
    return report

if __name__=="__main__":run()
