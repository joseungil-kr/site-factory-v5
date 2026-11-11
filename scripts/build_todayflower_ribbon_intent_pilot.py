"""Three *intent-preserving* independent purchase-question editorial candidates.

Same exact char-5-gram logic and article() as original semantic audit.
No changes to 5,070 existing URLs or production page generator. No invented
ribbon length, venue policy, stock, or live checkout behavior.
"""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from itertools import combinations
from collections import Counter

from v5.config import ROOT, read_site
from v5.audit import grams
from scripts.audit_todayflower_semantic_gate import article, score, LIMIT
from v5.todayflower_copy_pool import SCENARIOS

SITE="todayflower-nalmada"
ROOTOUT=ROOT/"reports"/SITE/"celebration-ribbon-intent-pilot"
SOURCE=ROOT/"sites"/SITE/"celebration-ribbon-search-evidence-20261111.json"
INTENT="축하 리본 문구"
ROLES=("personal_greeting","company_official_sender","joint_group_approval")
ROLE_LABELS={"personal_greeting":"개인 명의 축하",
             "company_official_sender":"회사·부서 공식 명의",
             "joint_group_approval":"공동·단체 명의"}
# Situations are EXPLICIT editorial test inputs, not inferred from geography.
BUYER_SITUATIONS=(
 {"senderType":"individual","approvalOwner":"self","eventPurpose":"personal_celebration"},
 {"senderType":"company","approvalOwner":"corporate_officer","eventPurpose":"formal_event"},
 {"senderType":"joint_group","approvalOwner":"group_representative","eventPurpose":"shared_celebration"},
)
def select_role(buyer):
    assert buyer["eventPurpose"] in ("personal_celebration","formal_event","shared_celebration")
    assert buyer["senderType"] in ("individual","company","joint_group")
    assert buyer["approvalOwner"] in ("self","corporate_officer","group_representative")
    mapping={("individual","self","personal_celebration"):"personal_greeting",
             ("company","corporate_officer","formal_event"):"company_official_sender",
             ("joint_group","group_representative","shared_celebration"):"joint_group_approval"}
    key=buyer["senderType"],buyer["approvalOwner"],buyer["eventPurpose"]
    assert key in mapping,"Unsupported sender/approval context must not silently fall back"
    return mapping[key]
STYLE="""*{box-sizing:border-box}body{margin:0;background:#f7f8f6;color:#173629;font:16px/1.75 'Noto Sans CJK KR',system-ui,sans-serif}main{max-width:1000px;padding:24px;margin:auto}header{background:#e8f1e9;padding:24px;border-radius:16px}h1{font-size:clamp(26px,4vw,36px);line-height:1.3}h2{font-size:21px}section{background:white;border:1px solid #dfe5dc;border-radius:14px;padding:23px;margin:16px 0}a{color:#13623c;overflow-wrap:anywhere}.caution{color:#755626}.tag{font-size:13px;color:#2c6b46;font-weight:700}.split{display:grid;grid-template-columns:1fr 1fr;gap:14px}.split div{background:#f2f5f0;padding:12px;border-radius:10px}dt{font-weight:700}dd{margin:2px 0 12px}li{margin:7px 0}@media(max-width:520px){main{padding:10px}header{padding:18px}section{padding:16px}.split{grid-template-columns:1fr}}"""
def h(t): return escape(str(t),quote=True)
def sha(t):return hashlib.sha256(t.encode("utf-8")).hexdigest()

def choose():
    data=read_site(SITE)
    assert len(data["pages"])==5070
    assert not data["site"]["publishEnabled"] and not data["site"]["indexNow"]["enabled"]
    population=[p for p in data["pages"][33:] if p["topic"]==INTENT]
    assert len(population)>=3 and any(p["number"]==4582 for p in population)
    bynum={p["number"]:p for p in population}
    first=bynum[4582]
    others=[p for p in population if p["number"]!=4582 and any(s.startswith("C") for s in p["productSkus"])]
    # deterministic, not cherry-picked by a similarity score
    others.sort(key=lambda p:p["number"])
    assert len(others)>=2
    return data, population, [first]+others[:2]

def question_rules():
    ledger=json.loads(SOURCE.read_text(encoding="utf-8"))
    ids={s["id"] for s in ledger["sources"]}
    assert len(ids)==len(ledger["sources"])==7
    assert len(ledger["questionToRules"])==5
    assert all(set(q["basis"])<=ids for q in ledger["questionToRules"])
    assert ledger["rankingVerified"] is False and ledger["observedRank"] is None
    return ledger

