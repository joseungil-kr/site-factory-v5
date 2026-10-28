"""Chromium interaction test for Officeplant filters, order-note safety and responsive layout."""
from __future__ import annotations
import base64
import json
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"dist/officeplant-public"
REPORT=ROOT/"reports/officeplant/browser-smoke.json"
CSS=(ROOT/"sites/officeplant/assets/officeplant.css").read_text(encoding="utf-8")
JS=(ROOT/"sites/officeplant/assets/officeplant.js").read_text(encoding="utf-8")
IMAGES={sku:"data:image/jpeg;base64,"+base64.b64encode((ROOT/"sites/officeplant/assets"/f"{sku}.jpg").read_bytes()).decode("ascii") for sku in ("D144","D149","D158")}

def render(source:Path,query:str="",include_js:bool=True):
    html=source.read_text(encoding="utf-8")
    html=html.replace("<head>","<head><base href='https://officeplant.nalmada.net/'><style>"+CSS+"</style>")
    html=html.replace('<link rel="stylesheet" href="/assets/officeplant.css">',"")
    html=html.replace('<script src="/assets/officeplant.js" defer></script>',"")
    for sku,data in IMAGES.items():
        html=html.replace(f'src="/assets/{sku}.jpg"',f'src="{data}"')
    prelude=f"<script>history.replaceState({{}},'', 'about:blank{query}');</script>" if query else ""
    script="<script>"+JS+"</script>" if include_js else ""
    return html.replace("</body>",prelude+script+"</body>")

