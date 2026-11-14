#!/usr/bin/env python3
"""Generate noindex winterbbang HTML previews from the existing copy pool.
Local file generation only; this script never deploys, edits DNS or submits URLs.
"""
from __future__ import annotations
import argparse
import html
import json
import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL_DEFAULT = ROOT / "docs/site-plans/winterbbang/copy-pool.seed.json"
OUT_DEFAULT = ROOT / "preview/winterbbang"
PHONE = "031-407-0103"
ASSET = "/assets/images"

REGIONS = [
 {"name":"서울특별시 강남구 역삼동","slug":"region-seoul-gangnam-yeoksam","blocks":["coffee-pairing","red-bean","batter-supply"]},
 {"name":"서울특별시 마포구 서교동","slug":"region-seoul-mapo-seogyo","blocks":["coffee-rush","tenwon-fill","redbean-supply"]},
 {"name":"경기도 안산시 상록구 본오동","slug":"region-gyeonggi-ansan-bono","blocks":["produce-counter","egg-hygiene","custard-supply"]},
 {"name":"경기도 수원시 팔달구 인계동","slug":"region-gyeonggi-suwon-ingye","blocks":["bunsik-cross","comparison","mix-support"]},
 {"name":"경기도 성남시 분당구 야탑동","slug":"region-gyeonggi-seongnam-yatap","blocks":["tea-pairing","egg-workflow","seasonal-order"]},
 {"name":"경기도 고양시 일산동구 정발산동","slug":"region-gyeonggi-goyang-jeongbalsan","blocks":["twisted-bundle","tenwon-portion","dealer-partner"]},
]
IMAGES = [
 ("hero.webp","겨울 간식 창업을 표현한 생성형 이미지"),
 ("shop-in-shop.webp","기존 매장 샵인샵을 표현한 생성형 이미지"),
 ("menu.webp","붕어빵·잉어빵·계란빵·십원빵을 표현한 생성형 이미지"),
 ("street.webp","야외 간식 판매를 표현한 생성형 이미지"),
 ("ingredients.webp","반죽과 속재료 및 조리 장비를 표현한 생성형 이미지"),
]
CSS = """
*{box-sizing:border-box}body{margin:0;color:#2e2118;background:#fffdf8;font:16px/1.7 system-ui,'Noto Sans KR',sans-serif}
a{color:inherit}.wrap{width:min(1100px,calc(100% - 32px));margin:auto}
header{background:#fff3e3;border-bottom:1px solid #ead7c1}.bar{padding:15px 0;display:flex;justify-content:space-between;align-items:center;gap:12px}
.brand{font-size:1.2rem;font-weight:900;text-decoration:none}.call{background:#d75d22;color:white;text-decoration:none;border-radius:99px;padding:10px 17px;font-weight:800;white-space:nowrap}
.hero{display:grid;grid-template-columns:1fr 1fr;gap:28px;align-items:center;padding:35px 0}.tag{color:#b64b1a;font-weight:800}h1{font-size:clamp(2rem,4vw,3.4rem);line-height:1.18;margin:.4em 0}.lead,.muted{color:#6a5c50}
img{display:block;width:100%;height:auto;object-fit:cover;border-radius:14px}.hero img{aspect-ratio:16/9}.pills{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}.pill{border:1px solid #e9c8a8;background:#fff5e9;padding:4px 10px;border-radius:30px}
section{padding:28px 0}.head h2{font-size:clamp(1.5rem,3vw,2.1rem);line-height:1.3}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.card,.copy{border:1px solid #ead7c1;border-radius:17px;background:#fff;padding:16px;min-width:0;overflow-wrap:anywhere}.card img{aspect-ratio:16/10;margin-bottom:10px}.copygrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.margin{padding:16px;border-left:4px solid #d75d22;background:#fff3e4;border-radius:0 12px 12px 0}.contact{background:#58341f;color:#fff;border-radius:20px;padding:24px;display:flex;justify-content:space-between;align-items:center;gap:20px}.contact p{margin:0;color:#f4e5d8}.contact .call{background:#fff;color:#58341f}.fine{font-size:.86rem;color:#6a5c50}footer{border-top:1px solid #ead7c1;margin-top:36px;padding:22px 0;color:#6a5c50;font-size:.86rem}
@media(max-width:720px){.hero{grid-template-columns:1fr;gap:18px;padding:24px 0}.grid,.copygrid{grid-template-columns:1fr}.contact{display:block}.contact .call{display:inline-block;margin-top:15px}.bar .call{font-size:.86rem;padding:8px 11px}}
"""

