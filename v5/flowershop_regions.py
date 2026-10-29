"""Pinned nationwide legal-dong (읍/면/동/가/로) expansion for flowershop.

Source: V4 official-codes.zip downloaded 2026-10-22 from code.go.kr.
Its sha256 and province distribution are checked; no AI API or live scraping.
This is a legal-dong inventory, not an independently verified administrative-dong
inventory nor proof of delivery coverage.
"""
from __future__ import annotations

import csv
from functools import lru_cache
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

from .config import ConfigError

ARCHIVE = "data/regions/flowershop_official_codes_20261022.zip"
POOL = "data/pools/flowershop_v4_opening_sentences.json"
SOURCE_SHA = "44a3fe4cacf88ce98e35fb883807d2725b589f427ff4d73ee40b914d1286bacd"
EXPECTED = {
    "강원특별자치도": 298,
    "경기도": 747,
    "경상남도": 546,
    "경상북도": 525,
    "대구광역시": 212,
    "대전광역시": 177,
    "부산광역시": 192,
    "서울특별시": 467,
    "세종특별자치시": 33,
    "울산광역시": 84,
    "인천광역시": 156,
    "전남광주통합특별시": 623,
    "전북특별자치도": 410,
    "제주특별자치도": 74,
    "충청남도": 285,
    "충청북도": 238,
}
EXPECTED_TOTAL = 5067
TOPICS = ("꽃집 개업화분", "화환전문 꽃집")
TOPIC_POOL_IDS = (
    (0, 1, 2, 3, 5, 6, 7, 9, 11, 13, 14),
    (0, 1, 2, 4, 5, 6, 7, 8, 9, 11, 13, 14, 15),
)


def _score(text: str) -> bytes:
    return hashlib.sha256(text.encode("utf-8")).digest()


@lru_cache(maxsize=2)
def current_regions(root: Path):
    path = root / ARCHIVE
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA:
        raise ConfigError("Nationwide legal-dong source checksum mismatch")
    with ZipFile(io.BytesIO(data)) as archive:
        names = [x for x in archive.namelist() if x.endswith(".txt")]
        if len(names) != 1:
            raise ConfigError("Unexpected official legal-dong ZIP layout")
        table = archive.read(names[0]).decode("cp949")
    reader = csv.DictReader(io.StringIO(table), delimiter="\t")
    if reader.fieldnames != ["법정동코드", "법정동명", "폐지여부"]:
        raise ConfigError("Official legal-dong columns changed")
    areas = []
    counts = {}
    for row in reader:
        if row["폐지여부"] != "존재":
            continue
        code = row["법정동코드"].strip()
        name = row["법정동명"].strip()
        parts = name.split()
        if not (len(code) == 10 and code.isdigit()):
            raise ConfigError("Malformed active official legal-dong code")
        # Retain legal-dong equivalents ending in 가/로 such as 신문로1가.
        if not (code.endswith("00") and len(parts) >= 2
                and parts[-1].endswith(("동", "읍", "면", "가", "로"))):
            continue
        province = parts[0]
        if province not in EXPECTED:
            raise ConfigError("Unexpected nationwide province in fixed source: " + province)
        counts[province] = counts.get(province, 0) + 1
        areas.append((code, name))
    areas.sort(key=lambda row: row[0])
    if (len(areas) != EXPECTED_TOTAL or counts != EXPECTED
            or len({r[0] for r in areas}) != len(areas)
            or len({r[1] for r in areas}) != len(areas)):
        raise ConfigError("Pinned official legal-dong coverage changed; do not renumber")
    return tuple(areas)


@lru_cache(maxsize=2)
def copy_topics(root: Path):
    data = json.loads((root / POOL).read_text(encoding="utf-8"))
    if len(data["topics"]) != 16:
        raise ConfigError("V4 sentence pool identity changed")
    for index, row in enumerate(data["topics"]):
        if (row["id"] != index or len(row["intros"]) != 4
                or len(row["questions"]) != 8 or len(row["answers"]) != 8):
            raise ConfigError("V4 sentence pool topic corrupted")
    return tuple(data["topics"])


