"""Deterministic 1%+ semantic copy review evidence for the production 310 Skyquote URLs.

Reviewer scores must be entered separately after reading these complete customer-visible
paragraphs and actual browser screenshots. This tool does not automatically award 90 points.
"""
from pathlib import Path
from html.parser import HTMLParser
from html import unescape
import hashlib,json,math,re,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/"dist/skyquote-public"
REPORT=ROOT/"reports/skyquote-copy"
ORIGIN="https://skyquote.nalmada.net"
BAN=[
  "AI 생성 설명 이미지", "실제 시공·장비 보유 증명이 아닙니다",
  "업계 최저가를 주장하지 않습니다", "보장하지 않습니다",
  "차량 톤수만으로 작업 가능성을 보장하지 않습니다",
  "실수를 피할 수 있습니다", "단정하지 마세요", "기재합니다",
  "실제 환경을 조사한 결과가 아닌 견적용 가정",
  "코드 원장에 존재하는 지역입니다", "영업지점을 증명하지 않습니다",
  "전국 출동 가능을 뜻하지 않습니다", "서울·경기 원장 두 자료",
]
class Reader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip=0;self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in ("style","script","head"):
            self.skip+=1
        if not self.skip and tag in ("p","h1","h2","h3","li","td","th","summary","figcaption"):
            self.parts.append("\n")
    def handle_endtag(self,tag):
        if tag in ("style","script","head"):
            self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if self.skip==0:
            stripped=data.strip()
            if stripped:self.parts.append(stripped+" ")
def readable(html):
    reader=Reader();reader.feed(html)
    return "\n".join(x.strip() for x in "".join(reader.parts).split("\n") if x.strip())

def main():
    manifest=json.loads((PUBLIC/"public-manifest.json").read_text())
    paths=manifest["paths"]
    assert len(paths)==310
    assert len(set(paths))==310
    sampled=["index.html","danwon.html","ansan/danwon-02.html","gojan.html","national/index.html","national/1150000000.html"]
    national=sorted(x for x in paths if x.startswith("national/") and x!="national/index.html" and x not in sampled)
    # Deterministic additional coverage of two different official-region pages.
    national.sort(key=lambda p:hashlib.sha256(("skyquote-review-20261106:"+p).encode()).hexdigest())
    sampled.extend(national[:2])
    assert len(sampled)>=math.ceil(len(paths)*0.01) and len(set(sampled))==len(sampled)
    REPORT.mkdir(parents=True,exist_ok=True)
    samples=[]
    for path in paths:
        text=(PUBLIC/path).read_text(encoding="utf-8")
        body=readable(text)
        for bad in BAN:
            assert bad not in body,(path,bad)
        assert text.count("<img ")==5,path
        assert text.count('loading="eager"')==1 and text.count('loading="lazy"')==4,path
        assert "010-5322-1952" in text or path=="national/index.html",path
        assert "30만 원" in body and "부가세는 별도" in body,path
        assert "반나절" in body and "하루" in body,path
        if path in sampled:
            url=ORIGIN+("/" if path=="index.html" else "/"+path)
            samples.append({"url":url,"path":path,"visibleText":body,"score":None,
              "natural":None,"accuracy":None,"nextAction":None,"repetition":None,
              "reviewStatus":"human_review_required"})
            print("SKYQUOTE_REVIEW_START",url,"\n"+body+"\nSKYQUOTE_REVIEW_END")
    assert len(samples)==len(sampled)
    feed=ET.parse(PUBLIC/"rss.xml").getroot().findall("./channel/item")
    assert 1<=len(feed)<=50
    for item in feed:
        body=readable(item.findtext("description") or "")
        for bad in BAN:assert bad not in body,(item.findtext("link"),bad)
        assert "부가세" in body and "4시간" in body
    report={"totalPages":len(paths),"minimumOnePercent":math.ceil(len(paths)*.01),
      "sampleCount":len(samples),"scope":"customer-visible HTML text and all RSS item bodies",
      "rssItems":len(feed),"allHtmlAndRssNegativeChecks":"passed",
      "scoreRubric":{"natural":25,"accuracy":25,"nextAction":30,"repetition":20},
      "samples":samples}
    (REPORT/"sample-readback.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("SKYQUOTE_310_COPY_EVIDENCE_PASS allHtml=310 rss="+str(len(feed))+
        " sampled="+str(len(samples))+" min1pct="+str(math.ceil(len(paths)*.01)))
if __name__=="__main__":main()
