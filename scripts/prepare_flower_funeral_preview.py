"""Add a useful nationwide funeral-hall directory to the approved QA-only HTML bundle.

Run only AFTER scripts/build_flower_funeral_national.py has passed its full-pair
0.49 gate and created all 1080 noindex pages. No custom-domain attachment or indexing.
"""
from __future__ import annotations

from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "flower-funeral-national-preview"
REPORT = ROOT / "reports" / "flower-funeral" / "pool-1080-1pct-audit.json"
SOURCE = ROOT / "data" / "flower" / "v4_facilities_1080.snapshot.json"

STYLE = """
:root{color-scheme:light}*{box-sizing:border-box}
body{margin:0;background:#fbfaf6;color:#234b3b;font-family:system-ui,-apple-system,'Malgun Gothic',sans-serif;line-height:1.8}
a{color:inherit;text-decoration:none}.container{max-width:1160px;padding:0 22px;margin:auto}
header{background:#fff;border-bottom:1px solid #e1eae3}.header-inner{display:flex;align-items:center;flex-wrap:wrap;gap:22px;justify-content:space-between;padding:17px 0}
.logo{font-size:25px;color:#17634b;font-weight:900}.logo span{color:#d64d7a}.nav{display:flex;gap:20px;flex-wrap:wrap;font-size:14px}
.btn{background:#17654d;color:#fff;font-weight:700;display:inline-block;padding:12px 20px;border-radius:10px}
.hero{background:linear-gradient(115deg,#eaf5eb 0%,#fff2ee 100%);padding:62px 0}
.hero-inner{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);align-items:center;gap:35px}
.kicker{font-size:12px;font-weight:800;color:#5b9478;letter-spacing:.12em}.hero h1{font-size:clamp(32px,4.5vw,55px);line-height:1.27;margin:16px 0}
.hero p{max-width:640px;font-size:17px;color:#526d5d}.flower-mark{border-radius:24px;border:1px solid #e2ebe1;background:#fffdfc;min-height:300px;display:grid;place-content:center;text-align:center;padding:24px}
.flower-mark .symbol{font-size:90px;color:#c56987;line-height:1.1}.flower-mark p{font-size:13px;color:#76867b}
.section{padding:45px 0}.section h2{font-size:25px;line-height:1.4}.sub{color:#627667}
.filters{display:grid;grid-template-columns:2fr 1fr;gap:12px;margin:24px 0}
input,select{background:#fff;border:1px solid #b9d1c1;border-radius:9px;padding:13px;font:inherit;width:100%}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:14px}
.card{display:block;border:1px solid #e0e8e2;border-radius:14px;padding:19px;background:white;min-height:120px}
.card strong{display:block;color:#205741}.card small{color:#658171;display:block}.card:hover{border-color:#82a78c}
.warning{background:#fff7f3;border-left:3px solid #ce8b83;padding:12px 18px;color:#794c45;margin:20px 0;font-size:13px}
footer{background:#1c4536;color:#f0f6ef;padding:27px 0;font-size:14px}
@media(max-width:720px){.nav{font-size:12px;gap:10px}.hero-inner,.filters{grid-template-columns:1fr}.flower-mark{min-height:120px}.flower-mark .symbol{font-size:42px}.hero{padding:38px 0}.section{padding:32px 0}}
"""

