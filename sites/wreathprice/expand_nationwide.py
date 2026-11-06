"""Expand price comparison drafts using pinned V4 official higher-level codes only.

Existing sample builder is reused without changes. This build creates an independent
noindex dist-expansion tree; no publishing, DNS, API, or IndexNow operations.
"""
from __future__ import annotations
import hashlib
import html
import json
import shutil
from pathlib import Path
from xml.etree import ElementTree as ET
import build as pilot

BASE=Path(__file__).resolve().parent
OUT=BASE/'dist-nationwide'
SOURCE=BASE/'verified-regions-nationwide.json'
DECISIONS=[
 ("근조 3단 예산 비교", "같은 근조 3단 중 기본형은 59,000원, 고급형은 79,000원, 특대형은 109,000원입니다. 실제 결제액에는 수령지별 배송비와 선택 옵션이 반영될 수 있습니다."),
 ("꽃 구성과 크기 문의", "상품명에 기재된 고급형·특대형 표기만으로 크기나 꽃의 수량을 알 수는 없습니다. 판매처 상품 상세에 기재된 구성과 규격을 기준으로 선택할 수 있습니다."),
 ("근조와 축하의 용도", "조문에 보내는 근조화환과 개업·기념행사용 축하화환은 목적이 다릅니다. 받는 시설의 행사명과 사용 목적에 맞춰 상품을 고를 수 있습니다."),
 ("배송비를 포함한 예산", "화환 기준가 외 배송지에 적용되는 요금과 리본 옵션이 있으면 결제총액이 달라집니다. 실제 주문서를 기준으로 예산을 비교할 수 있습니다."),
 ("리본 문구와 보내는 이름", "근조와 축하 리본은 문구와 보내는 이름을 정확하게 입력하는 것이 중요합니다. 리본 문구와 추가금은 상품별 주문 단계에서 안내됩니다."),
 ("3단 화환과 오브제의 형태", "3단 화환과 오브제는 형태가 다른 상품입니다. 받는 시설의 반입 가능 형태와 설치 공간을 확인하면 선택이 쉬워집니다."),
 ("도착 예정일 상담", "희망 날짜·시간을 판매처에 알려주시면 수령지의 접수 가능 여부와 도착 일정을 안내받을 수 있습니다."),
 ("상품 상세에서 확인할 정보", "상품 상세에서 표시가, 꽃 구성 안내, 선택 옵션과 주문 조건을 함께 확인할 수 있습니다."),
 ("받는 시설과 주소", "정확한 시설명과 배송 주소, 필요한 빈소·행사 정보를 준비하면 판매처에서 배송 조건을 안내하기 쉽습니다."),
 ("예산에 맞는 기본형 선택", "근조 B201은 표시가 59,000원으로 세 가지 3단 상품 중 기준가가 가장 낮습니다. 배송비와 리본 비용을 포함한 총액은 별도로 안내됩니다."),
 ("화환과 축하 오브제", "축하 3단 C205(149,000원)와 2단 오브제 C030(200,000원)는 용도가 비슷하더라도 형태가 달라 설치 조건에 맞춰 선택할 수 있습니다."),
 ("수령 시간과 비용", "수령시설명·주소와 희망 도착시각을 알려주시면 판매처에서 배송 일정과 추가비용을 안내합니다."),
 ("근조 리본 준비", "근조 리본에는 조의 문구와 보내는 이름을 입력할 수 있습니다. 실제 문구 작성과 제작비는 주문 옵션에서 확인됩니다."),
 ("축하 행사장 수령", "행사장에 화환을 놓을 공간이 있는지와 수령 가능한 시간을 확인하면 축하 상품 형태를 선택하는 데 도움이 됩니다."),
 ("같은 근조 3단 가격 차이", "B201과 B203의 기준가 차이는 20,000원, B203과 B205는 30,000원입니다. 사양 차이는 실제 상품 상세를 기준으로 비교할 수 있습니다."),
 ("주문 후 확인 경로", "상품 주문내역과 배송 진행 상황은 연결된 판매처에서 확인할 수 있습니다.")
]
ADDITIONAL=[
 "정확한 수령 주소를 기준으로 배송 가능 여부와 추가비용이 안내됩니다.",
 "사진과 상품의 구성은 다를 수 있으며 실제 판매 사진과 옵션은 상세 페이지에서 확인할 수 있습니다."
]

