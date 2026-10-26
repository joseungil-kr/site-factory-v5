"""Design B florist homepage and 1080-hall local search (noindex review only).

Product and flower photos are copied from the owner's V4 media files.
No venue buildings or inaccurate per-hall venue images are fabricated.
"""
from __future__ import annotations

from html import escape
import json
from pathlib import Path
from flower_design import head,header,footer,photo,price_cards,reference_note,contact_band

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"dist/flower-funeral-national-preview"
REPORT=ROOT/"reports/flower-funeral/pool-1080-1pct-audit.json"
SOURCE=ROOT/"data/flower/v4_facilities_1080.snapshot.json"

SEARCH_JS=r"""
(()=>{const input=document.getElementById("query"),province=document.getElementById("province"),
results=document.getElementById("results"),count=document.getElementById("count");
if(!input||!province||!results||!count)return;
let all=[];const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function show(){const q=input.value.trim().toLowerCase(),region=province.value;
const matches=all.filter(h=>(h.n+" "+h.r).toLowerCase().includes(q)&&(!region||h.r.startsWith(region)));
count.textContent=matches.length.toLocaleString("ko-KR")+"개 시설 검색됨 · 앞의 36개 표시";
results.innerHTML=matches.slice(0,36).map(h=>'<a class="hall-card" href="'+esc(h.u)+'"><strong>'+esc(h.n)+'</strong><small>'+esc(h.r)+'</small><span>근조화환 주문 안내 보기</span></a>').join("")||"<p>검색된 장례식장이 없습니다.</p>";}
fetch("/halls.json").then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(data=>{
if(!Array.isArray(data)||data.length!==1080)throw Error("Incomplete hall registry");
all=data;[...new Set(data.map(h=>h.r.split(" ")[0]).filter(Boolean))].sort().forEach(x=>{
const opt=document.createElement("option");opt.value=x;opt.textContent=x;province.append(opt)});
show()}).catch(()=>{count.textContent="장례식장 목록을 불러오지 못했습니다. 새로고침 후 다시 시도해 주세요."});
input.addEventListener("input",show);province.addEventListener("change",show);
})();
"""