def esc(value):
    return html.escape(str(value), quote=True)

def image(filename, alt, eager=False):
    loading = "eager" if eager else "lazy"
    priority = ' fetchpriority="high"' if eager else ""
    return (f'<img src="{ASSET}/{esc(filename)}" alt="{esc(alt)}" '
            f'loading="{loading}" decoding="async"{priority} width="1200" height="840">')

def copy_verified_assets(output_dir):
    """Bundle the five already-committed WebP assets, checking manifest hashes.

    No image generation, network calls or upload happens here. This function
    fails closed if any of the exact GitHub-tracked bytes differ.
    """
    manifest = ROOT / "docs/site-plans/winterbbang/images-manifest.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    expected_names = {name for name, _ in IMAGES}
    assets = data.get("assets", [])
    if {item.get("filename") for item in assets} != expected_names or len(assets) != 5:
        raise ValueError("Exactly the approved five image assets are required")
    dest = output_dir / "assets" / "images"
    dest.mkdir(parents=True, exist_ok=True)
    receipt = []
    for item in assets:
        filename = item["filename"]
        source = ROOT / "assets" / "library" / "winterbbang" / filename
        content = source.read_bytes()
        if content[:4] != b"RIFF" or content[8:12] != b"WEBP":
            raise ValueError("Invalid WebP image: " + filename)
        digest = hashlib.sha256(content).hexdigest()
        if digest != item["sha256"] or len(content) != item["bytes"]:
            raise ValueError("Asset SHA256/size mismatch: " + filename)
        destination = dest / filename
        if source.resolve() != destination.resolve():
            shutil.copyfile(source, destination)
        if hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
            raise ValueError("Preview asset copy readback failed: " + filename)
        receipt.append({"filename": filename, "sha256": digest, "bytes": len(content)})
    return receipt


