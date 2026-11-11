"""Offline Playwright functional and responsive audit. No external retailer navigation."""
from __future__ import annotations
import argparse
import json
import subprocess
import shutil
import sys
import time
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

EXPECTED = {
    "flower": ["D144","D149"],
    "open": ["D149","D144"],
    "wreath": ["C200","C206"],
}
PURPOSE_TEXT = {
    "flower": "오래 둘 선물",
    "open": "행사 일정과 인계",
    "wreath": "행사 현장 장식",
}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("build",type=Path)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    root=args.build.resolve()
    out=args.out.resolve()
    out.mkdir(parents=True,exist_ok=True)
    region_doc=json.loads((root/"regions.json").read_text("utf-8"))
    assert len(region_doc["regions"])==284
    compare=json.loads((root/"legacy-comparison-324.json").read_text("utf-8"))
    assert compare["legacyOldURLCount"]==324 and len(compare["items"])==324
    assert {r["host"] for r in compare["items"]}=={
        "clinicflower.nalmada.net","clinicopen.nalmada.net","clinicpresent.nalmada.net"}
    assert len(list(root.glob("*.html")))==1
    proc=subprocess.Popen([sys.executable,"-m","http.server","18781","--bind","127.0.0.1","--directory",str(root)],
                          stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    evidence=[]
    try:
        for attempt in range(40):
            try:
                with urllib.request.urlopen("http://127.0.0.1:18781/",timeout=2) as resp:
                    assert resp.status==200
                break
            except Exception:
                time.sleep(.25)
        else:raise RuntimeError("offline static server not responding")
        with sync_playwright() as pw:
            chrome=next((shutil.which(exe) for exe in ("google-chrome","google-chrome-stable","chromium","chromium-browser") if shutil.which(exe)),None)
            if chrome is None: raise RuntimeError("Installed Chrome/Chromium not found")
            browser=pw.chromium.launch(executable_path=chrome,headless=True,args=["--no-sandbox"])
            for width,height in ((390,844),(1440,900)):
                context=browser.new_context(viewport={"width":width,"height":height},device_scale_factor=1)
                page=context.new_page()
                response=page.goto("http://127.0.0.1:18781/",wait_until="networkidle")
                assert response and response.status==200
                page.evaluate("() => document.fonts.ready")
                assert page.locator("#regionCount").inner_text()=="코드 284개"
                assert page.locator('[role="option"]').count()==16
                assert page.locator("#selectedRegion").inner_text()=="선택된 지역 없음"
                page.locator("#regionSearch").fill("종로구")
                assert page.locator('[role="option"]').count()>=1
                page.locator('[role="option"]').filter(has_text="서울특별시 종로구").first.click()
                assert "서울특별시 종로구" in page.locator("#selectedRegion").inner_text()
                assert "배송 가능 여부와 무관" in page.locator("#searchStatus").inner_text()
                assert "지역별 독립 정보는 없습니다." in page.locator(".transparency strong").inner_text()
                selected=page.locator("#selectedRegion").inner_text()
                before_url=page.url
                for purpose,skus in EXPECTED.items():
                    page.locator(f'[data-purpose="{purpose}"]').click()
                    text=page.locator("#purposeDetail").inner_text()
                    assert PURPOSE_TEXT[purpose] in text,(purpose,text[:200])
                    assert page.locator(".advice article").count()==3
                    cards=page.locator("#products .product")
                    assert cards.count()==2
                    assert [cards.nth(i).get_attribute("data-sku") for i in range(2)]==skus
                    assert page.locator("#products .historical").count()==2
                    assert "현재 가격·재고·배송비 미확인" in page.locator("#products").inner_text()
                    for sku in skus:
                        anchor=page.locator(f'[data-sku-link="{sku}"]')
                        assert anchor.get_attribute("href")==f"https://fwith.co.kr/shop/item.php?it_id={sku}"
                        assert anchor.get_attribute("rel")=="noopener noreferrer"
                        # Verify actual tap target without opening the retailer's external page.
                        sku_hit=page.evaluate("""sku => {
                          document.documentElement.style.scrollBehavior='auto';
                          const a=document.querySelector('[data-sku-link="'+sku+'"]');
                          a.scrollIntoView({behavior:'instant',block:'center'});
                          const r=a.getBoundingClientRect();
                          const x=(r.left+r.right)/2,y=(r.top+r.bottom)/2;
                          const el=document.elementFromPoint(x,y);
                          return {hit:!!(el&&(el===a||a.contains(el))),x,y};
                        }""",sku)
                        assert sku_hit["hit"],(width,purpose,sku,sku_hit)
                    assert page.locator("#phoneCTA").get_attribute("href")=="tel:1844-0644"
                    cta_hit=page.evaluate("""() => {
                      document.documentElement.style.scrollBehavior='auto';
                      const a=document.querySelector('#phoneCTA');
                      a.scrollIntoView({behavior:'instant',block:'center'});
                      const r=a.getBoundingClientRect();
                      const x=(r.left+r.right)/2,y=(r.top+r.bottom)/2;
                      const el=document.elementFromPoint(x,y);
                      return {hit:!!(el&&(el===a||a.contains(el))),x,y};
                    }""")
                    assert cta_hit["hit"],(width,purpose,"phone CTA inaccessible",cta_hit)
                    assert selected==page.locator("#selectedRegion").inner_text()
                    assert page.url==before_url
                    info=page.evaluate("""() => ({w:innerWidth,scrollW:document.documentElement.scrollWidth,
                        htmlCount:document.querySelectorAll('html').length,
                        selected:document.querySelector('#selectedRegion').textContent,
                        selectedPurpose:document.querySelector('[role="tab"][aria-selected="true"]').dataset.purpose,
                        documentHeight:document.documentElement.scrollHeight})""")
                    assert info["scrollW"]<=width+2,(width,purpose,"overflow",info)
                    dest=out/f"{width}-{purpose}-full.png"
                    page.screenshot(path=str(dest),full_page=True,animations="disabled")
                    with Image.open(dest) as img:
                        assert img.width==width and img.height>height
                        bitmap=[img.width,img.height]
                    evidence.append({"width":width,"purpose":purpose,"selectedRegion":selected,
                                     "skus":skus,"viewportHeight":height,"fullScreenshot":dest.name,
                                     "bitmap":bitmap,"noRegionHTMLGenerated":True,"linkClickNotPerformed":True,"phoneCTAHitTest":True,"productLinkHitTests":2})
                    print("HUB_INTERACTION_PASS",width,purpose,",".join(skus),bitmap)
                page.locator("#clearSearch").click()
                assert page.locator("#regionSearch").input_value()==""
                assert page.locator('[role="option"]').count()==16
                context.close()
            browser.close()
    finally:
        proc.terminate()
        proc.wait(timeout=10)
    report={"results":evidence,"totalBrowserCases":len(evidence),
        "regionSearchSelectPass":True,"skuURLCheckPass":True,"phoneCTAHrefPass":True,"phoneCTAHitTestPass":True,"productTapTargetPass":True,
        "legacyPathsPreserved":324,"newRegionalHTML":0,"onePurposeGuideHTML":1,
        "mobileWidth":390,"desktopWidth":1440,"deploymentPerformed":False,
        "currentSellerPricesVerified":False,"humanEditorialApproved":False}
    (out/"browser-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf-8")
    assert len(evidence)==6
    print("HUB_BROWSER_AUDIT="+json.dumps({k:v for k,v in report.items() if k!="results"},ensure_ascii=False))

if __name__=="__main__":main()