def main():
    checks=[]
    def record(name,detail=None):
        checks.append({"check":name,"detail":detail or "pass","status":"pass"})
    with sync_playwright() as pw:
        executable=shutil.which("chromium") or shutil.which("chromium-browser")
        options={"headless":True,"args":["--no-sandbox","--disable-dev-shm-usage","--allow-file-access-from-files"]}
        if executable:
            options["executable_path"]=executable
        browser=pw.chromium.launch(**options)
        for label,width,height in (("desktop",1440,900),("mobile",390,844)):
            page=browser.new_page(viewport={"width":width,"height":height})
            page.set_content(render(OUT/"index.html"),wait_until="load")
            assert page.locator("h1").count()==1
            assert all(page.locator("#"+x).count()==1 for x in ("space-filter","budget-filter","purpose-filter"))
            dims=page.evaluate("({inner:innerWidth,scroll:document.documentElement.scrollWidth})")
            assert dims["scroll"]<=dims["inner"]+1,(label,"horizontal overflow",dims)
            page.locator("#collection").scroll_into_view_if_needed()
            page.wait_for_timeout(150)
            images=page.locator("#collection img").evaluate_all('(xs)=>xs.map(x=>({complete:x.complete,width:x.naturalWidth}))')
            assert len(images)==3 and all(x["complete"] and x["width"]==500 for x in images),(label,images)
            assert page.locator("#collection .product:not([hidden])").count()==3
            record(label+" homepage and images",{"width":width,"scrollWidth":dims["scroll"],"images":len(images)})
            if label=="desktop":
                page.select_option("#space-filter","desk")
                assert page.locator("#collection .product:not([hidden])").count()==2
                page.select_option("#space-filter","reception")
                assert page.locator("#collection .product:not([hidden])").count()==1
                record("space filter",{"desk":2,"reception":1})
                page.select_option("#space-filter","all")
                page.select_option("#budget-filter","50000")
                assert page.locator("#collection .product:not([hidden])").count()==1
                page.select_option("#budget-filter","60000")
                assert page.locator("#collection .product:not([hidden])").count()==2
                record("budget filter",{"50000":1,"60000":2})
                page.select_option("#budget-filter","999999")
                page.select_option("#purpose-filter","move")
                assert page.locator("#collection .product:not([hidden])").count()==2
                assert page.locator("#selection-advice").inner_text().startswith("이전한 주소")
                assert "purpose=move" in page.locator("a.subtle").first.get_attribute("href")
                page.select_option("#purpose-filter","partner")
                visible=page.locator("#collection .product:not([hidden])").evaluate_all('(xs)=>xs.map(x=>x.querySelector("h3").textContent.trim())')
                assert visible==["금전수 탁상용","녹보수 소형"],visible
                assert page.locator("#selection-advice").inner_text().startswith("받는 회사")
                assert "purpose=partner" in page.locator("a.subtle").first.get_attribute("href")
                record("purpose filter and order query",visible)
                page.select_option("#space-filter","desk")
                page.select_option("#budget-filter","50000")
                assert page.locator("#collection .product:not([hidden])").count()==0
                assert page.locator("#no-products").is_visible()
                assert page.locator("#no-products a[href='tel:18440644']").count()==1
                record("combined filter empty state","phone CTA visible")
                page.select_option("#space-filter","all")
                page.select_option("#budget-filter","70000")
                assert page.locator("#collection .product:not([hidden])").count()==2
                assert page.locator("#no-products").is_hidden()
                record("combined filter recovery",2)
            page.close()
        # Fail-closed test: without JavaScript there is no form and the action stays disabled.
        for mode in ("no-js","js-failure"):
            page=browser.new_page(viewport={"width":390,"height":844})
            markup=render(OUT/"order.html",include_js=False)
            if mode=="js-failure":
                markup=markup.replace("</body>","<script>throw new Error('synthetic JavaScript failure')</script></body>")
            page.set_content(markup,wait_until="load")
            assert page.locator("form").count()==0
            assert page.locator("#generate-note").is_disabled()
            assert page.locator("#reset-note").is_disabled()
            before=page.url
            for field,value in (("sender","SYNTHETIC-SENDER"),("recipient","SYNTHETIC-RECIPIENT"),("phone","5550100000"),("address","SYNTHETIC-ADDRESS")):
                page.locator('[name="'+field+'"]').fill(value)
            page.locator("#generate-note").dispatch_event("click")
            page.locator('[name="recipient"]').press("Enter")
            assert page.url==before and all(value not in page.url for value in ("SYNTHETIC-SENDER","SYNTHETIC-RECIPIENT","5550100000","SYNTHETIC-ADDRESS"))
            assert page.locator(".note-output").is_hidden()
            record(mode+" cannot submit private fields",{"formElements":0,"actionDisabled":True,"URLUnchanged":True})
            page.close()
        page=browser.new_page(viewport={"width":390,"height":844})
        page.set_content(render(OUT/"order.html","?sku=D149&purpose=partner"),wait_until="load")
        assert page.locator('select[name="sku"]').input_value()=="D149"
        assert page.locator('select[name="purpose"]').input_value()=="거래처 개업선물"
        page.locator('input[name="ribbon"]').fill("새로운 시작을 응원합니다")
        page.locator('input[name="sender"]').fill("테스트 회사")
        page.locator('input[name="recipient"]').fill("수령 담당자")
        page.locator('input[name="address"]').fill("테스트 주소")
        assert page.locator("form").count()==0
        assert page.locator("#generate-note").is_enabled()
        page.locator("#generate-note").click()
        assert page.locator(".note-output").is_visible()
        summary=page.locator("#summary").inner_text()
        assert "녹보수 소형" in summary and "거래처 개업선물" in summary and "테스트 주소" in summary
        checkout=page.locator("#checkout").get_attribute("href")
        assert "D149" in checkout and "테스트 주소" not in checkout
        assert "테스트 회사" not in page.url and "수령 담당자" not in page.url and "테스트 주소" not in page.url
        record("no personal values in checkout URL")
        record("order note and privacy-safe checkout",checkout)
        page.locator("#reset-note").click()
        assert page.locator(".note-output").is_hidden() and page.locator("#summary").inner_text()==""
        record("order note reset")
        page.close()
        page=browser.new_page(viewport={"width":390,"height":844})
        page.set_content(render(OUT/"regions.html"),wait_until="load")
        before=page.locator(".region-row:visible").count()
        page.locator("#region-search").fill("강매동")
        after=page.locator(".region-row:visible").count()
        assert before==1732 and after>=1 and after<before,(before,after)
        record("region search",{"before":before,"after":after})
        page.close()
        browser.close()
    result={"overall":"pass","checks":checks,"count":len(checks)}
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
