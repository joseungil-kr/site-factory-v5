"""Build 1,080 noindex funeral-hall pages ONLY after content-first similarity QA.

V4: curated 600 units + original 1,080 facility assignments, supplemented by
48 vetted-context draft statements. The V4 facility registry is NOT independently
verified and its publicationAllowed=false flag remains binding. No public release.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from html import escape
import json
from math import ceil
from pathlib import Path
from random import Random
import re
import shutil
from flower_design import head, header, photo, price_cards, reference_note, footer, contact_band, prepare_assets

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FACILITIES = DATA / "flower" / "v4_facilities_1080.snapshot.json"
ASSIGNMENTS = DATA / "flower" / "v4_facility_assignments_1080.snapshot.json"
POLICY = DATA / "flower" / "v4_assignment_policy.snapshot.json"
CURATED = DATA / "pools" / "flower_funeral_professional_600.v4.json"
SUPPLEMENT = DATA / "pools" / "flower_funeral_sample_pool.json"
OUT = ROOT / "dist" / "flower-funeral-national-preview"
REPORT = ROOT / "reports" / "flower-funeral" / "pool-1080-1pct-audit.json"

SEEDS = (20261027, 20261028, 20261029)
THRESHOLD = 0.49
CORE_FIELDS = ("opening", "body", "orderGuide", "faq", "closing")
SUPPORT_FIELDS = ("intro", "facility", "product", "ribbon", "delivery", "etiquette", "order")
HALL_TITLE = "{hall} 근조화환 주문 가격안내"
PHONE = "1844-0644"


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def _sha(path: Path):
    return sha256(path.read_bytes()).hexdigest()

def source_digests():
    return {p.name: _sha(p) for p in (FACILITIES, ASSIGNMENTS, POLICY, CURATED, SUPPLEMENT)}

def load_sources():
    source = _read(FACILITIES)
    mapping = _read(ASSIGNMENTS)
    policy = _read(POLICY)
    professional = _read(CURATED)
    supplement = _read(SUPPLEMENT)
    if source.get("publicationAllowed") is not False:
        raise ValueError("V4 publication gate changed; review required")
    facilities = source.get("facilities")
    assignments = mapping.get("assignments")
    if not isinstance(facilities,list) or not isinstance(assignments,list) or len(facilities)!=1080 or len(assignments)!=1080:
        raise ValueError("Must have original 1,080 V4 records and assignments")
    if len({f["id"] for f in facilities}) != 1080 or len({a["facilityId"] for a in assignments}) != 1080:
        raise ValueError("Duplicate facility or assignment ID")
    if any(f["id"]!=a["facilityId"] for f,a in zip(facilities,assignments)):
        raise ValueError("Facility and assignment order/id mismatch")
    if mapping.get("sourcePoolBlob")!="221fa69b9f41601bd66ec07d33b99d36632fa5b9":
        raise ValueError("V4 assignments reference an unexpected pool revision")
    if professional.get("totalUnits")!=600 or professional.get("readyForPublication") is not False:
        raise ValueError("Expected 600 editorial draft units, not approved for release")
    for key in CORE_FIELDS:
        if len(professional.get(key,[]))!=120:
            raise ValueError("Incomplete V4 professional category "+key)
    groups = supplement.get("groups")
    if not isinstance(groups,dict) or any(len(groups.get(k,[])) < 6 for k in SUPPORT_FIELDS):
        raise ValueError("Supplement pool must have all 7 content contexts")
    topic_groups = policy["groups"]
    excluded = {item["index"] for item in policy["excludedTopics"]}
    eligible = sorted(set(range(120))-excluded)
    if len(eligible)!=112:
        raise ValueError("Unexpected eligible V4 topic count")
    for a in assignments:
        permitted = topic_groups.get(a["group"])
        if not permitted:
            raise ValueError("Missing group: "+a["group"])
        for field in CORE_FIELDS:
            if a[field] not in permitted or a[field] in excluded:
                raise ValueError("Wrong-group or excluded topic in V4 assignment")
    return facilities,assignments,professional,groups,eligible

def _stable_options(options, key, count):
    if len(options) < count:
        raise ValueError("Not enough pool options")
    ranked = sorted(options,key=lambda x: sha256((key+"|"+str(x)).encode("utf-8")).digest())
    return ranked[:count]

def _fill(text, facility):
    result=text.replace("{facilityName}",facility["facilityName"]).replace("{regionName}",facility["regionName"])
    if re.search(r"\{[A-Za-z][A-Za-z0-9]*\}",result):
        raise ValueError("Unresolved source placeholder")
    return result

def create_content(facility, assignment, curated, supplement, eligible):
    facility_id=facility["id"]
    fields={}
    for field in CORE_FIELDS:
        assigned=assignment[field]
        extras=_stable_options([x for x in eligible if x!=assigned],facility_id+"|professional|"+field,3)
        indices=[assigned]+extras
        field_values=[]
        for i in indices:
            entry=curated[field][i]
            if field=="faq":
                field_values.append((_fill(entry["question"],facility),_fill(entry["answer"],facility)))
            else:
                field_values.append(_fill(entry,facility))
        fields[field]=field_values
    supplemental={}
    for field in SUPPORT_FIELDS:
        selected=_stable_options(list(range(len(supplement[field]))),facility_id+"|support|"+field,2 if field=="order" else 1)
        supplemental[field]=[supplement[field][x] for x in selected]
    title=HALL_TITLE.format(hall=facility["facilityName"])
    # The first five items preserve the V4 editorial assignment. Extra scenario
    # paragraphs are explicitly optional/general guidance, not venue-specific facts.
    lead=(f'{facility["regionName"]} 원장에 기록된 {facility["facilityName"]}으로 근조화환을 '
          '준비하신다면 빈소와 상주명, 장례 일정부터 확인해 주세요. '
          '아래 안내는 주문 시 참고할 일반적인 상황을 조합한 문서입니다.')
    sections=[
        ("부고를 받고 근조화환을 준비할 때",fields["opening"]+supplemental["intro"]),
        ("장례식장 위치와 빈소를 확인하는 순서",fields["body"]+supplemental["facility"]),
        ("근조화환 종류와 제작 품질을 비교할 때",supplemental["product"]),
        ("리본 문구와 조문 예절",supplemental["ribbon"]+supplemental["etiquette"]),
        ("주문 전 제작·배송 조건 확인",fields["orderGuide"]+supplemental["delivery"]),
        ("전화 주문과 추가 확인 사항",fields["closing"]+supplemental["order"])
    ]
    faq=fields["faq"]
    price_text=("근조화환 기본형 고급형 특대형 종류별 가격은 실제 상품과 배송지 조건에 "
                "따라 달라질 수 있습니다. 현재 확정된 가격표가 없으므로 각 유형의 금액은 상담 확인으로 표시합니다.")
    content_text=" ".join([title,facility["regionName"],lead,price_text]+
                          [heading+" "+" ".join(parts) for heading,parts in sections]+
                          [q+" "+a for q,a in faq])
    return {"title":title,"lead":lead,"sections":sections,"faq":faq,
            "priceText":price_text,"text":content_text}

def _fingerprint(text):
    t=re.sub(r"\s+","",text).lower()
    return {t[i:i+5] for i in range(max(0,len(t)-4))}

def _similarity(a,b):
    intersection=len(a & b)
    return intersection/(len(a)+len(b)-intersection) if (a or b) else 1.0

def _normalize(text,facility):
    text=text.replace(facility["sourceAddress"],"{ADDRESS}")
    return text.replace(facility["facilityName"],"{HALL}").replace(facility["regionName"],"{REGION}")


def _full_pairwise(gramsets,facilities,view):
    """Exact all-pairs Jaccard using integer bitsets; no MinHash approximation."""
    vocabulary={}
    masks=[]
    counts=[]
    for grams in gramsets:
        mask=0
        for gram in grams:
            if gram not in vocabulary:
                vocabulary[gram]=len(vocabulary)
            mask |= (1 << vocabulary[gram])
        masks.append(mask)
        counts.append(len(grams))
    maximum=0.0
    worst=None
    failing=0
    first_failures=[]
    compared=0
    for i in range(len(masks)-1):
        left=masks[i]
        left_count=counts[i]
        for j in range(i+1,len(masks)):
            overlap=(left & masks[j]).bit_count()
            denom=left_count+counts[j]-overlap
            score=overlap/denom if denom else 1.0
            compared+=1
            if score>maximum:
                maximum=score
                worst={"firstId":facilities[i]["id"],
                       "secondId":facilities[j]["id"],
                       "view":view,"jaccard":round(score,6)}
            if score>=THRESHOLD:
                failing+=1
                if len(first_failures)<10:
                    first_failures.append({"firstId":facilities[i]["id"],
                                           "secondId":facilities[j]["id"],
                                           "view":view,"jaccard":round(score,6)})
    return {"view":view,"comparisons":compared,
            "maximumJaccard":round(maximum,6),
            "worstPair":worst,
            "pairsAtOrAboveThreshold":failing,
            "failureExamples":first_failures,
            "vocabularySize":len(vocabulary)}

def create_population(facilities,assignments,curated,groups,eligible):
    return [create_content(f,a,curated,groups,eligible) for f,a in zip(facilities,assignments)]

def audit(facilities,contents):
    if len(contents)!=1080:
        raise ValueError("Incomplete corpus: stop before creating HTML")
    lengths=[len(x["text"]) for x in contents]
    min_len=min(lengths);max_len=max(lengths)
    raw_hashes=[sha256(c["text"].encode("utf-8")).hexdigest() for c in contents]
    duplicate_bodies=sum(n-1 for n in Counter(raw_hashes).values() if n>1)
    original=[_fingerprint(c["text"]) for c in contents]
    normalized=[_fingerprint(_normalize(c["text"],f)) for c,f in zip(contents,facilities)]
    samples=[]
    failures=[]
    overall=0.0
    for seed in SEEDS:
        rng=Random(seed)
        selected=rng.sample(range(1080),ceil(1080*.01))
        per_seed=[]
        for idx in selected:
            best_score=0.0;partner=None;mode=None
            for j in range(1080):
                if idx==j:continue
                for view,fp in (("actual",original),("normalized",normalized)):
                    score=_similarity(fp[idx],fp[j])
                    if score>best_score:best_score=score;partner=j;mode=view
            row={"seed":seed,"facilityId":facilities[idx]["id"],
                 "facility":facilities[idx]["facilityName"],
                 "bestMatchId":facilities[partner]["id"] if partner is not None else None,
                 "view":mode,"maximumJaccard":round(best_score,6)}
            per_seed.append(row)
            overall=max(overall,best_score)
            if best_score>=THRESHOLD:failures.append(row)
        samples.append({"seed":seed,"sampleSize":len(selected),
                        "pairsCompared":len(selected)*1079*2,
                        "maxScore":round(max(x["maximumJaccard"] for x in per_seed),6),
                        "results":per_seed})
    full_actual=_full_pairwise(original,facilities,"actual")
    full_normalized=_full_pairwise(normalized,facilities,"normalized")
    full_pairwise=[full_actual,full_normalized]
    full_maximum=max(x["maximumJaccard"] for x in full_pairwise)
    full_failed=sum(x["pairsAtOrAboveThreshold"] for x in full_pairwise)
    overall=max(overall,full_maximum)
    hall_titles=[(f["facilityName"],f["regionName"]) for f in facilities]
    duplicate_title_region=sum(v-1 for v in Counter(hall_titles).values() if v>1)
    passes=(not failures and not full_failed and not duplicate_bodies and not duplicate_title_region
            and min_len>=2500 and max_len<=3200)
    return {
        "mode":"POOL_FIRST_PRE_PUBLICATION_QA",
        "source":"V4 professional 600 curated copy units + 48 supplementary draft units",
        "facilityCount":1080,
        "sourcePublicationAllowed":False,
        "uniqueFacilityIds":len({f["id"] for f in facilities}),
        "sourceDigests":source_digests(),
        "metric":"whitespace-free lowercase character 5-gram Jaccard of rendered content text",
        "comparedViews":["actual rendered data","normalized hall/region/address"],
        "thresholdExclusive":THRESHOLD,
        "seedCount":len(SEEDS),
        "sampleCountPerSeed":ceil(1080*.01),
        "comparisons":sum(s["pairsCompared"] for s in samples),
        "maximumSimilarity":round(overall,6),
        "fullPairwise":full_pairwise,
        "fullPairComparisons":sum(x["comparisons"] for x in full_pairwise),
        "fullPairFailures":full_failed,
        "failures":failures,
        "exactDuplicateBodies":duplicate_bodies,
        "duplicateFacilityRegionTitles":duplicate_title_region,
        "characterLength":{"minimum":min_len,"maximum":max_len,
                           "median":sorted(lengths)[len(lengths)//2]},
        "samples":samples,
        "passes":passes,
        "limits":["Random 1% samples and exact full 1080-by-1080 pairwise audit both run; all comparisons exclude self.",
                  "Original V4 source facilities have unverified current address/operation status.",
                  "Similarity measures surface overlap only, not semantic originality, helpfulness or SEO quality.",
                  "The content pool is a draft. Final human design review and commercial verification are not complete.",
                  "Public deployment and IndexNow are forbidden."]
    }

def _paragraphs(items):
    return "".join("<p>"+escape(item)+"</p>" for item in items)

def render(facility,c):
    """B green-premium hero + D long-form document for all 1080 halls.

    No invented facility photos, maps, stock or guaranteed delivery claims.
    Only shared, owner-sourced product photos are repeated across hall pages.
    """
    name=escape(facility["facilityName"])
    region=escape(facility["regionName"])
    address=escape(facility["sourceAddress"])
    title=escape(c["title"])
    paragraphs=[]
    for heading, parts in c["sections"]:
        paragraphs.append('<section class="text-section"><h2>'+escape(heading)+'</h2>'+
                          _paragraphs(parts)+'</section>')
    # Real catalogue reference price cards, but no unverified current price.
    price_section=('<section id="prices" class="price-box">'
                   '<div class="eyebrow">CONDOLENCE WREATHS · PRODUCT GUIDE</div>'
                   '<h2>근조화환 종류별 가격 안내</h2>'
                   '<p>기본형·고급형·특대형 상품 구성과 참고 가격을 비교해 보세요.</p>'
                   +price_cards()+reference_note()+'</section>')
    paragraphs.insert(2,price_section)
    faq=('<section class="faq" id="faq"><h2>자주 묻는 질문</h2>'+
         "".join('<details><summary>'+escape(q)+'</summary><p>'+escape(a)+'</p></details>'
                 for q,a in c["faq"])+'</section>')
    hero=('<div class="wrap breadcrumb"><a href="/">홈</a><span>›</span>장례식장별 근조화환'
          '<span>›</span>'+region+'</div>'
          '<section class="hero detail-hero"><div class="wrap hero-inner"><div>'
          '<span class="eyebrow">FUNERAL FLOWER DELIVERY · '+region+'</span>'
          '<h1>'+title+'</h1><p class="lead">'+escape(c["lead"])+'</p>'
          '<div class="fact-row"><span>📍 '+region+'</span>'
          '<span>☎ 전화 주문 상담</span><span>🌿 근조화환 종류별 비교</span></div>'
          '<div class="hero-actions"><a class="btn" href="#prices">화환 종류·가격 보기</a>'
          '<a class="btn btn-outline" href="tel:18440644">☎ 1844-0644</a></div>'
          '<p class="reference">원장 기재 주소(현행 정보 미검증): '+address+'</p>'
          '</div><div class="hero-visual">'+photo("B203.jpg","근조 고급 3단 화환 공통 상품 사진","eager")+
          '<span class="photo-label">장례식장 건물 사진이 아닌 공통 근조화환 상품 사진</span>'
          '</div></div></section>')
    sidebar=('<aside class="aside"><div class="side-card tint"><h3>근조화환 전화 상담</h3>'
             '<p>장례식장명·빈소·상주명·희망일·리본 문구를 준비해 주세요.</p>'
             '<a class="btn" href="tel:18440644">☎ 1844-0644 전화하기</a></div>'
             '<div class="side-card"><h3>페이지 바로가기</h3>'
             '<p><a href="#prices">근조화환 종류와 참고 가격</a></p>'
             '<p><a href="#faq">자주 묻는 질문</a></p>'
             '<p><a href="/">전국 장례식장 찾기</a></p></div>'
             '<div class="notice">주소와 장례식장 운영 여부는 외부 검증 전입니다. '
             '원장 기재 정보가 실제와 다를 수 있으므로 주문 전 확인해 주세요.</div></aside>')
    return (head(c["title"]+" | "+facility["regionName"]+" | 날마다꽃",c["lead"])+
            header()+'<main id="main">'+hero+
            '<div class="wrap layout"><article class="article-card">'+
            "".join(paragraphs)+faq+'</article>'+sidebar+'</div>'+
            contact_band()+'</main>'+footer())

def build(facilities,contents,qa):
    if not qa["passes"]:
        raise ValueError("Refuse HTML generation until similarity quality gate passes")
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True,exist_ok=True)
    prepare_assets(OUT)
    files=[]
    for f,c in zip(facilities,contents):
        filename=f["id"]+".html"
        (OUT/filename).write_text(render(f,c),encoding="utf-8")
        files.append({"id":f["id"],"filename":filename,
                      "facility":f["facilityName"],"region":f["regionName"],
                      "locationVerification":f.get("locationVerification","not_verified")})
    (OUT/"manifest.json").write_text(json.dumps({
        "mode":"noindex-preview","pageCount":len(files),
        "sourceDigests":source_digests(),"qaPasses":qa["passes"],
        "qaReport":"reports/flower-funeral/pool-1080-1pct-audit.json",
        "pages":files},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"robots.txt").write_text("User-agent: *\nDisallow: /\n",encoding="utf-8")
    if len(list(OUT.glob("fh-*.html")))!=1080:
        raise ValueError("Generated HTML count != 1080")

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--audit-only",action="store_true",help="Audit all source texts before writing any HTML")
    args=arg.parse_args()
    facilities,assignments,curated,support,eligible=load_sources()
    contents=create_population(facilities,assignments,curated,support,eligible)
    qa=audit(facilities,contents)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary={k:v for k,v in qa.items() if k not in ("samples","limits")}
    print("FLOWER_FUNERAL_1080_POOL_QA="+json.dumps(summary,ensure_ascii=False))
    if not qa["passes"]:
        raise SystemExit(2)
    if not args.audit_only:
        build(facilities,contents,qa)
        print("FLOWER_FUNERAL_1080_GENERATED="+json.dumps({
            "pages":len(facilities),"location":"dist/flower-funeral-national-preview",
            "mode":"noindex-preview","similarityMax":qa["maximumSimilarity"]},
            ensure_ascii=False))

if __name__=="__main__":
    main()
