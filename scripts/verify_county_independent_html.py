"""Independent 95-file rendered HTML check; intentionally does not import
county_copy_pools extractors, purpose_render.assemble or the scoring rubric.

Checks the *actual* article[data-product-sku] cards against customer-visible
main-body prose, including SKU suffixes like B202는 and prices like 59,000원으로.
"""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from collections import Counter
import hashlib
import json
import re

from v5.config import ROOT

ID = "county-funeral-ownerprivate-test"
SKU = re.compile(r"(?<![A-Za-z0-9])B[0-9]{3}(?![0-9])")
PRICE = re.compile(r"(?<![0-9,])(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]{4,})원(?![0-9])")
VISUAL_REFERENCE = re.compile(r"(?:아래|위|옆|다음)\s*(?:에\s*있는\s*)?(?:그림|도형|이미지|사진)|(?:아래|위|다음)\s*자료\s*(?:에서|를)")
BAD = (
    "축하와 응원의 마음을 전하는 안내 서비스",
    "실물 상품 이미지를 사용할 권리는 아직 확인되지",
    "여기서 추측하지 않습니다",
    "비교을", "위치을", "명칭을을", "상품 선택을을",
    "네 상품만 비교한", "같은 등급으로 간주하지 않습니다",
    "현재 확보된 가격자료만으로 알 수 없습니다",
    "재확인한 법정동 코드", "이 명단은 배송 가능 여부의 확인 자료가 아니라", "현재 보유한 가격 원장",
    "형태 안내 이미지는 판매 상품 실물 사진과 차이가 있을 수 있습니다",
    "비교하는 안내입니다", "구분해 안내합니다",
    "고객의 연락처는 주문처에서 입력합니다",
)

