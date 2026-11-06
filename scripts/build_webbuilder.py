#!/usr/bin/env python3
"""Webbuilder: deterministic, isolated B2B website asset generator.

Builds preview or explicitly selected public assets; it does not deploy, alter DNS,
change production Workers, or submit URLs to search engines.
"""
from __future__ import annotations

import argparse
import csv
import html
import hashlib
import json
import math
import re
import shutil
from itertools import combinations
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "sites" / "webbuilder"
DEFAULT_OUTPUT = ROOT / "dist" / "webbuilder"
DEFAULT_REPORT = ROOT / "reports" / "webbuilder"
PHONE = "010-2490-0555"
TEL = "01024900555"
DOMAIN = "https://webbuilder.nalmada.net"
PRICE = 1000


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def load(name: str) -> dict:
    return json.loads((SITE / name).read_text(encoding="utf-8"))


def require_source() -> tuple[dict, dict, dict]:
    from v5.site_plan import require_site_plan

    require_site_plan("webbuilder")
    spec, keywords, pool = load("site-spec.json"), load("keyword-pool.json"), load("copy-pool.json")
    if spec["domain"] != DOMAIN or spec["conversion"]["phone"] != PHONE:
        raise ValueError("Webbuilder domain or phone drift")
    if spec["publishPolicy"]["production"] or spec["publishPolicy"]["indexNow"]:
        raise ValueError("Production and IndexNow must remain disabled")
    pricing = spec["pricing"]
    if not (pricing["billingCycle"] == "monthly"
            and pricing["headlinePriceKRW"] == 1000
            and pricing["domainRegistrationIncluded"] is True
            and pricing["domainIncluded"] is True
            and pricing["minimumPages"] == 10
            and pricing["minimumMonthlyKRW"] == 10000
            and pricing["providerOwnedSubdomainIncluded"] is True
            and pricing["providerPurchasedIndustryDomainCostsIncluded"] is True
            and pricing["customerDomainRegistrationIncluded"] is False
            and pricing["hostingIncluded"] is True
            and pricing["creationIncluded"] is True
            and pricing["baseOfferConfirmed"] is True
            and pricing["fullContractTermsConfirmed"] is False):
        raise ValueError("Monthly base offer drift: expected 1,000 KRW/page with provider-operated industry domain pool and hosting included")
    if (pool["pricingFact"]["monthlyFeePerPageKRW"] != pricing["headlinePriceKRW"]
            or pool["pricingFact"]["domainRegistrationIncluded"] is not True
            or pool["pricingFact"]["hostingIncluded"] is not True
            or pool["pricingFact"]["minimumPages"] != 10
            or pool["pricingFact"]["minimumMonthlyKRW"] != 10000
            or pool["pricingFact"]["providerOwnedIndustryDomainPool"] is not True
            or pool["pricingFact"]["candidateRootsPurchased"] is not False
            or [(x["pages"], x["amountKRW"]) for x in pool["pricingFact"]["monthlyExamples"]]
            != [(10, 10000), (20, 20000), (30, 30000), (50, 50000), (100, 100000)]):
        raise ValueError("Monthly price examples and contract facts drift")
    domain_policy = load("domain-policy.json")
    if (spec["domainProvision"]["type"] != "provider-managed-multi-domain-pool"
            or spec["domainProvision"]["rootDomainWhitelistFixed"] is not False
            or spec["domainProvision"]["domainRegistrationOrPurchaseExecuted"] is not False
            or domain_policy["offer"]["minPages"] != 10
            or domain_policy["publication"]["domainPurchaseApproved"] is not False):
        raise ValueError("Industry root domain policy drift")
    roots = {x["root"]: x["status"] for x in domain_policy["domainInventory"]}
    if (roots.get("leak119.net") != "candidate_example_not_purchased_or_verified"
            or roots.get("skycar24hr.com") != "candidate_example_not_purchased_or_verified"):
        raise ValueError("Unverified domain examples cannot be claimed as owned")
    if len(keywords["industries"]) < 30:
        raise ValueError("Insufficient candidate keyword sectors")
    extra_a = load("industry-expansion-a.json")["industry"]
    extra_b = load("industry-expansion-b.json")["industry"]
    supplemental = {**extra_a, **extra_b}
    if len(pool["industry"]) != 10 or len(extra_a) != 14 or len(extra_b) != 14 or len(supplemental) != 28:
        raise ValueError("Original 10 and supplemental 28 industry copy records required")
    if set(pool["industry"]) & set(supplemental):
        raise ValueError("New copy must never overwrite original 10 industry records")
    for ident, article in supplemental.items():
        narrative = "".join(article.get(f, "") for f in ("intro", "problem", "structure", "conversion", "difference"))
        if len(narrative) < 360 or len(article.get("checklist", [])) != 4:
            raise ValueError("Unfinished original industry narrative: "+ident)
    pool["industry"] = {**pool["industry"], **supplemental}
    launch = [x for x in keywords["industries"] if x["launch"]]
    if len(keywords["industries"]) != 38 or len(launch) != 38 or set(pool["industry"]) != {x["id"] for x in launch}:
        raise ValueError("38 sector launch source mismatch")
    if len(pool["heroVariants"]) < 10 or len(pool["faq"]) < 10:
        raise ValueError("Insufficient independently written copy pool")
    return spec, keywords, pool


def paragraph(text: str) -> str:
    return "<p>" + escape(text) + "</p>"


