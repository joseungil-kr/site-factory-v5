"""Expand price comparison drafts using pinned V4 official higher-level codes only.

Existing sample builder is reused without changes. This build creates an independent
noindex dist-expansion tree; no publishing, DNS, API, or IndexNow operations.
"""
from __future__ import annotations
import hashlib
import html
import json
import shutil
from itertools import combinations
from pathlib import Path
from xml.etree import ElementTree as ET
import build as pilot

BASE=Path(__file__).resolve().parent
OUT=BASE/'dist-expansion'
SOURCE=BASE/'verified-regions.json'
DECISIONS=[
  ("기본형과 고급형의 가격 차이", "표시가격만 비교하지 말고 같은 형태의 근조 3단 상품을 먼저 나란히 놓습니다. 꽃 품종이나 수량이 확정된 표시는 아니므로 사진과 상세 규격을 주문처에서 비교하세요."),
  ("세 단 화환 크기를 확인하는 순서", "기본·고급·특대라는 이름 자체가 치수 보증은 아닙니다. 높이와 폭, 꽃 종류를 상품 상세에서 먼저 확인하고 시설 반입 규정을 뒤이어 확인합니다."),
  ("축하와 근조의 용도 구분", "행사 목적이 다르면 문구와 꽃의 분위기뿐 아니라 설치 가능한 공간도 달라집니다. 주문 전 용도·행사장명·수령 시각을 먼저 구분해 전달하세요."),
  ("추가 배송비와 기본가격의 관계", "표시된 상품가 외에 주소·시간·수령 시설에 따라 추가금이 생길 수 있습니다. 금액을 확인하기 전에는 최종 합계를 확정으로 적지 않습니다."),
  ("리본 문구와 명의 점검", "근조 리본은 조의 문구와 보내는 이름을, 축하 리본은 축하 문구와 발신 명의를 각각 교정합니다. 리본 포함 여부와 제작 비용은 상품별로 확인하세요."),
  ("같은 가격대의 상품 형태 비교", "가격이 비슷해도 3단 화환과 오브제는 형태가 다릅니다. 실물 배치가 필요한 행사인지, 빈소에 들어가는 조문용인지 먼저 구별합니다."),
  ("행사 전날 확인해야 할 비용", "예정된 도착 날짜가 있다면 제작 가능 여부를 확인한 후 상품가·추가 배송비·리본 옵션을 차례로 확인하세요. 접수 마감은 고정값으로 표시하지 않습니다."),
  ("상품 상세에서 비교할 세 가지", "사진은 구성의 참고이고 동일한 꽃 품종·개수를 보장하지 않습니다. 판매 상세의 실측 여부, 꽃의 구성 설명, 옵션 가격을 나눠 읽습니다."),
  ("받는 곳 정보를 준비하는 법", "결제 이전에 시설명·주소·행사명이나 빈소 번호를 정확하게 준비합니다. 안내 페이지는 이 개인정보를 직접 수집하지 않습니다."),
  ("예산에 맞춰 먼저 고를 항목", "지출 한도가 있다면 주문 총액을 먼저 확인하는 것이 안전합니다. 상품 기준가만으로 예산 내 주문 가능 여부를 판단하지 않습니다."),
  ("화환과 오브제의 차이 점검", "근조 3단·축하 3단·축하 오브제는 이름부터 다른 상품 유형입니다. 설치 공간과 용도 확인을 마친 뒤 실제 주문 상세로 이동하세요."),
  ("수령 시간과 최종금액 확인", "배송 가능 시간과 실제 추가요금은 판매처가 정확한 수령지를 확인해야 알 수 있습니다. 당일 도착 가능이나 추가금 면제를 이 페이지가 보장하지 않습니다."),
  ("근조 리본 확인 체크", "보내는 단체명과 조의 문구의 오탈자를 먼저 확인합니다. 실제 판매처의 리본 옵션에 포함된 글자 수와 비용은 별도 확인 대상입니다."),
  ("축하 행사장의 상품 선택", "개업·결혼 등 축하 목적은 이벤트 유형별로 적절한 꽃 모양을 달리 고를 수 있습니다. 공간 반입 제한과 상품 구성은 판매 상세를 기준으로 판단하세요."),
  ("가격이 다른 상품을 비교하는 기준", "가격 차이가 꽃 개수나 품질 차이와 일대일로 대응한다고 추정하지 않습니다. 실제 상품명·표시가와 상세 구성만 분리하여 확인하세요."),
  ("주문 이후 확인할 항목", "상품 주문 후에는 판매처 주문내역과 배송 상태를 확인하세요. 안내 사이트는 결제·배송추적 시스템을 갖춘 판매 지점이라고 주장하지 않습니다.")
]
ADDITIONAL=[
 "실제 배송 가능 지역, 지역별 제작처 유무, 배송비 및 리본 가격은 확인되지 않았습니다.",
 "이 페이지의 지역 명칭은 법정동 코드 기반 탐색 단위이며 판매자의 지역 지점 또는 배송 완료 사례를 나타내지 않습니다.",
 "안내용 AI 이미지 다섯 장은 상품 실사진, 배송 현장 또는 납품 증명이 아닙니다."
]

