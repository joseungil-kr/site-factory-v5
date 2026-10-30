#!/usr/bin/env python3
"""Webbuilder: deterministic, offline-only B2B website preview generator.

Uses V5's approved site-plan and visitor-copy gates, without touching shared
site engine, V4 operations, DNS, production Workers or indexing services.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
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
        '<h2>우리 업종의 검색 홈페이지를 설계해보세요.</h2>'
        '<p>실제 서비스와 가능한 지역을 알려주시면 문서 구성을 함께 검토합니다.</p></div>'
        + illustration("mobile-contact.svg", "모바일 전화 상담을 나타내는 원본 일러스트", "bottom-illustration") +
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


def illustration(file: str, description: str, css_class: str) -> str:
    dimensions = {"webbuilder-hero.svg": (1200, 760), "industry-services.svg": (1000, 680),
                  "local-search.svg": (1000, 680), "managed-domain.svg": (1000, 680),
                  "mobile-contact.svg": (1000, 680)}
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
    if len(group) < 3:
        group.extend(x for x in sectors if x["cluster"] != item["cluster"] and x["id"] != item["id"])
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
        '<div class="hero-copy">' + kicker("동네 검색을 이해하는 홈페이지 제작") +
        '<h1>업종별 검색 홈페이지,<br><em>페이지당 월 1,000원부터.</em></h1>'
        '<p class="hero-lead">누수탐지, 하수구막힘, 이삿짐, 출장세차까지. '
        '지역 서비스업 사장님을 위한 검색 홈페이지를 제작합니다. 최소 10페이지 월 10,000원부터 시작하며 업종별 도메인 확보·관리, 홈페이지 주소 제공, 서버비까지 포함합니다.</p>'
        '<div class="hero-actions">' + cta("제작 비용 상담하기") +
        secondary("업종별 구성 보기", "/#industries") + '</div>'
        '<div class="hero-note"><span>●</span> 검색엔진 노출·순위는 보장하지 않습니다. '
        '서비스 범위와 문서 품질을 먼저 확인합니다.</div></div>'
        '<div class="hero-art">' + illustration("webbuilder-hero.svg", "반응형 홈페이지와 스마트폰 원본 벡터 일러스트", "hero-illustration") +
        '</div></div></section>'
        '<section class="stats-strip"><div class="container strip-grid">'
        '<div><strong>월 10,000원부터</strong><span>최소 10페이지 · 페이지당 월 1,000원</span></div>'
        '<div><strong>도메인까지 관리</strong><span>업종 맞춤 주소 확보·관리 제공</span></div>'
        '<div><strong>지역 맞춤</strong><span>실제 서비스 범위에 맞춰 구성</span></div>'
        '</div></section>'
        '<section id="industries" class="section"><div class="container">'
        '<div class="section-heading"><span class="eyebrow">업종별 홈페이지 제작</span>'
        '<h2>어떤 일을 하시는 사장님인가요?</h2>'
        '<p>서로 다른 서비스를 같은 광고 문구로 채우지 않습니다. 업종의 고객 문의 흐름부터 분리합니다.</p>'
        '</div><div class="industry-categories">' + grouped_industry_cards(sectors) + '</div></div></section>'
        '<section class="section section-muted"><div class="container feature-grid">'
        '<div><span class="eyebrow">왜 지역 검색 페이지인가요?</span><h2>동 이름보다 중요한 건<br>고객이 찾는 답입니다.</h2>'
        + paragraph(pool["heroVariants"][2]) + paragraph(pool["localStrategyVariants"][0])
        + secondary("제작 절차 확인하기", "/guide/process/") +
        '</div><div class="feature-panel">' + illustration("local-search.svg", "지역 검색을 표현한 원본 벡터 지도", "feature-illustration") +
        '<div class="feature-row"><b>01</b>'
        '<div><strong>실제 서비스 지역</strong><span>방문 가능한 동·시 기준으로 안내</span></div></div>'
        '<div class="feature-row"><b>02</b><div><strong>업종별 유용한 정보</strong>'
        '<span>가격 결정 요소, 상담 질문, 업무 범위</span></div></div>'
        '<div class="feature-row"><b>03</b><div><strong>검색·연락 구조</strong>'
        '<span>고유 제목, 모바일 문서, 전화 버튼</span></div></div></div>'
        '</div></section>'
        '<section class="section"><div class="container"><div class="section-heading">'
        '<span class="eyebrow">제작 절차</span><h2>작게 검증하고, 필요한 만큼 확장합니다.</h2>'
        '</div><div class="step-grid">' + steps + '</div></div></section>'
        '<section class="section section-muted"><div class="container pricing-grid">'
        '<div><span class="eyebrow">월 이용료 안내</span><h2>페이지 수만큼<br>월 이용료를 계산하세요.</h2>'
        '<p>최소 10페이지 월 10,000원부터입니다. 기본 홈페이지 제작, 업종별 도메인 확보·관리, 고객 전용 주소와 서버 운영비를 포함합니다. 세부 이용 조건은 계약 전에 안내합니다.</p>'
        + secondary("가격과 포함 범위", "/guide/pricing/") + '</div>'
        '<div class="price-panel">' + monthly_price_rows(pool, limit=3) +
        '<p class="price-footnote">최소 10페이지부터 신청할 수 있습니다. 부가세·계약기간·수정 및 주소 이용 조건은 계약 전에 안내합니다.</p></div>'
        '</div></section>'
        '<section class="section"><div class="container"><div class="section-heading">'
        '<span class="eyebrow">자주 묻는 질문</span><h2>제작 전에 알아둘 내용</h2></div>'
        '<div class="faq-list">' + sample_faq + '</div><div class="more-link">'
        '<a href="/guide/faq/">질문 전체 보기 ↗</a></div></div></section>'
    )
    return layout("업종별 검색 홈페이지 페이지당 월 1,000원부터 | 인터피아드",
                  "누수탐지, 하수구막힘, 이삿짐, 출장세차 등 지역서비스업 홈페이지. 페이지당 월 1,000원부터, 운영사 업종별 도메인 제공·서버비 포함. 인터피아드 010-2490-0555.",
                  body, active="home")


def render_sector(item: dict, data: dict, pool: dict, sectors: list[dict]) -> str:
    values = [data["intro"], data["problem"], data["structure"], data["conversion"], data["difference"]]
    heads = ["고객이 실제로 궁금해하는 것", "지역 서비스 페이지에서 피할 실수",
             "홈페이지에 담을 고유한 정보", "문의로 연결되는 구성", "비슷한 검색어와 구별되는 점"]
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
    other = [x for x in pool["examples"] if x["industry"] == item["label"]]
    sample_note = escape(other[0]["point"]) if other else "업종별 고객 검색어 유형을 설명하기 위한 문구 예시입니다."
    body = (
        '<section class="sub-hero"><div class="container narrow">'
        + kicker("업종별 지역검색 홈페이지 제작") +
        '<h1>' + escape(data["title"]) + '<br><em>페이지당 월 1,000원부터.</em></h1>'
        '<p class="sub-lead">' + escape(item["consultingAngle"]) + ' 실제 제공 서비스를 기준으로 고객 질문과 상담 흐름을 설명하는 홈페이지를 설계합니다.</p>'
        '<p class="small-note">최소 10페이지 월 10,000원부터 · 업종별 도메인 확보·관리 및 서버비 포함.</p><div class="hero-actions">'
        + cta(item["label"] + " 홈페이지 상담") + secondary("전체 업종 보기", "/#industries") +
        '</div></div></section>'
        '<section class="section"><div class="container article-layout">'
        '<article class="article">' + sections + '</article>'
        '<aside class="article-aside"><div class="aside-box"><span class="eyebrow">사업자 확인 목록</span>'
        '<h2>실제 서비스 정보부터</h2>' + illustration("industry-services.svg", "설비·청소·운송·설치 서비스를 나타내는 원본 일러스트", "aside-illustration") +
        '<ul class="check-list">' + checklist + '</ul>'
        '<a class="aside-phone" href="tel:' + TEL + '">' + PHONE + ' 상담하기 ↗</a></div></aside>'
        '</div></section>'
        '<section class="section section-muted"><div class="container narrow">'
        '<span class="eyebrow">고객사 홈페이지에 적용할 키워드 형태</span>'
        '<h2>실제 서비스 지역을 확인한 뒤 문서화합니다.</h2>'
        '<ul class="keyword-chips">' + sample_queries + '</ul>'
        '<p class="small-note">' + sample_note +
        ' 이 키워드는 설명을 위한 문구 예시이며 검색량·순위 또는 해당 지역 업체의 존재를 보증하지 않습니다.</p>'
        '</div></section>' + related_industry_cards(item, sectors)
    )
    return layout(data["title"] + " 페이지당 월 1,000원부터 | 인터피아드",
                  item["label"] + " 사업자용 지역검색 홈페이지 제작. " + item["consultingAngle"] +
                  ". 인터피아드 010-2490-0555.",
                  body)


def render_pricing(pool: dict) -> str:
    body = (
        '<section class="sub-hero"><div class="container narrow">' + kicker("제작 비용 안내") +
        '<h1>최소 10페이지, 월 10,000원부터.<br><em>업종별 맞춤 주소·서버비 포함.</em></h1>'
        '<p class="sub-lead">페이지당 월 1,000원, 최소 10페이지부터 제작합니다. 업종별 맞춤 도메인을 확보하고 관리해 드리며, 기본 홈페이지 제작·주소 제공·서버 운영비까지 포함합니다.</p>'
        '</div></section><section class="section"><div class="container narrow">'
        '<div class="price-panel full"><h2>페이지 수에 따른 월 이용료</h2>' + monthly_price_rows(pool) +
        illustration("managed-domain.svg", "업종별 홈페이지 주소 관리를 나타내는 원본 일러스트", "price-illustration") +
        '<p class="price-footnote">최소 10페이지부터 신청 가능하며, 월 1,000원/페이지입니다. 계약기간·부가세·수정 및 홈페이지 주소 이용 조건은 상담 시 안내합니다.</p></div>'
        '<div class="article-section"><h2>한 도시의 모든 동도 같은 금액인가요?</h2>'
        + paragraph("시마다 동 개수는 서로 다릅니다. 20~30페이지를 이용하는 경우 월 2만~3만원이지만, 해당 시 전체 동을 반드시 같은 월 이용료로 구성할 수 있다는 뜻은 아닙니다. 실제 서비스 가능 지역과 페이지 구성을 확인해 필요한 수를 산정합니다.")
        + '</div><div class="article-section"><h2>도메인·서버 운영은 어떻게 하나요?</h2>'
        + paragraph("인터피아드가 업종별 맞춤 도메인을 확보하고 관리해 드립니다. 홈페이지 주소 제공 및 기본 서버 운영비가 월 이용료에 포함되어 고객이 도메인을 별도로 구매하실 필요가 없습니다. 제공 주소의 이용 기간과 소유권 등 세부 조건은 계약 전에 안내합니다.")
        + '</div><div class="article-section"><h2>제작단가가 낮을 수 있는 이유</h2>'
        + paragraph(pool["offerVariants"][0]) + paragraph(pool["offerVariants"][1]) +
        '</div></div></section>'
    )
    return layout("홈페이지 최소 10페이지 월 10,000원부터 비용 안내 | 인터피아드",
                  "업종별 홈페이지 페이지당 월 1,000원, 업종별 맞춤 주소와 서버비 포함. 10~100페이지 월 이용료 및 계약 조건을 안내합니다.",
                  body, "pricing")


def render_process(pool: dict) -> str:
    steps = "".join(
        '<div class="process-step"><span class="step-number">' + f"{i:02d}" + '</span>'
        '<div><h2>' + escape(x["title"]) + '</h2>' + paragraph(x["text"]) + '</div></div>'
        for i, x in enumerate(pool["steps"], 1)
    )
    body = (
        '<section class="sub-hero"><div class="container narrow">' + kicker("지역 서비스업 제작 과정") +
        '<h1>동네 검색에 필요한 정보를,<br><em>확인하고 나눠서 제작합니다.</em></h1>'
        '<p class="sub-lead">업종별 서비스 내용과 실제 영업 범위를 먼저 확인해 불필요한 유사 문서가 쌓이지 않도록 합니다.</p>'
        '</div></section><section class="section"><div class="container narrow process-list">'
        + steps + '<div class="article-section"><h2>검색 노출은 별도 검증 항목입니다.</h2>'
        + paragraph(pool["qualityVariants"][8]) +
        '</div></div></section>'
    )
    return layout("업종별 지역검색 홈페이지 제작 과정 | 인터피아드",
                  "업종 확인, 실제 서비스 가능 지역, 고유 콘텐츠, 모바일 전화 연결, 검색 상태 관측까지 지역 업체 홈페이지 제작 절차.",
                  body, "process")


def render_faq(pool: dict) -> str:
    faq = "".join(
        '<details class="faq-item"><summary>' + escape(x["q"]) + '</summary>' +
        paragraph(x["a"]) + '</details>'
        for x in pool["faq"]
    )
    body = (
        '<section class="sub-hero"><div class="container narrow">' + kicker("제작 상담 전 확인") +
        '<h1>홈페이지 제작과 검색 노출,<br><em>어디까지 가능한가요?</em></h1>'
        '<p class="sub-lead">가격, 서버, 도메인, 검색 결과와 실제 서비스 자료에 관한 자주 묻는 질문을 모았습니다.</p>'
        '</div></section><section class="section"><div class="container narrow">'
        '<div class="faq-list">' + faq + '</div></div></section>'
    )
    return layout("홈페이지 제작·SEO 자주 묻는 질문 | 인터피아드",
                  "페이지당 월 1,000원 이용료, 업종별 주소·서버비 포함, 지역별 홈페이지와 검색 노출에 대한 질문을 안내합니다.",
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


def check_output(out: Path, pages: dict[str, str], pool: dict, expected: int) -> dict:
    from v5.visitor_copy import audit_html_tree

    if len(pages) != expected or expected != 42:
        raise ValueError("Unexpected page count")
    errors = []
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
    from xml.etree import ElementTree
    art_names = {"webbuilder-hero.svg", "industry-services.svg", "local-search.svg",
                 "managed-domain.svg", "mobile-contact.svg"}
    art_out = out / "assets" / "images"
    if {x.name for x in art_out.glob("*.svg")} != art_names:
        errors.append("Original SVG asset count or filenames differ")
    for art in sorted(art_names):
        source_path = SITE / "illustrations" / art
        dest_path = art_out / art
        if not dest_path.is_file() or dest_path.read_bytes() != source_path.read_bytes():
            errors.append("Missing or modified original illustration "+art)
            continue
        raw_svg = dest_path.read_text(encoding="utf-8")
        if "<script" in raw_svg.lower():
            errors.append("Executable content in SVG "+art)
        try:
            svg_root = ElementTree.fromstring(raw_svg)
            if svg_root.tag != "{http://www.w3.org/2000/svg}svg":
                errors.append("Invalid namespace in SVG "+art)
            if int(svg_root.attrib.get("width", "0")) < 768:
                errors.append("SVG narrower than 768 "+art)
        except (ElementTree.ParseError, ValueError) as exc:
            errors.append("Invalid SVG XML "+art+": "+str(exc))
    if image_refs < 50:
        errors.append("Expected original illustrations across homepage and industry pages")
    display_errors = audit_html_tree(out)
    if display_errors:
        errors.append("V5 visitor-copy gate " + str(display_errors))
    if (out / "sitemap.xml").exists():
        errors.append("preview sitemap prohibited")
    if (out / "robots.txt").read_text() != "User-agent: *\nDisallow: /\n":
        errors.append("robots.txt drift")
    if errors:
        raise ValueError("; ".join(errors[:8]))
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
        raise ValueError("Sector prose >=0.49 Jaccard: " + str(max_pair))
    return {"pages": len(pages), "titleUnique": len(titles), "linksChecked": total_links,
            "imageFiles": 5, "imageReferences": image_refs, "imagesSource": "original-project-SVG",
            "brokenLinks": 0, "previewNoindex": True, "sitemap": False,
            "narrativePairsChecked": len(similarities),
            "narrativeMaxChar5GramJaccard": round(max_pair[0], 6),
            "maxPair": [max_pair[1], max_pair[2]],
            "pricingApproved": False, "baseOfferApproved": True, "billingCycle": "monthly",
            "minimumPages": 10, "minimumMonthlyKRW": 10000,
            "domainAndHostingIncluded": True, "domainModel": "provider-managed-multi-industry-domains",
            "candidateIndustryDomainsPurchased": False, "fullContractTermsConfirmed": False,
            "domainDeployed": False, "indexNowSubmitted": False}


def build(out: Path = DEFAULT_OUTPUT, report: Path = DEFAULT_REPORT) -> dict:
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
    for art in sorted((SITE / "illustrations").glob("*.svg")):
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
            or '최소 10페이지 월 10,000원' not in home
            or '도메인 확보·관리' not in home
            or '도메인을 확보하고 관리해 드립니다' not in guide
            or '도메인을 확보하고 관리해 드립니다' not in faq):
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
    qa["sourceCommitMode"] = "offline preview only"
    (report / "qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qa


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    a = parser.parse_args()
    print(json.dumps(build(a.output, a.report), ensure_ascii=False, indent=2))
