"""Todayflower nationwide noindex generator from the V4 pinned legal-code ZIP.

This is historical administrative coverage (2026-10-22), NOT independently
verified service delivery, current legal status, local popularity, or any shop.
Keep original 33 reviewed pages unchanged and their numbering stable.
No generative API, web scrape, or new location information is used.
"""
from __future__ import annotations

import csv
from functools import lru_cache
import hashlib
import io
from pathlib import Path
from zipfile import ZipFile

from .config import ConfigError

ARCHIVE = "data/regions/todayflower_official_codes_20261022.zip"
ZIP_SHA256 = "44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd"
EXPECTED = {
    "강원특별자치도":298, "경기도":747, "경상남도":546,
    "경상북도":525, "대구광역시":212, "대전광역시":177,
    "부산광역시":192, "서울특별시":467, "세종특별자치시":33,
    "울산광역시":84, "인천광역시":156, "전남광주통합특별시":623,
    "전북특별자치도":410, "제주특별자치도":74,
    "충청남도":285, "충청북도":238
}
EXPECTED_DONG_COUNT=5067
EXPECTED_ORIGINAL=33
EXPECTED_NEW=5037
EXPECTED_TOTAL=5070
ORDER_KINDS=("bouquet","plant","celebration","condolence")
PRODUCT_LABELS={
    "G067":"가을산책 꽃다발", "G073":"시크릿가든 꽃다발",
    "D144":"금전수 탁상용", "D149":"녹보수 소형",
    "C200":"축하 3단 화환", "C206":"축하 4단 화환",
    "B201":"근조 3단 화환", "B205":"근조 특대 3단 화환"
}

PRODUCT_SETS=(
    ("G067","G073","D144","D149","C200","B201"),
    ("G073","D144","D149","C206","B201","B205"),
    ("G067","G073","D144","C200","C206","B201","B205"),
    ("G067","D144","D149","C200","B201","B205"),
    ("G073","D144","D149","C200","C206","B201"),
)
from .todayflower_copy_pool import SCENARIOS, SCENE_DETAILS

def _pick(items, seed):
    value=int.from_bytes(hashlib.sha256(seed.encode("utf-8")).digest()[:8],"big")
    return items[value%len(items)]

@lru_cache(maxsize=1)
def legal_regions(root:Path):
    data=(root/ARCHIVE).read_bytes()
    if hashlib.sha256(data).hexdigest()!=ZIP_SHA256:
        raise ConfigError("Todayflower pinned legal ZIP SHA-256 mismatch")
    with ZipFile(io.BytesIO(data)) as z:
        names=[n for n in z.namelist() if n.endswith(".txt")]
        if len(names)!=1:raise ConfigError("Unexpected legal ZIP contents")
        t=z.read(names[0]).decode("cp949")
    reader=csv.DictReader(io.StringIO(t),delimiter="\t")
    if reader.fieldnames!=["법정동코드","법정동명","폐지여부"]:
        raise ConfigError("Legal ZIP expected columns changed")
    regions=[];counts={}
    for row in reader:
        if row["폐지여부"]!="존재":continue
        code,name=row["법정동코드"].strip(),row["법정동명"].strip()
        parts=name.split()
        if not (len(code)==10 and code.isdigit()):
            raise ConfigError("Malformed legal code in archived source")
        if not (code.endswith("00") and len(parts)>=2
                and parts[-1].endswith(("동","읍","면","가","로"))):
            continue
        province=parts[0]
        if province not in EXPECTED:raise ConfigError("Unexpected archived province "+province)
        counts[province]=counts.get(province,0)+1
        regions.append((code,name))
    regions.sort()
    if counts!=EXPECTED or len(regions)!=EXPECTED_DONG_COUNT:
        raise ConfigError("Historical nationwide legal-code distribution changed")
    if len(set(regions))!=len(regions) or len({v[0] for v in regions})!=len(regions):
        raise ConfigError("Duplicate legal region codes")
    return tuple(regions)

