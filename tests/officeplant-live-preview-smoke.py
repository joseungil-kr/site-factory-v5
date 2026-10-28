"""Live HTTPS Chromium smoke test for the Officeplant noindex preview."""
from __future__ import annotations
import argparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from playwright.sync_api import sync_playwright

def get(url):
    try:
        with urlopen(Request(url, headers={"User-Agent":"Officeplant-Live-Preview-QA/1"}), timeout=25) as response:
            return response.status, response.headers, response.read(2_000_000)
    except HTTPError as exc:
        return exc.code, exc.headers, exc.read(2_000_000)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--origin", required=True)
    origin=parser.parse_args().origin.rstrip("/")
    checks=[]
    status, headers, body=get(origin+"/")
    html=body.decode("utf-8","replace")
    assert status==200 and "noindex" in headers.get("X-Robots-Tag","").lower()
    assert '<meta name="robots" content="noindex,nofollow">' in html
    assert 'rel="canonical"' not in html
    checks.append("homepage-noindex")
    status, headers, robots=get(origin+"/robots.txt")
    assert status==200 and b"Disallow: /" in robots
    status, _, _=get(origin+"/sitemap.xml")
    assert status==404
    checks.append("robots-disallow-and-no-sitemap")
    for path in ("/r/1-opening.html","/r/1732-gift.html","/regions.html","/moran.html","/order.html"):
        status,headers,body=get(origin+path)
        text=body.decode("utf-8","replace")
        assert status==200 and "noindex" in headers.get("X-Robots-Tag","").lower()
        assert '<meta name="robots" content="noindex,nofollow">' in text
        checks.append("GET "+path)
    for sku in ("D144","D149","D158"):
        status,headers,body=get(origin+"/assets/"+sku+".jpg")
        assert status==200 and headers.get("Content-Type","").startswith("image/jpeg") and body[:2]==b"\xff\xd8"
        checks.append("asset "+sku)
    status,headers,body=get(origin+"/not-a-real-officeplant-path")
    assert status==404 and "noindex" in headers.get("X-Robots-Tag","").lower()
    checks.append("404-noindex")
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
        for label,width,height in (("desktop",1440,900),("mobile",390,844)):
            page=browser.new_page(viewport={"width":width,"height":height})
            response=page.goto(origin+"/",wait_until="networkidle",timeout=60000)
            assert response and response.status==200
            assert page.locator("h1").count()==1
            page.locator("#collection").scroll_into_view_if_needed()
            images=page.locator("#collection img").evaluate_all("(xs)=>xs.map(x=>({complete:x.complete,width:x.naturalWidth}))")
            assert len(images)==3 and all(x["complete"] and x["width"]==500 for x in images),(label,images)
            dimensions=page.evaluate("({inner:innerWidth,scroll:document.documentElement.scrollWidth})")
            assert dimensions["scroll"]<=dimensions["inner"]+1,(label,dimensions)
            assert page.locator("#collection .product:not([hidden])").count()==3
            if label=="desktop":
                page.select_option("#space-filter","desk")
                assert page.locator("#collection .product:not([hidden])").count()==2
                page.select_option("#space-filter","reception")
                assert page.locator("#collection .product:not([hidden])").count()==1
                page.select_option("#space-filter","all")
                page.select_option("#budget-filter","50000")
                assert page.locator("#collection .product:not([hidden])").count()==1
                page.select_option("#budget-filter","60000")
                assert page.locator("#collection .product:not([hidden])").count()==2
                page.select_option("#budget-filter","999999")
                page.select_option("#purpose-filter","move")
                assert page.locator("#collection .product:not([hidden])").count()==2
                page.select_option("#purpose-filter","partner")
                visible=page.locator("#collection .product:not([hidden])").evaluate_all("(xs)=>xs.map(x=>x.querySelector('h3').textContent.trim())")
                assert visible==["금전수 탁상용","녹보수 소형"],visible
                page.select_option("#space-filter","desk")
                page.select_option("#budget-filter","50000")
                assert page.locator("#collection .product:not([hidden])").count()==0
                assert page.locator("#no-products").is_visible()
                checks.append("space-budget-purpose-combination")
            checks.append(label+"-real-assets-responsive-layout")
            page.close()
        for mode in ("no-js","js-runtime-failure"):
            page=browser.new_page(viewport={"width":390,"height":844})
            if mode=="no-js":
                page.route("**/assets/officeplant.js",lambda route:route.abort())
            else:
                page.route("**/assets/officeplant.js",lambda route:route.fulfill(status=200,content_type="application/javascript",body="throw new Error('synthetic JS failure')"))
            response=page.goto(origin+"/order.html",wait_until="networkidle",timeout=60000)
            assert response and response.status==200
            assert page.locator("form").count()==0
            assert page.locator("#generate-note").is_disabled()
            before=page.url
            for name,value in (("sender","SYNTHETIC-SENDER"),("recipient","SYNTHETIC-RECIPIENT"),("phone","5550100000"),("address","SYNTHETIC-ADDRESS")):
                page.locator('[name="'+name+'"]').fill(value)
            page.locator("#generate-note").dispatch_event("click")
            page.locator('[name="recipient"]').press("Enter")
            assert page.url==before
            assert all(value not in page.url for value in ("SYNTHETIC-SENDER","SYNTHETIC-RECIPIENT","5550100000","SYNTHETIC-ADDRESS"))
            assert page.locator(".note-output").is_hidden()
            checks.append(mode+"-private-data-never-submitted")
            page.close()
        page=browser.new_page(viewport={"width":390,"height":844})
        response=page.goto(origin+"/order.html?sku=D149&purpose=partner",wait_until="networkidle",timeout=60000)
        assert response and response.status==200
        assert page.locator("select[name=sku]").input_value()=="D149"
        assert page.locator("select[name=purpose]").input_value()=="거래처 개업선물"
        for name,value in (("sender","SYNTHETIC-SENDER"),("recipient","SYNTHETIC-RECIPIENT"),("phone","5550100000"),("address","SYNTHETIC-ADDRESS")):
            page.locator('[name="'+name+'"]').fill(value)
        page.locator("#generate-note").click()
        assert page.locator(".note-output").is_visible()
        checkout=page.locator("#checkout").get_attribute("href")
        assert "D149" in checkout and all(value not in checkout and value not in page.url for value in ("SYNTHETIC-SENDER","SYNTHETIC-RECIPIENT","5550100000","SYNTHETIC-ADDRESS"))
        page.locator("#reset-note").click()
        assert page.locator(".note-output").is_hidden()
        checks.extend(["normal-order-note-client-only","checkout-URL-no-personal-data","reset-note"])
        page.close()
        page=browser.new_page(viewport={"width":390,"height":844})
        response=page.goto(origin+"/regions.html",wait_until="networkidle",timeout=60000)
        assert response and response.status==200
        assert page.locator(".region-row").count()==1732
        page.locator("#region-search").fill("강매동")
        count=page.locator(".region-row:visible").count()
        assert 1<=count<1732,count
        checks.append("real-region-search")
        page.close()
        browser.close()
    print({"origin":origin,"overall":"PASS","checks":checks,"checkCount":len(checks),"privacyData":"synthetic-only"})
if __name__=="__main__":
    main()