def kicker(text: str) -> str:
    return '<span class="kicker">' + escape(text) + "</span>"


def cta(text: str = "우리 업종 제작 상담하기") -> str:
    return '<a class="btn btn-primary" href="tel:' + TEL + '">' + escape(text) + '</a>'


def secondary(text: str, href: str) -> str:
    return '<a class="btn btn-secondary" href="' + escape(href) + '">' + escape(text) + "</a>"


def layout(title: str, description: str, body: str, active: str = "") -> str:
    org = json.dumps(
        {"@context": "https://schema.org", "@type": "Organization",
         "name": "인터피아드", "url": "https://interpiad.com", "telephone": PHONE},
        ensure_ascii=False, separators=(",", ":")
    ).replace("<", "\\u003c")
    nav = [
        ("/", "처음", "home"),
        ("/#industries", "제작 업종", "industries"),
        ("/guide/pricing/", "비용 안내", "pricing"),
        ("/guide/process/", "제작 방식", "process"),
        ("/guide/faq/", "자주 묻는 질문", "faq"),
    ]
    items = "".join(
        '<a href="' + href + '"' + (' aria-current="page"' if key == active else "") + '>' + label + "</a>"
        for href, label, key in nav
    )
    return (
        '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        '<meta name="theme-color" content="#102444">'
        '<meta name="description" content="' + escape(description) + '">'
        '<meta property="og:type" content="website">'
        '<meta property="og:title" content="' + escape(title) + '">'
        '<meta property="og:description" content="' + escape(description) + '">'
        '<title>' + escape(title) + '</title>'
        '<link rel="stylesheet" href="/assets/site.css">'
        '<script type="application/ld+json">' + org + '</script></head><body>'
        '<a class="skip-link" href="#main">본문으로 이동</a>'
        '<header class="site-header"><div class="container header-inner">'
        '<a class="brand" href="/" aria-label="인터피아드 웹빌더 홈"><span class="brand-mark">i.</span>'
        '<span>interpiad <small>LOCAL WEB BUILDER</small></span></a>'
        '<nav class="nav" aria-label="주 메뉴">' + items + '</nav>'
        '<a class="header-phone" href="tel:' + TEL + '">상담 ' + PHONE + '</a>'
        '</div></header><main id="main">' + body + '</main>'
        '<section class="bottom-cta"><div class="container bottom-cta-inner">'
        '<div><span class="eyebrow">최소 10페이지부터, 필요한 정보부터</span>'
        '<h2>우리 업종에 맞는 홈페이지를 상담해보세요.</h2>'
        '<p>제공 서비스와 방문 가능 지역을 알려주시면 필요한 홈페이지 구성을 함께 살펴보겠습니다.</p></div>'
        + illustration("mobile-contact.webp", "모바일에서 홈페이지와 전화 상담 정보를 확인하는 화면 예시", "bottom-illustration") +
        cta("010-2490-0555 전화 상담") +
        '</div></section>'
        '<footer class="site-footer"><div class="container footer-inner">'
        '<div><strong>인터피아드</strong><p>지역 서비스업을 위한 홈페이지 제작 안내</p>'
        '<p>사업자 : 인터피아드 · <a href="https://interpiad.com" rel="noopener noreferrer">https://interpiad.com</a></p>'
        '<p>전화 : <a href="tel:' + TEL + '">' + PHONE + '</a></p></div>'
        '<div class="footer-links"><a href="/guide/pricing/">비용 안내</a>'
        '<a href="/guide/process/">제작 방식</a><a href="/guide/faq/">자주 묻는 질문</a></div>'
        '</div></footer></body></html>'
    )


def monthly_price_rows(pool: dict, limit: int | None = None) -> str:
    examples = pool["pricingFact"]["monthlyExamples"]
    if limit is not None:
        examples = examples[:limit]
    return "".join(
        '<div class="price-row' + (' highlighted' if item["pages"] == 20 else '') +
        '"><span>' + str(item["pages"]) + '페이지 × 월 1,000원</span><strong>월 ' +
        format(item["amountKRW"], ",") + '원</strong></div>'
        for item in examples
    )


def webp_dimensions(raw: bytes) -> tuple[int, int]:
    """Read dimensions of the verified lossy WebP frame using stdlib, no extra dependency."""
    if len(raw) < 30 or raw[:4] != b"RIFF" or raw[8:12] != b"WEBP":
        raise ValueError("Bad RIFF/WEBP file header")
    i = raw.find(b"\x9d\x01\x2a", 20, 60)
    if i < 0 or i + 7 > len(raw):
        raise ValueError("VP8 frame marker missing")
    return (int.from_bytes(raw[i + 3:i + 5], "little") & 0x3fff,
            int.from_bytes(raw[i + 5:i + 7], "little") & 0x3fff)


def illustration(file: str, description: str, css_class: str) -> str:
    dimensions = {"webbuilder-hero.webp": (1536, 1024), "industry-services.webp": (1024, 680),
                  "local-search.webp": (1024, 680), "managed-domain.webp": (1024, 680),
                  "mobile-contact.webp": (1024, 680)}
    if file not in dimensions:
        raise ValueError("Unexpected webbuilder image file: "+file)
    w, h = dimensions[file]
    return ('<img src="/assets/images/' + file + '" alt="' + escape(description) +
            '" class="' + escape(css_class) + '" width="' + str(w) +
            '" height="' + str(h) + '">')