def load_pool(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if len(data.get("blocks", [])) < 20:
        raise ValueError("copy pool missing or too small")
    return {b["decision"]: b["copy"] for b in data["blocks"]}

def render(pool, region=None):
    home = region is None
    name = "서울·경기" if home else region["name"]
    title = f"{name} 붕어빵·잉어빵·계란빵·십원빵 창업 상담"
    intro = ("기존 매장에 더하는 샵인샵부터 노점형 판매까지, 운영 공간과 메뉴에 맞는 겨울 간식 창업을 상담하세요."
             if home else f"{name}에서 겨울 간식 판매를 검토한다면 판매 장소, 운영 시간, 메뉴별 조리 공간부터 확인해 보세요.")
    keys = ["initial-choice","coffee-pairing","batter-supply"] if home else region["blocks"]
    heads = ["장소와 운영 동선","메뉴와 조리 준비","반죽·속재료 공급 상담"]
    copies = [pool[k] for k in keys]
    cards = [
      ("기존 매장 샵인샵", image("shop-in-shop.webp", IMAGES[1][1]), "카페·무인카페·청과점·분식점·꽈배기점·전통차집 등 기존 업종에 간식 메뉴를 추가하는 방식을 상담하세요."),
      ("네 가지 겨울 간식", image("menu.webp", IMAGES[2][1]), "붕어빵·잉어빵·계란빵·십원빵 모두 창업 및 공급 상담이 가능합니다."),
      ("노점형 판매 검토", image("street.webp", IMAGES[3][1]), "가게 앞이나 야외 판매는 장소 사용 권한과 관련 신고·시설 기준을 확인한 뒤 준비해야 합니다."),
      ("식자재 납품 지원", image("ingredients.webp", IMAGES[4][1]), "반죽·팥소·슈크림 등 필요한 원료와 메뉴별 조리 구성을 담당자와 상담할 수 있습니다."),
    ]
    card_html = "".join(f'<article class="card">{img}<h3>{esc(h)}</h3><p>{esc(t)}</p></article>' for h,img,t in cards)
    copy_html = "".join(f'<article class="copy"><h3>{esc(h)}</h3><p>{esc(c)}</p></article>' for h,c in zip(heads,copies))
    margin = ("예상 매출총이익률 60~70%는 판매가에서 재료비만 차감한 비율입니다. "
              "인건비·임차료·전기료·포장비·카드수수료 등 다른 비용을 차감한 순이익률이 아니며, "
              "실제 결과는 판매가격·재료 사용량·손실 등에 따라 달라질 수 있습니다.")
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | 백세푸드</title><meta name="description" content="{esc(name)} 겨울 간식 창업, 샵인샵 및 식자재 공급 상담.">
<meta name="robots" content="noindex,nofollow"><meta property="og:title" content="{esc(title)} | 백세푸드">
<meta property="og:description" content="겨울 간식 창업 및 공급 상담"><meta property="og:image" content="{ASSET}/hero.webp">
<style>{CSS}</style></head><body>
<header><div class="wrap bar"><a class="brand" href="/">백세푸드<small>분식창업·식자재 상담</small></a><a class="call" href="tel:0314070103">전화 상담 {PHONE}</a></div></header>
<main class="wrap"><section class="hero"><div><span class="tag">WINTER SNACK STARTUP</span><h1>{esc(title)}</h1><p class="lead">{esc(intro)}</p>
<div class="pills"><span class="pill">샵인샵</span><span class="pill">노점형</span><span class="pill">전국 식자재 상담</span></div><a class="call" href="tel:0314070103">백세푸드 창업 담당자에게 문의</a></div>
<div>{image("hero.webp",IMAGES[0][1],True)}</div></section>
<section><div class="head"><span class="tag">STARTUP OPTIONS</span><h2>내 공간과 운영 방식에 맞춰 시작하세요</h2><p class="muted">지역별 실제 장소·신고 조건은 창업 예정지 기준으로 확인해야 합니다.</p></div><div class="grid">{card_html}</div></section>
<section><div class="head"><span class="tag">REGIONAL GUIDE</span><h2>{esc(name)} 창업 준비 체크</h2></div><div class="copygrid">{copy_html}</div></section>
<section><div class="margin"><strong>매출총이익률 안내</strong><p>{esc(margin)}</p></div></section>
<section><div class="contact"><div><h2>창업 및 식자재 공급 상담</h2><p>붕어빵·잉어빵·계란빵·십원빵 / 백세푸드 분식창업 담당자</p></div><a class="call" href="tel:0314070103">{PHONE} 전화하기</a></div></section>
<p class="fine">이미지는 AI 생성 참고 이미지이며 실제 매장·고객·납품 실적 사진이 아닙니다. 영업 장소와 시설 조건은 관할 기관에 확인하세요.</p>
</main><footer><div class="wrap">백세푸드 · 분식창업 담당자 {PHONE} · <a href="tel:0314070103">전화 상담</a></div></footer></body></html>"""

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pool", type=Path, default=POOL_DEFAULT)
    parser.add_argument("--output-dir", type=Path, default=OUT_DEFAULT)
    parser.add_argument("--regions", type=int, default=len(REGIONS), help="number of representative regional pages, 0-6")
    args = parser.parse_args()
    if not 0 <= args.regions <= len(REGIONS):
        parser.error("--regions must be between 0 and 6")
    pool = load_pool(args.pool)
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    pages = [("index.html", render(pool))]
    pages += [(r["slug"] + ".html", render(pool, r)) for r in REGIONS[:args.regions]]
    for filename, content in pages:
        (out / filename).write_text(content, encoding="utf-8")
    assets = copy_verified_assets(out)
    report = {"site":"winterbbang","pages":len(pages),"regionalPages":len(pages)-1,
              "robots":"noindex,nofollow","phone":PHONE,"copyPoolBlocks":len(pool),
              "imagesReferenced":[x[0] for x in IMAGES],"imagesVerified":assets,
              "output":str(out)}
    (out / "render-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))

if __name__ == "__main__":
    main()
