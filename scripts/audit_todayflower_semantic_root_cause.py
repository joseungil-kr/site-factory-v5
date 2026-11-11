"""Attribution audit for Todayflower's original 4,503 violations, not a new SEO score.

Uses exactly scripts.audit_todayflower_semantic_gate.article(), .score(),
v5.audit.grams() with unchanged 333-page population and 0.49 threshold.
Counterfactuals are explanatory only: never called quality PASS or published.
"""
from __future__ import annotations
from collections import Counter
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re

from v5.config import ROOT, read_site
from v5.audit import grams
from v5.todayflower_copy_pool import SCENE_DETAILS
from scripts.audit_todayflower_semantic_gate import article, score, LIMIT
from scripts.build_todayflower_three_region_research import BASE as THREE_BASE
from scripts.extend_todayflower_5070_b205_evidence import extend_rows

SITE = "todayflower-nalmada"
OUT = ROOT/"reports"/SITE/"semantic-cause-v1"
SAMPLE_PAIRS = ((186,3012),(2412,2852))
REGRESSIONS=(186,3012,2412,2852,4582)
EXPECTED_POPULATION=333
EXPECTED_VIOLATIONS=4503
EXPECTED_PAIRS=55278

class CandidateText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth=0;self.active=False;self.skip=0;self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in ("style","script","noscript"):self.skip+=1
        if tag=="section" and not self.skip:
            self.depth+=1;self.active=True
    def handle_endtag(self,tag):
        if tag=="section" and not self.skip:
            self.depth=max(0,self.depth-1);self.active=self.depth>0
        if tag in ("style","script","noscript") and self.skip:self.skip-=1
    def handle_data(self,value):
        if self.active and not self.skip and value.strip():self.parts.append(value.strip())

def buyer_sections(html):
    parser=CandidateText();parser.feed(html)
    return " ".join(parser.parts)

def matched_pool_sentences(text, intent="행사장 꽃 반입"):
    vals=[s for group in SCENE_DETAILS[intent].values() for s in group]
    return [s for s in vals if s in text]

def intersect_stats(a,b):
    ag,bg=grams(a),grams(b)
    common=ag & bg
    return {"score":score(ag,bg),"gramsA":len(ag),"gramsB":len(bg),
            "sharedGrams":len(common),"unionGrams":len(ag|bg)}

def attribution(left,right,*,first=None,second=None):
    aa=article(left);bb=article(right)
    x=intersect_stats(aa,bb)
    poolsA=matched_pool_sentences(aa);poolsB=matched_pool_sentences(bb)
    shared=set(poolsA)&set(poolsB)
    # This is only a diagnostic counterfactual, not edited documents or a pass.
    aa_cut=aa;bb_cut=bb
    for sentence in poolsA: aa_cut=aa_cut.replace(sentence,"")
    for sentence in poolsB: bb_cut=bb_cut.replace(sentence,"")
    residual=intersect_stats(aa_cut,bb_cut)
    sections=[]
    for i in range(min(len(left["sections"]),len(right["sections"]))):
        a=left["sections"][i]["paragraph"];b=right["sections"][i]["paragraph"]
        sections.append({"slot":i,"leftHeading":left["sections"][i]["heading"],
                         "rightHeading":right["sections"][i]["heading"],
                         **intersect_stats(a,b)})
    return {"left":left["number"],"right":right["number"],
            "original":x,"sameIntent":left["topic"]==right["topic"],
            "sameRegion":left["region"]==right["region"],
            "sharedExactPoolSentences":len(shared),
            "leftPoolSentencesFound":len(poolsA),"rightPoolSentencesFound":len(poolsB),
            "removedPoolSentencesForAnalysisOnly":True,
            "counterfactualAfterRemovingKnownPoolSentences":residual,
            "sectionSlotMetrics":sections,
            "interpretation":"Counterfactual is NOT quality-tested HTML and cannot pass the original 49% gate."}