def industry_cards(sectors: list[dict]) -> str:
    cards = []
    for i, item in enumerate(sectors, 1):
        name = escape(item["label"])
        cards.append(
            '<a class="industry-card" href="/industry/' + escape(item["id"]) + '/">'
            '<span class="industry-card-number">' + f"{i:02d}" + '</span>'
            '<span class="industry-card-title">' + name + ' 홈페이지</span>'
            '<span class="industry-card-text">' + escape(item["consultingAngle"]) + '</span>'
            '<span class="industry-arrow" aria-hidden="true">↗</span></a>'
        )
    return "".join(cards)


def grouped_industry_cards(sectors: list[dict]) -> str:
    grouped = {}
    for item in sectors:
        grouped.setdefault(item["cluster"], []).append(item)
    return "".join(
        '<section class="industry-group"><h3 class="industry-group-heading">' +
        escape(category) + '<span>' + str(len(items)) + '개 업종</span></h3>' +
        '<div class="industry-grid">' + industry_cards(items) + '</div></section>'
        for category, items in grouped.items()
    )


def related_industry_cards(item: dict, sectors: list[dict]) -> str:
    group = [x for x in sectors if x["cluster"] == item["cluster"] and x["id"] != item["id"]]
    return (
        '<section class="section related-section"><div class="container narrow">'
        '<span class="eyebrow">함께 살펴볼 업종</span><h2>관련 홈페이지 제작 서비스</h2>'
        '<div class="related-links">' +
        "".join('<a href="/industry/' + escape(x["id"]) + '/">' +
                escape(x["label"]) + ' 홈페이지 제작 <span aria-hidden="true">↗</span></a>'
                for x in group[:3]) +
        '</div></div></section>'
    )


def render_home(keywords: dict, pool: dict) -> str:
    sectors = [x for x in keywords["industries"] if x["launch"]]
    examples = "".join(
        '<div class="query-row"><span class="query-dot"></span><span>' + escape(x["query"]) +
        '</span><span class="query-arrow">↗</span></div>'
        for x in pool["examples"][:4]
    )
    steps = "".join(
        '<div class="step"><span class="step-number">' + f"{i:02d}" + '</span>'
        '<h3>' + escape(x["title"]) + '</h3>' + paragraph(x["text"]) + "</div>"
        for i, x in enumerate(pool["steps"][:3], 1)
    )
    sample_faq = "".join(
        '<details class="faq-item"><summary>' + escape(x["q"]) + '</summary>' +
        paragraph(x["a"]) + '</details>'
        for x in pool["faq"][:3]
    )
    body = (
        '<section class="hero"><div class="container hero-grid">'
        '<div class="hero-copy">' + kicker("지역 서비스업 홈페이지 제작") +
        '<h1>업종별 홈페이지 제작,<br><em>페이지당 월 1,000원부터.</em></h1>'
        '<p class="hero-lead">누수탐지, 하수구막힘, 이삿짐, 출장세차까지. '
        '지역 서비스업 사업자를 위한 홈페이지를 제작합니다. 최소 10페이지, 페이지당 월 1,000원으로 월 10,000원부터 이용할 수 있습니다. 업종별 고객 전용 홈페이지 주소 제공과 도메인 운영, 기본 서버 비용을 월 이용료에 포함합니다.</p>'
        '<div class="hero-actions">' + cta("제작 비용 상담하기") +
        secondary("업종별 구성 보기", "/#industries") + '</div>'
        '<div class="hero-note"><span>●</span> 검색 결과는 검색엔진의 평가와 검색 환경에 따라 달라집니다. 노출 시점과 순위도 검색어와 이용자 환경에 따라 달라질 수 있습니다. '
        '홈페이지는 검색에 필요한 구조와 고객이 찾는 정보를 갖춰 제작합니다.</div></div>'
        '<div class="hero-art">' + illustration("webbuilder-hero.webp", "PC와 스마트폰에서 보는 홈페이지 화면 예시", "hero-illustration") +
        '</div></div></section>'
        '<section class="stats-strip"><div class="container strip-grid">'
        '<div><strong>월 10,000원부터</strong><span>최소 10페이지 · 페이지당 월 1,000원</span></div>'
        '<div><strong>고객 전용 주소</strong><span>업종별 도메인 운영·기본 서버비 포함</span></div>'
        '<div><strong>지역 맞춤</strong><span>방문 가능 지역과 서비스 범위 반영</span></div>'
        '</div></section>'
        '<section id="industries" class="section"><div class="container">'
        '<div class="section-heading"><span class="eyebrow">업종별 홈페이지 제작</span>'
        '<h2>어떤 서비스를 제공하시나요?</h2>'
        '<p>업종마다 고객이 찾는 정보가 다릅니다. 각 서비스의 상담 내용과 이용 조건을 반영해 홈페이지를 구성합니다.</p>'
        '</div><div class="industry-categories">' + grouped_industry_cards(sectors) + '</div></div></section>'
        '<section class="section section-muted"><div class="container feature-grid">'
        '<div><span class="eyebrow">지역 검색에 필요한 정보</span><h2>지역명보다 중요한 건<br>고객이 찾는 답입니다.</h2>'
        + paragraph(pool["heroVariants"][2]) + paragraph(pool["localStrategyVariants"][0])
        + secondary("제작 절차 확인하기", "/guide/process/") +
        '</div><div class="feature-panel">' + illustration("local-search.webp", "지역별 서비스 정보를 살펴보는 화면 예시", "feature-illustration") +
        '<div class="feature-row"><b>01</b>'
        '<div><strong>방문 가능 지역</strong><span>실제 출장 가능한 시·군·구와 동 안내</span></div></div>'
        '<div class="feature-row"><b>02</b><div><strong>업종별 유용한 정보</strong>'
        '<span>가격 결정 요소, 상담 질문, 업무 범위</span></div></div>'
        '<div class="feature-row"><b>03</b><div><strong>검색·연락 구조</strong>'
        '<span>고유 제목, 모바일 화면, 전화 연결</span></div></div></div>'
        '</div></section>'
        '<section class="section"><div class="container"><div class="section-heading">'
        '<span class="eyebrow">제작 절차</span><h2>서비스에 맞춰 순서대로 제작합니다.</h2>'
        '</div><div class="step-grid">' + steps + '</div></div></section>'
        '<section class="section section-muted"><div class="container pricing-grid">'
        '<div><span class="eyebrow">월 이용료 안내</span><h2>페이지 수만큼<br>월 이용료를 계산하세요.</h2>'
        '<p>최소 10페이지, 페이지당 월 1,000원으로 월 10,000원부터 이용할 수 있습니다. 기본 홈페이지 제작, 고객 전용 주소 제공, 도메인 운영과 기본 서버 비용이 월 이용료에 포함됩니다. 부가세 적용 여부와 계약기간·수정 범위·주소 이용 조건은 계약 전에 안내합니다.</p>'
        + secondary("가격과 포함 범위", "/guide/pricing/") + '</div>'
        '<div class="price-panel">' + monthly_price_rows(pool, limit=3) +
        '</div>'
        '</div></section>'
        '<section class="section"><div class="container"><div class="section-heading">'
        '<span class="eyebrow">자주 묻는 질문</span><h2>제작 전에 알아둘 내용</h2></div>'
        '<div class="faq-list">' + sample_faq + '</div><div class="more-link">'
        '<a href="/guide/faq/">질문 전체 보기 ↗</a></div></div></section>'
    )
    return layout("업종별 홈페이지 제작 페이지당 월 1,000원부터 | 인터피아드",
                  "누수탐지, 하수구막힘, 이삿짐, 출장세차 등 지역서비스업 홈페이지. 페이지당 월 1,000원부터, 고객 전용 주소와 도메인 운영·서버비 포함. 인터피아드 010-2490-0555.",
                  body, active="home")

