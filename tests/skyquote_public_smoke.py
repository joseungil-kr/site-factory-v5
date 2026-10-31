"""Pre-deploy static public QA; only exact approved domain can be indexable."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"dist/skyquote-public"
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
    for filename in m["paths"]:
        content=(OUT/filename).read_text(encoding="utf-8")
        h=H();h.feed(content)
        url="https://skyquote.nalmada.net"+("/" if filename=="index.html" else "/"+filename)
        assert h.meta==["index,follow"],filename
        assert h.canon==[url],filename
        assert url in locations,filename
        assert content.count('<img ')==5,filename
        assert 'href="//' not in content,filename
        assert not any(bad in content for bad in ('최저가를 보장합니다','전국 출동 가능합니다','업계 최저가 보장')),filename
    imgs=json.loads((ROOT/"sites/skyquote/assets-manifest.json").read_text())["assets"]
    for x in imgs:
        path=OUT/"assets"/Path(x["path"]).name
        assert hashlib.sha256(path.read_bytes()).hexdigest()==x["sha256"],path
    config=json.loads((ROOT/"sites/skyquote/wrangler.public.json").read_text())
    assert config["name"]=="sfv5-skyquote-public"
    assert config["workers_dev"] is False
    assert config["routes"]==[{"pattern":"skyquote.nalmada.net","custom_domain":True}]
    assert config["vars"]["SKYQUOTE_PUBLIC"]=="1"
    worker=(ROOT/"sites/skyquote/worker.public.js").read_text()
    assert "u.hostname===HOST" in worker and "response.status===404" in worker
    print("SKYQUOTE_PUBLIC_310_QA_PASS pages=310 canonicals=310 sitemap=310 imageHashes=5 hostGuard=true")
if __name__=="__main__":main()
