"""Onehour Sky: seeded 1% source-body comparison against the WHOLE V5 population.

Char-5-gram Jaccard. No random API or search-ranking claim.
Memory bounded: only sample grams indexed, full pages streamed.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from hashlib import sha256
from math import ceil
from random import Random
from pathlib import Path
import json
import re
from .config import ROOT, read_site

TARGET=0.49
SEED=20261027


def grams(text):
    normalized=re.sub(r"\s+","",text).lower()
    return {normalized[i:i+5] for i in range(max(0,len(normalized)-4))}


def body(page):
    return " ".join([page["intro"]]+[section["paragraph"] for section in page["sections"]])


def inspect(pages, *, seed=SEED, threshold=TARGET):
    if len(pages)!=5436:
        raise ValueError("National Onehour scope changed without a new review")
    # Fixed 1% of ALL docs, with one forced representative per distinct geography level.
    n=ceil(len(pages)*.01)
    levels=("national","province","municipality","ward","dong")
    selected=set()
    for role in levels:
        candidates=[i for i,p in enumerate(pages) if p.get("regionLevel","national")==role]
        if candidates:
            best=min(candidates,key=lambda i:sha256((str(seed)+"|"+pages[i]["id"]).encode()).digest())
            selected.add(best)
    rng=Random(seed)
    rest=[i for i in range(len(pages)) if i not in selected]
    selected.update(rng.sample(rest,n-len(selected)))
    sample=sorted(selected)
    sample_gr=[grams(body(pages[i])) for i in sample]
    inverted=defaultdict(list)
    for index, tokens in enumerate(sample_gr):
        for token in tokens:
            inverted[token].append(index)
    sample_lens=[len(v) for v in sample_gr]
    best=[{"score":0.0,"other":None} for _ in sample]
    hashes=Counter()
    for j,p in enumerate(pages):
        article=body(p)
        hashes[sha256(article.encode()).hexdigest()]+=1
        tokens=grams(article)
        intersections=Counter()
        for token in tokens:
            for k in inverted.get(token,()):
                intersections[k]+=1
        for k,sample_id in enumerate(sample):
            if sample_id==j:
                continue
            overlap=intersections[k]
            divisor=len(tokens)+sample_lens[k]-overlap
            score=overlap/divisor if divisor else 1.0
            if score>best[k]["score"]:
                best[k]={"score":score,"other":j}
    results=[]
    for k,i in enumerate(sample):
        score=best[k]["score"]
        other=best[k]["other"]
        results.append({
            "samplePage":pages[i]["number"],
            "sampleRegion":pages[i]["region"],
            "closestPage":pages[other]["number"] if other is not None else None,
            "closestRegion":pages[other]["region"] if other is not None else None,
            "maxSimilarity":round(score,6),
            "pass":score<threshold,
        })
    exact=sum(count-1 for count in hashes.values() if count>1)
    failures=[r for r in results if not r["pass"]]
    return {
        "site":"onehour-sky",
        "mode":"pinned-seeded-1pct-versus-every-other-page",
        "population":len(pages),
        "sampleCount":n,
        "samplePercent":round(n/len(pages)*100,4),
        "pairsCompared":n*(len(pages)-1),
        "metric":"whitespace-free-casefolded-character-5gram-Jaccard",
        "seed":seed,
        "thresholdExclusive":threshold,
        "wholePopulationExactBodyDuplicates":exact,
        "worstSampleToPopulationSimilarity":round(max((x["maxSimilarity"] for x in results),default=0),6),
        "failures":failures,
        "passed":not failures and exact==0,
        "samples":results,
        "limitations":[
            "1% sampled pages are compared against all pages; this is not all-pairs or semantic duplication proof.",
            "Actual local dispatch availability, photo rights, phone ownership, compliance and SEO rank are not confirmed.",
            "V4 source only enumerates dong/ga/ro entries plus higher areas; eup/myeon are not included."
        ]
    }


def main():
    pages=read_site("onehour-sky")["pages"]
    result=inspect(pages)
    out=ROOT/"reports"/"onehour-sky"/"sample_full_audit.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in ("samples","limitations")},ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__=="__main__":
    raise SystemExit(main())