def build_candidate(source,role,products):
    catalog={p["sku"]:p for p in products}
    listed=[sku for sku in source["productSkus"] if sku.startswith("C")]
    assert listed
    assert set(listed)<=set(catalog)
    sku=sorted(listed)[0]
    item=catalog[sku]
    assert item["orderUrl"]==f"https://fwith.co.kr/shop/item.php?it_id={sku}"
    sections={
     "personal_greeting":[
      ("행사의 성격부터 분류","받는 분의 행사가 결혼·개업·공연 중 어디에 해당하는지 먼저 결정합니다. 가까운 지인에게 보내는 개인 화환이라면 공적인 직함보다 관계를 알아볼 수 있는 이름을 우선할지 선택하세요."),
      ("두 줄을 각각 완성","축하 문구 초안은 ‘새 출발을 축하합니다’입니다. 보내는 사람 표기는 개인의 실제 이름을 별도 한 줄로 작성합니다. 예시는 사용자가 바꿀 수 있는 제안이지 판매처 기본 옵션이 아닙니다."),
      ("공개 장소와 표현의 온도","개인적인 별명이나 장난스러운 표현은 다른 참석자에게도 보일 수 있는지 먼저 판단합니다. 공식 행사라면 축하 대상이 누구인지 분명한 간결한 표현으로 바꾸는 편이 안전합니다."),
      ("제작 전 마지막 확인","축하문구와 발신자 이름 두 줄을 다시 읽고, 주문 화면에 선택한 상품번호와 동일한지 확인합니다. 리본 최대 글자 수와 실제 좌우 배치는 확인되지 않았으니 판매처에 최종 제작 가능 여부를 물어보세요.")],
     "company_official_sender":[
      ("보내는 법인·부서를 구분","회사 차원에서 보내는 화환인지 부서 단위 축하인지 결정합니다. 회사명과 부서명·직함 중 실제 발신 주체의 승인을 받은 표기만 리본에 남기는 것이 핵심입니다."),
      ("회사 표기 결재 확인","축하 표현의 편집 예시는 ‘뜻깊은 행사를 축하드립니다’입니다. 발신자 칸에는 회사의 공식 상호와 필요할 때만 직함·성명을 붙입니다. 법인명과 약칭을 섞지 않도록 승인된 철자를 대조하세요."),
      ("긴 직함의 제작 가능성","회사명과 직함을 모두 넣으려면 한 줄이 지나치게 길어질 수 있습니다. 줄바꿈·줄 수·한자·기호 허용 여부는 판매처마다 달라 확정할 수 없습니다. 제작 가능 시안을 먼저 확인해야 합니다."),
      ("승인·주문 대조","초안을 최종 승인한 담당자와 주문 담당자를 구분하고, 행사 목적·발신 표기·상품번호가 같은지 결제 전에 대조합니다. 특정 행사장의 반입 가능 여부도 주문처 또는 현장에 별도 확인하세요.")],
     "joint_group_approval":[
      ("공동 발신의 대표명을 확정","동문회·협회·여러 명의 공동 축하라면 명단 전체를 쓸지 모임 이름 하나로 쓸지 합의합니다. 주문 담당자와 실제 리본에 표시할 단체명의 책임자를 분리해 두세요."),
      ("합의한 두 줄을 한 번에 검토","축하 문구의 독립 편집 예시는 ‘오늘의 성취를 함께 기뻐합니다’입니다. 보내는 사람은 ‘○○모임 일동’처럼 승인된 단체명으로 별도 작성합니다. 단체의 실제 이름은 사용자가 확정해야 합니다."),
      ("변경 이력과 중복 주문 방지","단체명 뒤의 기수나 직함이 바뀌면 변경된 한 줄만 보내지 말고 축하문구·발신자 두 줄을 함께 다시 확인합니다. 모임 내 주문 담당자 한 명을 정해 동일 행사에 중복 주문이 생기지 않는지 점검합니다."),
      ("최종본 전달","최종 문구 두 줄, 상품번호, 행사 명칭, 받을 사람이나 현장 담당자를 별도 항목으로 정리해 주문처에 전달합니다. 리본 길이·인쇄 방식·수정 마감과 행사장 인수 조건은 아직 확인된 값이 없습니다.")]
    }
    assert role in sections
    subtitle={"personal_greeting":"개인 발신자가 문구 톤을 고르는 경우",
              "company_official_sender":"법인·부서의 승인된 발신 명칭이 필요한 경우",
              "joint_group_approval":"공동 발신·단체명 변경과 주문 책임을 정리해야 하는 경우"}[role]
    intro=subtitle+". 축하 리본 문구와 보내는 분 표기를 주문 전에 서로 다른 항목으로 확정합니다."
    return {"number":source["number"],"pageId":source["id"],"region":source["region"],
            "originalIntent":source["topic"],"topic":INTENT,"role":role,
            "roleLabel":ROLE_LABELS[role],"intro":intro,
            "sections":[{"heading":x,"paragraph":y} for x,y in sections[role]],
            "productSkus":[sku],"productName":item["name"],"orderUrl":item["orderUrl"],
            "sampleOnly":True,"buyerQuestions":["Q_PURPOSE","Q_SENDER","Q_PHRASE","Q_LENGTH","Q_CHECKOUT"],
            "editorialApproval":False,"currentRibbonLimitsKnown":False}

