"""Official-source-backed three-locality isolated buyer HTML, no images or publication."""
import html,json
from pathlib import Path
from scripts.worker6_shipping_render import lookup
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'sites/promotion-gift-plants'
OUT=ROOT/'reports/promotion-gift-plants/official-three-text'
def build():
 data=json.loads((SITE/'THREE_OFFICIAL_LOCALITY_BUYER_EVIDENCE_20261111.json').read_text(encoding='utf-8'))
 seller=json.loads((SITE/'seller-shipping-raw-rows.json').read_text(encoding='utf-8'))
 products={x['sku']:x for x in json.loads((SITE/'products.json').read_text(encoding='utf-8'))}
 raw={x['row']:x for x in seller['rows']}
 OUT.mkdir(parents=True,exist_ok=True)
 manifest=[]
 for n,c in enumerate(data['cases'],1):
  province,district,locality=c['region'].split(' ',2)
  match=lookup(province,district,locality)
  assert match['state']==c['feeState']
  assert {x['row'] for x in match['candidates']}==set(c['sellerRowIds'])
  assert c['sku']==seller['sourceUrl'].split('it_id=')[-1]=='D144'
  product=products[c['sku']]
  assert product['priceConfirmed'] and product['verifiedLive']
  official=c['official']
  assert official['checkedAt'] and official['scope'] and official['quote']
  h=lambda x:html.escape(str(x),quote=True)
  rows=''.join('<li>판매처 표 '+str(i)+'행: '+h(raw[i]['districtText'])+' / '+h(raw[i]['localityText'])+' / '+f"{raw[i]['extraKRW']:,}"+'원 표시</li>' for i in c['sellerRowIds'])
  body=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{h(c['region'])} 화분 구매 확인</title><style>body{{font-family:system-ui,sans-serif;max-width:52rem;margin:auto;padding:1.1rem;line-height:1.65}}a{{overflow-wrap:anywhere}}section{{padding:1rem 0;border-bottom:1px solid #ddd}}nav a{{margin-right:1rem}}</style></head><body><nav><a href="/">표본 목록</a><a href="/guide.html">공통 주문 안내</a></nav><main><h1>{h(c['region'])} {h(c['productPurpose'])}</h1><section><h2>상품 선택</h2><p>{h(product['name'])} {product['referencePrice']:,}원 · {h(product['priceCheckedOn'])} 당시 확인 가격입니다. 현재 가격은 주문 전 판매처에서 다시 확인하세요.</p><p>이 상품의 해당 지역 재고와 실제 배송 가능 여부는 미확인입니다.</p><a href="{h(product['orderUrl'])}" target="_blank" rel="noopener noreferrer">D144 상품 상세·주문</a></section><section><h2>지역 주소 확인에 필요한 공식 근거</h2><p>{h(official['quote'])}</p><p>{h(official['scope'])}</p><p><strong>주문 전 질문:</strong> {h(c['buyerQuestion'])}</p><p>공식자료 확인일 {h(official['checkedAt'])} · 자료 기준일 {h(official['sourceUpdatedAt'] or '원문 미표기')}</p><a href="{h(official['url'])}" target="_blank" rel="noopener noreferrer">지자체 공식 원문</a></section><section><h2>D144 배송비 표의 적용 범위</h2><ul>{rows}</ul><p>{'상위·읍면 표가 겹치므로 적용 우선순위가 확인되지 않았습니다.' if c['feeState']=='overlap-unknown-priority' else '해당 읍면 표에 표시된 금액이며 최종 배송비는 확인되지 않았습니다.'}</p><p>표 확인일 {h(seller['checkedAt'])} · 이 표는 D144 상품 페이지 자료입니다. 다른 SKU에 적용한다고 주장하지 않습니다.</p><a href="{h(seller['sourceUrl'])}" target="_blank" rel="noopener noreferrer">판매처 배송비 원문</a><p>정확한 주소·희망 수령일·상품번호를 준비해 <a href="tel:18440644">1844-0644</a>로 실제 수령·최종 비용을 문의하세요.</p></section></main></body></html>'''
  filename=f'{n}.html'
  (OUT/filename).write_text(body,encoding='utf-8')
  manifest.append({'file':filename,'id':c['id'],'region':c['region'],'sku':c['sku'],'sellerRows':c['sellerRowIds'],'feeState':c['feeState'],'officialUrl':official['url'],'officialCheckedAt':official['checkedAt'],'sourceUpdatedAt':official['sourceUpdatedAt'],'images':0,'public':False})
 guide='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>공통 주문 안내</title></head><body><a href="/">목록</a><h1>공통 주문 확인</h1><p>회사·자택·행사장 수령지는 각각 실제 담당자·상세 주소·반입 가능시간을 확인하세요. 지역 기관 주소는 그 기관이 실제 수령지일 때만 참고할 수 있습니다. 기관의 존재는 화분 수령 허가가 아닙니다.</p></body></html>'
 (OUT/'guide.html').write_text(guide,encoding='utf-8')
 index='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>공식 근거 표본</title></head><body><h1>공식 근거 표본</h1><a href="/guide.html">공통 주문 안내</a><ul>'+''.join(f'<li><a href="/{x["file"]}">{html.escape(x["region"])}</a></li>' for x in manifest)+'</ul></body></html>'
 (OUT/'index.html').write_text(index,encoding='utf-8')
 (OUT/'manifest.json').write_text(json.dumps({'pages':manifest,'notPublished':True,'similarity49Pass':False,'editorial85Pass':False,'imageLoadPass':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return manifest
if __name__=='__main__':print(json.dumps(build(),ensure_ascii=False))