class RenderedMain(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.main = False
        self.card = None
        self.pricing = False
        self.main_images = 0
        self.main_svgs = 0
        self.prose = []
        self.cards = []
        self.card_prices = {}
        self.links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "main" and a.get("id") == "main":
            self.main = True
        if not self.main:
            return
        if tag == "img":
            self.main_images += 1
        elif tag == "svg":
            self.main_svgs += 1
        if tag == "article" and a.get("data-product-sku"):
            self.card = a["data-product-sku"]
            self.cards.append(self.card)
            self.card_prices[self.card] = ""
        if tag == "p" and self.card is not None and "product-price" in a.get("class", "").split():
            self.pricing = True
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "p" and self.pricing:
            self.pricing = False
        if tag == "article" and self.card is not None:
            self.card = None
        if tag == "main":
            self.main = False

    def handle_data(self, data):
        if not self.main or not data.strip():
            return
        if self.card is None:
            self.prose.append(data.strip())
        elif self.pricing:
            self.card_prices[self.card] += data.strip()

def read(path: Path):
    text=path.read_text(encoding="utf-8")
    parsed=RenderedMain()
    parsed.feed(text)
    return text,parsed

def validate_one(path: Path, selected=None):
    html, doc=read(path)
    failures=[]
    if len(doc.cards) != len(set(doc.cards)) or not doc.cards:
        failures.append("Missing/duplicate product cards")
    if selected is not None and doc.cards != selected:
        failures.append(f"Card order differs from source {doc.cards} != {selected}")
    cards=set(doc.cards)
    prose=" ".join(doc.prose)
    visual_references=VISUAL_REFERENCE.findall(prose)
    if visual_references and doc.main_images + doc.main_svgs == 0:
        failures.append("Nonexistent inline visual reference: " + ", ".join(sorted(set(visual_references))))
    claimed=set(SKU.findall(prose))
    extra=sorted(claimed-cards)
    if extra:failures.append("Off-card SKU in actual visible HTML: "+",".join(extra))
    prices={}
    for sku,raw in doc.card_prices.items():
        amounts=PRICE.findall(raw)
        if len(amounts)!=1:
            failures.append(f"Card {sku} has {len(amounts)} prices: {raw!r}")
            continue
        prices[sku]=int(amounts[0].replace(",","").removesuffix("원"))
    allowed={f"{amount:,}원" for amount in prices.values()}
    allowed|={f"{abs(a-b):,}원" for a in prices.values() for b in prices.values() if a!=b}
    mentioned_prices={f"{int(v[:-1].replace(',','')):,}원" for v in PRICE.findall(prose)}
    unsupported=sorted(mentioned_prices-allowed)
    if unsupported:failures.append("Off-card price in actual visible HTML: "+",".join(unsupported))
    for phrase in BAD:
        if phrase in html:
            failures.append("Bad visitor copy: "+phrase)
    if prose.count('정확한 수령 시설 주소가 있으면') and prose.count('정확한 수령지 주소를 알려주시면'):
        failures.append('Repeated delivery-address instruction in rendered prose')
    # Audit the rendered navigation position rather than only the template.
    nav_marker='<nav aria-label="관련 지역">'
    if html.count(nav_marker)!=1 or html.find(nav_marker)>html.find('<section class="recommendations">'):
        failures.append("County navigation missing, duplicated or below product content")
    if "조의를 전하는 근조화환 상품·주문 안내" not in html:
        failures.append("County-only funeral footer missing")
    if 'name="robots" content="noindex,nofollow"' not in html:
        failures.append("Preview noindex absent")
    if 'rel="canonical"' in html:
        failures.append("Preview canonical present")
    if "실물 상품 사진" in html and "imageUseApproved" in html:
        failures.append("Internal image permission text leaked")
    for sku in cards:
        expected="https://fwith.co.kr/shop/item.php?it_id="+sku
        if expected not in doc.links:
            failures.append("Missing real seller order link for "+sku)
    return {
        "path":path.name,"cards":doc.cards,"visibleProseSKUs":sorted(claimed),
        "offCardSKUs":extra,"offCardPrices":unsupported,"cardPrices":prices,
        "proseCharacters":len(prose),"mainImages":doc.main_images,
        "mainSvgs":doc.main_svgs,"visualReferences":visual_references,
        "htmlSHA256":hashlib.sha256(html.encode("utf-8")).hexdigest(),
        "errors":failures,
    }

def scan_tree(root: Path, page_map:dict[int,list[str]]|None=None):
    htmls=sorted(root.glob("*.html"))
    numbered=[p for p in htmls if p.name=="index.html" or
              p.stem.isdigit() and 1<=int(p.stem)<=95]
    if len(numbered)!=95:
        raise AssertionError(("Expected 95 numbered HTML documents",len(numbered)))
    findings=[]
    for path in numbered:
        number=1 if path.name=="index.html" else int(path.stem)
        row=validate_one(path,page_map[number] if page_map else None)
        row["number"]=number
        findings.append(row)
    errors=[{"number":row["number"],"path":row["path"],"errors":row["errors"]}
            for row in findings if row["errors"]]
    report={
        "siteId":ID,"source":"independent rendered HTML parser",
        "pagesChecked":len(findings),"failedCount":len(errors),
        "failedPages":errors,"files":findings,
        "noPublicDeploy":True,
    }
    target=ROOT/"artifacts"/"v51-county-independent-html-audit.json"
    target.parent.mkdir(exist_ok=True,parents=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("COUNTY_INDEPENDENT_HTML_RESULT "+json.dumps({
      "pages":len(findings),"errors":len(errors),"failedPageNumbers":[e["number"] for e in errors]},ensure_ascii=False))
    if errors:
        raise AssertionError(("County rendered HTML semantic/catalog mismatch",errors[:18]))
    return report

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--dir",default=str(ROOT/"dist"/("unreleased-"+ID)))
    args=ap.parse_args()
    pages=json.loads((ROOT/"sites"/ID/"pages.json").read_text(encoding="utf-8"))
    scan_tree(Path(args.dir),{p["number"]:p["productSkus"] for p in pages})
