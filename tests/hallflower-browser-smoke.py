"""Real Chromium checks for Hallflower three-seed preview (synthetic data only)."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build_hallflower.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
builder.build()
root=ROOT/'dist/hallflower-preview'
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(root)))
Thread(target=server.serve_forever,daemon=True).start()
origin='http://127.0.0.1:'+str(server.server_port)
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for width in (390,1440):
            page=browser.new_page(viewport={'width':width,'height':844})
            page.goto(origin,wait_until='networkidle')
            assert page.locator('h1').count()==1
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),str(width)+' horizontal overflow'
            links=page.locator('a[href^="/halls/"]')
            assert links.count()==3
            for i in range(3):
                links.nth(i).click()
                assert page.locator('h1').count()==1
                assert page.locator('.card').count()==5
                assert page.locator('a[href^="https://fwith.co.kr/shop/item.php?it_id="]').count()==5
                assert page.locator('button#make-note').is_enabled()
                assert page.locator('a[href="tel:18440644"]').count()>0
                page.locator('input[name="빈소"]').fill('TEST-ROOM-101')
                page.locator('input[name="보내는분"]').fill('TEST-SENDER-ONLY')
                page.locator('#make-note').click()
                assert 'TEST-ROOM-101' in page.locator('#note-output').inner_text()
                assert 'TEST-ROOM-101' not in page.url
                assert 'TEST-SENDER-ONLY' not in page.url
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                page.goto(origin,wait_until='networkidle')
            page.close()
        context=browser.new_context(java_script_enabled=False)
        page=context.new_page();page.goto(origin+'/halls/1-fh-24ec0a8cbedf5c24ef4f.html')
        assert page.locator('#make-note').is_disabled()
        page.locator('input[name="빈소"]').fill('SYNTHETIC-ROOM')
        page.locator('input[name="빈소"]').press('Enter')
        assert 'SYNTHETIC-ROOM' not in page.url
        context.close()
        browser.close()
    print('HALLFLOWER_BROWSER_PASS: 390/1440 viewport, 3 pages, 5 products, fail closed')
finally:server.shutdown()
