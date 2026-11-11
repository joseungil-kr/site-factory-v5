"""Isolated role-separated Todayflower editorial candidate.

Never changes dist/, existing URLs, 5,070 source pages, production settings,
or site copy. Buyer advice belongs to 16 canonical intent guides; regions
own only archived location identity, navigation and exact seller evidence.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from html import escape
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

from v5.config import ROOT, read_site
from v5.audit import grams, similarity
from v5.todayflower_copy_pool import SCENARIOS, SCENE_DETAILS
from scripts.extend_todayflower_5070_b205_evidence import extend_rows
from scripts.audit_todayflower_semantic_gate import article

SITE = "todayflower-nalmada"
OUT = ROOT / "reports" / SITE / "candidate-role-separated"
EVENT = "행사장 꽃 반입"
REGRESSIONS = (186, 3012, 2412, 2852)
THRESHOLD = 0.49
STYLES = """*{box-sizing:border-box}body{font:16px/1.75 'Noto Sans CJK KR',system-ui,sans-serif;color:#193c31;background:#f5f8f5;margin:0}main{max-width:1020px;margin:auto;padding:22px}.hero{background:#e2f1e8;border-radius:16px;padding:25px}h1{font-size:clamp(25px,4vw,36px);line-height:1.35}h2{font-size:21px}section,nav.panel{padding:19px;margin:17px 0;background:white;border-radius:13px;border:1px solid #d8e4dc}a{color:#195b43;overflow-wrap:anywhere}li{margin:7px 0}.muted{font-size:14px;color:#506a5c}.tag{font-size:13px;color:#256047;font-weight:800}.nav-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}.nav-grid a{display:block;background:#edf4ef;padding:10px;border-radius:8px}@media(max-width:390px){main{padding:10px}.hero{padding:17px}section,nav.panel{padding:16px}.nav-grid{grid-template-columns:1fr}}"""


def html(text):
    return escape(str(text), quote=True)


def slug_prefix(text):
    # A digest of an existing pinned full administrative name, never a
    # fabricated district code. Display names are kept separately.
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def write_page(path, *, title, role, content):
    assert role in ("evidence_detail", "regional_navigation", "general_buying_guide")
    text=('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
          '<meta name="viewport" content="width=device-width,initial-scale=1">'
          '<meta name="robots" content="noindex,nofollow">'
          '<title>'+html(title)+'</title><style>'+STYLES+'</style></head>'
          '<body data-candidate-role="'+html(role)+'"><main><header class="hero">'
          '<span class="tag">운영 미반영 · 근거 범위별 편집 실험</span><h1>'+html(title)+'</h1>'
          '<p class="muted">해당 자료는 배송 가능한 지역이나 현재 주문 가능 상태를 증명하지 않습니다.</p>'
          '</header>'+content+'</main></body></html>')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text,encoding="utf-8")
    return hashlib.sha256(text.encode()).hexdigest()


def nav_links(items):
    return '<div class="nav-grid">' + ''.join(
        '<a href="'+html(href)+'">'+html(label)+'</a>' for href,label in items
    ) + '</div>'


def candidate_rows():
    rows,evidence=extend_rows()
    by_num={r["number"]:r for r in rows}
    pages=read_site(SITE)["pages"]
    event=[p for p in pages[33:] if p["topic"]==EVENT]
    assert len(event)==333, len(event)
    assert len({p["number"] for p in event})==333
    selected={p["number"] for p in event}|set(REGRESSIONS)
    # Three independently narrow B205 posted-fee examples remain a separate
    # research class, never a claimed independent locality page.
    evidence_sample={r["number"] for r in rows if r["wreathpriceMatchedIds"]}
    assert len(evidence_sample)==3
    selected |= evidence_sample
    assert all(n in by_num for n in selected)
    return rows,pages,event,selected,evidence


