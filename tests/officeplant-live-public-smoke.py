"""Read-only live public-host verification for Officeplant."""
from __future__ import annotations
import argparse
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from xml.etree import ElementTree as ET
from playwright.sync_api import sync_playwright

def get(url):
    try:
        with urlopen(Request(url,headers={"User-Agent":"Officeplant-Public-QA/1"}),timeout=30) as r:
            return r.status,r.headers,r.read(6_000_000)
    except HTTPError as e:
        return e.code,e.headers,e.read(6_000_000)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--origin",required=True)
    ap.add_argument("--preview-origin",required=True)
    a=ap.parse_args(); origin=a.origin.rstrip("/"); preview=a.preview_origin.rstrip("/")
    checks=[]
    status,headers,body=get(origin+"/robots.txt"); robots=body.decode("utf-8","replace")
    assert status==200 and "Allow: /" in robots and "Disallow: /" not in robots
    assert "Sitemap: "+origin+"/sitemap.xml" in robots
    status,headers,body=get(origin+"/sitemap.xml")
    urls=[x.text for x in ET.fromstring(body).findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    assert status==200 and len(urls)==len(set(urls))==3468
    assert urls[0]==origin+"/" and urls[-1]==origin+"/moran.html"
    key=(Path(__file__).resolve().parents[1]/"sites/officeplant/indexnow-public-key.txt").read_text().strip()
    status,headers,body=get(origin+"/"+key+".txt")
    assert status==200 and body.decode("utf-8","replace").strip()==key
    checks.extend(["robots-allow","sitemap-3468-unique","indexnow-key-verified"])
    for path in ("/","/r/1-opening.html","/r/1732-gift.html","/regions.html","/moran.html","/order.html"):
        status,headers,body=get(origin+path); html=body.decode("utf-8","replace")
        assert status==200 and "noindex" not in headers.get("X-Robots-Tag","").lower()
        assert '<meta name="robots" content="index,follow">' in html
        assert '<link rel="canonical" href="'+origin+path+'">' in html
        if path == "/":
            assert html.count('<meta name="naver-site-verification" content="a421d53d29070054a8681a2c99312aef9b9b4e80">') == 1
        else:
            assert 'name="naver-site-verification"' not in html
        checks.append("indexable "+path)
    status,headers,body=get(origin+"/not-a-real-officeplant-path")
    assert status==404 and "noindex" in headers.get("X-Robots-Tag","").lower()
    status,headers,body=get(preview+"/")
    assert status==200 and "noindex" in headers.get("X-Robots-Tag","").lower()
    status,headers,body=get(preview+"/robots.txt")
    assert status==200 and b"Disallow: /" in body
    status,headers,body=get(preview+"/sitemap.xml")
    assert status==404
    checks.extend(["404-noindex","workers-dev-preview-stays-noindex"])
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
        for label,width,height in (("desktop",1440,900),("mobile",390,844)):
            page=browser.new_page(viewport={"width":width,"height":height})
            response=page.goto(origin+"/",wait_until="networkidle",timeout=60000)
            assert response and response.status==200
            page.locator("#collection").scroll_into_view_if_needed()
            images=page.locator("#collection img").evaluate_all("(xs)=>xs.map(x=>({complete:x.complete,width:x.naturalWidth}))")
            assert len(images)==3 and all(x["complete"] and x["width"]==500 for x in images),(label,images)
            dims=page.evaluate("({inner:innerWidth,scroll:document.documentElement.scrollWidth})")
            assert dims["scroll"]<=dims["inner"]+1,(label,dims)
            checks.append(label+"-real-images-and-layout")
            page.close()
        page=browser.new_page(viewport={"width":390,"height":844})
        response=page.goto(origin+"/order.html?sku=D149&purpose=partner",wait_until="networkidle",timeout=60000)
        assert response and response.status==200
        for name,value in (("sender","SYNTHETIC-SENDER"),("recipient","SYNTHETIC-RECIPIENT"),("phone","5550100000"),("address","SYNTHETIC-ADDRESS")):
            page.locator('[name="'+name+'"]').fill(value)
        page.locator("#generate-note").click()
        assert page.locator(".note-output").is_visible()
        checkout=page.locator("#checkout").get_attribute("href")
        assert "D149" in checkout and all(value not in checkout and value not in page.url for value in ("SYNTHETIC-SENDER","SYNTHETIC-RECIPIENT","5550100000","SYNTHETIC-ADDRESS"))
        checks.append("order-note-no-personal-data-in-url")
        page.close();browser.close()
    print({"origin":origin,"overall":"PASS","checks":checks,"count":len(checks),"personalData":"synthetic only"})
if __name__=="__main__":main()
