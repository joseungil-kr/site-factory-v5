"""Pinned Seoul/Gyeonggi current-dong expansion with reusable descriptive customer copy.

Builds five-section flower and plant articles from the vetted region ledger.
"""
from __future__ import annotations
import json
from pathlib import Path

TOPICS=("축하화분","승진화분")
EXPECTED={"서울특별시":807,"경기도":925}
SOURCE_SHA="057679a9a6312dbb4dd284d2ca42856d40a828239b2483540a7000b630fc30eb"

def _province(parent):
    return "서울특별시" if parent.startswith("서울특별시 ") else "경기도"

def _display(parent,name):
    return ("서울 "+parent.removeprefix("서울특별시 ") if parent.startswith("서울특별시 ") else "경기 "+parent.removeprefix("경기도 "))+" "+name

def _page(row,region_index,topic_index,page_number):
    from .neutral_copy import clean
    parent,dong=row
    topic=TOPICS[topic_index]
    full=parent+" "+dong
    skus=("D144","D149","D158","D143","D151")
    page={"id":f"sg-{region_index+1:04d}-{topic_index+1}","number":page_number,
        "region":full,"searchKeyword":topic,"topic":"","title":"","intro":"",
        "sections":[],"productSkus":[skus[(region_index*3+topic_index)%5]],
        "faq":[]}
    return clean(page,row,region_index,topic_index)

def expand(site,pages,regions,root:Path):
    policy=site.get("regionalScale",{})
    if not policy.get("enabled"):return pages,regions
    if site["id"]!="seoul-gyeonggi-plants":raise ValueError("Bulk rollout only for isolated Seoul Gyeonggi site")
    source=json.loads((root/"data/regions/seoul_gyeonggi_current_dong.json").read_text(encoding="utf-8"))
    rows=source["rows"]
    if source["sourceSHA256"]!=SOURCE_SHA or source["asOf"]!="2026-10-12" or len(rows)!=1732 or len(set(map(tuple,rows)))!=1732:
        raise ValueError("Fixed region source changed; forbid renumbering without review")
    counts={"서울특별시":0,"경기도":0}
    for parent,name in rows:
        province=_province(parent)
        if not parent.startswith(province+" ") or not name.endswith(("동","가","로")) or len(name)>40:
            raise ValueError("Invalid current-dong inventory")
        counts[province]+=1
    if counts!=EXPECTED:raise ValueError("Expected Seoul 807 and Gyeonggi 925 present dong names")
    if len(pages)!=1 or pages[0]["number"]!=1 or tuple(policy.get("topics",[]))!=TOPICS or policy.get("startNumber")!=2:
        raise ValueError("Bulk collection identity changed")
    generated=[_page(row,i,t,2+i*2+t) for i,row in enumerate(rows) for t in range(2)]
    base_regions=list(regions["regions"])
    base_regions.extend({"name":parent+" "+name,"kind":"current-dong"} for parent,name in rows)
    return pages+generated,{**regions,"regions":base_regions,"sourceSHA256":source["sourceSHA256"]}
