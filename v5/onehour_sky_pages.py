"""Site Factory V5: isolated national 1-hour skycar regional pages.

Uses V4's pinned legal-region ledger and Onehour-only text pool.
Generation is deterministic and is strictly a noindex preview until real
dispatch coverage, image rights, phone and region-specific facts are checked.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REGIONS = ROOT / "data/regions/onehour_national_city_districts.json"
POOL = ROOT / "data/pools/onehour_sky_copy_pool.json"
EXPECTED_REGIONS = 284
EXPECTED_PAGES = 285
EXPECTED_SOURCE_SHA = "44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd"
BRAND = "한시간스카이"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows():
    source = _load(REGIONS)
    items = source.get("regions", [])
    counts = Counter(x.get("level") for x in items)
    if (source.get("originalSourceSha256") != EXPECTED_SOURCE_SHA
            or source.get("originalSourceDate") != "2026-10-22"
            or len(items) != EXPECTED_REGIONS
            or counts != {"province": 16, "municipality": 229, "ward": 39}):
        raise ValueError("Onehour region provenance or count changed")
    names = [x.get("name") for x in items]
    codes = [x.get("code") for x in items]
    if (len(set(names)) != EXPECTED_REGIONS or len(set(codes)) != EXPECTED_REGIONS
            or any(not isinstance(n, str) or not n.strip() for n in names)
            or any(not isinstance(c, str) or not re.fullmatch(r"[0-9]{10}", c) for c in codes)):
        raise ValueError("Invalid national region identifiers")
    if any(x["name"] == "전국" for x in items):
        raise ValueError("National root is reserved")
    return items


def _pool():
    doc = _load(POOL)
    if doc.get("site") != "onehour-sky" or doc.get("version") != 1:
        raise ValueError("Wrong customer text pool")
    shared = doc.get("shared", {})
    topics = doc.get("topics", {})
    if len(shared) != 9 or len(topics) != 8:
        raise ValueError("Onehour copy pool group count changed")
    deep = doc.get("deepDive", {})
    if len(deep)!=4 or any(len(v)!=14 for v in deep.values()):
        raise ValueError("Insufficient site-specific long-form copy buckets")
    phrases = [s for group in shared.values() for s in group]
    phrases.extend(s for group in deep.values() for s in group)
    for topic in topics.values():
        phrases.extend(topic[field] for field in ("scene", "risk", "request"))
    if (len(phrases) != 152 or len(set(phrases)) != len(phrases)
            or any(len(s) < 26 or s[-1] not in ".!?" for s in phrases)):
        raise ValueError("Insufficient or duplicate customer copy")
    return shared, topics, deep


def _choose(values, key, n):
    if len(values) < n:
        raise ValueError("Copy group shorter than section requirements")
    positions = sorted(range(len(values)), key=lambda i:
        sha256((key + "|" + str(i)).encode("utf-8")).digest())
    return [values[i] for i in positions[:n]]


def make_page(record, index, shared, topics, deep):
    full = record["name"]
    code = record["code"]
    salt = "onehour-v1|" + code + "|" + full
    ids = sorted(topics)
    topic_id = ids[int.from_bytes(sha256(salt.encode()).digest()[:8], "big") % len(ids)]
    topic = topics[topic_id]
    def take(bucket, count):
        return _choose(shared[bucket], salt + "|" + bucket, count)
    dispatch = take("dispatch", 2)
    arrival = take("arrival", 2)
    short = take("shortWork", 3)
    half = take("halfDay", 3)
    rates = take("rates", 3)
    access = take("access", 3)
    safety = take("safety", 3)
    consult = take("consultation", 3)
    cta = take("cta", 2)
    topic_label = topic["label"]
    prep_more = _choose(deep["dispatchPreparation"], salt + "|deep-dispatch", 2)
    setup_more = _choose(deep["setupWorkflow"], salt + "|deep-setup", 2)
    safety_more = _choose(deep["siteSafety"], salt + "|deep-safety", 2)
    cost_more = _choose(deep["costAgreement"], salt + "|deep-cost", 2)
    sections = [
        {"heading": full + " " + topic_label + " 1시간 작업을 준비할 때",
         "paragraph": " ".join([topic["scene"]] + short + [consult[0]])},
        {"heading": full + " 신속 배차와 예상 도착 시간",
         "paragraph": " ".join(dispatch + arrival + [cta[0]])},
        {"heading": "1시간 작업도 반나절 기준으로 협의하는 이유",
         "paragraph": " ".join(half + rates[:2])},
        {"heading": full + " 차량 진입과 작업대 안전 확인",
         "paragraph": " ".join([topic["risk"]] + access + safety)},
        {"heading": full + " 스카이차 상담 시 필요한 정보",
         "paragraph": " ".join([topic["request"]] + consult[1:] + rates[2:] + cta[1:])},
        {"heading": full + " 빠른 출동을 준비하는 점검 순서",
         "paragraph": " ".join(prep_more + setup_more)},
        {"heading": "짧은 현장 작업의 안전과 최종 견적 확인",
         "paragraph": " ".join(safety_more + cost_more)},
    ]
    intro = (
        f"{full}에서 {topic_label}을 위한 스카이차 1시간 작업이나 반일작업을 알아보신다면 "
        "현장 위치와 작업 높이, 장비를 세울 공간부터 확인해 주세요. "
        f"{BRAND}는 가까운 기사 연결을 우선 검토하며, 실제 도착 예상 시각과 배차 가능 여부는 상담으로 확인합니다. "
        "1시간 작업이라도 기본 출동·설치·작업비가 발생해 반나절 요금을 기준으로 협의합니다."
    )
    if any(len(s["paragraph"]) < 80 for s in sections):
        raise ValueError("Onehour regional page has short prose")
    return {
        "id": "onehour-area-" + code,
        "number": index + 2,
        "region": full,
        "searchKeyword": "스카이차",
        "topic": topic_label,
        "poolTopicId": topic_id,
        "title": f"{full} 스카이차 1시간 작업, 반일작업 전문 '{BRAND}'",
        "intro": intro,
        "sections": sections,
        "serviceIds": ["sky-1t", "sky-35t", "sky-5t"],
        "faq": [
            {"q": f"{full}에서 스카이차 1시간만 이용해도 되나요?",
             "a": "단시간 작업도 상담합니다. 출동·장비 세팅·작업의 기본비용이 있어 한 시간만 이용해도 반나절 기준요금으로 협의합니다."},
            {"q": f"{full} 현장에 한 시간 이내 도착할 수 있나요?",
             "a": "1시간 내 도착을 목표로 가까운 기사를 우선 확인하지만 전국 어느 지역이든 보장하는 것은 아닙니다. 작업 위치와 기사 배정 및 이동 여건을 확인한 뒤 예상 시간을 안내합니다."},
        ],
    }


def expand(pages, regions):
    if len(pages) != 1 or pages[0].get("id") != "onehour-home" or pages[0].get("number") != 1:
        raise ValueError("Onehour homepage is the fixed build seed")
    if len(regions.get("regions", [])) != 1 or regions["regions"][0].get("name") != "전국":
        raise ValueError("Onehour root region record changed")
    rows = _rows()
    shared, topics, deep = _pool()
    regional = [make_page(row, i, shared, topics, deep) for i, row in enumerate(rows)]
    result = pages + regional
    if len(result) != EXPECTED_PAGES or result[-1]["number"] != EXPECTED_PAGES:
        raise ValueError("Onehour generation count mismatch")
    named_regions = {"regions": list(regions["regions"])}
    named_regions["regions"].extend({"name": row["name"], "kind": row["level"], "code": row["code"]} for row in rows)
    named_regions["source"] = regions.get("source")
    return result, named_regions
