"""Audit two venue pages, historical seller notice scope, images and 390/1440 pixels."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent

def check(out):
    ledger=json.loads((HERE/"facility-evidence.json").read_text())
    mapping=json.loads((HERE/"sentence-source-map.json").read_text())
    assert len(ledger["facilities"])==2 and len(mapping["mappings"])>=6
    result=json.loads((out/"comparison.json").read_text())
    assert result["createdPages"]==2 and result["indexEligible"]==0
    assert result["sameBaselineURLsChanged"]==0 and result["oldFixed50Changed"]==0
    observed=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for venue in ledger["facilities"]:
            vid=venue["id"]
            htmlfile=out/vid/"index.html"
            old=(out/vid/"before.html").read_text()
            new=htmlfile.read_text()
            assert old!=new and "noindex,nofollow" in new
            assert not re.search(r'<link[^>]+canonical',new)
            assert new.count("shop/item.php?it_id=")==2
            assert "현재" in new and "미확인" in new
            assert all('data-role="'+role+'"' in new for role in
                       ["venue-identity","buyer-decision","venue-checklist","product-compare",
                        "seller-notice","checkout-boundary","visual-reference"])
            if vid=="sejong-eunhasu":
                assert "축하 2단 오브제" in new and "근조용으로 전용하지 않습니다" in new
                assert "바로 주문 가능한 확정 SKU는 없습니다" in new
                assert "C205" not in new
                assert 'data-role="operator-dated-policy"' in new
                assert "2018-10-01" in new
                assert "신근조화환대" in new
                assert "기존 3단화환 반입 금지" in new
                assert "현재" in new and "확인한 결과는 아닙니다" in new
                assert "축하용 C030을" in new and "근조용 대체상품으로 권장하지 않습니다" in new
            else:
                assert "전날" in new and "당일" in new
                assert "근조 특대" not in new
                assert 'data-role="operator-dated-policy"' not in new
                assert hashlib.sha256(new.encode()).hexdigest()=="8ef8ae5cf6ef019aad3262498df7ef1ff613dd94f38ee342ea566d747c3611ed", "Wonju HTML changed without new operator evidence"
            for width in (390,1440):
                page=browser.new_page(viewport={"width":width,"height":900},
                                      device_scale_factor=1)
                page.goto(htmlfile.resolve().as_uri(),wait_until="load")
                pic=page.locator("figure img")
                pic.scroll_into_view_if_needed()
                pic.evaluate("""async img => {
                    img.loading='eager';
                    await img.decode();
                    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
                }""")
                assert pic.evaluate("img => img.complete && img.naturalWidth >= 768")
                page.evaluate("window.scrollTo(0,0)")
                shot=out/(vid+"-"+str(width)+".png")
                page.screenshot(path=str(shot),full_page=True,animations="disabled")
                img=Image.open(shot).convert("RGB")
                rect=pic.evaluate("""e => {let r=e.getBoundingClientRect();
                    return {x:r.left+scrollX,y:r.top+scrollY,w:r.width,h:r.height}}""")
                area=img.crop((int(rect["x"]+rect["w"]*.2),int(rect["y"]+rect["h"]*.2),
                               int(rect["x"]+rect["w"]*.8),int(rect["y"]+rect["h"]*.8)))
                entropy=round(area.entropy(),2)
                assert entropy > 3.0,(vid,width,entropy)
                dims=page.evaluate("""() => ({
                  screenWidth:innerWidth,bodyWidth:document.documentElement.scrollWidth,
                  productLinks:[...document.querySelectorAll('a[href*="shop/item.php?it_id="]')].length,
                  sellerForms:document.querySelectorAll('form').length,
                  noindex:document.querySelector('meta[name=robots]')?.content,
                  imageLoaded:[...document.images].filter(i=>i.complete&&i.naturalWidth>0).length
                })""")
                assert dims["bodyWidth"]<=dims["screenWidth"],dims
                assert dims["productLinks"]==2 and dims["sellerForms"]==0
                assert dims["noindex"]=="noindex,nofollow" and dims["imageLoaded"]==1
                observed.append(dict(venue=vid,viewport=width,pixelEntropy=entropy,
                                     screenshot=shot.name,**dims))
                page.close()
        browser.close()
    (out/"screen-evidence.json").write_text(json.dumps(observed,ensure_ascii=False,indent=2)+"\n")
    assert len(observed)==4
    print("TWO_VENUE_REAL_RENDER_PASS",json.dumps(observed,ensure_ascii=False))
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    a=parser.parse_args()
    check(a.out)
