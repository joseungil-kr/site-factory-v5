"""Todayflower-only customer-copy screening and deterministic 1% sample ledger.

The scores are machine-assisted prescreen results, not human editorial approval.
They cannot alone authorize a Cloudflare release.
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re

from v5.config import read_site, ROOT
from v5 import markup

SITE = "todayflower-nalmada"
ORIGIN = "https://todayflower.nalmada.net"
SAMPLE_N = 51
BAD = re.compile(
    r"보장하지 (?:않습니다|않아요)|약속하지 (?:않습니다|않아요)|"
    r"가정하지 마세요|단정하지 마세요|AI(?: 생성| 연출| 제작)|"
    r"미검증|검수용|미리보기용|확인되지 않은 상품|"
    r"법정동 코드는|출처는 2026년|증명하지 않습니다|"
    r"당일배송을 확정하는 화면이 아닙니다|"
    r"실제 상품 제작·배송 증빙이 아닙니다|"
    r"구 단위 주소 비교 관련 꽃|판매처 표시가 확인|"
    r"화분와|화환와|꽃다발와|을\(를\)"
)
PROMISE = re.compile(r"무조건 당일|당일배송 보장|전국 3시간|무료배송 확정|최저가 보장")

class VisitorText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "template"):
            self.skip += 1
        if not self.skip:
            for key, value in attrs:
                if key in ("alt","title","aria-label") and value:
                    self.parts.append(value)
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "template") and self.skip:
            self.skip -= 1
    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(data.strip())

def stable_key(page):
    return hashlib.sha256(("todayflower-copy-v2:"+page["id"]).encode()).digest()

def pick_sample(pages):
    selected = {}
    def add(p):
        selected[p["number"]] = p
    bynum={p["number"]:p for p in pages}
    for n in (1,2,3,28,29,34,403,405,2500,5071):
        add(bynum[n])
    provinces=sorted({p["region"].split()[0] for p in pages[33:]})
    for province in provinces:
        group=[p for p in pages[33:] if p["region"].split()[0]==province]
        add(min(group,key=stable_key))
    intents=sorted({p["topic"] for p in pages[33:]})
    for intent in intents:
        group=[p for p in pages[33:] if p["topic"]==intent]
        add(min(group,key=stable_key))
    for p in sorted(pages,key=stable_key):
        if len(selected)>=SAMPLE_N:
            break
        add(p)
    assert len(selected)==SAMPLE_N,(len(selected),len(provinces),len(intents))
    return sorted(selected.values(),key=lambda p:p["number"])

def score(p, html, catalog):
    parser=VisitorText();parser.feed(html)
    visible=" ".join(parser.parts)
    body=" ".join([p["intro"],p.get("sectionLead",""),
                   *[x["paragraph"] for x in p["sections"]],
                   *[f["a"] for f in p["faq"]]])
    natural=25;accuracy=30;helpful=30;repetition=15
    notes=[]
    if BAD.search(visible):
        natural-=12;notes.append("내부/방어형 표현 또는 잘못된 조사")
    if len(body)<350:
        natural-=5;notes.append("핵심 구매 안내가 짧음")
    if any(len(x["paragraph"])>1000 for x in p["sections"]):
        natural-=4;notes.append("긴 본문 단락")
    if PROMISE.search(visible):
        accuracy-=22;notes.append("근거 없는 배송/가격 보장")
    if re.search(r"법정동 코드는|출처는 2026년|실제 판매 증빙|가상 상품",visible):
        accuracy-=9;notes.append("고객에게 내부 증거를 노출")
    if not any(x in body for x in ("주소","수령")):
        helpful-=7;notes.append("받는 장소 정보 부족")
    if not any(x in body for x in ("상품번호","SKU","상품 상세")):
        helpful-=6;notes.append("상품 선택 연결 부족")
    if not all(x in html for x in ('href="tel:18440644"',
        'href="#products"','href="#order"')):
        helpful-=10;notes.append("전화·상품·주문 전환 링크 부족")
    productlinks=[x for x in p["productSkus"]
                  if ('https://fwith.co.kr/shop/item.php?it_id='+x) in html]
    if len(productlinks)!=len(p["productSkus"]):
        helpful-=12;notes.append("상품 직접 주문 링크 누락")
    if not any(x in html for x in ("원</p>","상품 상세에서 가격 확인")):
        helpful-=6;notes.append("상품 가격 또는 가격 확인 경로 누락")
    if not html.count('src="https://fwith.co.kr/data/item/flower379/'):
        helpful-=6;notes.append("실제 판매처 상품 이미지 누락")
    blocklist=[p["intro"],*[x["paragraph"] for x in p["sections"]],
               *[f["a"] for f in p["faq"]]]
    same=len(blocklist)-len(set(blocklist))
    if same:
        repetition-=min(10,4*same);notes.append("동일 문단 반복")
    if body.count("확인해 주세요")>6:
        repetition-=3;notes.append("확인 지시 과다")
    if body.count("알려주시면")>5:
        repetition-=4;notes.append("상담 권유 반복")
    if body.count("상품번호")>9:
        repetition-=3;notes.append("상품번호 반복 과다")
    for label,v in (("natural",natural),("accuracy",accuracy),
                    ("helpful",helpful),("repetition",repetition)):
        assert v>=0,(p["number"],label,v)
    categories={"natural":natural,"accuracy":accuracy,
                "helpful":helpful,"repetition":repetition}
    return categories,sum(categories.values()),notes

def main():
    data=read_site(SITE);pages=data["pages"]
    assert len(pages)==5070
    catalog={p["sku"]:p for p in data["products"]}
    selected=pick_sample(pages)
    root=ROOT/"dist"/SITE
    assert root.is_dir(),"Build before sample QA"
    rows=[]
    for page in selected:
        path="/" if page["number"]==1 else "/"+str(page["number"])+".html"
        name="index.html" if path=="/" else path[1:]
        html=(root/name).read_text(encoding="utf-8")
        cats,total,notes=score(page,html,catalog)
        rows.append({
            "number":page["number"],"url":ORIGIN+path,
            "province":page["region"].split()[0],
            "region":page["region"],"intent":page["topic"],
            "categories":cats,"score":total,
            "reason":notes or ["본문·상품·주문 정보에서 정량 선별 위험 없음"],
            "excerpt":{"title":page["title"],"intro":page["intro"],
                       "sections":[{"heading":s["heading"],"text":s["paragraph"]}
                                   for s in page["sections"]],
                       "faq":[{"q":f["q"],"a":f["a"]} for f in page["faq"]]},
        })
        print("TODAYFLOWER_SAMPLE_SCORE "+json.dumps({
          "url":ORIGIN+path,"score":total,
          "natural":cats["natural"],"accuracy":cats["accuracy"],
          "helpful":cats["helpful"],"repetition":cats["repetition"],
          "reason":notes},ensure_ascii=False),flush=True)
    report={
        "site":ORIGIN,"fullPopulation":len(pages),"sampleSize":len(rows),
        "stratifiedBy":["original sample","boundary","province","buyer intent"],
        "rubricMax":{"natural":25,"accuracy":30,"helpful":30,"repetition":15},
        "method":"mechanical prescreen, not independent human editorial score",
        "humanReadThrough":"PENDING","deployApproved":False,
        "firstPassAllAtLeast90":all(x["score"]>=90 for x in rows),
        "below90":[{"url":x["url"],"score":x["score"]} for x in rows if x["score"]<90],
        "results":rows
    }
    path=ROOT/"reports"/SITE/"customer-review-sample.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TODAYFLOWER_SAMPLE_SUMMARY "+json.dumps({
      "sample":len(rows),"min":min(r["score"] for r in rows),
      "max":max(r["score"] for r in rows),"below90":len(report["below90"]),
      "method":report["method"]},ensure_ascii=False))
    if report["below90"]:
        raise SystemExit("FAIL: 90-point prescreen threshold not met")
if __name__=="__main__":
    main()