def build():
    rows,pages,event,selected,evidence=candidate_rows()
    evidence_sample={r["number"] for r in rows if r["wreathpriceMatchedIds"]}
    by_num={r["number"]:r for r in rows}
    by_page={p["number"]:p for p in pages}
    assert len(rows)==5070
    target=OUT/"candidate"
    target.mkdir(parents=True,exist_ok=True)

    # Every displayed region name and ancestor is taken from a real pinned
    # legal code name. Province/parent group labels are navigation groupings
    # only, not newly asserted municipal administrative identities.
    provinces=defaultdict(list)
    districts=defaultdict(list)
    for n in sorted(selected):
        row=by_num[n]
        parts=row["regionName"].split()
        province=parts[0]
        parent=" ".join(parts[:-1]) if len(parts)>2 else province
        provinces[province].append(n)
        districts[(province,parent)].append(n)

    guide_paths={}
    guide_sha={}
    for intent,focus,product,q1,q2,response in SCENARIOS:
        key=slug_prefix(intent)
        path=target/"guides"/(key+".html")
        guide_paths[intent]=f"../guides/{key}.html"
        detail=SCENE_DETAILS[intent]
        # One editorial owner per intent; no prose copies in locality pages.
        content=('<section><h2>선택 기준</h2><p>'+html(focus)+'</p>'
                 '<p>'+html(product)+'</p><p>'+html(detail["selection"][0])+'</p></section>'
                 '<section><h2>수령·인계</h2><p>'+html(detail["receiver"][0])+'</p></section>'
                 '<section><h2>주문 전 확인</h2><p>'+html(detail["delivery"][0])+'</p>'
                 '<p class="muted">상품번호와 정확한 주소를 판매처에서 확인하세요. '
                 '현재 상품 재고, 배송 마감 및 추가배송비는 이 글로 확정되지 않습니다.</p></section>'
                 '<nav class="panel"><a href="../index.html">지역·목적 탐색으로 이동</a></nav>')
        guide_sha[intent]=write_page(path,title=intent+" | 공통 구매 안내",
                                     role="general_buying_guide",content=content)
    assert len(guide_sha)==len(SCENARIOS)==16

    hub_paths={}
    hub_sha={}
    for (province,parent),nums in sorted(districts.items()):
        key=slug_prefix(parent)
        href=f"hubs/{key}.html"
        hub_paths[(province,parent)]=href
        links=[(f"../regional/{n}.html",by_num[n]["regionName"]) for n in nums]
        content=('<section><h2>해당 지역의 보존된 탐색 항목</h2>'
                 '<p class="muted">아래는 실재하는 행정구역명과 저장된 URL에 '
                 '대한 이동 링크이며, 배송/시설 조건 증거는 아닙니다.</p>'
                 +nav_links(links)+'</section><nav class="panel"><a href="../index.html">'
                 '전체 탐색</a></nav>')
        hub_sha[href]=write_page(target/href,title=parent+" · 지역별 탐색",
                                role="regional_navigation",content=content)
    province_paths={}
    for province in sorted(provinces):
        ref=f"hubs/province-{slug_prefix(province)}.html"
        province_paths[province]=ref
        hubs=[(f"{slug_prefix(parent)}.html",parent)
              for p,parent in sorted(districts) if p==province]
        content='<section><h2>하위 탐색</h2>'+nav_links(hubs)+'</section>'
        content+='<nav class="panel"><a href="../index.html">전체 탐색</a></nav>'
        hub_sha[ref]=write_page(target/ref,title=province+" 탐색",
                               role="regional_navigation",content=content)
    assert len(hub_sha)==len(districts)+len(provinces)

    candidate_files=[]
    original_texts=[]
    candidate_texts=[]
    baseline_visible=[]
    candidate_visible=[]
    original_files=OUT/"original-actual-html"
    original_files.mkdir(parents=True,exist_ok=True)
    class Visible(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts=[];self.skip=0
        def handle_starttag(self,tag,attrs):
            if tag in ("script","style","noscript"):self.skip+=1
        def handle_endtag(self,tag):
            if tag in ("script","style","noscript") and self.skip:self.skip-=1
        def handle_data(self,value):
            if not self.skip and value.strip():self.parts.append(value.strip())
    def visible_text(raw):
        p=Visible();p.feed(raw)
        return " ".join(p.parts)
    for n in sorted(selected):
        row=by_num[n]
        page=by_page[n]
        parts=row["regionName"].split()
        province=parts[0]
        parent=" ".join(parts[:-1]) if len(parts)>2 else province
        intent=page["topic"]
        assert intent in guide_paths or n<=33
        actual_intent= intent if intent in guide_paths else "배송지 상세주소"
        official_region=(row["regionName"]+" (고정 자료의 법정동·상위지역 표기, 코드 "
                         +row["regionCode"]+")")
        nav=[(f"../{hub_paths[(province,parent)]}","상위 지역 탐색"),
             (f"../{province_paths[province]}","광역 탐색"),
             (guide_paths[actual_intent], actual_intent+" 공통 구매 안내")]
        narrative=('<section><h2>확인된 행정구역</h2><p>'+html(official_region)+'</p>'
                   '<p class="muted">고정 지역 코드 자료 기준일: 2026-10-22. '
                   '이 값은 현재 서비스 가능 지역을 증명하지 않습니다.</p></section>'
                   '<nav class="panel" aria-label="지역과 구매의도 탐색">'
                   '<h2>연결된 탐색과 주문 안내</h2>'+nav_links(nav)+'</nav>')
        if row["wreathpriceMatchedIds"]:
            # Exact, previously validated B205-only seller publication.
            assert row["sellerPostedFeeSku"]=="B205"
            assert row["sellerPostedFeeSourceObservedAt"]=="2026-11-11"
            narrative+=('<section data-evidence="B205-only"><h2>판매처 게시 근거 (B205 전용)</h2>'
                        '<p>'+html(row["regionName"])+'의 B205 상품 게시 추가배송비 '
                        +f'{row["sellerPostedFeeKRW"]:,}'+'원</p>'
                        '<p class="muted">2026-11-11 조회 · 판매처 게시일 미상 · '
                        '현재 주문 적용 및 배송 가능 여부 미확인. '
                        'C030·다른 SKU 요율에 대한 주장 아님.</p>'
                        '<p><a href="'+html(row["sellerPostedFeeSourceURL"])+'">'
                        'B205 판매처 원문</a></p></section>')
        else:
            narrative+=('<section><h2>지역별 배송·시설 정보</h2>'
                        '<p>이 페이지에 적용할 수 있는 구체적인 시설 반입 조건이나 '
                        '현재 상품별 배송 조건은 확보되지 않았습니다.</p>'
                        '<p class="muted">이 지역의 배송이 불가능하거나 무료라는 뜻도 아닙니다. '
                        '구매 기준은 위의 공통 목적별 안내에서 확인할 수 있습니다.</p></section>')
        # Differentiate schema role from publication eligibility: even exact
        # seller fee remains a research facet, not an independently useful
        # regional detail article.
        role="regional_navigation"
        p=target/"regional"/f"{n}.html"
        digest=write_page(p,title=row["regionName"]+" · 지역 탐색 및 출처 현황",
                          role=role,content=narrative)
        original=(ROOT/"dist"/SITE/("index.html" if n==1 else f"{n}.html"))
        assert original.is_file(),("original generated HTML missing",n)
        original_html=original.read_text(encoding="utf-8")
        assert 'noindex,nofollow' in original_html
        (original_files/f"{n}.html").write_text(original_html,encoding="utf-8")
        candidate_html=p.read_text(encoding="utf-8")
        candidate_files.append({"baselineSHA256":hashlib.sha256(original_html.encode()).hexdigest(),
            "number":n,"urlPath":row["urlPath"],
            "regionCode":row["regionCode"],"intent":intent,
            "role":role,"htmlPath":str(p.relative_to(OUT)),
            "sha256":digest,"matchedFacts":row["wreathpriceMatchedIds"],
            "missingEvidence":not bool(row["wreathpriceMatchedIds"]),
            "guide":guide_paths[actual_intent],
            "evidenceOnlyNotPageEligibility":True})
        if intent==EVENT:
            original_texts.append((n, grams(article(page))))
            candidate_texts.append((n, grams(official_region+" "+(
                str(row["sellerPostedFeeKRW"]) if row["wreathpriceMatchedIds"] else
                "개별 시설 및 지역 배송 자료 없음"))))
            baseline_visible.append((n,grams(visible_text(original_html))))
            candidate_visible.append((n,grams(visible_text(candidate_html))))
    # The textual Jaccard comparison uses separately recorded content slices;
    # don't call thin navigational pages a quality pass.
    def collisions(items):
        violations=0;maximum=(0,None,None)
        for i,(num,a) in enumerate(items):
            for num2,b in items[i+1:]:
                val=len(a&b)/len(a|b) if a|b else 1
                if val>=THRESHOLD: violations+=1
                if val>maximum[0]:maximum=(val,num,num2)
        return {"pairs":len(items)*(len(items)-1)//2,
                "overStrict49Percent":violations,"max":maximum}
    prev=collisions(original_texts)
    cand=collisions(candidate_texts)
    real_before=collisions(baseline_visible)
    real_after=collisions(candidate_visible)
    assert prev["pairs"]==cand["pairs"]==real_before["pairs"]==real_after["pairs"]==55278
    assert prev["overStrict49Percent"]==4503
    # Write portal AFTER link targets already exist.
    indexlinks=[(f"./{province_paths[p]}",p) for p in sorted(provinces)]
    guidelinks=[("./guides/"+Path(v).name,k) for k,v in sorted(guide_paths.items())]
    write_page(target/"index.html",title="Todayflower · 격리 지역 및 구매 목적 탐색",
               role="regional_navigation",
               content='<section><h2>광역 탐색</h2>'+nav_links(indexlinks)+'</section>'
                       '<section><h2>공통 구매의도 안내</h2>'+nav_links(guidelinks)+'</section>')

    # Structural audit (no external network) of EVERY generated href.
    import re
    all_html=sorted(target.rglob("*.html"))
    link_total=0
    for path in all_html:
        text=path.read_text(encoding="utf-8")
        assert 'noindex,nofollow' in text and 'rel="canonical"' not in text
        for ref in re.findall(r'<a href="([^"]+)"',text):
            if ref.startswith("https://"):
                assert ref.startswith("https://fwith.co.kr/shop/item.php?it_id=B205")
                continue
            assert not ref.startswith(("/", "#", "javascript:", "data:")),ref
            dest=(path.parent/ref).resolve()
            assert dest.is_relative_to(target.resolve()),(path,ref)
            assert dest.is_file(),(path,ref)
            link_total+=1
    expected_count=len(selected)+len(hub_sha)+len(guide_sha)+1
    assert len(all_html)==expected_count
    reg_numbers={r["number"] for r in candidate_files}
    assert len(reg_numbers)==len(selected)==len(candidate_files)
    assert set(REGRESSIONS).issubset(reg_numbers)
    assert all((target/"regional"/f"{n}.html").exists() for n in REGRESSIONS)
    assert not (ROOT/"dist"/SITE/"candidate").exists()

    # Guides own copy; regional pages must not contain any original intent
    # decision sentence. Explicit semantic ownership, not mere char count.
    guidance={line for groups in SCENE_DETAILS.values()
              for lines in groups.values() for line in lines}
    for row in candidate_files:
        page=(OUT/row["htmlPath"]).read_text(encoding="utf-8")
        assert not any(g in page for g in guidance)
    # Explicitly separate mechanical overlap from editorial utility:
    # reducing words/duplicated advice does not establish a useful locality.
    region_lengths=[]
    for item in candidate_files:
        source=(OUT/item["htmlPath"]).read_text(encoding="utf-8")
        region_lengths.append(len(visible_text(source)))
    thin_count=sum(length<350 for length in region_lengths)
    report={
        "candidateThinRegionPagesUnder350VisibleChars":thin_count,
        "candidateRegionVisibleCharsMin":min(region_lengths),
        "candidateRegionVisibleCharsMax":max(region_lengths),
        "candidateOnly": True,"publicReleaseApproved":False,
        "searchIndexable":False,"noExistingUrlChanged":True,
        "originalQualityGateUnchanged":True,
        "candidateEditorialApproved":False,
        "regionalCandidateCount":len(selected),
        "eventSameIntentPageCount":333,"fixedRegressions":list(REGRESSIONS),
        "sellerFeeResearchSampleCount":len(evidence_sample),
        "guidesOwnedByIntent":len(guide_sha),"hubs":len(hub_sha),
        "allHtmlFiles":len(all_html),"linksChecked":link_total,
        "sourceToCandidate":candidate_files,
        "original333ArticleSimilarity":prev,
        "candidate333FactualMetadataSimilarity":cand,
        "original333ActualVisibleHtmlSimilarity":real_before,
        "candidate333ActualVisibleHtmlSimilarity":real_after,
        "comparisonPopulationIdentical": True,
        "candidateBelow49NeverImpliesEditorialApproval": True,
        "unresolvedEditorialIssue":"Navigation-only pages lack independent commercial utility; not publishable solely due to low overlap",
        "noInventedLocalService":True,
        "legacy5070QualityPassed":False,
        "sellerShippingCurrentlyVerified":False
    }
    p=OUT/"candidate-role-qa.json"
    p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TODAYFLOWER_CANDIDATE_333 "+json.dumps(
        {"candidatePages":len(selected),"htmlFiles":len(all_html),
         "hubs":len(hub_sha),"guides":len(guide_sha),"links":link_total,
         "before":prev,"afterFactualMetadataOnly":cand,
         "beforeActualHtml":real_before,"afterActualHtml":real_after,
         "publishable":False},ensure_ascii=False),flush=True)
    return report


if __name__=="__main__":
    build()
