"""Same-buyer-situation counterfactual on originally failing 186/3012 pair.

Do not infer a wedding happened in either area. Use identical wedding input
for both archived region identities; preserve SKU constraints and actual HTML.
Never modifies original generator, 5070 URLs, production or index status.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from v5.config import ROOT,read_site
from v5.audit import grams
from scripts.audit_todayflower_semantic_gate import article,score,LIMIT
from scripts.build_todayflower_event_49pilot import CASES,make,html,OUT as EVENT_OUT

OUT=ROOT/"reports/todayflower-nalmada/event-intent-same-wedding-control"
NUMBERS=(186,3012)
def sha(raw):return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def build():
    data=read_site("todayflower-nalmada")
    assert len(data["pages"])==5070
    assert data["site"]["publishEnabled"] is False
    assert data["site"]["indexNow"]["enabled"] is False
    pages={p["number"]:p for p in data["pages"]}
    assert all(pages[n]["topic"]=="행사장 꽃 반입" for n in NUMBERS)
    catalog={p["sku"]:p for p in data["products"]}
    original=score(grams(article(pages[186])),grams(article(pages[3012])))
    assert original>0.93
    same=[]
    for n in NUMBERS:
        p=make(pages[n],CASES[186],catalog)
        assert p["topic"]=="행사장 꽃 반입"
        assert p["scenario"]=="wedding"
        assert p["scenarioExplicitInput"] is True
        assert p["productSkus"][0] in pages[n]["productSkus"]
        assert p["orderUrl"]==catalog[p["productSkus"][0]]["orderUrl"]
        same.append(p)
    both_wedding=score(grams(article(same[0])),grams(article(same[1])))
    # The previously published experiment compared different BUYER inputs,
    # not a genuine regional difference. Preserve its original measurement.
    oldw=make(pages[186],CASES[186],catalog)
    oldp=make(pages[3012],CASES[3012],catalog)
    different=score(grams(article(oldw)),grams(article(oldp)))
    assert abs(different-0.08100558659217877)<1e-12
    assert both_wedding>different+0.30, (both_wedding,different)
    OUT.mkdir(parents=True,exist_ok=True)
    files=[]
    for p in same:
        raw=html(p)
        f=OUT/f"same-wedding-candidate-{p['number']}.html"
        f.write_text(raw,encoding="utf-8")
        assert 'noindex,nofollow' in raw
        assert raw.count('data-cta-sku=')==1
        assert f'data-cta-sku="{p["productSkus"][0]}"' in raw
        assert p["orderUrl"] in raw
        files.append({"number":p["number"],"sha256":sha(raw),"html":f.name,
                      "sku":p["productSkus"][0],"orderUrl":p["orderUrl"],
                      "scenario":"wedding","sourceRegion":p["region"],
                      "regionEventVerified":False})
    report={"sourceExistingCaseScript":"scripts/build_todayflower_event_49pilot.py",
            "originalIntent":"행사장 꽃 반입","sameBuyerContext":"wedding",
            "originalViolationPair":[186,3012],"originalSameIntentScore":original,
            "differentSituationCandidateScore":different,
            "sameSituationCandidateScore":both_wedding,
            "relativeEffect":{"buyerSituationDifference":both_wedding-different,
                              "verifiedRegionalSpecificityEffect":None,
                              "interpretation":"The low 8.10% cross-candidate score largely comes from different hypothetical buyer situations; identical wedding input yields high repetition despite different region names."},
            "sameArticleScoreAndGating":"scripts.audit_todayflower_semantic_gate.article/score; v5.audit.grams n=5",
            "threshold":LIMIT,"sameSituationViolates49Percent":both_wedding>=LIMIT,
            "sameSituationArticleIdenticalBeyondRegion":False,
            "verifiedLocalEventFacts":0,
            "editorialApproved":False,"publishApproved":False,"urlsChanged":0,
            "files":files}
    (OUT/"same-wedding-control.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TODAYFLOWER_SAME_WEDDING_CONTROL "+json.dumps({
       "original":original,"differentBuyer":different,
       "sameBuyer":both_wedding,"fails49":both_wedding>=LIMIT,
       "files":[x["html"] for x in files]},ensure_ascii=False))
    return report
if __name__=="__main__":build()