def main():
    info=read_site(SITE)
    assert len(info["pages"])==5070
    assert not info["site"]["publishEnabled"] and not info["site"]["indexNow"]["enabled"]
    all_pages={p["number"]:p for p in info["pages"]}
    corpus=[p for p in info["pages"][33:] if p["topic"]=="행사장 꽃 반입"]
    assert len(corpus)==EXPECTED_POPULATION
    assert all(n in all_pages for n in REGRESSIONS)
    # Do NOT remove borderline or missing-evidence pages from the denominator.
    failures=[];maxi=(0.0,None,None)
    for i,a in enumerate(corpus):
        ga=grams(article(a))
        for b in corpus[i+1:]:
            v=score(ga,grams(article(b)))
            if v>maxi[0]:maxi=(v,a["number"],b["number"])
            if v>=LIMIT:
                failures.append((a["number"],b["number"],round(v,7)))
    assert EXPECTED_VIOLATIONS==len(failures)
    assert EXPECTED_PAIRS==len(corpus)*(len(corpus)-1)//2
    assert maxi[1:]==(186,3012)
    representative=[attribution(all_pages[a],all_pages[b]) for a,b in SAMPLE_PAIRS]
    worst=representative[0]
    assert worst["original"]["score"]>=LIMIT
    assert representative[1]["original"]["score"]<LIMIT

    ledger=json.loads((ROOT/"sites"/SITE/"isolated-three-region-evidence-20261111.json").read_text(encoding="utf-8"))
    rows,_=extend_rows()
    mapped={r["number"]:r for r in rows}
    assert mapped[4582]["sellerPostedFeeSku"]=="B205"
    assert mapped[4582]["sellerPostedFeeCurrentEffective"] is False
    assert mapped[1039]["wreathpriceMatchedIds"] and mapped[4360]["wreathpriceMatchedIds"]
    # Source article is unchanged generated content; candidate is the
    # historical source-specific, noindex HTML from the existing generator.
    original=article(all_pages[4582])
    candidate_file=THREE_BASE/"seoseok-4582.html"
    assert candidate_file.is_file(), "Generate existing three-region QA output first"
    candidate_raw=candidate_file.read_text(encoding="utf-8")
    assert 'noindex,nofollow' in candidate_raw
    candidate=buyer_sections(candidate_raw)
    candidate_compare=intersect_stats(original,candidate)
    buyer_claims=ledger["claimMap"]
    assert len(buyer_claims)==4 and {f["id"] for f in buyer_claims}=={"S1","S2","S3","S4"}
    known={"S1","S2","S3","S4"}
    assert set(re.findall(r'data-evidence-ids="(S[0-9]+)"',candidate_raw))==known
    sources={s["id"]:s for s in ledger["sources"]}
    for f in buyer_claims:
        assert all(x in sources for x in f["sources"])
        assert f["claim"] in candidate_raw
    full_scope=["시설명·공식 주소","본관·별관 구분","시설 접수처",
                "판매처 B205 지역 한정 과거 요율"]
    missing=["현행 시설 외부 근조화환 반입 허용 여부","현행 시설 인수 위치·수령 담당자",
             "B205 해당 주소 배송 가능 여부","현재 B205 주문 시 추가배송비·최종 결제금액",
             "상품 재고와 주문 마감"]
    summary={
        "method":{"source":"scripts.audit_todayflower_semantic_gate.article and score; v5.audit.grams",
                  "nGram":5,"stripWhitespace":True,"casefold":True,"threshold":LIMIT,
                  "populationName":"행사장 꽃 반입","populationPages":len(corpus),
                  "pairs":EXPECTED_PAIRS,"unmodifiedOriginalViolations":len(failures),
                  "maximum":list(maxi),"retainedFailures":True},
        "representative":representative,
        "seoSeok":{"number":4582,"regionalCode":mapped[4582]["regionCode"],
            "actualCandidateFile":str(candidate_file.relative_to(ROOT)),
            "originalArticle":original,"candidateBuyerSections":candidate,
            "candidateSourceIds":[x["id"] for x in buyer_claims],
            "candidateClaimCount":len(buyer_claims),
            "originalToCandidateSameMethod":candidate_compare,
            "originalCharCount":len(original),"candidateBuyerCharCount":len(candidate),
            "confirmedBuyerContext":full_scope,"missingToCompleteBuyerDecision":missing,
            "sourceStatus":"2026-11-11 collected/historical; seller current checkout and venue inbound unknown",
            "editorialApproved":False,"publishApproved":False},
        "candidateRule":{"name":"evidence-gated editorial selection only",
            "description":"Never emit an independent locality buyer article solely due to archived region identity, seller posting or random template variations.",
            "evaluated":[
                {"number":4582,"role":"source_bounded_draft_hold","reason":"four mapped facility/SKU claims but live inbound/checkout missing"},
                {"number":1039,"role":"location_evidence_only_hold","reason":"official funeral home listing but no current inbound/checkout"},
                {"number":4360,"role":"no_exact_facility_hold","reason":"no independently verified in-region facility listing"}],
            "independentBuyerPagePublishable":0,
            "noNationwideGeneratorModification":True},
        "conclusion":"Text-level Jaccard reduction does not prove buyer utility. Source-specific details improve relevance but current receipt/fee/stock facts are absent; stop geographic expansion."
    }
    # Candidate-only minimum generation rule: preserve the 333 historic
    # region identities as DATA but emit NO standalone buyer HTML when this
    # pinned source snapshot has no applicable facility/merchant evidence.
    # This is not an alteration of the deployed 5070-page generator.
    mapped_event=[]
    for page in corpus:
        evidence_row=mapped[page["number"]]
        matched=evidence_row["matchedFactIds"]
        assert not matched, ("unexpected regional fact requires re-review",page["number"])
        mapped_event.append({
            "number":page["number"],"urlPath":evidence_row["urlPath"],
            "regionCode":evidence_row["regionCode"],"intent":page["topic"],
            "mappedFactIds":matched,"candidateRole":"shared_intent_reference",
            "allowIndependentBuyerHtml":False,
            "reason":"no_exclusive_local_purchase_evidence_in_pinned_snapshot",
        })
    assert len(mapped_event)==333
    summary["candidateRule"]["sameIntentRowsDataOnly"]=333
    summary["candidateRule"]["sameIntentStandaloneHtmlApproved"]=0
    summary["candidateRule"]["sharedIntentCopyOwner"]="intent guide, not 333 locality bodies"
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"candidate-333-eligibility.json").write_text(
        json.dumps({"recordCount":333,"records":mapped_event,
                    "qualityGatePassed":False,
                    "scope":"isolated editorial candidate rule, not existing URL changes"},
                   ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"analysis.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # Only a small number of real original HTML samples, no new bulk pages.
    dist=ROOT/"dist"/SITE
    for n in REGRESSIONS:
        path=dist/f"{n}.html"
        assert path.is_file()
        (OUT/f"original-{n}.html").write_bytes(path.read_bytes())
    (OUT/"candidate-seoseok-4582.html").write_bytes(candidate_file.read_bytes())
    (OUT/"failure-4503-sample.json").write_text(json.dumps({
        "total":len(failures),"sampleSize":min(30,len(failures)),
        "first30":failures[:30],"maximum":list(maxi),
        "note":"The original same-intent set and 49% threshold are unchanged."
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TODAYFLOWER_ROOT_CAUSE "+json.dumps({
        "violations":len(failures),"pairs":EXPECTED_PAIRS,
        "worst":maxi,"samples":len(representative),
        "candidateOriginalToEditedScore":candidate_compare["score"],
        "evidenceClaims":len(buyer_claims),"independentBuyerPublishable":0,
        "candidateChange":"analysis-and-eligibility-rules-only"
    },ensure_ascii=False),flush=True)
    return summary

if __name__=="__main__":main()