def read_json(path):return json.loads(path.read_text(encoding='utf-8'))
def escape(value):return html.escape(str(value),quote=True)

def build():
    source=read_json(SOURCE)
    spec=read_json(BASE/'site-spec.json')
    assert source['sourceBlobSha']=='13d43fc3f2492b29b1680858235fe0ac0cd10580'
    entries=[x for x in source['entries'] if x['code'] not in source['existingPilotCodes']]
    assert len(source['entries'])==284 and len(entries)==282
    assert all(x['sourceStatus']=='존재' and x['level'] in ('province','municipality','ward') for x in entries)
    assert len({x['code'] for x in entries})==282
    assert len({x['code'] for x in source['entries']})==284
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
    comparison_variants=set()
    for i,area in enumerate(entries):
        label=area['fullName']
        title=label+' 화환 가격, 근조·축하 상품과 최종 주문금액 | 알뜰화환'
        focus,explainer=DECISIONS[i%len(DECISIONS)]
        # Compare like-for-like funeral three-tier items only.
        # Celebration and objet products are a separate purpose/form introduction.
        products=catalog[:3]
        assert all(p['kind']=='근조' for p in products)
        low,mid,high=products
        spread=high['referenceKRW']-low['referenceKRW']
        selection=', '.join(p['sku'] for p in products)
        comparison_variants.add(selection)
        # Claims are SKU catalogue facts and official administrative hierarchy,
        # not unverified locality-level delivery facts.
        intro=(label+'에서 화환 가격을 알아보신다면 먼저 근조와 축하 중 용도에 맞는 상품을 고르고, '
          +'판매처의 확인된 표시 가격과 주문 시 추가되는 비용을 구분해 보세요. '
          +'받는 시설과 상세 주소를 알려주시면 판매처에서 실제 배송 조건을 안내합니다.')
        rows=''.join('<tr><td>'+escape(p['kind'])+'</td><td>'+escape(p['sku'])+'</td><td>'+escape(p['name'])+
          '</td><td>'+format(p['referenceKRW'],',')+'원</td><td><a href="'+escape(p['orderUrl'])+
          '" rel="noopener noreferrer">실제 상품·주문 조건 확인</a></td></tr>' for p in catalog)
        figures=''.join(
          '<figure class="card"><img src="/assets/'+escape(name)+'" width="'+str(media[name]['width'])+
          '" height="'+str(media[name]['height'])+'" loading="lazy" decoding="async" alt="'+
          escape(name.replace('.webp',' ').replace('-',' ')+' 상품 형태 참고 이미지')+
          '"><figcaption>AI로 생성한 유형 설명용 이미지 — 실제 판매 상품/납품 사진 아님</figcaption></figure>'
          for name in spec['images'])
        guidance=('시·구 행정구역 이름만으로 최종 배송비를 계산할 수 없습니다. '
                  '정확한 수령 시설 주소와 날짜를 판매처에 전달해 지역별 추가금을 확인하세요.'
                  if area['level']=='municipality' else
                  '일반구 단위 명칭뿐 아니라 실제 동·도로명 주소와 시설명을 확인해야 합니다. '
                  '지역별 배송비와 접수 시간은 수령 시설의 상세 주소를 기준으로 안내됩니다.')
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
          '<h3>동일 용도 근조 3단 화환 기준가 비교</h3>'
          '<p>근조 3단 기본형('+escape(low['sku'])+')은 '+format(low['referenceKRW'],',')+
          '원, 고급형('+escape(mid['sku'])+')은 '+format(mid['referenceKRW'],',')+
          '원, 특대형('+escape(high['sku'])+')은 '+format(high['referenceKRW'],',')+
          '원으로 기록돼 있습니다. 기본형과 고급형은 '
          +format(mid['referenceKRW']-low['referenceKRW'],',')+
          '원, 고급형과 특대형은 '+format(high['referenceKRW']-mid['referenceKRW'],',')+
          '원, 기본형과 특대형은 '+format(spread,',')+
          '원의 <strong>표시가 차이</strong>가 있습니다. '
          '이는 꽃 수량·품질이나 배송비 차이를 입증하지 않습니다.</p>'
          '<h3>용도와 형태가 다른 상품 안내</h3>'
          '<p>축하 3단 화환('+escape(catalog[3]['sku'])+')과 축하 2단 오브제('
          +escape(catalog[4]['sku'])+')는 서로 형태가 다른 축하용 상품입니다. '
          '근조 3단 상품의 등급·가격 순위에 섞어 비교하지 않고, 행사 목적·설치 공간과 상세 구성을 따로 확인합니다.</p></section>'
          '<section><h2>상품 형태와 리본 옵션</h2>'
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
    assert len(records)==282 and len(comparison_variants)==1
    report={'site':'wreathprice','mode':'noindex-offline-expansion',
      'sourceBlobSha':source['sourceBlobSha'],'officialRetrievedOn':source['retrievedOn'],
      'pilotPages':3,'expandedPages':len(records),'hubPages':1,'totalPages':4+len(records),
      'imagesPerPage':5,'verifiedDeliveryAreas':0,'distinctComparisonSets':len(comparison_variants),
      'editorialFocusCount':len({x['focus'] for x in records}),
      'regionSpecificServiceEvidenceCount':0,
      'contentUniquenessClaim':False,
      'sitemap':False,'publicDeployment':False,'listedAdministrativeRegions':len(source['entries']), 'records':records}
    # Navigation makes every nationwide draft reachable from the existing home.
    # These are administrative lookup links, NOT delivery coverage claims.
    route_by_code={r['officialCode']:r['url'] for r in records}
    route_by_code['4127000000']='/ansan/'
    route_by_code['4127100000']='/ansan/sangnok/'
    nav_rows=[]
    for area in source['entries']:
        href=route_by_code[area['code']]
        nav_rows.append('<li><a href="'+escape(href)+'">'+escape(area['fullName'])+'</a></li>')
    nav_body='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>전국 화환 가격 지역명 안내 | 알뜰화환</title><meta name="description" content="2026-10-22에 확보한 법정동 코드 기준 전국 상위 행정구역명 284개 안내. 근조·축하 화환의 실제 배송 가능 여부와 추가금은 판매처에 확인하세요."><link rel="stylesheet" href="/assets/site.css"></head><body><header><div class="wrap"><a href="/">알뜰화환</a></div></header><main class="wrap"><section><h1>전국 화환 가격 지역명 찾아보기</h1><p>지역명은 2026-10-22에 확보한 상위 법정동 코드 자료에서 확인했습니다. 전국 배송 가능 지역을 뜻하지 않으며, 실제 배송 가능 여부와 추가금은 주문 전 판매처 상담으로 확인하세요.</p><p>근조·축하 상품 기준 가격은 지역 배송비나 리본 옵션 비용을 포함한다고 확정할 수 없습니다.</p><ul>'+''.join(nav_rows)+'</ul></section></main></body></html>'
    (OUT/'regions').mkdir(exist_ok=True)
    (OUT/'regions/index.html').write_text(nav_body,encoding='utf-8')
    home=OUT/'ansan/index.html'
    html_home=home.read_text(encoding='utf-8')
    assert '</main>' in html_home
    first_16=records[:16]
    direct_links=''.join('<li><a href="'+escape(r['url'])+'">'+escape(r['officialName'])+' 화환 가격</a></li>' for r in first_16)
    hub_section='<section><h2>전국 지역명으로 화환 기준 가격 확인</h2><p>전국 지역명 목록은 법정동 상위 지역명 안내입니다. 해당 지역으로의 배송 가능, 추가 배송료, 도착시각을 보증하지 않습니다.</p><ul>'+direct_links+'</ul><a class="btn" href="/regions/">전국 284개 상위 지역명 전체 보기</a></section>'
    home.write_text(html_home.replace('</main>',hub_section+'</main>'),encoding='utf-8')
    for rec in records:
        page=OUT/rec['url'].lstrip('/')
        body=page.read_text(encoding='utf-8')
        body=body.replace('</main>','<section><p><a href="/">화환 가격 홈</a> · <a href="/regions/">전국 지역명 목록</a></p></section></main>')
        page.write_text(body,encoding='utf-8')
        rec['htmlSHA256']=hashlib.sha256(body.encode('utf-8')).hexdigest()
    (OUT/'expansion-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('WREATHPRICE_VERIFIED_REGION_NO_INDEX_BUILD '+json.dumps(
      {k:v for k,v in report.items() if k!='records'},ensure_ascii=False))

if __name__=='__main__':build()
