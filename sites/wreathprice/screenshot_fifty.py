"""Screenshot actual locally generated WreathPrice HTML, never visit production."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def main(root, evidence):
    root=root.resolve(); evidence=evidence.resolve()
    evidence.mkdir(parents=True,exist_ok=True)
    observations=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for code in ["1111010100","1111010200","4111010100"]:
            html=root/"locality"/(code+".html")
            if not html.is_file(): continue
            for width in (390,1440):
                page=browser.new_page(viewport={"width":width,"height":900},
                                      device_scale_factor=1)
                # Use local file URL with generated /assets absolute paths replaced
                # by file URLs, ensuring screenshots use real generated HTML/CSS.
                contents=html.read_text(encoding="utf-8")
                contents=contents.replace('href="/assets/site.css"',
                         'href="'+(root/"assets"/"site.css").as_uri()+'"')
                contents=contents.replace('src="/assets/',
                         'src="'+(root/"assets").as_uri()+'/')
                page.goto(html.as_uri())
                # Direct file URL does not resolve /assets; inject only resource paths.
                page.set_content(contents,wait_until="load")
                page.screenshot(path=str(evidence/f"{code}-{width}.png"),full_page=True)
                metrics=page.evaluate("""() => ({
                  innerWidth: window.innerWidth,
                  scrollWidth: document.documentElement.scrollWidth,
                  productLinks: [...document.querySelectorAll('a[href*="shop/item.php?it_id="]')].length,
                  imageCount: [...document.images].length,
                  loadedImages: [...document.images].filter(i => i.complete && i.naturalWidth>0).length,
                  narrowButtons: [...document.querySelectorAll('a[href*="shop/item.php?it_id="]')].filter(a => a.getBoundingClientRect().height<44).length
                })""")
                assert metrics["scrollWidth"] <= metrics["innerWidth"],metrics
                assert metrics["productLinks"]==5,metrics
                assert metrics["loadedImages"]==5,metrics
                if width==390: assert metrics["narrowButtons"]==0,metrics
                observations.append(dict(code=code,width=width,**metrics))
                page.close()
        browser.close()
    assert len(observations)>=4
    (evidence/"screen-observations.json").write_text(json.dumps(observations,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(observations,ensure_ascii=False))
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",required=True,type=Path)
    parser.add_argument("--evidence",required=True,type=Path)
    args=parser.parse_args()
    main(args.root,args.evidence)
