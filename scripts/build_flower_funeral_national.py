"""Nationwide funeral-hall rollout, gated by independently verified hall registry.

Never synthesize hall names or addresses from regional names. Preview only until
explicit design approval, product-price verification and live deployment checks.
"""
from __future__ import annotations
import argparse, hashlib, html, json, random, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data/flower/funeral_halls_verified.json"
POOL=ROOT/"data/pools/flower_funeral_sample_pool.json"
OUT=ROOT/"dist/flower-funeral-national-preview"
TITLE="{hall} 근조화환 주문 가격안내"
SEED=20261027

def load():
    records=json.loads(REGISTRY.read_text(encoding="utf-8"))
    groups=json.loads(POOL.read_text(encoding="utf-8"))["groups"]
    seen=set()
    for record in records:
        if not all(record.get(k) for k in ("name","address","sourceUrl","verifiedAt","region")):
            raise ValueError("Unverified hall: no name/address/source/date/region")
        if not str(record["sourceUrl"]).startswith("https://"):
            raise ValueError("Hall source must be a verifiable HTTPS URL")
        if record["name"] in seen:raise ValueError("Duplicate hall")
        seen.add(record["name"])
    if not all(len(v)>=3 for v in groups.values()):raise ValueError("Pool buckets too narrow")
    return records,groups

def section_text(pool,hall,key):
    sentences=pool[key].copy()
    random.Random(int(hashlib.sha256((str(SEED)+hall+key).encode()).hexdigest()[:14],16)).shuffle(sentences)
    return " ".join(sentences)

def render(record,groups):
    name=html.escape(record["name"])
    title=html.escape(TITLE.format(hall=record["name"]))
    intro=f'{name}으로 근조화환을 보내려면 장례식장 주소, 빈소와 상주명, 희망 전달 시간을 확인해 주세요.'
    sections="".join('<section><h2>'+html.escape({"intro":"조문을 준비하는 마음","facility":"장례식장 정보 확인","product":"근조화환 종류 선택","ribbon":"리본 문구","delivery":"꽃 제작과 배송","etiquette":"조문 예절","order":"전화 주문 준비"}.get(key,key))+'</h2><p>'+html.escape(section_text(groups,record["name"],key))+'</p></section>' for key in ("intro","facility","product","ribbon","delivery","etiquette","order"))
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+title+' | 날마다꽃</title><style>*{box-sizing:border-box}body{font-family:system-ui,sans-serif;margin:0;color:#163d31;background:#fbfaf6;line-height:1.8}.wrap{width:min(980px,calc(100% - 36px));margin:auto}header{padding:20px;background:#eaf4eb}header strong{color:#166047}.hero{padding:35px 0;background:#f3f7ee}h1{font-size:clamp(25px,4vw,40px)}.layout{display:grid;grid-template-columns:1fr 210px;gap:26px;margin-top:30px}article section{border-bottom:1px solid #e2e8e1;margin-bottom:20px}aside{background:#eaf4eb;border-radius:12px;padding:20px;align-self:start}table{border-collapse:collapse;width:100%}td,th{padding:12px;border-bottom:1px solid #ddd;text-align:left}a{color:#11694c}@media(max-width:650px){.layout{grid-template-columns:1fr}}</style></head><body><header><div class="wrap"><strong>✿ 날마다꽃</strong> · 전국 근조화환 상담 1844-0644</div></header><div class="hero"><div class="wrap"><h1>'+title+'</h1><p>'+intro+'</p><p>주소: '+html.escape(record["address"])+'</p><p>공통 근조화환 상품 이미지 사용 예정 — 시설 건물 사진은 사용하지 않습니다.</p></div></div><main class="wrap layout"><article>'+sections+'<section><h2>근조화환 종류별 가격안내</h2><p>상품별 실제 판매 금액과 배송비 검증 전이므로 가격을 게시하지 않습니다. 상담으로 확인해 주세요.</p><table><tr><th>상품 구분</th><th>가격</th></tr><tr><td>근조화환 기본형</td><td>상담 확인</td></tr><tr><td>근조화환 고급형</td><td>상담 확인</td></tr><tr><td>근조화환 특대형</td><td>상담 확인</td></tr></table></section></article><aside><h2>전화 주문 상담</h2><p>장례식장명·빈소·발신인·리본 문구를 알려주세요.</p><a href="tel:18440644">1844-0644 전화하기</a></aside></main></body></html>')

def build():
    records,groups=load()
    OUT.mkdir(parents=True,exist_ok=True)
    pages=[]
    for i,record in enumerate(records,1):
        filename=f"hall-{i:05d}.html"
        (OUT/filename).write_text(render(record,groups),encoding="utf-8")
        pages.append({"name":record["name"],"path":filename,"sourceUrl":record["sourceUrl"],"verifiedAt":record["verifiedAt"]})
    (OUT/"manifest.json").write_text(json.dumps({"mode":"preview-noindex","numberOfHalls":len(pages),"pages":pages},ensure_ascii=False,indent=2),encoding="utf-8")
    (OUT/"robots.txt").write_text("User-agent: *\nDisallow: /\n",encoding="utf-8")
    print(json.dumps({"pages":len(pages),"mode":"preview-noindex"},ensure_ascii=False))
if __name__=="__main__":build()
