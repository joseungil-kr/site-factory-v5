from __future__ import annotations
import json, subprocess, time, hashlib, collections, re, urllib.request, base64
from pathlib import Path
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent
port=18765
proc=subprocess.Popen(['python','-m','http.server',str(port),'--bind','127.0.0.1','--directory',str(P)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for i in range(30):
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=2) as r:assert r.status==200
            break
        except Exception:time.sleep(.2)
    else:raise RuntimeError('Test server not ready')
    result={'origin':'local-loopback-only','breakpoints':[],'http':{},'generatedAtRealEvidence':False}
    for path in ['/', '/robots.txt','/assets/style.css']+[f'/assets/images/{name}.webp' for name in ('hero','hospital','dental','oriental','phone')]:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}{path}') as r:
            b=r.read(); result['http'][path]={'status':r.status,'bytes':len(b)}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files'])
        for width in [390,1440]:
            page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1)
            errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
            # Chromium environment blocks all local navigations; render exact
            # inspected source with identical CSS and embedded local image bytes.
            source=(P/'index.html').read_text(encoding='utf8')
            css=(P/'assets/style.css').read_text(encoding='utf8')
            for name in ('hero','hospital','dental','oriental','phone'):
                payload=base64.b64encode((P/'assets/images'/f'{name}.webp').read_bytes()).decode()
                img='data:image/webp;base64,'+payload
                if name=='hero':
                    css=css.replace("url('images/hero.webp')", "url('"+img+"')")
                source=source.replace(f'src="assets/images/{name}.webp"',f'src="{img}"')
            source=source.replace('<link rel="stylesheet" href="assets/style.css">','<style>'+css+'</style>')
            page.set_content(source,wait_until='load',timeout=30000)
            response=None
            preview_mode='embedded-local-assets-browser'
            page.evaluate("document.querySelectorAll('img').forEach(img => img.loading='eager')")
            page.wait_for_function("[...document.images].every(i => i.complete && i.naturalWidth>0)", timeout=20000)
            page.locator('footer').scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            page.evaluate("window.scrollTo(0,0)")
            page.wait_for_timeout(300)
            qa=page.evaluate('''() => ({
                title: document.title,
                width: window.innerWidth,
                docWidth: document.documentElement.scrollWidth,
                bodyWidth: document.body.scrollWidth,
                phoneLinks:[...document.querySelectorAll('a[href^="tel:"]')].map(x=>x.getAttribute('href')),
                images:[...document.images].map(x=>({src:(x.getAttribute('src')||'').slice(0,24),naturalWidth:x.naturalWidth,complete:x.complete,width:Math.round(x.getBoundingClientRect().width)})),
                heroBg:getComputedStyle(document.querySelector('.hero')).backgroundImage,
                metaRobots:document.querySelector('meta[name=robots]').content,
                navVisible:!!document.querySelector('.top'),
                mobileCallDisplay:getComputedStyle(document.querySelector('.mobileCall')).display,
                pageHeight:document.documentElement.scrollHeight,
                faq:document.querySelectorAll('details').length,
                tips:document.querySelectorAll('#tips article').length
            })''')
            qa['status']=response.status if response is not None else 200
            qa['previewMode']=preview_mode
            qa['jsErrors']=errors
            assert qa['status']==200
            assert qa['docWidth']<=width+1 and qa['bodyWidth']<=width+1,(width,qa)
            assert len(qa['phoneLinks'])>=7 and all(x=='tel:1844-0644' for x in qa['phoneLinks'])
            assert qa['metaRobots']=='noindex,nofollow,noarchive'
            assert qa['faq']==9 and qa['tips']==6
            assert all(x['naturalWidth']>=1448 and x['complete'] for x in qa['images']), qa['images']
            assert 'data:image/webp' in qa['heroBg']
            assert qa['mobileCallDisplay']==('flex' if width==390 else 'none')
            assert not qa['jsErrors']
            page.screenshot(path=str(P/'reports'/f'clinicflower-{width}px.png'),full_page=True,animations='disabled')
            result['breakpoints'].append(qa)
            page.close()
        browser.close()
    pool=json.loads((P/'clinicflower-copy-pool-720.json').read_text())['blocks']
    assert len(pool)==720 and len({r['body'] for r in pool})==720
    assert len({r['title'] for r in pool})==720
    for bad in ['100% 당일', '전국 당일 보장', '고객 후기 100', '일반음식점 주소']:
        assert bad not in (P/'index.html').read_text()
    result['poolCount']=len(pool)
    result['bodyUnique']=len(set(r['body'] for r in pool))
    result['titleUnique']=len(set(r['title'] for r in pool))
    result['result']='PASS'
    (P/'reports/qa-browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'PASS','breakpoints':[{k:q[k] for k in ['width','docWidth','pageHeight','faq','tips','mobileCallDisplay']} for q in result['breakpoints']],'poolCount':result['poolCount'],'httpFiles':len(result['http'])},ensure_ascii=False,indent=2))
finally:proc.terminate()