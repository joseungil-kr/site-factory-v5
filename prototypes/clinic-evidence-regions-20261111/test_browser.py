"""Read-only Playwright audit of three evidence-based regional HTML pages."""
import argparse,json,shutil,subprocess,sys,time,urllib.request
from pathlib import Path
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright
from PIL import Image

SLUGS=("ansan-opening","seoul-relocation","suwon-celebration")
SKUS={"ansan-opening":("D149","D144"),
      "seoul-relocation":("D144","D149"),
      "suwon-celebration":("C200","C206")}
SOURCES={"ansan-opening":("A-LOCATION","A-FLOOR"),
         "seoul-relocation":("S-ADDRESS","S-MAP","S-ROUTE"),
         "suwon-celebration":("W-HIRA","W-SITE")}
class Parser(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.links=[];self.robots=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "data-source-id" in a:self.ids.append(a["data-source-id"])
        if tag=="a":self.links.append(a.get("href",""))
        if tag=="meta" and a.get("name")=="robots":self.robots.append(a.get("content"))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("build",type=Path);parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    base=a.build.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    html=sorted(x.name for x in base.glob("*.html"))
    assert html==["ansan-opening.html","index.html","seoul-relocation.html","suwon-celebration.html"],html
    ledger=json.loads((base/"evidence.json").read_text("utf-8"))
    assert len(ledger["cases"])==3
    comparison=json.loads((base/"comparison-to-legacy.json").read_text("utf-8"))
    assert set(comparison)==set(SLUGS)
    for slug in SLUGS:
        doc=Parser();doc.feed((base/(slug+".html")).read_text("utf-8"))
        assert doc.robots==["noindex,nofollow"],(slug,doc.robots)
        assert tuple(doc.ids)==SOURCES[slug],(slug,doc.ids)
        assert "./index.html" in doc.links
        assert "tel:1844-0644" in doc.links
        assert set("./"+x+".html" for x in SLUGS).issubset(doc.links)
        assert comparison[slug]["matchedOldRecordCount"]>0
        assert comparison[slug]["existingURLChange"]=="NONE"
        assert comparison[slug]["redirect"]=="NONE"
        for sku in SKUS[slug]:
            assert "https://fwith.co.kr/shop/item.php?it_id="+sku in doc.links
    server=subprocess.Popen([sys.executable,"-m","http.server","18792","--bind","127.0.0.1","--directory",str(base)],
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    screenshots=[];results=[]
    try:
        for _ in range(30):
            try:
                with urllib.request.urlopen("http://127.0.0.1:18792/",timeout=2) as response:
                    assert response.status==200
                break
            except Exception:time.sleep(.3)
        else:raise RuntimeError("HTTP server not ready")
        with sync_playwright() as pw:
            chrome=next((shutil.which(x) for x in ("google-chrome","google-chrome-stable","chromium","chromium-browser") if shutil.which(x)),None)
            if not chrome:raise RuntimeError("Chrome/Chromium unavailable")
            browser=pw.chromium.launch(executable_path=chrome,headless=True,args=["--no-sandbox"])
            for width,height in ((390,844),(1440,900)):
                context=browser.new_context(viewport={"width":width,"height":height},device_scale_factor=1)
                page=context.new_page()
                idx=page.goto("http://127.0.0.1:18792/index.html",wait_until="networkidle")
                assert idx and idx.status==200
                assert page.locator(".case-card").count()==3
                for slug in SLUGS:
                    link=page.locator(f'a[href="./{slug}.html"]').first
                    link.click()
                    assert page.url.endswith(slug+".html"),(width,slug,page.url)
                    assert page.locator("h1").count()==1
                    assert page.locator(".fact").count()==len(SOURCES[slug])
                    assert page.locator(".decisions li").count()==3
                    assert page.locator(".product").count()==2
                    assert page.locator("meta[name=robots]").get_attribute("content")=="noindex,nofollow"
                    assert "2026-11-05" in page.locator("#sku").inner_text()
                    assert "현재 가격" in page.locator("#sku").inner_text()
                    assert page.locator("a[href='tel:1844-0644']").count()==1
                    assert page.locator("a.source").count()==len(SOURCES[slug])
                    for sku in SKUS[slug]:
                        el=page.locator(f'[data-sku="{sku}"] a')
                        assert el.count()==1
                        assert el.get_attribute("href")=="https://fwith.co.kr/shop/item.php?it_id="+sku
                        assert el.get_attribute("rel")=="noopener noreferrer"
                    assert page.evaluate("() => document.documentElement.scrollWidth<=innerWidth+2")
                    assert page.evaluate("() => document.fonts.ready.then(()=>document.fonts.status)")=="loaded"
                    cta=page.locator("a[href='tel:1844-0644']")
                    cta.scroll_into_view_if_needed()
                    assert cta.is_visible()
                    box=cta.bounding_box()
                    assert box and box["width"]>100 and box["height"]>=44,(slug,width,box)
                    image=out/(f"{slug}-{width}-full.png")
                    page.screenshot(path=str(image),full_page=True,animations="disabled")
                    with Image.open(image) as im:
                        assert im.width==width and im.height>height
                        size=list(im.size)
                    screenshots.append(image.name)
                    results.append({"slug":slug,"viewport":width,"url":page.url,
                                    "sourceIds":SOURCES[slug],"sku":SKUS[slug],
                                    "fullPagePNG":image.name,"size":size,
                                    "ctaAccessible":True,"linksVerified":True,
                                    "externalLinkClickNotPerformed":True})
                    print("CASE_BROWSER_PASS",slug,width,size)
                    page.locator('a.logo').click()
                    assert page.url.endswith("index.html")
                context.close()
            browser.close()
    finally:
        server.terminate();server.wait(timeout=10)
    report={"cases":results,"screenshots":screenshots,"browserCases":len(results),
        "originalLegacyRoutesChanged":0,"noPublicDeployment":True,
        "humanEditorialApproval":False,"liveProductCurrentnessVerified":False}
    (out/"test-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf-8")
    print("CASE_BROWSER_REPORT="+json.dumps({k:v for k,v in report.items() if k!="cases" and k!="screenshots"},ensure_ascii=False))
if __name__=="__main__":main()
