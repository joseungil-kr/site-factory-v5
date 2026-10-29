# 꽃이랑 · 전국 근조화환 당일배송/화환전문 꽃집 지역사이트 (V5-2 작업자2)

**배포되지 않은 신규 사이트.** 도메인 후보 https://wreath.nalmada.net/ . V5 기존 Wallsky/Quicksky/Daysky/Flower/Onehour를 변경하지 않는다.

## 지역/문서 범위
- 2025년 기준 보조 전국 읍면동·지역명 `Guk0/KoreanAddressJson/address2.json`에서 중복 제거한 5,034개. 상위 지역 이름만 V4 `data/regions/master.json`(2026-10-22 확보)에 대조한 결과 3,596건 일치, 1,438건 매칭 미확인. **하위 읍면동의 2026년 법적 최신성·지역별 주문 가능성까지 확인된 것은 아니다.**
- 두 의도: `{지역명} 근조화환 당일배송` 및 `{지역명} 화환전문 꽃집`. 각 지역 2개 문서 = 10,068개.
- 지역 탐색 17 시도 페이지·250 시군구 페이지·홈페이지 1개, 합계 **10,336개 URL**.
- 페이지의 상품 선택, 3단/오브제, 리본 문구, 빈소·수령시설, 주문 마감 확인, 추가 배송비, 판매처 주문·배송조회 설명은 원문 3개 구조만 참고하여 독립 집필. 지역에 특정 장례식장이 실제 있다고 단정하지 않음.

## 상품/주문 근거
- `sites/wreath-region/products.json` — 기존 V4 `data/funeral-products/CATALOGUE.json`(2026-10-22)에서 근조화환 6종의 상품명·기준가·실제 판매처 이미지·`https://fwith.co.kr/shop/item.php?it_id=<SKU>`를 고정했다.
- 2026-10-29 [원격 GET 테스트](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40810652440): 6개 상품 상세/6개 실물 JPG 이미지 모두 200·판매상품 SKU·구매 버튼 확인.
- 가격은 원장 확인일 기준 **참고가**이므로 최종 결제 전에는 실제 상품가격·배송 추가비용·상품 재고·현지 제작·반입 가능성을 판매처에서 재확인. 전화 1844-0644는 판매처에서 표시하는 번호.
- 주문자/고인/상주/수령인 이름·전화·주소·리본 입력값을 이 사이트의 URL·폼·로그로 전달하지 않음. 실제 개인정보 입력은 판매처 주문서 안에서만 한다.

## 생성·검증
```bash
python -m v5 plan-check --site wreath-region
python -m unittest discover -s tests -p 'test_wreath_region.py' -v
node --test tests/wreath-worker.test.mjs
python -m scripts.build_wreath_region --sample
python -m scripts.qa_wreath_region --sample
python -m scripts.build_wreath_region
python -m scripts.qa_wreath_region
# 아래는 오프라인 Canonical·사이트맵 생성 후보 검사뿐이며 실제 공개 아님
python -m scripts.build_wreath_region --public
python -m scripts.qa_wreath_region
```
- 대표 지역 6곳×2 의도 + 허브 = 23개 noindex HTML, [성공 run 40810124055](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40810124055).
- 전국 preview 10,336개, 10,337개 HTML(404 포함), 내부 링크 103,077건, 원본 주문 링크와 실사진 60,414건씩, 오류 0.
- 고정 표본 118개 × 전체 지역 문서 10,068개(자신 제외) = 정확한 1,187,906쌍 5-gram Jaccard. 최고 0.473684 (<0.49), 중복 본문 0, 위반 0. **모든 지역 본문 쌍 전수검사는 아님.**
- [전국 preview 검수 run 40810543208](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40810543208), [오프라인 공개 후보 run 40810797144](https://github.com/joseungil-kr/site-factory-v5/actions/runs/40810797144).
- 미리보기는 index 차단: HTML noindex·robots Disallow·sitemap 없음; Worker에서 기본 `WREATH_PUBLIC=0`.
- 대표 화면 브라우저 검수는 별도 `wreath-visual-qa.yml` 실행 결과 참조.

## 공개·검색 인계 (차단 조건)
- 보유 `nalmada.net` Cloudflare Zone active/custom-domain 조회 가능하나, 제안 호스트 `wreath.nalmada.net`은 현재 기존 custom-domain 연결 0개. DNS 레코드와 Workers Route 조회는 둘 다 HTTP 403이므로 **충돌 없음 검증 실패**. 기존 CF 관리 UI에서 직접 확인하고 부모와 도메인 연결을 조율하기 전까지 공개 배포하지 않는다.
- 전용 후보 Worker는 `sfv52-wreath-preview`. 기존 Quicksky/Wallsky/Flower/Daysky Workers/DNS/Secrets/권한은 그대로 유지한다.
- 공개 연결 이후에만 HTTPS 200/404, 실제 canonical·sitemap 전체 URL, product image/주문 링크, 모바일, IndexNow 유효 키 접수증 검사 및 검색 등록. Google/Naver 인증·제출은 부모 담당과 중복하지 않는다.
- **현재까지는 정적 산출물 생성·검증만 완료, 실제 Cloudflare 운영 URL 없음.**

## SEO 경쟁 원문
[sites/wreath-region/BENCHMARK.md](BENCHMARK.md) 세 원문 검색 결과 구조와 V5 제작 반영점을 참고.
