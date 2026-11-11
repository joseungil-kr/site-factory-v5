"""Verify real decoded image pixels on generated WreathPrice HTML at 390/1440.
No production requests, deployment, or credentials.
"""
import argparse, hashlib, json
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageStat
from playwright.sync_api import sync_playwright

IMAGE_FILES = ("funeral-wreath.webp","celebration-wreath.webp","flower-detail.webp",
               "ribbon-guide.webp","florist-preparation.webp")

def main(root, evidence):
    root=root.resolve(); evidence=evidence.resolve()
    evidence.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((root.parent/"image-manifest.json").read_text())["images"]
    known={x["filename"]:x for x in manifest}
    evidence_images=[]
    for filename in IMAGE_FILES:
        payload=(root/"assets"/filename).read_bytes()
        digest=hashlib.sha256(payload).hexdigest()
        assert digest == known[filename]["sha256"], filename
        im=Image.open(BytesIO(payload)).convert("RGB")
        assert im.width == known[filename]["width"] and im.height == known[filename]["height"], filename
        assert im.getbbox() and im.getextrema()[0][1] > im.getextrema()[0][0],filename
        evidence_images.append(dict(name=filename,bytes=len(payload),sha256=digest,
                                    width=im.width,height=im.height,sourceEntropy=round(im.entropy(),3)))
    observations=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for code in ("1111010100","1111010200","1123010100","5172034000","5013025300"):
            html=root/"locality"/(code+".html")
            assert html.is_file(),html
            for width in (390,1440):
                page=browser.new_page(viewport={"width":width,"height":900},
                                      device_scale_factor=1)
                contents=html.read_text(encoding="utf-8")
                contents=contents.replace('href="/assets/site.css"',
                         'href="'+(root/"assets"/"site.css").as_uri()+'"')
                contents=contents.replace('src="/assets/',
                         'src="'+(root/"assets").as_uri()+'/')
                page.goto(html.as_uri())
                page.set_content(contents,wait_until="load")
                image_elements=page.locator("figure.card img")
                assert image_elements.count()==5,(code,width,image_elements.count())
                for i in range(5):
                    img=image_elements.nth(i)
                    img.scroll_into_view_if_needed(timeout=15000)
                    img.evaluate("""async (img) => {
                      img.loading = 'eager';
                      await img.decode();
                      await new Promise(resolve => requestAnimationFrame(() =>
                        requestAnimationFrame(resolve)));
                    }""")
                    assert img.evaluate("(img) => img.complete && img.naturalWidth > 0")
                page.evaluate("window.scrollTo(0,0)")
                page.wait_for_timeout(150)
                shot=evidence/f"{code}-{width}.png"
                page.screenshot(path=str(shot),full_page=True,animations="disabled")
                png=Image.open(shot).convert("RGB")
                rects=page.locator("figure.card img").evaluate_all(
                  """els => els.map(el => {const r=el.getBoundingClientRect();
                    return {x:r.left+scrollX,y:r.top+scrollY,w:r.width,h:r.height}})""")
                visual=[]
                for i,r in enumerate(rects):
                    # Inset removes borders/caption; measure actual image pixel diversity.
                    x1=max(0,int(r["x"]+r["w"]*.12)); x2=min(png.width,int(r["x"]+r["w"]*.88))
                    y1=max(0,int(r["y"]+r["h"]*.12)); y2=min(png.height,int(r["y"]+r["h"]*.88))
                    crop=png.crop((x1,y1,x2,y2))
                    assert crop.width>30 and crop.height>20,(code,width,i,r)
                    entropy=round(crop.entropy(),3)
                    colors=crop.resize((40,20)).getcolors(800)
                    distinct=len(colors) if colors else 800
                    assert entropy>3.0 and distinct>30,(code,width,i,entropy,distinct)
                    visual.append(dict(asset=IMAGE_FILES[i],pixelEntropy=entropy,distinctSampleColors=distinct))
                metrics=page.evaluate("""() => ({
                  innerWidth:innerWidth,scrollWidth:document.documentElement.scrollWidth,
                  productLinks:[...document.querySelectorAll('a[href*="shop/item.php?it_id="]')].length,
                  imageCount:document.images.length,
                  decodedImages:[...document.images].filter(i=>i.complete&&i.naturalWidth>0).length,
                  narrowButtons:[...document.querySelectorAll('a[href*="shop/item.php?it_id="]')]
                    .filter(a=>a.getBoundingClientRect().height<44).length
                })""")
                assert metrics["scrollWidth"]<=metrics["innerWidth"],metrics
                assert metrics["productLinks"]==5 and metrics["decodedImages"]==5,metrics
                if width==390:assert metrics["narrowButtons"]==0,metrics
                observations.append(dict(code=code,width=width,**metrics,visibleImagePixels=visual))
                page.close()
        browser.close()
    assert len(observations)==10
    result=dict(assets=evidence_images,rendered=observations)
    (evidence/"screen-observations.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True,type=Path)
    ap.add_argument("--evidence",required=True,type=Path)
    args=ap.parse_args()
    main(args.root,args.evidence)
