#!/usr/bin/env python3
"""Baeksefood 85-city, four-menu recipe transfer site generator.

430 noindex HTML pages. Reads pinned Site Factory V5 site-spec/city ledger,
original copy POOL, and five user-approved AI WebP images. No network/DNS/API
calls, and never silently enables search indexing or production deployment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import shutil
from collections import Counter
from html import escape
from pathlib import Path

from v5.site_plan import require_site_plan

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "sites/baekse"
OUT = ROOT / "dist/baekse"
REPORT = ROOT / "reports/baekse"
SOURCE_ASSETS = ROOT / "assets/library/baekse"
ASSET_ROOT = "/assets/baekse"
PHONE = "031-407-0103"
TEL = "tel:0314070103"
MENUS = {
    "dakhanmari":{"name":"닭한마리","image":"dakhanmari.webp","subtitle":"육수와 다데기, 닭 한 냄비 조리부터","verified":"백세푸드 공식 5일 집중 기술전수 과정이 안내되어 있습니다.","source":"https://baeksefood.com/academy/"},
    "dak-kalguksu":{"name":"닭칼국수","image":"dak-kalguksu.webp","subtitle":"기존 식당의 점심 메뉴·샵인샵 도입","verified":"백세푸드 공식 홈페이지에서 부메뉴·샵인샵 도입 방식이 안내되어 있습니다.","source":"https://baeksefood.com/blog/dak-kalguksu-startup/"},
    "sundaeguk":{"name":"순대국","image":"sundaeguk.webp","subtitle":"국물·순대·고명 조리 상담","verified":"교육 내용과 일정은 선택한 주방 여건에 따라 전화로 상담합니다.","source":"https://baeksefood.com/"},
    "someori":{"name":"소머리국밥","image":"kitchen-training.webp","subtitle":"고기 손질과 육수 조리 방식 검토","verified":"교육 내용과 일정은 선택한 주방 여건에 따라 전화로 상담합니다.","source":"https://baeksefood.com/"}
}
GROUPS = ("startup","kitchen","broth","ingredient","training","supply","mix","finance","market")
HEADINGS = {
    "startup":"창업 형태부터 결정하세요",
    "kitchen":"우리 매장 주방 동선",
    "broth":"육수의 맛과 반복 조리",
    "ingredient":"원재료 손질과 보관",
    "training":"조리법 전수교육 확인",
    "supply":"육수·소스 공급 선택",
    "mix":"기존 메뉴와 함께 운영",
    "finance":"원가와 실제 운영비",
    "market":"메뉴 도입 전 고객 검토",
    "menu":"메뉴별 전수 상담 포인트"
}
ASSETS = ["hero.webp","dakhanmari.webp","dak-kalguksu.webp","sundaeguk.webp","kitchen-training.webp"]

def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(s: str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def token(s: str):
    return sha(s)[:12]

def city_title(city: dict):
    if city["level"]=="metropolitan-city":
        return city["city"]
    return city["region"]+" "+city["city"]

def city_path(city: dict):
    return "/c/"+token(city_title(city))+".html"

def city_menu_path(city:dict,menu:str):
    return "/r/"+token(city_title(city)+"|"+menu)+"-"+menu+".html"

def menu_path(menu:str):
    return "/m/"+menu+".html"

def choose(rows:list,seed:str):
    return rows[int(sha(seed)[:16],16)%len(rows)]

def select_copy(pool:dict,city:dict,menu:str):
    key=city_title(city)+"|"+menu
    return [(HEADINGS[fam],choose(pool["families"][fam],key+"|"+fam)["copy"])
            for fam in GROUPS] + [(HEADINGS["menu"],choose(pool["menus"][menu],key+"|specific")["copy"])]

def asset(name):
    return ASSET_ROOT+"/"+name

def img(name,alt,priority=False):
    fetch=' fetchpriority="high"' if priority else ""
    loading="eager" if priority else "lazy"
    return (f'<img src="{asset(name)}" alt="{escape(alt,quote=True)}" '
            f'width="1280" height="720" loading="{loading}" decoding="async"{fetch}>')

def link(href,text,css=""):
    return f'<a class="{css}" href="{escape(href,quote=True)}">{escape(text)}</a>'

def head(title,description):
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
      '<meta name="viewport" content="width=device-width,initial-scale=1">'
      '<meta name="robots" content="noindex,nofollow">'
      f'<title>{escape(title)}</title>'
      f'<meta name="description" content="{escape(description,quote=True)}">'
      '<meta name="theme-color" content="#faf7f0">'
      '<link rel="stylesheet" href="/assets/site.css">'
      '</head><body>')

def header():
    return ('<header class="site-header"><div class="wrap nav">'
      '<a class="brand" href="/">백세푸드<small>RECIPE TRANSFER · FOOD BUSINESS</small></a>'
      '<nav class="navlinks" aria-label="메뉴"><a href="/m/dakhanmari.html">닭한마리</a>'
      '<a href="/m/dak-kalguksu.html">닭칼국수</a><a href="/m/sundaeguk.html">순대국</a>'
      '<a href="/m/someori.html">소머리국밥</a></nav>'
      f'<a class="cta" href="{TEL}">전수 상담 {PHONE}</a>'
      '</div></header>')

def footer():
    return ('<footer class="site-footer"><div class="wrap footer-grid"><div>'
      '<strong>백세푸드 · 레시피 기술전수·창업 상담</strong>'
      f'<small>문의 {PHONE} · 전수·식자재 상담</small>'
      '<small>기술전수 과정과 교육 장소, 메뉴별 지원 조건은 유선으로 상담해 주세요.</small>'
      '</div><nav aria-label="하단메뉴">'
      '<a href="/">홈</a><a href="/m/dakhanmari.html">닭한마리</a>'
      '<a href="/m/dak-kalguksu.html">닭칼국수</a><a href="/m/sundaeguk.html">순대국</a>'
      '<a href="/m/someori.html">소머리국밥</a>'
      '<a href="https://baeksefood.com/academy/" rel="noopener">공식 전수교육</a></nav></div></footer></body></html>')

def consult(menu=None):
    name=MENUS[menu]["name"] if menu else "국물메뉴"
    return ('<section class="section"><div class="consult"><div>'
      '<h2>내 매장에 맞는 '+name+' 창업, 전화로 상담하세요</h2>'
      '<p>기존 매장 여부와 관심 메뉴, 사용 가능한 주방 시설을 알려주시면 상담에 도움이 됩니다.</p>'
      '</div>'+link(TEL,PHONE+" 전화 상담","cta")+'</div></section>')

def menu_cards(current=None):
    cards=[]
    for key,obj in MENUS.items():
        cards.append('<article class="card"><div class="photo">'+img(obj["image"],obj["name"]+" 메뉴를 표현한 이미지")+'</div>'
          '<div class="details"><h3>'+escape(obj["name"])+' 전수·창업</h3>'
          '<p>'+escape(obj["subtitle"])+'</p>'
          +link(menu_path(key),"자세히 알아보기","more")+'</div></article>')
    return '<div class="grid">'+"".join(cards)+'</div>'

def breadcrumbs(parts):
    return '<div class="wrap breadcrumbs"><a href="/">홈</a>'+''.join(
        '<span>›</span>'+link(path,label) for label,path in parts)+'</div>'

def menus_block():
    return '<section class="section"><div class="wrap"><span class="eyebrow">FOUR MENUS</span><h2>전수·창업을 상담하는 네 가지 메뉴</h2><p class="intro">기존 식당 메뉴 추가부터 독립 상호의 창업까지, 메뉴별 조리 과정과 운영 형태를 함께 검토합니다.</p>'+menu_cards()+'</div></section>'

def city_directory(cities):
    grouped={}
    for c in cities:
        grouped.setdefault(c["region"],[]).append(c)
    ordered=sorted(grouped.items(),key=lambda x:(0 if x[0] in (
      "서울특별시","부산광역시","대구광역시","인천광역시","대전광역시",
      "울산광역시","세종특별자치시","전남광주통합특별시") else 1,x[0]))
    parts=['<section class="section alt"><div class="wrap"><span class="eyebrow">NATIONWIDE CITIES</span>'
           '<h2>전국 시 단위 전수·창업 상담 지역</h2><p class="intro">'
           '군·구·동·읍·면은 별도 페이지로 만들지 않았습니다. 원하는 도시를 선택해 메뉴별 상담 내용을 확인할 수 있습니다.</p>']
    for region,group in ordered:
        parts.append('<div class="city-group"><h3>'+escape(region)+'</h3><div class="city-list">')
        for item in group:
            parts.append(link(city_path(item),item["city"]))
        parts.append('</div></div>')
    return "".join(parts)+'</div></section>'

def render_home(cities):
    title="백세푸드 닭한마리·닭칼국수·순대국·소머리국밥 전수 창업"
    home_head=head(title,title+" 및 전국 시 단위 창업 상담. "+PHONE)
    verification='<meta name="naver-site-verification" content="3203fa257fed369e603424067cbfab1f2611638b" />'
    assert home_head.count("</head>")==1 and verification not in home_head
    home_head=home_head.replace("</head>",verification+"</head>",1)
    content=[home_head,header()]
    content.append('<main><div class="wrap hero"><div><span class="eyebrow">BAEKSE FOOD · RECIPE TRANSFER</span>'
      '<h1>'+escape(title)+'</h1>'
      '<p>닭한마리·닭칼국수·순대국·소머리국밥 메뉴를 검토하는 예비 창업자와 기존 식당을 위한 전수 상담입니다. '
      '육수와 조리 과정, 주방 여건부터 식자재 공급 방식까지 함께 살펴보세요.</p>'
      '<div class="hero-action">'+link(TEL,"031-407-0103 전수 상담","cta")
      +link("/m/dakhanmari.html","전수교육 내용 보기","cta light")+'</div>'
      '<div class="hero-trust">독립 상호 · 기존 매장 메뉴 추가 · 전국 시 단위 문의</div></div>'
      '<div class="hero-image">'+img("hero.webp","닭한마리와 국물 메뉴를 함께 표현한 이미지",True)+'</div></div>')
    content.append(menus_block())
    content.append('<section class="section alt"><div class="wrap"><span class="eyebrow">HOW TO START</span>'
      '<h2>상담부터 조리 준비까지</h2><p class="intro">메뉴와 매장 형태에 맞는 진행 방법을 확인하세요.</p>'
      '<div class="steps"><article class="step"><span class="num">01</span><strong>운영 형태 확인</strong><p>신규 창업·기존 매장·독립 상호 중 원하는 형태를 정리합니다.</p></article>'
      '<article class="step"><span class="num">02</span><strong>메뉴·주방 상담</strong><p>조리 메뉴와 화구, 보관 설비, 필요한 교육 과정을 확인합니다.</p></article>'
      '<article class="step"><span class="num">03</span><strong>기술전수·공급 협의</strong><p>교육 범위와 일정, 필요한 육수·소스 공급 방식을 상담합니다.</p></article></div></div></section>')
    content.append(city_directory(cities))
    content.append('<div class="wrap">'+consult()+'</div></main>')
    content.append(footer())
    return "".join(content)

def render_menu(key,cities,pool):
    menu=MENUS[key]
    title=menu["name"]+" 레시피 전수·창업 안내"
    intro=menu["verified"]
    desc=menu["name"]+" 기술전수 및 기존 식당 메뉴 추가 상담. "+PHONE
    parts=[head(title+" | 백세푸드",desc),header(),breadcrumbs([("메뉴 안내",menu_path(key))]),
       '<main><div class="wrap hero"><div><span class="eyebrow">RECIPE TRANSFER</span><h1>'+escape(title)+'</h1>'
       '<p>'+escape(intro)+' 주방 동선과 조리 방식, 기존 메뉴와의 조합을 함께 검토하세요.</p>'
       '<div class="hero-action">'+link(TEL,PHONE+" 상담","cta")+'</div></div>'
       '<div class="hero-image">'+img(menu["image"],menu["name"]+" 조리 메뉴 이미지",True)+'</div></div>',
       '<section class="section alt"><div class="wrap"><h2>메뉴를 도입할 때 점검할 내용</h2>'
       '<div class="copy-grid">']
    index=0
    for fam in ("broth","training","supply","finance"):
        row=pool["families"][fam][(index*3+len(key))%len(pool["families"][fam])]
        parts.append('<article class="copy-block"><h3>'+escape(HEADINGS[fam])+'</h3><p>'+escape(row["copy"])+'</p></article>')
        index+=1
    parts.append('</div></div></section>')
    parts.append('<section class="section"><div class="wrap"><h2>시 단위 상담 지역</h2><p class="intro">해당 도시의 기존 매장·창업 계획에 맞는 상담 안내로 이동합니다.</p>'
                 '<div class="city-list">')
    parts.extend(link(city_menu_path(c,key),city_title(c)) for c in cities)
    parts.append('</div></div></section>')
    parts.append('<div class="wrap">'+consult(key)+'</div></main>')
    parts.append(footer())
    return "".join(parts)

def render_city(city):
    name=city_title(city)
    title=name+" 국물메뉴 레시피 전수·창업 상담"
    desc=name+" 닭한마리·닭칼국수·순대국·소머리국밥 기술전수 및 창업 상담. "+PHONE
    parts=[head(title+" | 백세푸드",desc),header(),breadcrumbs([(name,city_path(city))]),
       '<section class="subhero"><div class="wrap"><span class="eyebrow">CITY GUIDE</span>'
       '<h1>'+escape(title)+'</h1>'
       '<p>'+escape(name)+'에서 식당을 운영하거나 창업을 고려한다면, 관심 메뉴와 주방 여건을 정리한 뒤 백세푸드에 상담해 보세요. '
       '전수 프로그램과 교육 장소는 메뉴별 상담으로 안내합니다.</p></div></section>',
       '<main><div class="wrap"><section class="section"><h2>관심 메뉴 선택</h2><div class="grid">']
    for key,obj in MENUS.items():
        parts.append('<article class="card"><div class="photo">'+img(obj["image"],obj["name"]+" 메뉴 이미지")+'</div><div class="details">'
                     '<h3>'+escape(name+" "+obj["name"]+" 전수")+'</h3>'
                     '<p>'+escape(obj["subtitle"])+'</p>'+link(city_menu_path(city,key),"메뉴 상담 보기","more")+'</div></article>')
    parts.append('</div></section>'+consult()+'</div></main>'+footer())
    return "".join(parts)

def render_city_menu(city,key,pool):
    name=city_title(city)
    obj=MENUS[key]
    title=name+" "+obj["name"]+" 레시피 전수·창업 상담"
    description=name+"에서 "+obj["name"]+" 레시피 전수와 창업을 고민하신다면 조리·원료 공급·매장 조건부터 확인해 보세요. "+PHONE
    selected=select_copy(pool,city,key)
    parts=[head(title+" | 백세푸드",description),header(),
           breadcrumbs([(name,city_path(city)),(obj["name"],city_menu_path(city,key))]),
           '<main><div class="wrap hero"><div><span class="eyebrow">CITY × MENU</span><h1>'+escape(title)+'</h1>'
           '<p>'+escape(description)+'</p>'
           '<div class="hero-action">'+link(TEL,PHONE+" 전수 상담","cta")
           +link(menu_path(key),obj["name"]+" 과정 살펴보기","cta light")+'</div>'
           '<div class="hero-trust">기술전수 · 기존 식당 메뉴 추가 · 독립 상호 창업 상담</div></div>'
           '<div class="hero-image">'+img(obj["image"],obj["name"]+"를 표현한 이미지",True)+'</div></div>',
           '<section class="section alt"><div class="wrap"><span class="eyebrow">PRACTICAL CHECKLIST</span>'
           '<h2>'+escape(name)+" "+escape(obj["name"])+" 창업 준비 체크"+'</h2>'
           '<p class="intro">판매 장소와 조리 시설이 정해지면 교육 내용과 실제 운영 방식을 보다 구체적으로 상담할 수 있습니다.</p>'
           '<div class="copy-grid">']
    for section,paragraph in selected:
        parts.append('<article class="copy-block"><h3>'+escape(section)+'</h3><p>'+escape(paragraph)+'</p></article>')
    parts.append('</div></div></section>')
    parts.append('<section class="section"><div class="wrap menu-banner">'
                 '<div>'+img("kitchen-training.webp","국물요리 조리 실습을 표현한 이미지")+'</div>'
                 '<div class="content"><span class="eyebrow">TRAINING & SUPPLY</span>'
                 '<h2>교육과 식자재 공급 방식</h2>'
                 '<p>'+escape(obj["verified"])+' 문의 시 메뉴 종류, 보유한 주방시설, 기존 매장 운영 여부를 알려주세요.</p>'
                 +link(TEL,PHONE+" 문의하기","cta")+'</div></div></section>')
    # Unique visible FAQ ties the user intent to each city+menu.
    faqs=[
      ("어디에서 교육을 받을 수 있나요?",obj["verified"]+" 상세 교육 장소와 방식은 백세푸드 전수 담당자에게 확인해 주세요."),
      ("기존 식당에 메뉴만 추가할 수 있나요?","기존 주방의 화구와 원료 보관 여건을 검토해 메뉴 추가가 적합한지 상담할 수 있습니다."),
      ("창업 비용과 전수료는 어떻게 안내받나요?","매장 유형과 메뉴별 전수 범위에 따라 달라질 수 있으므로 "+PHONE+"으로 문의해 주세요."),
    ]
    parts.append('<section class="section"><div class="wrap"><h2>자주 묻는 질문</h2><div class="faqs">')
    for q,a in faqs:parts.append('<details><summary>'+escape(q)+'</summary><p>'+escape(a)+'</p></details>')
    parts.append('</div></div></section>')
    parts.append('<section class="section"><div class="wrap"><h2>다른 메뉴도 비교해 보세요</h2><div class="city-list">')
    for other in MENUS:
        if other!=key:parts.append(link(city_menu_path(city,other),name+" "+MENUS[other]["name"]))
    parts.append(link(city_path(city),name+" 메뉴 전체보기"))
    parts.append('</div></div></section>')
    parts.append('<div class="wrap">'+consult(key)+'</div></main>'+footer())
    return "".join(parts), "\n".join(p for _,p in selected)

def quality_gram(text):
    text=re.sub(r"\s+","",text)
    return {text[i:i+5] for i in range(len(text)-4)}

def audit_similar(narratives,threshold=0.49):
    rows=sorted(narratives.items())
    sample_size=max(4,math.ceil(len(rows)*.01))
    rng=random.Random(20261030)
    picks=rng.sample(rows,sample_size)
    grams=[quality_gram(s) for path,s in rows]
    idx={p:i for i,(p,_) in enumerate(rows)}
    worst={"value":0.0,"a":None,"b":None}
    checked=0;fails=0
    for path,_ in picks:
        source=grams[idx[path]]
        for (other,_),second in zip(rows,grams):
            if path==other:continue
            sim=len(source & second)/len(source | second)
            checked+=1
            if sim>=threshold:fails+=1
            if sim>worst["value"]:worst={"value":round(sim,6),"a":path,"b":other}
    return {"metric":"char-5gram-jaccard","thresholdExclusive":threshold,
       "sampleCount":sample_size,"population":len(rows),"comparisons":checked,
       "max":worst,"aboveThreshold":fails,"passed":fails==0,
       "limitation":"1% fixed sample versus all, not exhaustive all-pairs nor guaranteed search ranking"}

def build(out=OUT,report=REPORT,allow_missing_assets=False):
    require_site_plan("baekse")
    spec=read(SITE/"site-spec.json")
    source=read(SITE/"cities.json")
    pool=read(SITE/"copy-pool.json")
    media=read(SITE/"images-manifest.json")
    cities=source["cities"]
    assert spec["targetPageCount"]==430
    assert len(cities)==85 and len(set(city_title(c) for c in cities))==85
    assert len([c for c in cities if c["level"]=="metropolitan-city"])==8
    assert all(c["city"].endswith("시") and not c["city"].endswith(("군","구","동","읍","면")) for c in cities)
    assert pool["copyCount"]==104 and len(media["assets"])==5
    if out.exists():shutil.rmtree(out)
    out.mkdir(parents=True)
    pages={}; narratives={}
    def add(route,title,body,page_type):
        if route in pages:raise AssertionError("Duplicate route "+route)
        if '<meta name="robots" content="noindex,nofollow">' not in body:raise AssertionError("Preview not noindex "+route)
        if 'rel="canonical"' in body:raise AssertionError("Preview unexpected canonical")
        if PHONE not in body or TEL not in body:raise AssertionError("Contact missing "+route)
        forbidden=["매출 보장","월 순이익 보장","현지 직영 매장","상권 1위","수료자 후기"]
        if any(x in body for x in forbidden):raise AssertionError("Unsupported marketing claim "+route)
        path=out/("index.html" if route=="/" else route.lstrip("/"))
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(body,encoding="utf-8",newline="\n")
        pages[route]={"pageType":page_type,"bytes":path.stat().st_size,
                      "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"title":title}
    add("/","home",render_home(cities),"home")
    for key in MENUS:
        add(menu_path(key),key,render_menu(key,cities,pool),"menu-guide")
    for c in cities:
        add(city_path(c),city_title(c),render_city(c),"city-hub")
        for key in MENUS:
            page,narr=render_city_menu(c,key,pool)
            route=city_menu_path(c,key)
            add(route,city_title(c)+" "+MENUS[key]["name"],page,"city-menu")
            narratives[route]=narr
    assert len(pages)==430 and len(narratives)==340
    # Every internal href is a known generated route.
    hrefs=set()
    for f in out.rglob("*.html"):
        body=f.read_text(encoding="utf-8")
        hrefs.update(re.findall(r'<a[^>]+href="([^"]+)"',body))
    missing={x for x in hrefs if x.startswith("/") and x not in pages}
    assert not missing,("Broken internal targets",list(missing)[:10])
    titles=[]
    descriptions=[]
    for p in out.rglob("*.html"):
        body=p.read_text(encoding="utf-8")
        title=re.search(r"<title>(.*?)</title>",body,re.S)
        meta=re.search(r'<meta name="description" content="([^"]+)"',body)
        assert title and meta,p
        titles.append(title.group(1));descriptions.append(meta.group(1))
    assert len(set(titles))==430 and len(set(descriptions))==430
    (out/"assets").mkdir(exist_ok=True)
    shutil.copyfile(SITE/"theme.css",out/"assets/site.css")
    copied=[]
    for meta in media["assets"]:
        src=ROOT/meta["path"]
        if not src.is_file():
            if not allow_missing_assets:raise FileNotFoundError("Missing required actual image: "+str(src))
            continue
        binary=src.read_bytes()
        assert binary[:4]==b"RIFF" and binary[8:12]==b"WEBP",meta["filename"]
        assert hashlib.sha256(binary).hexdigest()==meta["sha256"] and len(binary)==meta["bytes"]
        target=out/"assets/baekse"/meta["filename"]
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,target)
        assert hashlib.sha256(target.read_bytes()).hexdigest()==meta["sha256"]
        copied.append(meta["filename"])
    (out/"robots.txt").write_text("User-agent: *\nDisallow: /\n",encoding="utf-8")
    (out/"404.html").write_text('<!doctype html><html lang="ko"><head><meta name="robots" content="noindex,nofollow"><title>페이지를 찾을 수 없습니다</title></head><body><main><h1>페이지를 찾을 수 없습니다</h1><p><a href="/">백세푸드 홈으로</a></p></main></body></html>',encoding="utf-8")
    assert not (out/"sitemap.xml").exists()
    similarity=audit_similar(narratives)
    audit={"site":"baekse","status":"PASS" if similarity["passed"] and len(copied)==5 else ("CONTENT_ONLY_PASS_IMAGES_NOT_UPLOADED" if similarity["passed"] else "FAIL"),
           "sitePages":len(pages),"cityNames":len(cities),"cityMenuPages":len(narratives),
           "pageTypes":dict(Counter(x["pageType"] for x in pages.values())),
           "uniqueTitles":len(set(titles)),"uniqueDescriptions":len(set(descriptions)),
           "imageOriginalCount":len(media["assets"]),"imagesCopiedAndShaVerified":copied,
           "missingImages":sorted(set(ASSETS)-set(copied)),
           "internalBrokenLinks":len(missing),"previewNoindex":True,"sitemapNotPublic":True,
           "copyPool":pool["copyCount"],"similarity":similarity,
           "publicReleaseAllowed":False,"operationalDeployment":False,
           "regionScope":"only 85 city names, 8 metropolitan/special and 77 basic/administrative (including former Jeonnam five cities); no county/district/town/neighborhood URLs",
           "limit":"Technical and lexical QA is not evidence of city-specific sales, training venue, or search indexing."}
    report.mkdir(parents=True,exist_ok=True)
    (report/"audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (report/"manifest.json").write_text(json.dumps({"site":"baekse","count":len(pages),"pages":pages},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"count":len(pages),"cityMenu":len(narratives),
        "copyPool":pool["copyCount"],"imageFiles":len(copied),"similarity":similarity,
        "status":audit["status"]},ensure_ascii=False))
    assert similarity["passed"],"City menu narratives violate 49% lexical similarity gate"
    return audit

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=OUT)
    parser.add_argument("--report",type=Path,default=REPORT)
    parser.add_argument("--allow-missing-assets",action="store_true",
        help="Text/HTML-only QA in GitHub until user-approved 5 WebP files are committed; never for public release")
    args=parser.parse_args()
    build(args.out,args.report,args.allow_missing_assets)
