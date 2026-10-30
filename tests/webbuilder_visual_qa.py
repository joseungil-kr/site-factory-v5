"""Offline PC/mobile screenshot QA. Does not deploy, authenticate or call the public site."""
from __future__ import annotations
import functools
import http.client
import http.server
import json
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "webbuilder"
OUT = ROOT / "reports" / "webbuilder" / "visual"

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

def main():
    assert (DIST / "industry" / "watertank" / "index.html").exists(), "Build 42-page site first"
    OUT.mkdir(parents=True, exist_ok=True)
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(Handler, directory=str(DIST))
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    targets = [("/", "home"), ("/industry/leak/", "original-leak"),
               ("/industry/waterproof/", "new-waterproof"),
               ("/industry/skycar/", "new-skycar"),
               ("/industry/watertank/", "new-watertank"),
               ("/guide/pricing/", "pricing"), ("/guide/faq/", "faq")]
    findings = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            for label, width, height, is_mobile in [
                ("pc1440", 1440, 900, False), ("mobile390", 390, 844, True)
            ]:
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    is_mobile=is_mobile, has_touch=is_mobile, device_scale_factor=1,
                )
                page = context.new_page()
                for uri, name in targets:
                    response = page.goto(origin + uri, wait_until="networkidle", timeout=45000)
                    assert response is not None and response.status == 200, (label, uri, "HTTP")
                    page.locator("h1").first.wait_for()
                    metrics = page.evaluate("""() => ({
                        scrollWidth: document.documentElement.scrollWidth,
                        clientWidth: document.documentElement.clientWidth,
                        images: [...document.images].map(i => ({
                            src: new URL(i.src).pathname, complete: i.complete,
                            width: i.naturalWidth
                        })),
                        hasPhone: [...document.querySelectorAll('a[href^="tel:"]')]
                           .some(a => a.getAttribute('href') === 'tel:01024900555'),
                        hasFooter: document.body.textContent.includes('사업자 : 인터피아드'),
                        robots: document.querySelector('meta[name="robots"]')?.content,
                        h1: document.querySelectorAll('h1').length,
                        links: document.querySelectorAll('a[href^="/industry/"]').length,
                        navigation: [...document.querySelectorAll('.nav a')].map(x => {
                          const r = x.getBoundingClientRect();
                          return {left: r.left, right: r.right, height: r.height};
                        }),
                        forbiddenExamples: ['*.leak119.net', '*.skycar24hr.com',
                            'leak119.nalmada.net'].filter(s => document.body.textContent.includes(s))
                    })""")
                    assert metrics["scrollWidth"] <= metrics["clientWidth"] + 2, (
                        label, uri, "horizontal overflow", metrics
                    )
                    assert metrics["images"] and all(
                        i["complete"] and i["width"] >= 768 for i in metrics["images"]
                    ), (label, uri, "image loading", metrics["images"])
                    assert metrics["hasPhone"] and metrics["hasFooter"], (label, uri, "contact missing")
                    assert metrics["robots"] == "noindex,nofollow,noarchive", (label, uri, "noindex")
                    assert metrics["h1"] == 1 and not metrics["forbiddenExamples"], (label, uri, "copy")
                    assert len(metrics["navigation"]) == 5, (label, uri, "nav count")
                    assert all(link["left"] >= -1 and link["right"] <= width + 1
                               and link["height"] >= (30 if is_mobile else 20)
                               for link in metrics["navigation"]), (
                        label, uri, "clipped header navigation", metrics["navigation"])
                    screenshot = OUT / f"{label}-{name}.png"
                    page.screenshot(path=str(screenshot), full_page=True, animations="disabled")
                    findings.append({"device": label, "path": uri,
                                     "screenshot": str(screenshot), **metrics})
                    print("VISUAL_PASS", label, uri, "SVG", len(metrics["images"]), "overflow=0")
                context.close()
            browser.close()
        conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        conn.request("GET", "/definitely-missing-path/")
        response = conn.getresponse()
        assert response.status == 404, ("404 semantics", response.status)
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    (OUT / "results.json").write_text(json.dumps(
        {"status": "PASS", "screenshots": len(findings), "devices": [390, 1440],
         "brokenImages": 0, "overflow": 0, "findings": findings},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("WEBBUILDER_VISUAL_PASS", len(findings), "screenshots")

if __name__ == "__main__":
    main()