def render_sector(item: dict, data: dict, pool: dict, sectors: list[dict]) -> str:
    values = [data["intro"], data["problem"], data["structure"], data["conversion"], data["difference"]]
    heads = ["고객이 찾는 정보", "자주 묻는 상황", "홈페이지에 담을 내용",
             "상담에 필요한 정보", "서비스별 안내 포인트"]
    sections = "".join(
        '<section class="article-section"><span class="article-index">' + f"{i:02d}" +
        '</span><h2>' + escape(heads[i-1]) + '</h2>' + paragraph(value) + '</section>'
        for i, value in enumerate(values, 1)
    )
    checklist = "".join('<li>' + escape(x) + '</li>' for x in data["checklist"])
    sample_queries = "".join(
        '<li>' + escape(x) + '</li>'
        for x in item["exampleCustomerQueries"]
    )
    body = (
        '<section class="sub-hero"><div class="container narrow">'
        + kicker("업종별 홈페이지 제작") +
        '<h1>' + escape(data["title"]) + '<br><em>페이지당 월 1,000원부터.</em></h1>'
        '<p class="sub-lead">' + escape(item["consultingAngle"]) + '</p>'
        '<p class="small-note">최소 10페이지 월 10,000원부터 · 고객 전용 주소 제공·도메인 운영 및 기본 서버비 포함.</p><div class="hero-actions">'
        + cta(item["label"] + " 홈페이지 상담") + secondary("전체 업종 보기", "/#industries") +
        '</div></div></section>'
        '<section class="section"><div class="container article-layout">'
        '<article class="article">' + sections + '</article>'
        '<aside class="article-aside"><div class="aside-box"><span class="eyebrow">홈페이지에 담을 정보</span>'
        '<h2>상담 전에 확인할 내용</h2>' + illustration("industry-services.webp", "설비·청소·운송·설치 서비스 안내 이미지", "aside-illustration") +
        '<ul class="check-list">' + checklist + '</ul>'
        '<a class="aside-phone" href="tel:' + TEL + '">' + PHONE + ' 상담하기 ↗</a></div></aside>'
        '</div></section>'
        '<section class="section section-muted"><div class="container narrow">'
        '<span class="eyebrow">검색어 구성 예시</span>'
        '<h2>서비스 지역과 검색 의도에 맞춰 구성합니다.</h2>'
        '<ul class="keyword-chips">' + sample_queries + '</ul>'
        '<p class="small-note">업종명과 실제 서비스 지역을 조합한 검색어 예시입니다. 페이지에는 사업자가 제공하는 서비스와 방문 가능 지역을 반영합니다.</p>'
        '</div></section>' + related_industry_cards(item, sectors)
    )
    return layout(data["title"] + " 페이지당 월 1,000원부터 | 인터피아드",
                  item["label"] + " 홈페이지 제작 안내. " + item["consultingAngle"] +
                  ". 인터피아드 010-2490-0555.",
                  body)