def html_doc(p,ledger):
    assert p["originalIntent"]==p["topic"]==INTENT
    sections="".join('<section data-section="'+str(i)+'"><h2>'+h(x["heading"])+'</h2>'
                     '<p data-copy="section-'+str(i)+'">'+h(x["paragraph"])+'</p></section>'
                     for i,x in enumerate(p["sections"]))
    meta=('<section><h2>상품과 주문 이동</h2><p>고정 상품원장의 상품명: <strong>'
          +h(p["productName"])+'</strong> / 상품번호 <strong>'+h(p["productSkus"][0])+'</strong></p>'
          '<p>현재 가격·재고·리본 길이·배송 가능 여부·입력 UI는 검증되지 않았습니다.</p>'
          '<p><a data-cta-sku="'+h(p["productSkus"][0])+'" href="'+h(p["orderUrl"])+'">'
          '해당 상품의 판매처 원문 확인</a></p></section>')
    refs='<section><h2>확인된 원문과 편집 구분</h2><p>실제 검색결과의 노출 순위는 확인되지 않았습니다. '
    refs+='리본 선택 흐름은 경쟁자료의 관찰 주제를 참고했지만 문장과 예시는 새로 작성한 편집 제안입니다.</p><ul>'
    for src in ledger["sources"]:
        if src["id"] in ("COMP_ORDER","COMP_EXAMPLES","COMP_RIBBON","SELLER_C206"):
            refs+='<li><a href="'+h(src["url"])+'">'+h(src["title"])+'</a> — '+h(status_labels.get(src["access"],"확인범위가 제한된 자료"))+'</li>'
    refs+='</ul></section>'
    status_labels={"search_index_excerpt; direct open cache miss":"검색에 표시된 요약 확인 · 원문 직접 열기 실패",
                   "seller indexed product page snippet, direct open cache miss":"판매처 검색 요약 확인 · 직접 열기 실패",
                   "direct page read failed; use pinned Todayflower catalog only":"원문 접근 실패 · 기존 상품원장만 사용"}
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow"><title>'+h(p["region"])+' 축하 리본 문구 · '+h(p["roleLabel"])+'</title>'
            '<style>'+STYLE+'</style></head><body><main><header><div class="tag">격리 사용자 상황별 후보 · 운영 미반영</div>'
            '<h1>'+h(p["region"])+' 축하 리본 문구</h1>'
            '<p>지명만으로 문서 내용이 달라지는 것은 아닙니다. 이 후보는 <strong>'+h(p["role"])+'</strong>'
            ' 구매 상황에 한정된 편집 테스트입니다.</p></header>'
            '<article class="article-content"><p data-copy="intro">'+h(p["intro"])+'</p>'+sections+'</article>'
            +meta+refs+'</main></body></html>')

