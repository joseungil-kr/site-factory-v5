"use strict";
const PURPOSES = {
  flower: {
    title: "개원·개업화분 — 오래 둘 선물",
    intro: "병원·치과·한의원에 오래 비치할 화분을 고를 때는 식물 크기와 관리 여건을 확인합니다. 지역을 선택했다고 배송 가능 여부가 확인되는 것은 아닙니다.",
    advice: [
      ["배치 공간", "접수대·대기실·원장실 중 비치할 위치와 통행에 필요한 폭을 먼저 확인하세요."],
      ["식물 관리", "선물을 받을 곳의 채광과 물주기를 담당할 사람이 있는지 문의하세요."],
      ["선물 문구", "정확한 의료기관 명칭과 보내는 사람의 이름을 리본 제작 전에 확인하세요."]
    ],
    sku: ["D144","D149"]
  },
  open: {
    title: "개원식 화분 — 행사 일정과 인계",
    intro: "개원식 날짜와 실제 진료 시작일은 다를 수 있습니다. 행사가 있는지와 정확한 수령 담당자·시간을 먼저 확인하는 안내입니다.",
    advice: [
      ["행사 날짜", "진료 개시일과 개원 축하행사일을 구분하고 희망 전달일을 상담하세요."],
      ["수령 담당자", "행사 준비 중 실제 연락받을 직원과 예비 연락 방법을 확인하세요."],
      ["행사 장소", "로비·접수대·별도 행사장 중 화분을 인계할 장소를 확인하세요."]
    ],
    sku: ["D149","D144"]
  },
  wreath: {
    title: "개원 축하화환 — 행사 현장 장식",
    intro: "화환은 화분과 다른 행사 축하용 꽃 장식입니다. 설치 가능한 공간과 화환의 규격·반입 절차를 확인하세요.",
    advice: [
      ["화환 규격", "축하화환을 놓을 자리의 높이·폭과 반입 동선을 문의하세요."],
      ["꽃 구성", "판매처 상품 상세의 구성과 원하는 색감, 대체 가능성을 상담하세요."],
      ["현장 반입", "행사 담당자에게 설치 가능 위치·희망 반입 시각을 확인하세요."]
    ],
    sku: ["C200","C206"]
  }
};
const $ = (id) => document.getElementById(id);
const state = { regions: [], selected: null, purpose: "flower", products: {}, ready: false };
function normalize(s) {return String(s || "").normalize("NFC").toLocaleLowerCase("ko").replace(/\s+/g," ").trim();}
function e(tag, className, text) {
  const n=document.createElement(tag);
  if(className)n.className=className;
  if(text !== undefined)n.textContent=String(text);
  return n;
}
function setStatus(message) {$("searchStatus").textContent=message;}
function matchedRegions(query) {
  const q=normalize(query);
  if(!q)return state.regions.filter(r=>r.level==="province").slice(0,16);
  return state.regions.filter(r=>normalize(r.fullName).includes(q)||normalize(r.name).includes(q)).slice(0,35);
}
function renderRegions() {
  const results=$("regionResults");
  results.replaceChildren();
  const q=$("regionSearch").value;
  const matches=matchedRegions(q);
  setStatus(q?`검색 결과 ${matches.length}개 표시 (최대 35개). 지역 선택은 배송 가능 여부와 무관합니다.`: "시·도 16개 표시. 지역명을 입력하면 시·군·구도 찾을 수 있습니다.");
  for(const r of matches){
    const button=e("button","region",r.fullName);
    button.type="button";button.dataset.regionCode=r.code;
    button.setAttribute("role","option");
    button.setAttribute("aria-selected",String(state.selected?.code===r.code));
    const detail=e("span","",`법정동 상위코드 ${r.code} · ${r.level==="province"?"시·도":r.level==="ward"?"일반구":"시·군·구"}`);
    button.append(detail);
    button.addEventListener("click",()=>chooseRegion(r));
    results.append(button);
  }
  if(!matches.length)results.append(e("p","muted","일치하는 코드가 없습니다. 지역명을 다시 확인하세요."));
}
function chooseRegion(region){
  state.selected=region;
  $("selectedRegion").textContent=`선택: ${region.fullName} · 보존 코드 ${region.code} (현재 행정구역 상태 별도 확인 필요)`;
  renderRegions();
}
function renderPurpose(){
  const p=PURPOSES[state.purpose];
  for(const tab of document.querySelectorAll(".tab")){
    const active=tab.dataset.purpose===state.purpose;
    tab.setAttribute("aria-selected",String(active));
    tab.tabIndex=active?0:-1;
  }
  const panel=$("purposeDetail");panel.replaceChildren();
  const card=e("div","purpose-card");
  card.append(e("h3","",p.title),e("p","",p.intro));
  const details=e("div","advice");
  p.advice.forEach(([heading,body])=>{
    const article=e("article","");
    article.append(e("h4","",heading),e("p","",body));
    details.append(article);
  });
  card.append(details);panel.append(card);
  panel.setAttribute("aria-labelledby","tab-"+state.purpose);
  renderProducts();
}
function renderProducts(){
  const p=PURPOSES[state.purpose];
  const root=$("products");root.replaceChildren();
  for(const sku of p.sku){
    const product=state.products[sku];
    if(!product){root.append(e("p","muted","상품 정보가 로드되지 않았습니다."));continue;}
    const box=e("article","product");box.dataset.sku=sku;
    box.append(e("div","sku",sku),e("h3","",product.name));
    const historical=e("p","historical",`${Number(product.priceKRWHistorical).toLocaleString("ko-KR")}원`);
    box.append(historical,e("p","disclosure",`2026-11-05 확인 가격 · 현재 가격·재고·배송비 미확인`));
    const a=e("a","","판매처 원문 상품 상세 보기");
    a.href=product.orderUrl;a.target="_blank";a.rel="noopener noreferrer";
    a.dataset.skuLink=sku;
    box.append(a);root.append(box);
  }
}
async function boot(){
  try{
    const [regional,ledger]=await Promise.all([
      fetch("./regions.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("REGIONS_HTTP_"+r.status);return r.json();}),
      fetch("./catalog.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("CATALOG_HTTP_"+r.status);return r.json();})
    ]);
    if(!Array.isArray(regional.regions)||regional.regions.length!==284)throw Error("Region count differs from pinned source");
    if(!Array.isArray(ledger.items)||ledger.items.length!==4)throw Error("Catalog count differs");
    state.regions=regional.regions;
    state.products=Object.fromEntries(ledger.items.map(p=>[p.sku,p]));
    state.ready=true;
    $("regionCount").textContent=`코드 ${regional.regions.length}개`;
    renderRegions();renderPurpose();
  } catch(error) {
    setStatus("데이터를 불러오지 못했습니다. 비공개 프로토타입의 JSON 파일을 확인하세요.");
    $("selectedRegion").textContent="지역 데이터 오류: "+String(error.message||error);
  }
}
$("regionSearch").addEventListener("input",()=>{if(state.ready)renderRegions();});
$("clearSearch").addEventListener("click",()=>{$("regionSearch").value="";renderRegions();$("regionSearch").focus();});
document.querySelectorAll(".tab").forEach(tab=>{
  tab.addEventListener("click",()=>{state.purpose=tab.dataset.purpose;renderPurpose();});
  tab.addEventListener("keydown",event=>{
    if(!["ArrowLeft","ArrowRight"].includes(event.key))return;
    event.preventDefault();
    const keys=["flower","open","wreath"];
    const next=(keys.indexOf(state.purpose)+(event.key==="ArrowRight"?1:2))%3;
    state.purpose=keys[next];renderPurpose();$("tab-"+state.purpose).focus();
  });
});
boot();