def render_pricing(pool: dict) -> str:
    body = (
        '<section class="sub-hero"><div class="container narrow">' + kicker("제작 비용 안내") +
        '<h1>최소 10페이지, 월 10,000원부터.<br><em>고객 전용 주소·서버비 포함.</em></h1>'
        '<p class="sub-lead">페이지당 월 1,000원, 최소 10페이지부터 제작합니다. 업종과 서비스에 맞는 고객 전용 홈페이지 주소를 제공합니다. 기본 홈페이지 제작·도메인 운영·기본 서버 비용을 월 이용료에 포함합니다.</p>'
        '</div></section><section class="section"><div class="container narrow">'
        '<div class="price-panel full"><h2>페이지 수에 따른 월 이용료</h2>' + monthly_price_rows(pool) +
        illustration("managed-domain.webp", "홈페이지 화면 구성 예시", "price-illustration") +
        '<p class="small-note">홈페이지 화면 구성 예시입니다.</p>'
        '<p class="price-footnote">표의 금액은 페이지 수에 페이지당 월 1,000원을 적용한 기준 금액입니다.</p></div>'
        '<div class="article-section"><h2>페이지 수는 어떻게 정하나요?</h2>'
        + paragraph("20페이지는 월 20,000원, 30페이지는 월 30,000원입니다. 페이지 수는 사업자가 제공하는 서비스와 실제 영업 지역, 각 페이지에 담을 정보에 맞춰 정합니다. 서비스별 고객 질문과 별도 안내가 필요한 지역을 기준으로 구성을 상담합니다.")
        + '</div><div class="article-section"><h2>주소와 서버 운영은 어떻게 제공되나요?</h2>'
        + paragraph("기본 상품은 운영사가 관리하는 도메인 아래에 고객 전용 홈페이지 주소를 제공하는 방식입니다. 도메인 운영과 기본 서버 비용은 월 이용료에 포함됩니다. 주소 이용 기간, 계약 종료 후 처리와 소유권 조건은 계약 전에 안내합니다.")
        + '</div><div class="article-section"><h2>월 이용료에 포함되는 항목</h2>'
        + paragraph(pool["offerVariants"][0]) + paragraph(pool["offerVariants"][1]) +
        '</div><div class="article-section"><h2>계약 전에 확인할 조건</h2>'
        + paragraph("부가세 적용 여부, 계약기간, 수정 범위, 주소 이용 및 계약 종료 후 처리 조건은 계약 전에 안내합니다. 세부 내용은 상담과 계약서에서 확인할 수 있습니다.")
        + '</div></div></section>'
    )
    return layout("홈페이지 최소 10페이지 월 10,000원부터 비용 안내 | 인터피아드",
                  "업종별 홈페이지 페이지당 월 1,000원, 고객 전용 주소와 도메인 운영·서버비 포함. 10~100페이지 월 이용료 및 계약 조건을 안내합니다.",
                  body, "pricing")

def render_process(pool: dict) -> str:
    steps = "".join(
        '<div class="process-step"><span class="step-number">' + f"{i:02d}" + '</span>'
        '<div><h2>' + escape(x["title"]) + '</h2>' + paragraph(x["text"]) + '</div></div>'
        for i, x in enumerate(pool["steps"], 1)
    )
    body = (
        '<section class="sub-hero"><div class="container narrow">' + kicker("홈페이지 제작 과정") +
        '<h1>서비스와 지역을 정리해,<br><em>필요한 홈페이지를 만듭니다.</em></h1>'
        '<p class="sub-lead">고객이 찾는 정보와 사업자의 운영 범위를 반영해 페이지를 구성합니다.</p>'
        '</div></section><section class="section"><div class="container narrow process-list">'
        + steps + '<div class="article-section"><h2>검색 결과 확인 안내</h2>'
        + paragraph(pool["qualityVariants"][8]) +
        '</div></div></section>'
    )
    return layout("업종별 홈페이지 제작 과정 | 인터피아드",
                  "서비스 확인, 방문 가능 지역, 업종별 콘텐츠, 모바일 전화 연결과 공개 후 검색 상태 확인까지 홈페이지 제작 절차를 안내합니다.",
                  body, "process")

def render_faq(pool: dict) -> str:
    faq = "".join(
        '<details class="faq-item"><summary>' + escape(x["q"]) + '</summary>' +
        paragraph(x["a"]) + '</details>'
        for x in pool["faq"]
    )
    body = (
        '<section class="sub-hero"><div class="container narrow">' + kicker("제작 상담 전 확인") +
        '<h1>홈페이지 제작,<br><em>궁금한 내용을 확인하세요.</em></h1>'
        '<p class="sub-lead">월 이용료, 홈페이지 주소, 페이지 구성, 검색 결과와 운영 조건에 관한 질문을 안내합니다.</p>'
        '</div></section><section class="section"><div class="container narrow">'
        '<div class="faq-list">' + faq + '</div></div></section>'
    )
    return layout("홈페이지 제작 자주 묻는 질문 | 인터피아드",
                  "페이지당 월 1,000원 이용료, 고객 전용 주소·서버비 포함, 지역별 홈페이지와 검색 결과에 관한 질문을 안내합니다.",
                  body, "faq")

def grams(s: str) -> set[str]:
    clean = re.sub(r"\s+", "", s)
    return {clean[i:i+5] for i in range(max(0, len(clean) - 4))}


