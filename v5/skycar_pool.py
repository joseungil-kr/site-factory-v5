"""Daysky-only regional skycar copy pool.

This module performs OFFLINE candidate generation and reproducible quality QA.
It does not edit the published 29-page ledger, deploy, submit URLs or grant indexing.
The candidate generator uses human-curated work topics and reusable contextual
sentences without asserting real work completion, local street conditions or reach heights.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from math import ceil
from pathlib import Path
from random import Random
import json
import re

ROOT = Path(__file__).resolve().parents[1]
POOL_ROOT = ROOT / "data" / "pools"
REGION_LEDGER = ROOT / "data" / "regions" / "seoul_gyeonggi_current_dong.json"
EXISTING_SITE = ROOT / "sites" / "daysky"
REGION_SHA = "057679a9a6312dbb4dd284d2ca42856d40a828239b2483540a7000b630fc30eb"
TARGET_SCORE = 0.49
QA_SEED = 20261025
POOL_VERSION = 1


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_pool():
    work = _read(POOL_ROOT / "daysky_work_pool.json")
    common = _read(POOL_ROOT / "daysky_shared_pool.json")
    if (work.get("site"), common.get("site")) != ("daysky", "daysky"):
        raise ValueError("Wrong industry copy pool")
    if work["version"] != POOL_VERSION or common["version"] != POOL_VERSION:
        raise ValueError("Unpinned copy pool version")
    topics = work["topics"]
    shared = common["shared"]
    if len(topics) < 8 or len(shared) < 10:
        raise ValueError("Insufficient domain-specific or general copy groups")
    all_sentences = []
    for key, group in topics.items():
        for field in ("lead", "scene", "access", "workflow", "handoff"):
            values = group[field]
            if len(values) < (6 if field == "lead" else 8):
                raise ValueError("Insufficient pool variants: " + key + "." + field)
            all_sentences.extend(values)
    for key, values in shared.items():
        if len(values) < 14:
            raise ValueError("Insufficient shared variants: " + key)
        all_sentences.extend(values)
    if len(all_sentences) != len(set(all_sentences)):
        raise ValueError("Duplicate exact sentence in dedicated pool")
    if any(not isinstance(s, str) or len(s) < 26 or s[-1] not in ".!?" for s in all_sentences):
        raise ValueError("Too-short or unpunctuated pool sentence")
    forbidden = ("영진", "fwith", "1844-0644", "완료한 현장", "실제로 시공한")
    if any(w in s for w in forbidden for s in all_sentences):
        raise ValueError("Other customer brand or unverified actual work claim in copy pool")
    return {"topics": topics, "shared": shared, "sentenceCount": len(all_sentences)}


def _ranked(pool, key: str, count: int):
    """Stable domain-separated selection; no repeated fragment within a slot."""
    if count > len(pool):
        raise ValueError("Copy bucket exhausted")
    ranking = sorted(range(len(pool)), key=lambda i: sha256((key + "|" + str(i)).encode("utf-8")).digest())
    return [pool[i] for i in ranking[:count]]


def _province(parent: str):
    if parent.startswith("서울특별시 "):
        return "서울"
    if parent.startswith("경기도 "):
        return "경기"
    raise ValueError("Unsupported area: " + parent)


def _display(parent: str, dong: str):
    return ("서울 " + parent.removeprefix("서울특별시 ") if parent.startswith("서울특별시 ")
            else "경기 " + parent.removeprefix("경기도 ")) + " " + dong


def _page(parent: str, dong: str, number: int, index: int, pool, *, variant: int = 0):
    full = parent + " " + dong
    topic_ids = tuple(sorted(pool["topics"]))
    topic_id = topic_ids[int.from_bytes(sha256(("topic|" + full).encode()).digest()[:8], "big") % len(topic_ids)]
    topic = pool["topics"][topic_id]
    shared = pool["shared"]
    label = topic["label"]
    display = _display(parent, dong)
    salt = "daysky-copy-v1|" + full + "|" + topic_id + "|" + str(variant)

    def choose(source, key, n=1):
        return _ranked(source, salt + "|" + key, n)

    scene = choose(topic["scene"], "topic-scene", 4)
    workflow = choose(topic["workflow"], "topic-workflow", 3)
    access = choose(topic["access"], "topic-access", 3)
    handoff = choose(topic["handoff"], "topic-handoff", 3)
    region_context = choose(shared["regionContext"], "region-context", 2)
    coordination = choose(shared["coordination"], "coordination", 2)
    lead = choose(topic["lead"], "lead")[0]

    intro = (f"{display}에서 {label}을 위해 스카이차를 알아보신다면 현장 이용 계획부터 "
             f"구체적으로 살펴보는 것이 좋습니다. {lead} {region_context[0]} "
             "당일스카이는 1톤·3.5톤·5톤 장비의 이용 시간과 작업 비용을 전화로 상담합니다.")

    def section(heading, parts):
        if len(parts) != len(set(parts)):
            raise ValueError("Repeated sentence within regional section")
        return {"heading": heading, "paragraph": " ".join(parts)}

    sections = [
        section(f"{label}에 필요한 작업 범위",
                scene[:3] + workflow[:2]),
        section(f"{display} 현장 진입과 장비 설치 조건",
                access + choose(shared["access"], "shared-access")
                + choose(shared["ground"], "shared-ground", 2)),
        section("1톤·3.5톤·5톤 장비를 선택할 때",
                [scene[3]] + choose(shared["equipment"], "equipment", 3)
                + choose(shared["safety"], "safety") + [region_context[1]]),
        section(f"{display} 스카이차 사용 시간과 기준요금",
                choose(shared["timing"], "timing", 2)
                + choose(shared["pricing"], "pricing", 2)
                + [workflow[2], coordination[0]]),
        section("현장 사진과 전화 상담 준비",
                handoff + choose(shared["photo"], "photo", 2)
                + choose(shared["consult"], "consult") + [coordination[1]]),
    ]
    page = {
        "id": "daysky-pool-" + sha256(full.encode("utf-8")).hexdigest()[:16],
        "number": number,
        "region": full,
        "searchKeyword": "스카이차",
        "topic": label,
        "poolTopicId": topic_id,
        "title": f"{display} 당일 스카이차 작업 비용 | {label}",
        "intro": intro,
        "sections": sections,
        "serviceIds": ["sky-1t", "sky-35t", "sky-5t"],
        "faq": [
            {
                "q": f"{display}에서 {label} 작업에 어떤 정보를 준비하면 될까요?",
                "a": handoff[0] + " 작업 위치와 현장 조건을 전달하면 장비 상담에 도움이 됩니다.",
            },
            {
                "q": f"{display} 스카이차 1시간·4시간·8시간 비용은 어떻게 확인하나요?",
                "a": "1톤·3.5톤·5톤별 기본 요금표를 비교할 수 있으며, 부가세와 현장 조건에 따른 금액은 전화 상담에서 안내합니다.",
            },
        ],
    }
    return page


def candidates():
    """Construct pages in memory, preserving 1..29 and never rewriting production."""
    ledger = _read(REGION_LEDGER)
    rows = ledger["rows"]
    if (ledger.get("asOf") != "2026-10-12" or ledger.get("sourceSHA256") != REGION_SHA
            or len(rows) != 1732 or len({tuple(x) for x in rows}) != 1732):
        raise ValueError("Region ledger differs from the pinned 2026-10-12 snapshot")
    old_pages = _read(EXISTING_SITE / "pages.json")
    old_regions = _read(EXISTING_SITE / "regions.json")
    if len(old_pages) != 29 or [p["number"] for p in old_pages] != list(range(1, 30)):
        raise ValueError("Existing published URL ledger changed; do not renumber")
    existing = {row["name"] for row in old_regions["regions"]}
    matching = sum(parent + " " + dong in existing for parent, dong in rows)
    if matching != 25:
        raise ValueError("Ansan published region inventory no longer matches 25 dongs")
    pool = load_pool()
    output = []
    for index, (parent, dong) in enumerate(rows):
        if parent + " " + dong in existing:
            continue
        output.append(_page(parent, dong, 30 + len(output), index, pool))
    if len(output) != 1707 or output[-1]["number"] != 1736:
        raise ValueError("Unexpected generated region count")
    return old_pages, output, pool


def body(page):
    return " ".join([page["intro"]] + [part["paragraph"] for part in page["sections"]])


def _grams(text, n=5):
    """Same whitespace-free 5-gram Jaccard metric as V5 audit.py."""
    plain = re.sub(r"\s+", "", text).lower()
    return {plain[i:i+n] for i in range(max(0, len(plain)-n+1))}


def _jaccard(left, right):
    overlap = len(left & right)
    return overlap / (len(left) + len(right) - overlap) if (left or right) else 1.0


def audit_random_one_percent(seed: int = QA_SEED, threshold: float = TARGET_SCORE):
    """Random 1% of each province vs ALL old+new documents, not just sample pairs."""
    old, new, pool = candidates()
    groups = {
        "서울": [page for page in new if page["region"].startswith("서울특별시 ")],
        "경기": [page for page in new if page["region"].startswith("경기도 ")],
    }
    rng = Random(seed)
    sample = []
    for province in ("서울", "경기"):
        number = max(1, ceil(len(groups[province]) * 0.01))
        sample += rng.sample(groups[province], number)
    all_pages = old + new
    fingerprints = {page["id"]: _grams(body(page)) for page in all_pages}
    hashes = [sha256(body(page).encode("utf-8")).hexdigest() for page in all_pages]
    repeated = sum(n-1 for n in Counter(hashes).values() if n > 1)
    results = []
    for page in sample:
        own = fingerprints[page["id"]]
        worst = (0.0, None)
        for other in all_pages:
            if other["id"] == page["id"]:
                continue
            score = _jaccard(own, fingerprints[other["id"]])
            if score > worst[0]:
                worst = (score, other)
        results.append({
            "sampleNumber": page["number"], "sampleRegion": page["region"],
            "sampleTopic": page["topic"], "maximumSimilarity": round(worst[0], 6),
            "closestPageNumber": worst[1]["number"],
            "closestPageRegion": worst[1]["region"],
            "closestPageTopic": worst[1]["topic"] if "topic" in worst[1] else "",
        })
    scores = sorted(x["maximumSimilarity"] for x in results)
    over = [x for x in results if x["maximumSimilarity"] >= threshold]
    return {
        "mode": "seeded-random-province-stratified-1pct-versus-all",
        "seed": seed,
        "thresholdExclusive": threshold,
        "sourceAsOf": "2026-10-12",
        "fullDongCount": 1732,
        "existingAnsanDongCount": 25,
        "existingPublishedPages": len(old),
        "newUnpublishedCandidates": len(new),
        "evaluatedTotalDocuments": len(all_pages),
        "provincePopulations": {k: len(v) for k,v in groups.items()},
        "sampleSize": len(sample),
        "sampleShare": round(len(sample) / len(new), 6),
        "pairsCompared": len(sample) * (len(all_pages) - 1),
        "exactDuplicateBodiesInPopulation": repeated,
        "poolTopicCount": len(pool["topics"]),
        "poolSharedBuckets": len(pool["shared"]),
        "poolDistinctSentences": pool["sentenceCount"],
        "worstSampleToPopulationScore": max(scores, default=0),
        "medianWorstScore": scores[len(scores)//2] if scores else None,
        "failingSamples": over,
        "passesSample": not over and repeated == 0,
        "samples": results,
        "limitations": [
            "Only the sampled regions receive cross-population similarity checks; this is not a full pairwise proof.",
            "The metric is whitespace-free character 5-gram Jaccard similarity, not semantic plagiarism or search rank.",
            "Candidate pages exist only in memory; no live Daysky URL or existing source page is modified.",
            "Existing source is a 2026-10-12 current-dong snapshot. Eup and myeon require separate official records.",
        ],
    }