def package():
    manifest=json.loads((OUT/"manifest.json").read_text(encoding="utf-8"))
    report=json.loads(REPORT.read_text(encoding="utf-8"))
    source=json.loads(SOURCE.read_text(encoding="utf-8"))
    assert report["passes"] and report["fullPairFailures"]==0 and report["fullPairComparisons"]==1165320
    assert report["maximumSimilarity"]<0.49
    assert source["publicationAllowed"] is False
    facilities=source["facilities"]
    pages=manifest["pages"]
    assert manifest["mode"]=="noindex-preview" and manifest["qaPasses"] and len(pages)==len(facilities)==1080
    assert {f["id"] for f in facilities}=={p["id"] for p in pages}
    for p in pages:
        markup=(OUT/p["filename"]).read_text(encoding="utf-8")
        assert '<meta name="robots" content="noindex,nofollow">' in markup and "날마다꽃" in markup
        assert 'src="/assets/images/B203.jpg"' in markup
        assert 'class="article-card"' in markup and 'class="product-card"' in markup
    for local in ("assets/css/site.css","assets/images/B201.jpg","assets/images/B203.jpg",
                  "assets/images/B205.jpg","assets/images/A160.jpg","assets/images/D143.jpg"):
        assert (OUT/local).is_file(),local
    directory=[{"n":p["facility"],"r":p["region"],"u":"/"+p["filename"]} for p in pages]
    (OUT/"halls.json").write_text(json.dumps(directory,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    samples="".join('<a class="hall-card" href="'+escape(h["u"],quote=True)+'"><strong>'+escape(h["n"])+
        '</strong><small>'+escape(h["r"])+'</small><span>근조화환 주문 안내 보기</span></a>'
        for h in directory[:12])
    hero=('<section class="hero"><div class="wrap hero-inner"><div><span class="eyebrow">'
          'NALMADA FLOWER · NATIONWIDE FLOWER DELIVERY</span>'
          '<h1>전국 어디든, 마음을 전하는 <em>꽃배달</em></h1>'
          '<p class="lead">근조화환을 중심으로 꽃바구니와 화분까지, '
          '날마다꽃이 상품 안내와 주문 상담을 도와드립니다. '
          '전국 장례식장 1,080곳의 근조화환 주문 참고 정보를 찾아보세요.</p>'
          '<div class="hero-actions"><a class="btn" href="#directory">장례식장 찾기</a>'
          '<a class="btn btn-outline" href="tel:18440644">☎ 1844-0644 상담</a></div>'
          '<div class="badges"><span>근조화환 종류별 비교</span><span>리본 문구 안내</span>'
          '<span>전화 주문 상담</span></div></div>'
          '<div class="hero-visual">'+photo("A160.jpg","날마다꽃 꽃바구니 공통 상품 사진","eager")+
          '<span class="photo-label">보유 상품 사진 · 실제 상품 구성은 달라질 수 있습니다</span></div>'
          '</div></section>')
    categories=('<section id="categories" class="wrap section">'
        '<div class="section-title"><div><h2>꽃배달 상품별 안내</h2>'
        '<p>전국 장례식장 검색과 함께 선물 용도에 맞춰 상담하세요.</p></div></div>'
        '<div class="cat-grid">'
        '<a class="cat-card" href="#products">'+photo("B201.jpg","근조 3단 화환 대표 상품")+
        '<div class="cat-desc"><strong>근조화환</strong><p>장례식장 주문·가격안내</p></div></a>'
        '<div class="cat-card"><div class="cat-icon" aria-hidden="true">✿</div>'
        '<div class="cat-desc"><strong>축하화환</strong><p>상품 정보 준비 중 · 전화 문의</p></div></div>'
        '<div class="cat-card">'+photo("A160.jpg","꽃바구니 상품 사진")+
        '<div class="cat-desc"><strong>꽃바구니</strong><p>기념일·감사 꽃선물 상담</p></div></div>'
        '<div class="cat-card">'+photo("D143.jpg","관엽식물 상품 사진")+
        '<div class="cat-desc"><strong>관엽식물·화분</strong><p>승진·개업 선물 상담</p></div></div>'
        '</div></section>')
    products_html=('<section class="wrap section" id="products">'
        '<div class="section-title"><div><h2>근조화환 종류별 상품</h2>'
        '<p>기존 판매처의 상품 사진과 기준일이 표시된 참고 가격입니다.</p></div></div>'
        +price_cards()+reference_note()+'</section>')
    directory_html=('<section class="wrap section" id="directory"><div class="search-panel">'
        '<span class="eyebrow">FUNERAL HALL DIRECTORY</span>'
        '<h2>전국 장례식장 찾아보기</h2>'
        '<p>원장에 기록된 전국 1,080곳입니다. 최신 주소·운영상태는 별도 확인이 필요합니다.</p>'
        '<div class="filters"><label>장례식장명 또는 지역'
        '<input type="search" id="query" placeholder="예: 안산, 서울, 장례식장명" autocomplete="off"></label>'
        '<label>광역 지역 선택<select id="province"><option value="">전국 전체</option></select></label></div>'
        '<p id="count" aria-live="polite">장례식장 목록을 불러오는 중입니다.</p>'
        '<div id="results" class="hall-grid">'+samples+'</div></div>'
        '<div class="notice" style="margin-top:15px">시설명·주소·운영상태를 별도로 확인하지 않은 검수용 원장입니다. '
        '이 페이지는 검색엔진에 제출하지 않습니다.</div></section>')
    guide=('<section class="wrap section" id="ordering">'
        '<div class="section-title"><div><h2>근조화환 주문 준비</h2>'
        '<p>꽃의 종류뿐 아니라 실제 전달 조건을 먼저 확인하는 것이 중요합니다.</p></div></div>'
        '<div class="service-grid">'
        '<div><h3>01. 시설과 빈소</h3><p>장례식장 주소, 빈소, 상주명과 발인 예정일을 확인해 주세요.</p></div>'
        '<div><h3>02. 화환과 리본</h3><p>근조화환 종류, 예산, 리본 문구와 보내는 사람 이름을 정리하세요.</p></div>'
        '<div><h3>03. 제작·배송 상담</h3><p>해당 지역의 실제 제작과 도착 가능 시간을 상담으로 확인해 주세요.</p></div>'
        '</div></section>')
    index=(head("전국 꽃배달·근조화환 주문 가격안내 | 날마다꽃",
                "전국 장례식장 1,080곳 근조화환 주문 안내. 날마다꽃 꽃바구니와 관엽화분 상품 상담.")+
           header()+'<main id="main">'+hero+categories+products_html+directory_html+guide+contact_band()+
           '</main><script src="/assets/js/hall-search.js" defer></script>'+footer())
    (OUT/"index.html").write_text(index,encoding="utf-8")
    js=OUT/"assets/js/hall-search.js"
    js.parent.mkdir(parents=True,exist_ok=True)
    js.write_text(SEARCH_JS,encoding="utf-8")
    missing=(head("페이지를 찾을 수 없습니다 | 날마다꽃","요청한 페이지를 찾을 수 없습니다.")+
             header()+'<main id="main" class="wrap section"><h1>페이지를 찾을 수 없습니다</h1>'
             '<p>전국 장례식장 목록에서 필요한 시설을 다시 검색해 주세요.</p>'
             '<a class="btn" href="/">날마다꽃 홈으로</a></main>'+footer())
    (OUT/"404.html").write_text(missing,encoding="utf-8")
    assert "Disallow: /" in (OUT/"robots.txt").read_text(encoding="utf-8")
    assert not (OUT/"sitemap.xml").exists()
    assert len(list(OUT.glob("fh-*.html")))==1080
    print(json.dumps({"pageCount":1080,"homepage":True,"directoryCount":len(directory),
                      "sharedImages":5,"design":"B + D","indexable":False},ensure_ascii=False))

if __name__=="__main__":package()
