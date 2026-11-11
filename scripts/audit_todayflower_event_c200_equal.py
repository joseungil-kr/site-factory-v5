"""Same wedding + same C200 + same purpose, two regions: editorial pool control.

Reuse original V5 article(), grams(), score(), fixed 49% gate. Emit only
research HTML and a shared guide. Do not invent regional fact or claim pass.
"""
from __future__ import annotations
from html import escape
from html.parser import HTMLParser
import hashlib,json
from pathlib import Path
from v5.config import ROOT,read_site
from v5.audit import grams
from scripts.audit_todayflower_semantic_gate import article,score,LIMIT
from scripts.build_todayflower_event_49pilot import STYLE

SITE="todayflower-nalmada"
OUT=ROOT/"reports"/SITE/"event-c200-equivalent-control"
LEDGER=ROOT/"sites"/SITE/"event-c200-equivalent-evidence-20261111.json"
REGIONS=(186,3012)
INTENT="행사장 꽃 반입"
SKU="C200"
CASE={"buyerEvent":"wedding","productSku":"C200","buyerPurpose":"외부 축하화환을 예식장 행사에 보내기","senderType":"customer_unset"}

# Five unique decision owners, shared across different places absent local proof.
POOL={
 "venue_check":("반입 허용 확인","외부 축하화환을 행사장에 들일 수 있는지 시설 담당자에게 먼저 확인합니다. 확인 전에는 설치가 가능하다고 적지 않으며 시설 답변의 담당자와 날짜를 별도로 기록합니다."),
 "recipient_details":("예식 정보와 인수 담당","예식장 공식 명칭과 정확한 주소, 예식일과 홀 이름을 구분해 준비합니다. 인수 담당자와 전달 가능한 시간은 예약 확인 또는 주최 측 안내를 기준으로 다시 대조합니다."),
 "product_choice":("축하화환 C200 비교","상품번호 C200은 기존 상품원장에 있는 축하화환입니다. 실제 구성 크기와 설치 형태는 현재 검증되지 않았으므로 판매처 상품 상세와 시설 측 안내를 각각 확인한 뒤 제품을 선택합니다."),
 "ribbon_confirmation":("축하 문구와 발신자 확인","리본의 축하 문구와 보내는 단체·사람의 표기는 분리해 초안을 정리합니다. 실제 입력칸과 글자 제한, 수정 마감은 판매처에 확인하고 제작 전 철자와 발신자 공식 명칭을 최종 검토합니다."),
 "checkout_hold":("주문 제출 전 교차 확인","상품번호·예식장명·홀명·리본 문구·발신자명·수령 담당자를 한 번 더 대조합니다. 현재 재고, 배송 가능 여부, 추가배송비, 완료사진 및 주문 수락 시점은 확인되지 않았습니다.")
}
def H(x):return escape(str(x),quote=True)
def digest(s):return hashlib.sha256(s.encode("utf-8")).hexdigest()

def model(page,products,ledger):
    assert page["topic"]==INTENT and SKU in page["productSkus"]
    item=products[SKU]
    assert item["sku"]==SKU and item["orderUrl"]=="https://fwith.co.kr/shop/item.php?it_id=C200"
    return {"number":page["number"],"region":page["region"],"topic":INTENT,"scenario":dict(CASE),
      "role":"shared_buyer_guide_not_independent_region_detail",
      "intro":"동일 예식 목적·동일 C200 상품 조건에서 작성한 공통 주문 확인 안내입니다. 개별 지역 행사나 반입 조건이 검증됐다는 뜻은 아닙니다.",
      "sections":[{"heading":heading,"paragraph":body,"slot":slot} for slot,(heading,body) in POOL.items()],
      "productSkus":[SKU],"productName":item["name"],"orderUrl":item["orderUrl"],
      "verifiedRegionalFacts":[],"approvedForIndex":False}
def render(p):
    sections="".join('<section data-copy-slot="'+H(x["slot"])+'"><h2>'+H(x["heading"])+'</h2>'+
        '<p data-article-slot="'+H(x["slot"])+'">'+H(x["paragraph"])+'</p></section>'
        for x in p["sections"])
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'+
     '<meta name="viewport" content="width=device-width,initial-scale=1">'+
     '<meta name="robots" content="noindex,nofollow"><title>'+H(p["region"])+
     ' 행사장 꽃 반입 C200 공통 구매 검토</title><style>'+STYLE+'</style></head><body><main>'+
     '<header><p>격리 동일조건 대조·지역별 공개 불가</p><h1>'+H(p["region"])+
     ' C200 행사장 꽃 반입</h1></header><article class="article-content">'+
     '<p data-article-intro="true">'+H(p["intro"])+'</p>'+sections+'</article>'+
     '<section><h2>판매처 상품 확인</h2><p>'+H(p["productName"])+' (C200)</p>'+
     '<p>현재 상품 규격·재고·배송·리본 입력 정책은 확인되지 않았습니다.</p>'+
     '<a data-cta-sku="C200" href="'+H(p["orderUrl"])+'">판매처 C200 상세 확인</a></section>'+
     '</main></body></html>')
