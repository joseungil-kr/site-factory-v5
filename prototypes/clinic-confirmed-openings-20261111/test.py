"""Offline candidate and corresponding legacy HTML inspection; screenshots via Playwright."""
from __future__ import annotations
from pathlib import Path
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright
from PIL import Image
import argparse,collections,hashlib,json,shutil,subprocess,sys,time,urllib.request
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
class Parse(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[];self.text=[];self.meta=[]
    def handle_starttag(self,t,attrs):
        x=dict(attrs)
        if t=="a":self.links.append(x.get("href",""))
        if t=="meta" and x.get("name")=="robots":self.meta.append(x.get("content"))
    def handle_data(self,v):
        if v.strip():self.text.append(v.strip())
def compare(build,output):
    sys.path.insert(0,str(ROOT/"sites/nalmada-shared3"))
    import build_national as original
    ledger=json.loads((ROOT/"sites/nalmada-shared3/clinic-retail-candidate-ledger-20261111.json").read_text("utf-8"))
    original.RETAIL_LEDGER={x["sku"]:x for x in ledger["items"]}
    raw=json.loads((ROOT/"data/regions/nationwide_locality_candidates_5034.json").read_text("utf-8"))
    regions=original.parse_regions(raw)
    evidence=json.loads((build/"evidence.json").read_text("utf-8"))
    records={}
    output.mkdir(parents=True)
    for c in evidence["approvedCases"]:
        x=c["legacy"];region=regions[x["index"]-1]
        oldhtml,_=original.render_region(x["site"],region,None,"public")
        oldfile=output/(c["id"]+"-legacy.html");oldfile.write_text(oldhtml,"utf-8")
        newfile=build/(c["id"]+".html")
        newhtml=newfile.read_text("utf-8")
        oldp=Parse();oldp.feed(oldhtml)
        newp=Parse();newp.feed(newhtml)
        assert oldp.meta==["index,follow"] and newp.meta==["noindex,nofollow"]
        assert not any(h.startswith("http") and ("snuh.org" in h or "suwon.go.kr" in h) for h in oldp.links)
        assert all(x["url"] in newp.links for x in c["officialSources"])
        assert c["eventDate"] in newhtml and "과거" in newhtml and "현재 판매가 아님" in newhtml
        assert "tel:1844-0644" in oldp.links and "tel:1844-0644" in newp.links
        assert len([v for v in newp.links if "fwith.co.kr/shop/item.php?it_id=" in v])==2
        records[c["id"]]={"legacyPath":"https://"+original.SITE_META[x["site"]]["host"]+x["path"],
          "oldSHA256":hashlib.sha256(oldfile.read_bytes()).hexdigest(),
          "candidateSHA256":hashlib.sha256(newfile.read_bytes()).hexdigest(),
          "oldText":" ".join(oldp.text)[:3500],
          "newText":" ".join(newp.text)[:5000],
          "officialSources":[z["id"] for z in c["officialSources"]],
          "date":c["eventDate"],"previousLiveByteParity":False}
    return records
def browser(build,out,evidence):
    evidence_rows=[]
    server=subprocess.Popen([sys.executable,"-m","http.server","18832","--bind","127.0.0.1","--directory",str(build)],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for attempt in range(40):
            try:
                with urllib.request.urlopen("http://127.0.0.1:18832/index.html",timeout=2) as resp:
                    assert resp.status==200
                break
            except Exception:time.sleep(.25)
        else:raise RuntimeError("Server not reachable")
        with sync_playwright() as pw:
            chrome=next((shutil.which(x) for x in ("google-chrome","google-chrome-stable","chromium","chromium-browser") if shutil.which(x)),None)
            if not chrome:raise RuntimeError("Missing Chrome")
            engine=pw.chromium.launch(executable_path=chrome,headless=True,args=["--no-sandbox"])
            for width,height in ((390,844),(1440,900)):
                context=engine.new_context(viewport={"width":width,"height":height})
                page=context.new_page()
                index=page.goto("http://127.0.0.1:18832/index.html",wait_until="networkidle")
                assert index.status==200
                assert page.locator(".case-card").count()==2
                for c in evidence["approvedCases"]:
                    page.locator('a[href="'+c["id"]+'.html"]').click()
                    assert page.url.endswith(c["id"]+".html")
                    await_fonts=page.evaluate("async () => {await document.fonts.ready;return document.fonts.status}")
                    assert await_fonts=="loaded"
                    assert page.locator("h1").count()==1
                    assert page.locator("a.source").count()==len(c["officialSources"])
                    assert page.locator(".product").count()==2
                    assert c["eventDate"] in page.locator("main").inner_text()
                    assert "현재 판매가 아님" in page.locator("main").inner_text()
                    assert page.locator('meta[name="robots"]').get_attribute("content")=="noindex,nofollow"
                    assert page.locator('a[href="tel:1844-0644"]').count()==1
                    for sku in c["skus"]:
                        assert page.locator('article[data-sku="'+sku+'"] a').get_attribute("href")=="https://fwith.co.kr/shop/item.php?it_id="+sku
                    assert page.evaluate("() => document.documentElement.scrollWidth<=innerWidth+2")
                    file=out/(c["id"]+"-"+str(width)+"-full.png")
                    page.screenshot(path=str(file),full_page=True,animations="disabled")
                    with Image.open(file) as im:
                        assert im.width==width and im.height>height
                        size=im.size
                    print("HISTORICAL_BROWSER_PASS",c["id"],width,size)
                    evidence_rows.append({"id":c["id"],"width":width,"image":file.name,"size":size,
                        "sourceCount":len(c["officialSources"]),"priceCurrentVerified":False})
                    page.goto("http://127.0.0.1:18832/index.html",wait_until="networkidle")
                context.close()
            engine.close()
    finally:
        server.terminate();server.wait(timeout=10)
    return evidence_rows
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--build",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    build=args.build.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    ev=json.loads((build/"evidence.json").read_text("utf-8"))
    comparison=compare(build,out/"legacy")
    screens=browser(build,out,ev)
    results={"confirmedCases":len(ev["approvedCases"]),"deferredCases":len(ev["deferredCases"]),
        "screenshotCount":len(screens),"screenshots":screens,"legacy":comparison,
        "noDeploy":True,"oldRoutesChanged":0,"sellerCurrentnessVerified":False}
    assert results["confirmedCases"]==2 and results["screenshotCount"]==4
    (out/"audit.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n","utf-8")
    print("HISTORIC_OPENING_AUDIT_PASS",json.dumps({k:v for k,v in results.items() if k not in ("screenshots","legacy")},ensure_ascii=False))
if __name__=="__main__":main()