def _make_page(code,name,number):
    # Region identity is sourced from pinned legal codes. Regional delivery
    # availability is never inferred from region existence.
    scenario=SCENARIOS[int.from_bytes(
        hashlib.sha256(("todayflower:"+code).encode()).digest()[:8],"big")%len(SCENARIOS)]
    intent,focus,products,q1,q2,response=scenario
    details=SCENE_DETAILS[intent]
    assert set(details)=={"selection","receiver","delivery"}
    seed=code+":todayflower:buyer-intent-v2"
    # Separate per-page/per-intent permutation avoids repeating clusters
    # without adding unrelated text or inventing local facts.
    orders={}
    for group,items in details.items():
        assert len(items)==12 and len(set(items))==12
        orders[group]=sorted(items,key=lambda value:hashlib.sha256(
            (seed+":"+group+":"+value).encode("utf-8")).digest())
    def one(group, offset):
        return orders[group][offset]
    skus=PRODUCT_SETS[int.from_bytes(
        hashlib.sha256((seed+":sku").encode()).digest()[:2],"big")%len(PRODUCT_SETS)]
    choices=sorted(skus,key=lambda sku:hashlib.sha256(
        (seed+":compare:"+sku).encode("utf-8")).digest())
    compare=(f"연결된 상품 카드에서 {PRODUCT_LABELS[choices[0]]}({choices[0]})과 "
             f"{PRODUCT_LABELS[choices[1]]}({choices[1]})의 사진과 표시가격을 "
             "비교해 보세요. 원하는 크기와 상품 종류는 각 상세 화면에서 살펴볼 수 있습니다.")
    sections=[
        {"heading":intent+" 상품과 선택 기준",
         "paragraph":products+" "+one("selection",0)},
        {"heading":"수령 주소와 인계 담당자",
         "paragraph":one("receiver",0)+" "+one("receiver",2)},
        {"heading":"상품 사진·규격·옵션 비교",
         "paragraph":one("selection",4)+" "+compare},
        {"heading":"배송 일정과 최종 결제금액",
         "paragraph":one("delivery",0)+" "+one("delivery",2)}
    ]
    faqs=[
        {"q":f"{name}에서 "+q1,
         "a":response+" "+one("delivery",4)},
        {"q":q2,
         "a":one("selection",3)+" "+one("selection",5)},
        {"q":f"{name} 꽃배달을 주문할 때 어떤 정보를 준비하면 좋나요?",
         "a":one("receiver",4)+" "+one("delivery",1)}
    ]

    return {
        "id":"today-national-"+code,
        "number":number,
        "region":name,
        "topic":intent,
        "searchKeyword":"꽃배달 당일배송",
        "title":name+" 꽃배달 당일배송 | "+intent+"·상품 선택·주문 안내",
        "intro":name+" 꽃배달을 준비하신다면 "+focus,
        "heroTag":name+" · "+intent,
        "sectionLead":"원하는 상품번호와 수령 주소, 희망일을 알려주시면 접수 가능한 일정과 비용을 안내받을 수 있습니다.",
        "sections":sections,
        "productSkus":list(skus),
        "faq":faqs,
        "evidenceScope":"2026-10-22 pinned legal-code snapshot; no per-address delivery promise"
    }

def expand(site,pages,regions,root:Path):
    policy=site.get("todayflowerNational") or {}
    if not policy.get("enabled",False):return pages,regions
    if site.get("id")!="todayflower-nalmada":
        raise ConfigError("Todayflower national generator may not change other sites")
    if site.get("publishEnabled") or site.get("indexNow",{}).get("enabled"):
        raise ConfigError("Bulk nationwide generation is preview-only until verified public release")
    if (len(pages)!=EXPECTED_ORIGINAL or [p["number"] for p in pages]!=list(range(1,34))
            or policy.get("expectedLegalDongCount")!=EXPECTED_DONG_COUNT
            or policy.get("expectedPageCount")!=EXPECTED_TOTAL
            or policy.get("archiveSHA256")!=ZIP_SHA256):
        raise ConfigError("Current 33 reviewed pages or national source identity mismatch")
    official=legal_regions(root)
    prior={r["code"]:r["name"] for r in regions["regions"] if r.get("level")=="legal-dong"}
    if len(prior)!=30:
        raise ConfigError("The preserved Ansan 30 legal-dong source inventory changed")
    official_map=dict(official)
    for code,name in prior.items():
        if official_map.get(code)!=name:
            raise ConfigError("Existing Ansan official code/name disagrees with nationwide snapshot: "+code)
    new=[(code,name) for code,name in official if code not in prior]
    if len(new)!=EXPECTED_NEW:
        raise ConfigError("Unexpected nationwide legal-dong delta count")
    # 404.html is the V5 real error document; numbered page 404 would
    # overwrite it. Reserve 404 in Todayflower only, without altering V5,
    # Flowershop, or any other site's existing filename numbering.
    generated=[_make_page(code,name,(i+34 if i+34<404 else i+35))
               for i,(code,name) in enumerate(new)]
    original_ids={p["id"] for p in pages}
    if any(p["id"] in original_ids for p in generated):
        raise ConfigError("National page identity collision")
    all_regions=list(regions["regions"])
    all_regions.extend({
        "code":code, "name":name, "level":"legal-dong",
        "sourceAsOf":"2026-10-22",
        "deliveryVerified":False,
    } for code,name in new)
    if len(pages)+len(generated)!=EXPECTED_TOTAL or len(all_regions)!=EXPECTED_TOTAL:
        raise ConfigError("Unexpected national page or region count")
    return pages+generated, {
        **regions,"regions":all_regions,
        "nationwideLegalDongCount":EXPECTED_DONG_COUNT,
        "nationwideAddedCount":EXPECTED_NEW,
        "nationwideArchiveSHA256":ZIP_SHA256,
        "scopeNote":"Pinned historical legal-code inventory, NOT current legal status or verified local same-day delivery",
    }