def generate():
    info=read_site(SITE)
    assert len(info["pages"])==5070
    assert not info["site"]["publishEnabled"] and not info["site"]["indexNow"]["enabled"]
    catalog={x["sku"]:x for x in info["products"]}
    pages={p["number"]:p for p in info["pages"]}
    src=json.loads(LEDGER.read_text(encoding="utf-8"))
    assert src["rankingVerified"] is False
    assert src["verifiedRegionLocalFactsFor1863012"]==0
    assert src["currentC200OrderConditionsVerified"] is False
    assert set(POOL)=={q["contentSlot"] for q in src["checks"]}
    outcomes=[]; models=[]
    for n in REGIONS:
        p=pages[n]
        assert p["topic"]==INTENT and SKU in p["productSkus"]
        m=model(p,catalog,src)
        raw=render(m)
        assert raw.count('data-cta-sku="C200"')==1
        assert 'noindex,nofollow' in raw
        OUT.mkdir(parents=True,exist_ok=True)
        target=OUT/f"candidate-{n}.html"
        target.write_text(raw,encoding="utf-8")
        models.append(m)
        outcomes.append({"number":n,"candidateHtml":target.name,"sha256":digest(raw),
                         "sku":SKU,"ctaURL":m["orderUrl"],"originalArticleSHA256":digest(article(p)),
                         "candidateArticleSHA256":digest(article(m))})
    before=score(grams(article(pages[186])),grams(article(pages[3012])))
    after=score(grams(article(models[0])),grams(article(models[1])))
    assert before>0.93 and after==1.0
    assert article(models[0])==article(models[1])
    assert models[0]["scenario"]==models[1]["scenario"]==CASE
    # Each source, question, rule and paragraph must be traceable by exact slot.
    sources={s["id"]:s for s in src["sources"]}
    trace=[]
    for q in src["checks"]:
        slot=q["contentSlot"]
        para=POOL[slot][1]
        assert slot in POOL and all(sid in sources for sid in q["sourceIds"])
        assert all(para in (OUT/f"candidate-{n}.html").read_text(encoding="utf-8") for n in REGIONS)
        trace.append({"id":q["id"],"customerQuestion":q["customerQuestion"],
                      "sourceIds":q["sourceIds"],"sourceURLs":[sources[sid]["url"] for sid in q["sourceIds"]],
                      "sourceAccess":[sources[sid]["retrieval"] for sid in q["sourceIds"]],
                      "editorialSourceType":q["type"],"selectionCondition":CASE,
                      "poolSlot":slot,"exactParagraph":para,
                      "htmlSelector":f'[data-article-slot="{slot}"]',
                      "applicableToBothRegions":True,"verifiedLocalFact":False})
    # Output one separate shared-copy reference. Two regional HTML files are
    # control-only duplicates, intentionally not future publish candidates.
    (OUT/"buyer-question-trace.json").write_text(json.dumps(trace,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"page-models.json").write_text(json.dumps(models,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report={"originalIntent":INTENT,"buyerScenario":CASE,
        "originalPopulationFixed":333,"originalExistingViolationsNotChanged":4503,
        "threshold":LIMIT,"method":"scripts.audit_todayflower_semantic_gate.article/score + v5.audit.grams",
        "original186_3012Similarity":before,"identicalBuyerC200CandidateSimilarity":after,
        "identicalBuyerContextStillFails49Percent":after>=LIMIT,
        "distinctRegionalBuyerDetailEvidence":0,
        "buyerDecisionSlots":len(POOL),"questionTraceCount":len(trace),
        "candidateControlFiles":outcomes,"candidateRole":"shared_copy_only",
        "independentLocalityHtmlApproved":0,
        "competitionSourcesDirectlyFullyRead":0,
        "competitionRankVerified":False,
        "sourceScopes":"new search excerpts and one source with only unrelated readable line; not proof of other merchant policy on C200",
        "humanEditorialApproved":False,"publicationApproved":False,
        "noOriginal5070UrlOrHtmlChange":True,
        "conclusion":"The original 93% duplicate is not solved by a shared guide and region name; identical C200/wedding input yields identical body. Hold both regional buyer documents; reuse shared customer-question pool once."}
    (OUT/"control-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TODAYFLOWER_EQUIVALENT_C200 "+json.dumps({"original":before,"candidateSameConditions":after,
       "gateFailed":after>=LIMIT,"html":len(outcomes),"published":0},ensure_ascii=False))
    return report
if __name__=="__main__":generate()
