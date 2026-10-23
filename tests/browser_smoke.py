"""Run with: python tests/browser_smoke.py. Chromium is optional for normal CI."""
from __future__ import annotations
import functools
import http.server
import json
import threading
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from v5.engine import ROOT,build

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def main():
    build('ansan-promotion-plant')
    path=ROOT/'dist/ansan-promotion-plant'
    results=ROOT/'reports/ansan-promotion-plant/screenshots'
    results.mkdir(parents=True,exist_ok=True)
    h=functools.partial(Handler,directory=str(path))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),h)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    findings=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
            for label,w,h in [('desktop',1280,840),('mobile',390,844)]:
                page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
                response=page.goto(base+'/',wait_until='networkidle')
                if response.status!=200:raise AssertionError(f'{label} homepage not HTTP 200')
                page.locator('h1').wait_for()
                dims=page.evaluate('({scroll:document.documentElement.scrollWidth,inner:innerWidth})')
                if dims['scroll']>dims['inner']+1:raise AssertionError(f'{label} horizontal overflow: {dims}')
                images=page.locator('img').evaluate_all('(nodes) => nodes.map(n => ({complete:n.complete, natural:n.naturalWidth}))')
                if not images or any(not x['complete'] or x['natural']<=0 for x in images):
                    raise AssertionError(f'{label} image failed: {images}')
                assert page.get_by_role('navigation',name='다른 글 페이지').count()==1
                assert page.get_by_role('link',name='화분 예산 계산기').count()==1
                shot=results/(label+'.png')
                page.screenshot(path=str(shot),full_page=True)
                findings.append({'viewport':label,'width':w,'scrollWidth':dims['scroll'],'images':len(images),'png':str(shot),'status':'pass'})
                page.close()
            page=browser.new_page(viewport={'width':390,'height':844})
            response=page.goto(base+'/'+quote('견적계산기.html'),wait_until='networkidle')
            assert response.status==200
            page.locator('#sku').select_option('D149')
            page.locator('#quantity').fill('3')
            page.get_by_role('button',name='예산 계산').click()
            value=page.locator('#estimate').text_content()
            if '195,000원' not in value:raise AssertionError('Unexpected calculator output: '+value)
            findings.append({'module':'calculator','SKU':'D149','quantity':3,'result':value,'status':'pass'})
            response=page.goto(base+'/500.html',wait_until='domcontentloaded')
            if response.status!=404:raise AssertionError('Missing URL did not return 404')
            findings.append({'module':'missing-url','statusCode':404,'status':'pass'})
            page.close();browser.close()
    finally:
        server.shutdown();server.server_close();thread.join(timeout=2)
    manifest=ROOT/'reports/ansan-promotion-plant/browser-smoke.json'
    manifest.write_text(json.dumps({'findings':findings,'overall':'pass'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'findings':findings,'overall':'pass'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