def package():
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert report["passes"] and report["maximumSimilarity"] < .49
    assert report["fullPairFailures"] == 0 and report["fullPairComparisons"] == 1165320
    assert source["publicationAllowed"] is False
    records = source["facilities"]
    pages = manifest["pages"]
    assert manifest["mode"] == "noindex-preview" and manifest["qaPasses"] and len(pages) == len(records) == 1080
    assert {r["id"] for r in records} == {p["id"] for p in pages}
    for p in pages:
        file = OUT / p["filename"]
        assert file.is_file() and file.name.startswith("fh-")
        markup = file.read_text(encoding="utf-8")
        assert '<meta name="robots" content="noindex,nofollow">' in markup
        assert '날마다꽃' in markup

    directory = [{"n": p["facility"], "r": p["region"], "u": "/" + p["filename"]}
                 for p in pages]
    (OUT / "halls.json").write_text(json.dumps(directory, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    sample_cards = "".join(
        '<a class="card" href="' + escape(p["u"], quote=True) + '"><strong>' + escape(p["n"]) +
        '</strong><small>' + escape(p["r"]) + '</small><span>주문 안내 보기</span></a>'
        for p in directory[:12]
    )
    index = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>전국 장례식장 근조화환 주문·가격안내 | 날마다꽃</title>
<meta name="description" content="전국 장례식장 1,080곳의 근조화환 주문 안내 미리보기. 시설 정보와 상품 가격은 검증 진행 중입니다.">
<style>""" + STYLE + """</style></head><body>
<header><div class="container header-inner"><a class="logo" href="/">✿ 날마다<span>꽃</span></a>
<nav class="nav" aria-label="메뉴"><a href="#directory">장례식장 찾기</a><a href="#ordering">주문 준비</a><a href="#about">서비스 안내</a></nav>
<a class="btn" href="tel:18440644">☎ 1844-0644</a></div></header>
<main><section class="hero"><div class="container hero-inner"><div>
<div class="kicker">NALMADA FLOWER · CONDOLENCE SERVICE</div>
<h1>마음을 담은 근조화환,<br>날마다꽃이 안내합니다.</h1>
<p>전국 장례식장 이름이나 지역을 검색하고, 근조화환 종류·리본 문구·주문 준비에 관한 안내를 확인하세요.</p>
<a class="btn" href="#directory">장례식장 검색하기</a></div>
<div class="flower-mark" aria-label="꽃 장식 일러스트"><div class="symbol" aria-hidden="true">✿</div>
<p>공통 근조화환 이미지 사용 예정<br>장례식장 건물 사진은 사용하지 않습니다</p></div></div></section>
<section id="directory" class="section container"><div class="kicker">FUNERAL HALL DIRECTORY</div>
<h2>전국 장례식장 찾아보기</h2><p class="sub">V4 장례식장 원장 기준 1,080개 시설. 실제 주소·운영 상태는 별도 확인이 필요합니다.</p>
<div class="filters"><label>장례식장명 또는 지역<input id="query" placeholder="예: 안산, 서울, 장례식장명" autocomplete="off"></label>
<label>지역 구분<select id="province"><option value="">전국 전체</option></select></label></div>
<p id="count" aria-live="polite">장례식장 목록을 불러오는 중입니다.</p>
<div id="results" class="cards">""" + sample_cards + """</div>
<div class="warning">검수용 사이트입니다. 현재 시설 주소·운영 상태와 근조화환 가격은 확인 중이며, 배송 가능 여부를 보장하지 않습니다.</div></section>
<section class="section container" id="ordering"><div class="kicker">ORDER GUIDE</div><h2>근조화환 주문 전에 확인하세요</h2>
<p>장례식장명, 빈소와 상주명, 발인 일정, 받는 분 정보, 리본에 적을 문구와 보내는 사람의 이름을 준비하면 상담이 수월합니다.</p>
<p>기본형·고급형·특대형 금액과 제작 조건, 배송비는 개별 확인 후 안내합니다.</p>
<a class="btn" href="tel:18440644">전화 주문 문의 1844-0644</a></section>
<section class="section container" id="about"><h2>날마다꽃 안내</h2><p>근조화환을 중심으로 실제 시설 정보와 상품 가격 확인 절차를 준비하고 있습니다. 현재 페이지는 디자인 및 문서 검수용입니다.</p></section>
</main><footer><div class="container">날마다꽃 · 전국 장례식장 근조화환 안내 · 검수용 noindex · 전화 1844-0644</div></footer>
<script>
(()=>{const query=document.getElementById("query"),province=document.getElementById("province"),
results=document.getElementById("results"),count=document.getElementById("count");
let all=[];const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function display(){const q=query.value.trim().toLowerCase(),p=province.value;
const found=all.filter(x=>(x.n+" "+x.r).toLowerCase().includes(q)&&(!p||x.r.startsWith(p)));
count.textContent=found.length.toLocaleString("ko-KR")+"개 시설 검색됨 · 앞의 36개 표시";
results.innerHTML=found.slice(0,36).map(x=>'<a class="card" href="'+esc(x.u)+'"><strong>'+esc(x.n)+'</strong><small>'+esc(x.r)+'</small><span>주문 안내 보기</span></a>').join("")||'<p>검색 결과가 없습니다.</p>';}
fetch("/halls.json").then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(data=>{
all=data;const provinces=[...new Set(all.map(x=>x.r.split(" ")[0]).filter(Boolean))].sort();
provinces.forEach(x=>{const o=document.createElement("option");o.value=x;o.textContent=x;province.append(o)});
display()}).catch(()=>{count.textContent="목록을 불러오지 못했습니다. 다시 접속해 주세요."});
query.addEventListener("input",display);province.addEventListener("change",display);
})();
</script></body></html>"""
    (OUT / "index.html").write_text(index, encoding="utf-8")
    error = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>페이지를 찾을 수 없습니다 | 날마다꽃</title><style>""" + STYLE + """</style></head><body><main class="container section"><h1>페이지를 찾을 수 없습니다</h1><a class="btn" href="/">날마다꽃 홈으로</a></main></body></html>"""
    (OUT / "404.html").write_text(error, encoding="utf-8")
    assert "Disallow: /" in (OUT / "robots.txt").read_text(encoding="utf-8")
    assert not (OUT / "sitemap.xml").exists()
    assert len(list(OUT.glob("fh-*.html"))) == 1080
    print(json.dumps({"package":"flower-1080-preview","halls":len(pages),"homepage":True,
                      "searchIndex":True,"notFoundPage":True,"mode":"noindex"},ensure_ascii=False))

if __name__ == "__main__":
    package()
