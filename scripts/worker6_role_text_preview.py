"""Isolated text-only buyer/region/evidence role preview; never publish."""
import html,json
from pathlib import Path
from urllib.parse import quote
from scripts.worker6_shipping_render import lookup
from scripts.worker6_nationwide_inputs import prepare
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/promotion-gift-plants/role-preview'
CASES=[
 ('경기도','파주시','적성면','D144'),
 ('경기도','가평군','설악면','D144'),
 ('경기도','포천시','이동면','D144'),
 ('강원도','강릉시','주문진읍','D144'),
]
def source_ledger():
 return json.loads((ROOT/'sites/promotion-gift-plants/seller-shipping-raw-rows.json').read_text(encoding='utf-8'))
def catalog():
 return {x['sku']:x for x in json.loads((ROOT/'sites/promotion-gift-plants/products.json').read_text(encoding='utf-8'))}
def evidence(province,district,locality,sku):
 if sku!='D144':return {'state':'sku-source-unverified','rows':[],'note':'이 상품의 지역별 추가요금 원문을 별도로 확인하지 못했습니다.'}
 x=lookup(province,district,locality)
 return {'state':x['state'],'rows':x['candidates'],'note':'표시된 금액은 최종 배송비나 배송 가능 여부를 보증하지 않습니다.'}
def render():
 pages,regions=prepare()
 candidates={p['region']:p for p in pages if p['pageKind']=='locality-detail'}
 out=[];OUT.mkdir(parents=True,exist_ok=True)
 product=catalog()['D144']
 assert product['priceConfirmed'] and product['verifiedLive']
 for n,(province,district,locality,sku) in enumerate(CASES,1):
  region=' '.join((province,district,locality))
  assert region in candidates
  e=evidence(province,district,locality,sku)
  seller=source_ledger()
  title=html.escape(region+' 화분 주문 정보')
  href=html.escape(product['orderUrl'],quote=True)
  # Only show seller's exact row text and D144 product evidence; no inferred local availability.
  raw={r['row']:r for r in seller['rows']}
  rows=[]
  for candidate in e['rows']:
   r=raw[candidate['row']]
   rows.append(f'<li>표 {r["row"]}행 · {html.escape(r["districtText"])} · {html.escape(r["localityText"])} · {r["extraKRW"]:,}원 (표시액)</li>')
  evidence_html='<ul>'+''.join(rows)+'</ul>' if rows else '<p>일치하는 요금표 행을 확인하지 못했습니다. 무료배송 또는 배송불가를 뜻하지 않습니다.</p>'
  # Fixed three roles: purpose guide is one shared URL; navigation lists region names only.
  text=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{title}</title><style>body{{font-family:system-ui,sans-serif;max-width:48rem;margin:auto;padding:1.2rem;line-height:1.7}}nav a{{margin-right:1rem}}section{{border-top:1px solid #ddd;padding:1rem 0}}</style></head><body><nav><a href="/">지역 탐색</a><a href="/guide.html">공통 주문 안내</a></nav><main><h1>{title}</h1><section><h2>확인된 상품 정보</h2><p>{html.escape(product["name"])} · {product["referencePrice"]:,}원 (판매처 확인일 {product["priceCheckedOn"]})</p><a href="{href}" target="_blank" rel="noopener noreferrer">꽃이랑 D144 상품 상세</a></section><section><h2>판매처 D144 지역 요금표 근거</h2>{evidence_html}<p>{html.escape(e["note"])}</p><p>표 확인일 {seller["checkedAt"]}. <a href="{html.escape(seller["sourceUrl"],quote=True)}" target="_blank" rel="noopener noreferrer">배송비 원문</a></p><p>정확한 주소와 상품번호를 알려주고 <a href="tel:18440644">1844-0644</a>에서 최종 추가요금·수령 가능 시각을 확인하세요.</p></section></main></body></html>'''
  filename=f'{n}.html'
  (OUT/filename).write_text(text,encoding='utf-8')
  out.append({'file':filename,'region':region,'sourceFlag':candidates[region]['sourceFlag'],'sellerSku':sku,'sellerRowState':e['state'],'rowIds':[r['row'] for r in e['rows']],'sourceUrl':seller['sourceUrl'],'checkedAt':seller['checkedAt'],'finalShippingConfirmed':False,'localStockConfirmed':False})
 guide='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>공통 주문 안내</title></head><body><a href="/">지역 탐색</a><h1>승진·축하 화분 주문 공통 안내</h1><p>회사 수령: 부서와 층·호실, 자택 수령: 상세주소와 부재 시 연락, 행사장 수령: 행사명·반입시간을 확인하세요.</p><p>전화 주문 08:00~23:00, 배송 가능 시간대 06:00~20:00는 지역 꽃집 운영시간에 따릅니다. 개별 당일 도착·재고·최종 배송비는 보장하지 않습니다.</p></body></html>'
 (OUT/'guide.html').write_text(guide,encoding='utf-8')
 index='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>지역 탐색</title></head><body><h1>지역 탐색</h1><a href="/guide.html">공통 주문 안내</a><ul>'+''.join(f'<li><a href="/{r["file"]}">{html.escape(r["region"])}</a></li>' for r in out)+'</ul></body></html>'
 (OUT/'index.html').write_text(index,encoding='utf-8')
 (OUT/'manifest.json').write_text(json.dumps({'scope':'isolated text-only sample; NOT 5302 published','pages':out,'quality85Passed':False,'similarity49Passed':False,'imageLoadVerified':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return out
if __name__=='__main__':print(json.dumps(render(),ensure_ascii=False))