def export_keywords(keywords: dict, path: Path) -> int:
    count = 0
    seen = set()
    with path.open("w", encoding="utf-8-sig", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["type", "industry", "industry_id", "priority", "keyword", "meaning"])
        for sector in keywords["industries"]:
            priority = "launch" if sector["launch"] else "research_only"
            for template in keywords["buyerIntentTemplates"]:
                phrase = template.replace("{업종}", sector["label"])
                key = ("buyer", phrase)
                if key in seen:
                    continue
                seen.add(key)
                writer.writerow(["buyer", sector["label"], sector["id"], priority, phrase,
                                 "Homepage creation buyer intent; proposed, not search-volume tested"])
                count += 1
            for phrase in sector["exampleCustomerQueries"]:
                key = ("customer_example", phrase)
                if key in seen:
                    continue
                seen.add(key)
                writer.writerow(["customer_example", sector["label"], sector["id"], priority, phrase,
                                 "Future client keyword structure ONLY; verify real delivery area"])
                count += 1
    return count


def target_for_link(path: Path, href: str) -> Path | None:
    if not href.startswith("/") or href.startswith("//"):
        return None
    p = urlsplit(href).path
    if p == "/":
        return path / "index.html"
    if p.endswith("/"):
        return path / p.lstrip("/") / "index.html"
    return path / p.lstrip("/")


def visible_copy(source: str) -> str:
    without_scripts = re.sub(r"<script\b[^>]*>.*?</script>", " ", source, flags=re.I | re.S)
    without_styles = re.sub(r"<style\b[^>]*>.*?</style>", " ", without_scripts, flags=re.I | re.S)
    alts = " ".join(re.findall(r'\balt="([^"]*)"', without_styles))
    text = re.sub(r"<[^>]+>", " ", without_styles)
    return " ".join((html.unescape(text) + " " + html.unescape(alts)).split())


def copy_source_fingerprint() -> str:
    paths = [
        ROOT / "scripts" / "build_webbuilder.py",
        SITE / "copy-review-policy.json",
        SITE / "copy-pool.json",
        SITE / "industry-expansion-a.json",
        SITE / "industry-expansion-b.json",
        SITE / "keyword-pool.json",
    ]
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def audit_webbuilder_copy(pages: dict[str, str], expected: int, policy: dict) -> list[str]:
    errors = []
    sample_paths = policy.get("samplePaths", [])
    minimum = max(int(policy.get("minimumSampleCount", 1)),
                  math.ceil(expected * float(policy.get("minimumSampleRate", 0.01))))
    if len(sample_paths) < minimum:
        errors.append("manual review sample below 1% minimum")
    if len(sample_paths) != len(set(sample_paths)):
        errors.append("duplicate manual review sample path")
    for url_path in sample_paths:
        relative = "index.html" if url_path == "/" else url_path.strip("/") + "/index.html"
        if relative not in pages:
            errors.append("manual review sample missing " + url_path)
    for relative, source in pages.items():
        visible = visible_copy(source)
        for phrase in policy.get("forbiddenPhrases", []):
            if phrase in visible:
                errors.append(relative + ": forbidden customer copy phrase: " + phrase)
        for pattern in policy.get("forbiddenRegex", []):
            if re.search(pattern, visible, flags=re.I):
                errors.append(relative + ": forbidden customer copy pattern: " + pattern)
    for url_path, phrases in policy.get("requiredByPath", {}).items():
        relative = "index.html" if url_path == "/" else url_path.strip("/") + "/index.html"
        visible = visible_copy(pages.get(relative, ""))
        for phrase in phrases:
            if phrase not in visible:
                errors.append(relative + ": required customer disclosure missing: " + phrase)
    return errors