class VisibleCopy(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.stack=[];self.values=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="p" and a.get("data-copy"):self.stack.append(a["data-copy"])
    def handle_endtag(self,tag):
        if tag=="p" and self.stack:self.stack.pop()
    def handle_data(self,data):
        if self.stack:self.values.append((self.stack[-1],data))

def audit():
    source,population,selected=choose()
    ledger=question_rules()
    OUT=ROOTOUT
    OUT.mkdir(parents=True,exist_ok=True)
    pages=[];records=[];pairs=[]
    base={p["number"]:p for p in selected}
    original_candidates=sorted([p["number"] for p in selected])
    assert 4582 in original_candidates
    for source_page,buyer in zip(selected,BUYER_SITUATIONS):
        role=select_role(buyer)
        row=build_candidate(source_page,role,source["products"])
        row["buyerSituation"]=buyer
        page_html=html_doc(row,ledger)
        doc=OUT/f'candidate-{row["number"]}.html'
        doc.write_text(page_html,encoding="utf-8")
        extractor=VisibleCopy();extractor.feed(page_html)
        fragments={}
        for k,v in extractor.values:fragments[k]=fragments.get(k,"")+v
        expected={"intro":row["intro"]}
        expected.update({f"section-{i}":sec["paragraph"] for i,sec in enumerate(row["sections"])})
        assert fragments==expected,(row["number"],fragments,expected)
        assert 'noindex,nofollow' in page_html
        assert page_html.count('data-cta-sku=')==1
        assert row["productSkus"][0] in source_page["productSkus"]
        for link in re.findall(r'<a[^>]+href="([^"]+)"',page_html):
            assert link.startswith("https://") and link in {x["url"] for x in ledger["sources"]}|{row["orderUrl"]}
        baseline=article(source_page)
        assert source_page["topic"]==INTENT
        actual=article(row)
        original_doc=OUT/f'original-{row["number"]}.html'
        candidate_source=ROOT/"dist"/SITE/f'{row["number"]}.html'
        assert candidate_source.is_file()
        original_doc.write_bytes(candidate_source.read_bytes())
        rec={"number":row["number"],"role":role,"intent":row["topic"],
             "region":row["region"],"sku":row["productSkus"][0],
             "orderURL":row["orderUrl"],"originalArticleSHA256":sha(baseline),
             "candidateArticleSHA256":sha(actual),"originalHtmlSHA256":hashlib.sha256(original_doc.read_bytes()).hexdigest(),
             "candidateHtmlSHA256":sha(page_html),"sourceToQuestionIds":row["buyerQuestions"],
             "sourceQuestionsToHtmlSections":[{"questionId":q,"documentPart":part} for q,part in zip(
             row["buyerQuestions"],["intro","section-0","section-1","section-2","section-3"])],
             "originalToCandidateSimilarity":score(grams(baseline),grams(actual))}
        pages.append(row);records.append(rec)
    for a,b in combinations(pages,2):
        pairs.append({"left":a["number"],"right":b["number"],
                      "originalOriginal":score(grams(article(base[a["number"]])),grams(article(base[b["number"]]))),
                      "candidateCandidate":score(grams(article(a)),grams(article(b)))})
    cross=[]
    for x in pages:
        for b in population:
            cross.append({"candidate":x["number"],"original":b["number"],
                          "similarity":score(grams(article(x)),grams(article(b)))})
    assert len(cross)==3*len(population)
    summary={
      "originalIntent":INTENT,"candidateCount":3,"chosenNumbers":[x["number"] for x in pages],
      "selectionPolicy":"4582 plus lowest numbered two same-intent, C SKU pages; no score-based selection",
      "roleAssignment":"explicit buyerSituation input senderType/approvalOwner/eventPurpose, never inferred from region or randomized",
      "buyerSituations":list(BUYER_SITUATIONS),
      "sameIntentOriginalPopulation":len(population),"exactMethod":"scripts.audit_todayflower_semantic_gate.article+score / v5.audit.grams n=5, whitespace removed",
      "threshold":LIMIT,"pairwise":pairs,
      "crossPopulationPairs":len(cross),
      "crossPopulationViolations":sum(x["similarity"]>=LIMIT for x in cross),
      "maxCrossPopulation":max(cross,key=lambda x:x["similarity"]),
      "sourceCount":len(ledger["sources"]),"competitionRankingVerified":False,
      "sourceToQuestionToHTML":records,
      "utilityGates":{"customerSituationDistinct":3,"sectionsPerCandidate":4,
                      "skuLinksExact":3,"unverifiedRibbonLimitsHonest":3,
                      "manualEditorialApproved":0,
                      "regionalSpecificFactsVerified":0,
                      "independentRegionalBuyerPagesApproved":0},
      "noExistingPageOrUrlModified":True,"notNationwideSolution":True,
      "caution":"Below-threshold alone is not editorial approval; pages differentiated by buyer scenario, not verified region-specific service evidence."
    }
    (OUT/"pilot-report.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"pilot-candidate-page-models.json").write_text(json.dumps(pages,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"research-evidence-copy.json").write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TODAYFLOWER_RIBBON_INTENT_PILOT "+json.dumps({
      "numbers":summary["chosenNumbers"],"intent":INTENT,
      "originalPopulation":len(population),"candidatePairs":pairs,
      "crossPopulationPairs":len(cross),"crossViolations":summary["crossPopulationViolations"],
      "qualityApproved":False
    },ensure_ascii=False),flush=True)
    return summary

if __name__=="__main__":audit()
