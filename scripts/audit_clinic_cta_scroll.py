"""Read-only interaction test of the mobile fixed CTA against real isolated HTML/CSS."""
from __future__ import annotations
import json, subprocess, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

SITES=("clinicflower","clinicopen","clinicpresent")
VIEWPORTS=((390,844),(640,900),(1440,900))
def run(root:Path,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    evidence=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome",args=["--no-sandbox"]) if Path("/usr/bin/google-chrome").exists() else p.chromium.launch(headless=True,args=["--no-sandbox"])
        for site in SITES:
            base=root/"public"/"sites"/site
            assets=base/"assets"
            if not assets.exists(): assets.symlink_to(Path("../../assets"))
            proc=subprocess.Popen(["python","-m","http.server","18766","--bind","127.0.0.1","--directory",str(base)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            try:
                for _ in range(40):
                    try:
                        with urllib.request.urlopen("http://127.0.0.1:18766/r/00139.html",timeout=1) as res: assert res.status==200
                        break
                    except Exception:time.sleep(.2)
                else:raise RuntimeError("Local HTTP unavailable")
                for width,height in VIEWPORTS:
                    context=browser.new_context(viewport={"width":width,"height":height},device_scale_factor=1)
                    page=context.new_page()
                    page.goto("http://127.0.0.1:18766/r/00139.html",wait_until="networkidle")
                    # Disable the page's smooth-scroll animation for deterministic hit testing.
                    page.evaluate("() => {document.documentElement.style.scrollBehavior='auto';document.body.style.scrollBehavior='auto'}")
                    page.evaluate("() => document.fonts.ready")
                    metrics=page.evaluate("""() => {
                      const fixed=document.querySelector('.mobileCall');
                      const button=document.querySelector('.footCall .call');
                      const img=document.querySelector('img');
                      const body=document.body;
                      const cs=getComputedStyle(fixed);
                      return {fixedDisplay:cs.display,fixedPosition:cs.position,fixedHeight:fixed.getBoundingClientRect().height,bodyPaddingBottom:parseFloat(getComputedStyle(body).paddingBottom),imageDecoded:!!(img&&img.complete&&img.naturalWidth>0),buttonHref:button?.getAttribute('href'),documentHeight:document.documentElement.scrollHeight,viewport:innerHeight};
                    }""")
                    assert metrics["imageDecoded"] and metrics["buttonHref"]=="tel:1844-0644"
                    if width<=640:
                        assert metrics["fixedDisplay"]=="flex"
                        assert metrics["fixedPosition"]=="fixed"
                        assert metrics["bodyPaddingBottom"]>=metrics["fixedHeight"],(site,width,metrics)
                    else:
                        assert metrics["fixedDisplay"]=="none"
                    states=[]
                    for name,position in (("top",0),("middle",0.5),("bottom",1)):
                        state=page.evaluate("""(v) => {
                          const max=document.documentElement.scrollHeight-innerHeight;
                          scrollTo(0,Math.round(max*v));
                          const fixed=document.querySelector('.mobileCall').getBoundingClientRect();
                          const target=document.querySelector('.footCall .call').getBoundingClientRect();
                          const overlap=!(target.bottom<=fixed.top || target.top>=fixed.bottom);
                          return {scrollY,scrollMax:max,fixedTop:fixed.top,footerCTATop:target.top,footerCTABottom:target.bottom,rawOverlap:overlap};
                        }""",position)
                        state["position"]=name
                        states.append(state)
                    # Explicitly scroll footer CTA to the center of the unobstructed viewport
                    hit=page.evaluate("""() => {
                      const a=document.querySelector('.footCall .call');
                      a.scrollIntoView({behavior:'instant',block:'center',inline:'nearest'});
                      const r=a.getBoundingClientRect(),x=Math.max(1,Math.min(innerWidth-1,(r.left+r.right)/2)),y=Math.max(1,Math.min(innerHeight-1,(r.top+r.bottom)/2));
                      const target=document.elementFromPoint(x,y);
                      return {ctaTop:r.top,ctaBottom:r.bottom,x,y,hit:!!(target&&(target===a||a.contains(target))),targetTag:target?.tagName,scrollY};
                    }""")
                    assert hit["hit"],(site,width,"footer CTA occluded",hit)
                    # Anchor remains tappable after reaching the document bottom;
                    # body bottom padding offsets the intentional fixed bar.
                    page.evaluate("() => scrollTo(0,document.documentElement.scrollHeight)")
                    final=page.evaluate("""() => {
                       const a=document.querySelector('.footCall .call');
                       const r=a.getBoundingClientRect(),fixed=document.querySelector('.mobileCall').getBoundingClientRect();
                       return {top:r.top,bottom:r.bottom,fixedTop:fixed.top,scrollY,footerCTAVisible:r.bottom>0&&r.top<innerHeight,permanentlyObscured:fixed.height>0&&r.top>=fixed.top};
                    }""")
                    assert not final["permanentlyObscured"],(site,width,"footer CTA remains under overlay",final)
                    file=out/(site+"-"+str(width)+"-bottom-viewport.png")
                    page.screenshot(path=str(file),full_page=False,animations="disabled")
                    record={"site":site,"width":width,"height":height,"fixed":metrics,"positions":states,"footerHitTest":hit,"finalBottom":final,"screenshot":file.name,"passed":True}
                    print("CTA_SCROLL_PASS",site,width,json.dumps({"hit":hit["hit"],"fixedHeight":metrics["fixedHeight"],"padding":metrics["bodyPaddingBottom"],"final":final},ensure_ascii=False))
                    evidence.append(record)
                    context.close()
            finally:
                proc.terminate()
                proc.wait(timeout=10)
        browser.close()
    (out/"cta-scroll-evidence.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    assert len(evidence)==9
if __name__=="__main__":
    import sys
    run(Path(sys.argv[1]),Path(sys.argv[2]))