def read_json(path):return json.loads(path.read_text(encoding='utf-8'))
def escape(value):return html.escape(str(value),quote=True)

def build():
    source=read_json(SOURCE)
    spec=read_json(BASE/'site-spec.json')
    assert source['sourceBlobSha']=='13d43fc3f2492b29b1680858235fe0ac0cd10580'
    assert len(source['expandEntries'])==16 and source['excludedRepresentativeCount']==2
    assert all(x['sourceStatus']=='존재' and x['level'] in ('municipality','ward') for x in source['expandEntries'])
    assert len({x['code'] for x in source['expandEntries']})==16
    assert all(x['fullName'].startswith('경기도 ') for x in source['expandEntries'])
    assert len(spec['catalog'])==5 and len(spec['images'])==5
    # Retain exactly the previously approved pilot build and image assets.
    pilot.build()
    if OUT.exists():shutil.rmtree(OUT)
    shutil.copytree(BASE/'dist',OUT)
    (OUT/'region').mkdir(exist_ok=True)
    catalog=spec['catalog']
    assert [x['sku'] for x in catalog]==['B201','B203','B205','C205','C030']
    images=read_json(BASE/'image-manifest.json')['images']
    media={x['filename']:x for x in images}
    assert set(spec['images'])==set(media)
    records=[]
    variants=set()
    combos=list(combinations(range(5),3))
    for i,area in enumerate(source['expandEntries']):
        label=area['fullName']
        title=label+' 화환 가격, 근조·축하 상품과 최종 주문금액 | 알뜰화환'
        focus,explainer=DECISIONS[i]
        choices=combos[i%len(combos)]
        products=[catalog[j] for j in choices]
        low,high=min(products,key=lambda x:x['referenceKRW']),max(products,key=lambda x:x['referenceKRW'])
        spread=high['referenceKRW']-low['referenceKRW']
        selection=(', '.join(p['sku'] for p in products))
        variants.add((focus,selection))
        # Claims are SKU catalogue facts and official administrative hierarchy,
        # not unverified locality-level delivery facts.
        intro=(label+'은 '+area['level']+' 등급의 법정동 코드 '
          +area['code']+'에 대응하는 상위 행정구역 명칭입니다. '
          +'아래 금액은 판매 상품의 확인 당시 기준가이며, 이 지역으로 배송할 수 있다는 근거는 아닙니다.')
        rows=''.join('<tr><td>'+escape(p['kind'])+'</td><td>'+escape(p['sku'])+'</td><td>'+escape(p['name'])+
          '</td><td>'+format(p['referenceKRW'],',')+'원</td><td><a href="'+escape(p['orderUrl'])+
          '" rel="noopener noreferrer">실제 상품·주문 조건 확인</a></td></tr>' for p in catalog)
        figures=''.join(
          '<figure class="card"><img src="/assets/'+escape(name)+'" width="'+str(media[name]['width'])+
          '" height="'+str(media[name]['height'])+'" loading="lazy" decoding="async" alt="'+
          escape(name.replace('.webp',' ').replace('-',' ')+' AI 생성 화환 유형 안내 이미지')+
          '"><figcaption>AI로 생성한 유형 설명용 이미지 — 실제 판매 상품/납품 사진 아님</figcaption></figure>'
          for name in spec['images'])
        guidance=('시·구 행정구역 이름만으로 최종 배송비를 계산할 수 없습니다. '
                  '정확한 수령 시설 주소와 날짜를 판매처에 전달해 지역별 추가금을 확인하세요.'
                  if area['level']=='municipality' else
                  '일반구 단위 명칭뿐 아니라 실제 동·도로명 주소와 시설명을 확인해야 합니다. '
                  '해당 지역의 고정 배송비나 당일 배송 마감을 추정하지 않습니다.')
        html_text=(
          '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
          '<meta name="viewport" content="width=device-width,initial-scale=1">'
          '<meta name="robots" content="noindex,nofollow"><title>'+escape(title)+'</title>'
          '<meta name="description" content="'+escape(intro[:145])+'">'
          '<link rel="stylesheet" href="/assets/site.css"></head><body>'
          '<header><div class="wrap"><b>알뜰화환 · 검증된 상품 기준가 비교</b></div></header>'
          '<section class="hero"><div class="wrap"><h1>'+escape(title)+'</h1><p>'+escape(intro)+'</p></div></section>'
          '<main class="wrap"><section><h2>상품가와 최종 주문금액의 차이</h2>'
          '<p>최종 금액 = 상품 표시가 + 실제 확인된 배송 추가비 + 리본·옵션 비용(해당 시)입니다.'
          ' 지금은 추가 배송비와 리본 비용의 포함 여부를 확인하지 못했습니다.</p></section>'
          '<section><h2>실제 판매 상품 가격표</h2><div class="overflow"><table>'
          '<thead><tr><th>용도</th><th>SKU</th><th>상품명</th><th>확인 기준가</th><th>주문 조건</th></tr></thead>'
          '<tbody>'+rows+'</tbody></table></div>'
          '<p>근조 B201/B203/B205: 2026-10-22 확보 원장. 축하 C205/C030: 2026-10-30 확인 기록.'
          ' 재고, 판매가 변경 및 최종 결제액은 실주문 단계에서 확인하세요.</p></section>'
          '<section><h2>'+escape(focus)+'</h2><p>'+escape(explainer)+'</p>'
          '<p>이번 비교 예시의 세 상품 '+escape(selection)+' 중 표시가가 가장 낮은 '
          +escape(low['sku'])+'은 '+format(low['referenceKRW'],',')+'원, 가장 높은 '
          +escape(high['sku'])+'은 '+format(high['referenceKRW'],',')+
          '원입니다. 표시가 차이는 '+format(spread,',')+
          '원이나 사양·배송료 차이를 뜻하지 않습니다.</p></section>'
          '<section><h2>AI 이미지로 살펴보는 형태와 옵션</h2>'
          '<div class="cards">'+figures+'</div></section>'
          '<section><h2>해당 지역명으로 주문 전에 확인할 사항</h2><p>'
          +escape(guidance)+'</p><ol><li>근조·축하 상품 종류와 SKU 선택</li>'
          '<li>수령 시설명·정확한 배송 주소와 희망 도착일 확인</li>'
          '<li>배송 추가비·리본 문구 및 옵션 비용을 판매처에 확인</li>'
          '<li>결제 직전 판매처 주문서의 총액 확인</li></ol>'
          '<p>'+escape(' '.join(ADDITIONAL))+'</p></section>'
          '<section><h2>자주 묻는 질문</h2><details><summary>표시가격으로 바로 결제할 수 있나요?</summary>'
          '<p>아닙니다. 실제 주문 상세에서 배송료와 옵션 및 재고를 확인하세요.</p></details>'
          '<details><summary>이 지역 배송이 확정되나요?</summary><p>아닙니다. 정확한 수령지별'
          ' 제작·배송 가능 여부가 확인되지 않았습니다.</p></details></section></main>'
          '<footer><div class="wrap">알뜰화환 · 상품 정보 비교 안내 · 실제 주문은 fwith.co.kr에서 진행'
          '</div></footer></body></html>')
        relative='region/'+area['code']+'.html'
        (OUT/relative).write_text(html_text,encoding='utf-8')
        records.append({'url':'/'+relative,'officialCode':area['code'],'officialName':label,
          'level':area['level'],'parent':area['parent'],'sourceRecord':area['sourceRecord'],
          'focus':focus,'comparedSKUs':list(selection.split(', ')),
          'lowReferencePrice':low['referenceKRW'],'highReferencePrice':high['referenceKRW'],
          'referenceSpread':spread,'htmlSHA256':hashlib.sha256(html_text.encode('utf-8')).hexdigest()})
    assert len(records)==16 and len(variants)==16
    report={'site':'wreathprice','mode':'noindex-offline-expansion',
      'sourceBlobSha':source['sourceBlobSha'],'officialRetrievedOn':source['retrievedOn'],
      'pilotPages':3,'expandedPages':len(records),'totalPages':3+len(records),
      'imagesPerPage':5,'verifiedDeliveryAreas':0,'uniqueEditorialFocusPairs':len(variants),
      'sitemap':False,'publicDeployment':False,'records':records}
    (OUT/'expansion-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('WREATHPRICE_VERIFIED_REGION_NO_INDEX_BUILD '+json.dumps(
      {k:v for k,v in report.items() if k!='records'},ensure_ascii=False))

if __name__=='__main__':build()
