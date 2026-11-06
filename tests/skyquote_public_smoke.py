"""Pre-deploy public QA including all pages, Naver homepage meta, RSS content and preserved image hashes."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"dist/skyquote-public"
class H(HTMLParser):
    def __init__(self):super().__init__();self.meta=[];self.canon=[]
    def handle_starttag(self,t,a):
        d=dict(a)
        if t=="meta" and d.get("name")=="robots":self.meta.append(d.get("content"))
        if t=="link" and d.get("rel")=="canonical":self.canon.append(d.get("href"))
def main():
    m=json.loads((OUT/"public-manifest.json").read_text())
    assert m["publicHost"]=="skyquote.nalmada.net" and m["sitePages"]==310 and m["sitemapUrls"]==310
    assert len(m["paths"])==310
    sitemap=ET.fromstring((OUT/"sitemap.xml").read_bytes())
    locations=[x.text for x in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    assert len(locations)==310 and len(set(locations))==310
    assert all(x.startswith("https://skyquote.nalmada.net/") for x in locations)
    assert (OUT/"robots.txt").read_text()=='User-agent: *\nAllow: /\nSitemap: https://skyquote.nalmada.net/sitemap.xml\n'
    expected='<meta name="naver-site-verification" content="f8afb036a43ba44dc04b4c73de487908bed4a65e" />'
    homepage=(OUT/"index.html").read_text(encoding="utf-8")
    assert homepage.count(expected)==1 and homepage.count("naver-site-verification")==1
    assert homepage.index("<head>")<homepage.index(expected)<homepage.index("</head>")
    feed=ET.parse(OUT/"rss.xml").getroot()
    items=feed.findall('./channel/item')
    assert 1<=len(items)<=50
    for item in items:
        body=item.findtext("description") or ""
        assert "영진스카이 공개 이용요금" in body and "30만 원" in body and "작업 지점까지 높이(미터)" in body
        for bad in ("AI 생성 설명 이미지","실제 시공·장비 보유 증명이 아닙니다","업계 최저가를 주장하지 않습니다","단정하지 마세요","기재합니다"):
            assert bad not in body,bad
        assert item.findtext("description")==item.findtext("{http://purl.org/rss/1.0/modules/content/}encoded")
    for filename in m["paths"]:
        content=(OUT/filename).read_text(encoding="utf-8")
        h=H();h.feed(content)
        url="https://skyquote.nalmada.net"+("/" if filename=="index.html" else "/"+filename)
        assert h.meta==["index,follow"] and h.canon==[url],filename
        assert url in locations and content.count('<img ')==5,filename
        assert "AI 생성 설명 이미지" not in content and "<figcaption>" not in content,filename
        assert "영진스카이 공개 이용요금" in content and "30만 원" in content,filename
        assert "작업 지점까지 높이(미터)" in content,filename
        assert content.count('loading="eager"')==1 and content.count('loading="lazy"')==4,filename
        assert 'href="//' not in content,filename
        if filename!="index.html":assert "naver-site-verification" not in content,filename
        for bad in ("업계 최저가를 주장하지 않습니다","차량 톤수만으로 작업 가능성을 보장하지 않습니다","실수를 피할 수 있습니다","기재합니다","단정하지 마세요"):
            assert bad not in content,(filename,bad)
    imgs=json.loads((ROOT/"sites/skyquote/assets-manifest.json").read_text())["assets"]
    for x in imgs:
        p=OUT/"assets"/Path(x["path"]).name
        assert hashlib.sha256(p.read_bytes()).hexdigest()==x["sha256"],p
    config=json.loads((ROOT/"sites/skyquote/wrangler.dual-host.json").read_text())
    assert config["name"]=="sfv5-skyquote-preview" and config["workers_dev"] is True
    assert config["routes"]==[{"pattern":"skyquote.nalmada.net","custom_domain":True}]
    worker=(ROOT/"sites/skyquote/worker.dual-host.js").read_text()
    assert "incoming.hostname===PUBLIC_HOST" in worker and '"/rss.xml"' in worker
    print("SKYQUOTE_PUBLIC_310_QA_PASS pages=310 canonical=310 sitemap=310 RSS="+str(len(items))+" imageHashes=5 exactHost=true")
if __name__=="__main__":main()