def _pick(values, seed: str):
    index = int.from_bytes(_score(seed)[:8], "big") % len(values)
    return values[index]


def _substitute(text, region: str, keyword: str):
    return text.replace("{region}", region).replace("{key}", keyword)


def make_page(code: str, full_name: str, region_index: int, kind: int, copy):
    keyword = TOPICS[kind]
    key = code + ":" + str(kind)
    options = TOPIC_POOL_IDS[kind]
    chosen = sorted(options, key=lambda i: _score(key + ":topic:" + str(i)))[:5]
    selected = [copy[i] for i in chosen]
    intro = _substitute(
        _pick(selected[0]["intros"], key + ":lead"), full_name, keyword
    )
    if kind == 0:
        title = full_name + " 꽃집 개업화분 | 선물 종류·배송 주문 안내"
        intro += " 화분과 축하화환의 크기·설치 공간·상품 가격을 비교하고, 최종 배송 조건은 판매처 상세화면에서 확인해 주세요."
        skus = ["D144", "D149", "C200"]
    else:
        title = full_name + " 화환전문 꽃집 | 축하·근조화환 종류와 주문"
        intro += " 축하 행사와 조문은 서로 다른 주문 목적입니다. 화환 종류와 리본 문구를 구분해 선택하고 배송 가능 시간을 상담해 주세요."
        skus = ["C200", "C206", "B201", "B205"]
    sections = []
    for index, topic in enumerate(selected):
        first = _substitute(
            _pick(topic["intros"], key + ":body:" + str(index)),
            full_name, keyword
        )
        answer = _substitute(
            _pick(topic["answers"], key + ":detail:" + str(index)),
            full_name, keyword
        )
        sections.append({"heading": topic["title"], "paragraph": first + " " + answer})
    faqs = []
    for index, topic in enumerate(selected[1:4:2]):
        question = _substitute(
            _pick(topic["questions"], key + ":faq-q:" + str(index)),
            full_name, keyword
        )
        answer = _substitute(
            _pick(topic["answers"], key + ":faq-a:" + str(index)),
            full_name, keyword
        )
        faqs.append({"q": question, "a": answer})
    return {
        "id": "fs-" + code + "-" + str(kind + 1),
        "number": 4 + region_index * 2 + kind,
        "region": full_name,
        "topic": keyword,
        "searchKeyword": keyword,
        "title": title,
        "intro": intro,
        "sections": sections,
        "productSkus": skus,
        "faq": faqs,
    }


def expand(site, pages, regions, root: Path):
    policy = site.get("flowershopNational", {})
    if not policy.get("enabled", False):
        return pages, regions
    if site.get("id") != "flowershop-nalmada":
        raise ConfigError("Nationwide flowershop source cannot be used by another site")
    if (len(pages) != 3 or [p["number"] for p in pages] != [1, 2, 3]
            or policy.get("startNumber") != 4
            or policy.get("expectedDongCount") != EXPECTED_TOTAL
            or tuple(policy.get("topics", [])) != TOPICS):
        raise ConfigError("Flowershop pilot or national identity mismatch")
    areas = current_regions(root)
    copy = copy_topics(root)
    generated = [
        make_page(code, name, i, kind, copy)
        for i, (code, name) in enumerate(areas)
        for kind in range(len(TOPICS))
    ]
    all_regions = list(regions["regions"])
    all_regions.extend({
        "name": name, "code": code, "level": "legal-dong",
        "sourceAsOf": "2026-10-22"
    } for code, name in areas)
    return pages + generated, {
        **regions,
        "regions": all_regions,
        "nationwideSourceSha256": SOURCE_SHA,
        "nationwideLegalDongCount": len(areas),
        "scopeNote": "Pinned official legal-dong inventory; not the administrative-dong list"
    }