def check_output(out: Path, pages: dict[str, str], pool: dict, expected: int) -> dict:
    from v5.visitor_copy import audit_html_tree

    if len(pages) != expected or expected != 42:
        raise ValueError("Unexpected page count")
    errors = []
    policy = load("copy-review-policy.json")
    copy_errors = audit_webbuilder_copy(pages, expected, policy)
    errors.extend("Webbuilder copy gate " + item for item in copy_errors)
    titles = set()
    total_links = 0
    image_refs = 0
    for relative, source in pages.items():
        if '<meta name="robots" content="noindex,nofollow,noarchive">' not in source:
            errors.append("noindex missing " + relative)
        if "<link rel=\"canonical\"" in source or "sitemap.xml" in source:
            errors.append("preview indexing artifact " + relative)
        if f'href="tel:{TEL}"' not in source:
            errors.append("phone missing " + relative)
        if 'https://interpiad.com' not in source or "사업자 : 인터피아드" not in source:
            errors.append("business footer missing " + relative)
        ts = re.findall(r"<title>(.*?)</title>", source)
        hs = re.findall(r"<h1\b[^>]*>(.*?)</h1>", source, re.S)
        if len(ts) != 1 or len(hs) != 1 or ts[0] in titles:
            errors.append("title/H1 invalid " + relative)
        if ts:
            titles.add(ts[0])
        for claim in pool["restrictedClaims"]:
            if claim in source:
                errors.append("restricted claim found " + relative + ":" + claim)
        for src in re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', source):
            image_refs += 1
            img_path = out / src.lstrip("/")
            if not src.startswith("/assets/images/") or not img_path.is_file():
                errors.append("Missing original illustration: "+relative+" -> "+src)
        for href in re.findall(r'\bhref="([^"]+)"', source):
            dest = target_for_link(out, href)
            if dest is not None:
                total_links += 1
                if not dest.is_file():
                    errors.append("broken link " + relative + " -> " + href)
    source_dir = SITE / "illustrations" / "generated"
    art_out = out / "assets" / "images"
    provenance = json.loads((source_dir / "provenance.json").read_text(encoding="utf-8"))
    inventory = {x["fileName"]: x for x in provenance["assetRefs"]}
    if len(inventory) != 5 or {x.name for x in art_out.glob("*.webp")} != set(inventory):
        errors.append("Exactly five verified generated raster assets required")
    if list(art_out.glob("*.svg")):
        errors.append("Inactive SVG illustration leaked into preview")
    for name, info in sorted(inventory.items()):
        source_path = source_dir / name
        dest_path = art_out / name
        if not source_path.is_file() or not dest_path.is_file():
            errors.append("Missing generated image: "+name)
            continue
        raw = dest_path.read_bytes()
        if raw != source_path.read_bytes():
            errors.append("Raster build/source byte mismatch: "+name)
        if len(raw) != info["bytes"] or hashlib.sha256(raw).hexdigest() != info["sha256"]:
            errors.append("Generated raster SHA-256/size mismatch: "+name)
        try:
            dims = webp_dimensions(raw)
            if dims != (info["width"], info["height"]) or dims[0] < 768:
                errors.append("Raster dimensions mismatch or undersized: "+name+" "+str(dims))
        except ValueError as exc:
            errors.append("Invalid WebP asset: "+name+" "+str(exc))
    if image_refs < 50:
        errors.append("Expected generated raster images in homepage/industry sections")
    display_errors = audit_html_tree(out)
    if display_errors:
        errors.append("V5 visitor-copy gate " + str(display_errors))
    if (out / "sitemap.xml").exists():
        errors.append("preview sitemap prohibited")
    if (out / "robots.txt").read_text() != "User-agent: *\nDisallow: /\n":
        errors.append("robots.txt drift")
    narratives = {key: "".join(str(item.get(f, "")) for f in
                  ("intro", "problem", "structure", "conversion", "difference"))
                  for key, item in pool["industry"].items()}
    similarities = []
    for a, b in combinations(sorted(narratives), 2):
        ga, gb = grams(narratives[a]), grams(narratives[b])
        score = len(ga & gb) / len(ga | gb) if ga or gb else 0
        similarities.append((score, a, b))
    max_pair = max(similarities) if similarities else (0.0, None, None)
    if max_pair[0] >= .49:
        errors.append("Sector prose >=0.49 Jaccard: " + str(max_pair))
    fingerprint = copy_source_fingerprint()
    scorecard_path = SITE / policy.get("scorecardFile", "copy-review-scorecard.json")
    review_status = "PENDING_MANUAL_REVIEW"
    review_minimum_score = None
    live_verification = "UNVERIFIED"
    minimum_sample = max(int(policy.get("minimumSampleCount", 1)),
                         math.ceil(expected * float(policy.get("minimumSampleRate", 0.01))))
    if scorecard_path.is_file():
        scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
        samples = scorecard.get("samples", [])
        expected_paths = set(policy["samplePaths"])
        sample_paths = [x.get("path") for x in samples]
        scores = [int(x.get("score", 0)) for x in samples]
        rubric_ids = {x["id"] for x in policy["rubric"]}
        if scorecard.get("status") != "complete":
            errors.append("manual copy scorecard is not complete")
        if scorecard.get("totalDocuments") != expected:
            errors.append("manual copy scorecard document count mismatch")
        if len(samples) < minimum_sample or set(sample_paths) != expected_paths or len(sample_paths) != len(set(sample_paths)):
            errors.append("manual copy scorecard sample coverage mismatch")
        if scorecard.get("sourceFingerprint") != fingerprint:
            errors.append("manual copy scorecard source fingerprint is stale")
        if not scores or min(scores) < int(policy["scoreThreshold"]):
            errors.append("manual copy score below required threshold")
        for sample in samples:
            dimensions = sample.get("dimensions", {})
            if set(dimensions) != rubric_ids or sum(int(v) for v in dimensions.values()) != int(sample.get("score", -1)):
                errors.append("manual copy score breakdown mismatch: " + str(sample.get("path")))
            if sample.get("decision") != "PASS":
                errors.append("manual copy sample not passed: " + str(sample.get("path")))
            if sample.get("url") != DOMAIN + sample.get("path", ""):
                errors.append("manual copy sample URL mismatch: " + str(sample.get("path")))
        if not errors:
            review_status = "PASS_GENERATED_SOURCE"
            review_minimum_score = min(scores)
            live_verification = scorecard.get("liveVerification", "UNVERIFIED")
    if errors:
        raise ValueError("; ".join(errors[:8]))
    return {"pages": len(pages), "titleUnique": len(titles), "linksChecked": total_links,
            "imageFiles": 5, "imageReferences": image_refs, "imagesSource": "generated-raster-WebP-derived-from-3-original-PNGs",
            "brokenLinks": 0, "previewNoindex": True, "sitemap": False,
            "narrativePairsChecked": len(similarities),
            "narrativeMaxChar5GramJaccard": round(max_pair[0], 6),
            "maxPair": [max_pair[1], max_pair[2]],
            "pricingApproved": False, "baseOfferApproved": True, "billingCycle": "monthly",
            "minimumPages": 10, "minimumMonthlyKRW": 10000,
            "domainAndHostingIncluded": True, "domainModel": "provider-managed-multi-industry-domains",
            "candidateIndustryDomainsPurchased": False, "fullContractTermsConfirmed": False,
            "domainDeployed": False, "indexNowSubmitted": False,
            "copyToneAudit": "PASS", "copyToneFilesChecked": len(pages),
            "copyReviewStatus": review_status, "copyReviewSampleCount": len(policy["samplePaths"]),
            "copyReviewThreshold": int(policy["scoreThreshold"]),
            "copyReviewMinimumScore": review_minimum_score,
            "copyLiveVerification": live_verification, "copySourceFingerprint": fingerprint}


