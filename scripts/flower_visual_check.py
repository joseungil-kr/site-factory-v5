"""Browser-level readback for flower.nalmada.net reviewed NOINDEX preview.

Uses local generated HTML only; screenshot artifacts are not an approval for
the production domain, products, or facility information.
"""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"dist/flower-funeral-national-preview"
SHOTS=ROOT/"reports/flower-funeral/visual"
WIDTHS=(("desktop",1440,960),("mobile",390,844))

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):
        pass

def inspect(page,name):
    title=page.title()
    assert "날마다꽃" in title,(name,title)
    assert page.locator('meta[name="robots"]').get_attribute("content")=="noindex,nofollow"
    page.locator(".btn").first.wait_for()
    width=page.evaluate("document.documentElement.scrollWidth")
    viewport=page.evaluate("window.innerWidth")
    assert width<=viewport+2,{"page":name,"scrollWidth":width,"viewport":viewport}
    images=page.locator("img")
    count=images.count()
    for i in range(count):
        image=images.nth(i)
        image.scroll_into_view_if_needed(timeout=15000)
        ok=image.evaluate("(img)=>img.complete && img.naturalWidth>0")
        assert ok,{"page":name,"imageIndex":i,"src":image.get_attribute("src")}
    assert count>=3,(name,count)
    return {"title":title,"imagesLoaded":count,"scrollWidth":width,"viewport":viewport}

def main():
    manifest=json.loads((DIST/"manifest.json").read_text(encoding="utf-8"))
    assert manifest["pageCount"]==1080 and manifest["qaPasses"]
    sample=manifest["pages"][531]["filename"]
    SHOTS.mkdir(parents=True,exist_ok=True)
    handler=partial(QuietHandler,directory=str(DIST))
    server=ThreadingHTTPServer(("127.0.0.1",0),handler)
    t=Thread(target=server.serve_forever,daemon=True);t.start()
    origin=f"http://127.0.0.1:{server.server_port}"
    report=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            for tag,width,height in WIDTHS:
                page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1)
                page.goto(origin+"/",wait_until="networkidle",timeout=60000)
                page.wait_for_function("document.querySelectorAll('#results .hall-card').length >= 12",timeout=30000)
                data=inspect(page,"home-"+tag)
                assert page.locator("#query").count()==1
                page.locator("#query").fill("안산")
                page.wait_for_timeout(100)
                found=page.locator("#results .hall-card").count()
                assert found>0,("search failed",tag)
                page.locator("#query").fill("")
                page.screenshot(path=str(SHOTS/f"{tag}-home.png"),full_page=True)
                report.append({"page":"home","viewport":tag,"searchMatched":found,**data})
                page.goto(origin+"/"+sample,wait_until="networkidle",timeout=60000)
                data=inspect(page,"hall-"+tag)
                assert page.locator("h1").count()==1
                assert page.locator(".article-card .text-section").count()==6
                assert page.locator("#prices .product-card").count()==3
                assert page.locator(".aside .btn").count()==1
                assert "시설 주소와 현재 운영" in page.content() or "운영 여부" in page.content()
                page.screenshot(path=str(SHOTS/f"{tag}-hall.png"),full_page=True)
                report.append({"page":"hall","viewport":tag,**data})
                page.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()
    (SHOTS/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("NALMADA_FLOWER_DESIGN_VISUAL_QA="+json.dumps(report,ensure_ascii=False))

if __name__=="__main__":
    main()
