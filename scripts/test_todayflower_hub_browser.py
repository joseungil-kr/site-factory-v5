"""Real Chromium UI audit for isolated 333-row hub (file://, no server)."""
from __future__ import annotations
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

from scripts.build_todayflower_hub_prototype import OUT

def run():
    report={"testedWidths":[],"searches":[],"filters":[],"feeScope":[],"links":[],"screenshots":[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for width,height in ((390,844),(1440,900)):
            page=browser.new_page(viewport={"width":width,"height":height}, device_scale_factor=1)
            errors=[]
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.goto((OUT/"index.html").resolve().as_uri())
            assert page.locator("#count").inner_text()=="333 / 333개 지역"
            assert page.locator("#results button").count()==333
            assert page.evaluate("document.documentElement.scrollWidth<=innerWidth"),width
            page.screenshot(path=str(OUT/f"hub-initial-{width}.png"),full_page=True)
            report["screenshots"].append(f"hub-initial-{width}.png")
            page.locator("#region-search").fill("4315012300")
            assert page.locator("#count").inner_text()=="1 / 333개 지역"
            assert page.locator("#results button").count()==1
            page.locator("#results button").first.click()
            assert page.locator("#region-code").inner_text()=="4315012300"
            assert "제천시 산곡동" in page.locator("#region-name").inner_text()
            assert "충청북도 제천시" in page.locator("#region-parent").inner_text()
            assert page.locator("#fee").is_hidden()
            href=page.locator("#common-link").get_attribute("href")
            assert href=="./buying-guide.html#intent-13",href
            assert (OUT/"buying-guide.html").exists()
            page.screenshot(path=str(OUT/f"hub-selected-2852-{width}.png"),full_page=True)
            report["screenshots"].append(f"hub-selected-2852-{width}.png")
            report["searches"].append({"width":width,"query":"4315012300","matches":1,
                                      "selectedCode":"4315012300","feeVisible":False})
            # Same interface filters exactly, not synthetic hardcoded result.
            page.locator("#region-search").fill("")
            page.locator("#province").select_option("충청북도")
            assert 0<page.locator("#results button").count()<333
            assert all("충청북도" in txt for txt in page.locator("#results button").all_inner_texts())
            report["filters"].append({"width":width,"province":"충청북도",
                                       "matches":page.locator("#results button").count()})
            page.locator("#province").select_option("")
            # Seller fee must not be displayed for 333 general search results.
            # Separate 3 proofs reveal exact SKU/area evidence on selection only.
            assert page.locator("#proof-list button").count()==3
            assert page.locator("#fee").is_hidden()
            first=page.locator("#proof-list button").first
            first.click()
            assert page.locator("#fee").is_visible()
            fee=page.locator("#fee-detail").inner_text()
            region=page.locator("#region-name").inner_text()
            assert region in fee and "B205" in fee and "원" in fee
            assert page.locator("#fee-source").get_attribute("href")=="https://fwith.co.kr/shop/item.php?it_id=B205"
            assert "현행 적용 미확인" in page.locator("#proof-list").inner_text() or "현행 적용" in page.locator("#fee").inner_text()
            report["feeScope"].append({"width":width,"selectedRegion":region,
                                       "sellerSku":"B205","sourceURL":page.locator("#fee-source").get_attribute("href"),
                                       "currentEffective":False})
            page.screenshot(path=str(OUT/f"hub-selected-b205-{width}.png"),full_page=True)
            report["screenshots"].append(f"hub-selected-b205-{width}.png")
            page.locator("#common-link").click()
            assert page.url.endswith("buying-guide.html#intent-13"),page.url
            assert page.locator("#intent-13 h2").inner_text()=="행사장 꽃 반입"
            assert page.locator('section[id^="intent-"]').count()==16
            assert page.evaluate("document.documentElement.scrollWidth<=innerWidth")
            page.screenshot(path=str(OUT/f"guide-{width}.png"),full_page=True)
            report["screenshots"].append(f"guide-{width}.png")
            report["links"].append({"width":width,"guideAnchorResolved":True,
                                    "intentGuideSections":16})
            assert not errors,errors
            report["testedWidths"].append(width)
            page.close()
        browser.close()
    assert len(report["screenshots"])==8
    (OUT/"browser-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TODAYFLOWER_HUB_BROWSER_PASS "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":run()