def build(out: Path = DEFAULT_OUTPUT, report: Path = DEFAULT_REPORT, mode: str = "preview") -> dict:
    if mode not in ("preview", "public"):
        raise ValueError("Unknown publication mode")
    spec, keywords, pool = require_source()
    out, report = out.resolve(), report.resolve()
    if out != DEFAULT_OUTPUT.resolve() or report != DEFAULT_REPORT.resolve():
        raise ValueError("Webbuilder build is restricted to its isolated dist/reports folders")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    report.mkdir(parents=True, exist_ok=True)
    sectors = [s for s in keywords["industries"] if s["launch"]]
    pages = {"index.html": render_home(keywords, pool)}
    for sector in sectors:
        pages[f'industry/{sector["id"]}/index.html'] = render_sector(
            sector, pool["industry"][sector["id"]], pool, sectors
        )
    pages["guide/pricing/index.html"] = render_pricing(pool)
    pages["guide/process/index.html"] = render_process(pool)
    pages["guide/faq/index.html"] = render_faq(pool)
    for relative, source in pages.items():
        dest = out / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(source + "\n", encoding="utf-8")
    (out / "404.html").write_text(layout("페이지를 찾을 수 없습니다 | 인터피아드",
        "요청하신 페이지를 찾을 수 없습니다.",
        '<section class="sub-hero"><div class="container narrow"><h1>찾으시는 페이지가 없습니다.</h1>'
        + secondary("홈으로 이동", "/") + '</div></section>') + "\n", encoding="utf-8")
    (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (out / "assets").mkdir(exist_ok=True)
    shutil.copy2(SITE / "site.css", out / "assets" / "site.css")
    images_out = out / "assets" / "images"
    images_out.mkdir(parents=True, exist_ok=True)
    for art in sorted((SITE / "illustrations" / "generated").glob("*.webp")):
        shutil.copy2(art, images_out / art.name)
    qa = check_output(out, pages, pool, spec["targetPageCount"])
    for example in pool["pricingFact"]["monthlyExamples"]:
        text = (out / "guide" / "pricing" / "index.html").read_text(encoding="utf-8")
        if (f'{example["pages"]}페이지 × 월 1,000원' not in text
                or f'월 {example["amountKRW"]:,}원' not in text):
            raise ValueError("Missing or incorrect monthly pricing for "+str(example["pages"]))
    home = (out / "index.html").read_text(encoding="utf-8")
    guide = (out / "guide" / "pricing" / "index.html").read_text(encoding="utf-8")
    faq = (out / "guide" / "faq" / "index.html").read_text(encoding="utf-8")
    if ('페이지당 월 1,000원부터' not in home
            or '최소 10페이지' not in home
            or '월 10,000원' not in home
            or '고객 전용 홈페이지 주소 제공' not in home
            or '도메인 운영과 기본 서버 비용' not in guide
            or '도메인 운영과 기본 서버 비용' not in faq):
        raise ValueError("Monthly minimum or customer-focused domain service messaging missing")
    for preview in out.rglob("*.html"):
        customer_html = preview.read_text(encoding="utf-8")
        if any(technical in customer_html for technical in
                ("*.leak119.net", "*.skycar24hr.com", "leak119.nalmada.net",
                 "구매·배정 전", "미배정", "Cloudflare", "worker.preview.js")):
            raise ValueError("Internal domain examples/implementation leaked into customer page: "+str(preview))
    qa["keywordCandidates"] = export_keywords(keywords, report / "keyword-candidates.csv")
    qa["launchIndustries"] = len(sectors)
    qa["researchIndustries"] = len(keywords["industries"]) - len(sectors)
    qa["extensionIndustries"] = 28
    qa["originalIndustriesPreserved"] = 10
    if mode == "public":
        urls = []
        for relative in pages:
            path = "/" if relative == "index.html" else "/" + relative.removesuffix("index.html")
            url = DOMAIN + path
            urls.append(url)
            dest = out / relative
            source = dest.read_text(encoding="utf-8")
            source = source.replace('content="noindex,nofollow,noarchive"', 'content="index,follow"', 1)
            source = source.replace("</head>", '<link rel="canonical" href="' + url + '"></head>', 1)
            if relative == "index.html":
                source = source.replace("</head>", '<meta name="naver-site-verification" content="1992f8e06229005ed7038234611e654b31db4dbf" /></head>', 1)
            dest.write_text(source, encoding="utf-8")
        (out / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + "".join("<url><loc>" + escape(url) + "</loc></url>" for url in urls)
            + "</urlset>\n", encoding="utf-8")
        (out / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + DOMAIN + "/sitemap.xml\n", encoding="utf-8")
    qa["sourceCommitMode"] = mode + " local build; deployment is separate"
    qa["previewNoindex"] = mode == "preview"
    qa["sitemap"] = mode == "public"
    (report / "qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qa


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--mode", choices=("preview", "public"), default="preview")
    a = parser.parse_args()
    print(json.dumps(build(a.output, a.report, a.mode), ensure_ascii=False, indent=2))
