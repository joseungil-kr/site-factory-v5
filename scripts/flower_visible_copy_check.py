"""Fail the Nalmada Flower preview build on visible developer-status copy.

Check customer-facing text (including image alt/title), not HTML meta robots.
Technical QA and commercial provenance stay in JSON and GitHub reports.
"""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"dist/flower-funeral-national-preview"
FORBIDDEN=(
    r"검수용",r"공사\s*중",r"(?:사이트|페이지|상품\s*정보|서비스|콘텐츠|디자인)\s*(?:가\s*)?준비\s*중",r"미검증",r"(?:가격|상품|이미지|시설\s*정보|판매가)\s*미확정",
    r"보유\s*상품\s*사진",r"공통\s*상품\s*사진",
    r"실제\s*상품\s*구성은\s*달라질\s*수\s*있습니다",
    r"장례식장\s*건물\s*사진이\s*아닌",r"원장\s*(?:기재|기준)",
    r"참고\s*(?:가격|금액|가)",r"검색\s*제외",r"디자인\s*시안",
    r"사진\s*사용\s*예정",r"자리\s*표시자",r"상품\s*정보\s*준비",
)
PATTERNS=tuple(re.compile(x,re.I) for x in FORBIDDEN)

class VisibleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ignore=0
        self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in ("style","script","template","noscript"):
            self.ignore+=1
        if not self.ignore:
            for key,value in attrs:
                if key in ("alt","title","aria-label","placeholder") and value:self.parts.append(value)
    def handle_endtag(self,tag):
        if tag in ("style","script","template","noscript") and self.ignore:self.ignore-=1
    def handle_data(self,data):
        if not self.ignore and data.strip():self.parts.append(data)

def main():
    files=sorted(OUT.glob("*.html"))
    assert len(files)==1082, f"Expected 1080 facility + home + 404, found {len(files)}"
    issues={}
    for path in files:
        parser=VisibleParser()
        parser.feed(path.read_text(encoding="utf-8"))
        text=" ".join(parser.parts)
        bad=sorted({m.group(0) for pattern in PATTERNS for m in pattern.finditer(text)})
        if bad:issues[path.name]=bad
    if issues:
        for file,matches in list(issues.items())[:18]:
            print("VISITOR_COPY_FAIL",file,matches)
        raise SystemExit(f"{len(issues)} page(s) contain temporary/status copy")
    css=(OUT/"assets/css/site.css").read_text(encoding="utf-8")
    assert ".hero-visual img" in css and "object-fit:cover" in css
    assert ".product-card img" in css and "object-fit:cover" in css
    print("NALMADA_VISITOR_COPY_AND_IMAGE_FILL_PASS",len(files),"HTML pages")

if __name__=="__main__":
    main()
