# 신규 사이트 공유 Worker 운영 빌드·배포 준비

`v5.shared_release`는 V5의 기존 생성기를 재사용해 **신규 상품 주문형 및 서비스 문의형 사이트**의
운영용 HTML·이미지·SEO·RSS 산출물을 하나의 Worker 패키지로 준비한다.
기존 사이트의 내용·도메인·주문 링크·Worker·배포 워크플로는 변경하지 않는다.
배포·DNS·권한·보안 설정 변경과 운영 사이트 HTTP 호출은 실행하지 않는다.

HTML은 호스트를 구분하기 위해 요청당 Worker 실행 1회를 사용한다. 이미지·CSS는 로컬에서 0회 진입을 확인했지만
실제 Cloudflare 호출 집계나 비용 절감은 미검증이다. HTML까지 0회라는 가정이나 zone rewrite는 사용하지 않는다.

## 신규 사이트 입력과 생성

이미 승인된 신규 사이트 입력 원장을 사용한다. 이 작업에서 실제 신규 사업 사이트를 만들거나
상품의 재고·가격·이미지 사용 승인을 새로 만들어 기록하지 않았다.

- `site.json`: `deliveryMode: "shared-static"`, `workerName: "sfv5-new-sites-<group>"`.
- 기존 publish 조건: 실제 HTTPS 도메인, `publishEnabled: true`, 승인된 이미지·개인정보 검토,
  상품별 검증 상태와 데모가 아닌 자료. analytics와 legacy `publicIndexingApproved`는 꺼 둔다.
- `site-spec.json`: 기존 계획 검사를 통과한 `approved: true`, `publishPolicy.mode: "publish"`.
  계획의 도메인·페이지 수가 실제 입력과 일치해야 한다.
- 전체 이미지 목록을 기존 `scripts.check_image_origin`의 명시적 release 검증에 넣는다.
  기존 이미지를 재사용해도 출처 증거가 없으면 중단한다.
- 다른 사이트가 사용하는 도메인이나 이 묶음 밖에서 사용하는 Worker 이름은 거부한다.
  여러 신규 사이트의 Worker 이름은 동일해야 하고 이 묶음의 전체 구성원을 함께 준비해야 한다.
- 새 폴더만 허용한다. 기존 소스나 이전 릴리스 폴더를 덮어쓰지 않는다.

```console
python -m v5.shared_release prepare --site <new-a> --site <new-b> --worker sfv5-new-sites-fwith --output dist/shared-fwith-r1
python -m v5.shared_release verify dist/shared-fwith-r1
```

상품형은 `v5.engine.build(..., mode='publish')`와 기존 품질 검사를 그대로 호출한다.
서비스형은 기존 `service-lead` preview 생성기의 원본을 보관한 뒤 별도 파생본의 SEO만 운영용으로 준비한다.
서비스형의 `publishEnabled`는 기존 검증 규칙에 따라 false로 유지한다. 새 사이트의 승인된 publish 계획 외에
`servicePublicationApproved`, `serviceFactsApproved`, 이미지·개인정보 검토를 요구하며
계획의 phone 문의 값이 사이트 전화와 정확히 같아야 한다. 기존 서비스 렌더러·validator·engine는 바꾸지 않는다.
본문·전화·문의·요금 UI는 원본과 동일하고, 파생본의 canonical·robots·sitemap·RSS를 별도로 검사한다.
설정된 Naver 검증 값은 40자리 hex 검사 후 홈페이지에만 반영한다.
불확실한 가격 문구 등 새 사이트용 방문자 문구 검사도 통과해야 한다.

단일 사이트용 `v5.deploy.preflight`에는 새 `deliveryMode`에만 적용되는 거부 조건을 추가했다.
이를 통해 기존 `prepare-worker`/publish 경로가 공유 Worker를 사이트 하나의 파일로 덮어쓰지 못하게 한다.
기존 사이트는 이 속성이 없어 기존 동작이 유지된다. engine·markup·기존 Worker·workflows는 수정하지 않았다.

## 파일과 호스트 격리, SEO와 RSS

- 허용된 정확한 호스트와 해당 파일 목록으로 HTML을 선택한다. 다른 호스트의 내부 HTML은 404다.
- `/`, `/index.html`, 번호 HTML과 한글 파일명 규칙을 유지한다. 퍼센트 문자 파일명도 재인코딩해 다른 파일로 잘못 매칭하지 않는다.
- 기존 publish 생성기의 canonical·sitemap·robots를 보존하고 패키징 후 호스트·URL·파일 실재성을 다시 검사한다.
  sitemap URL은 해당 호스트의 정확한 canonical과 일치해야 한다. 404와 검색 페이지는 noindex를 유지한다.
- `/rss.xml`은 실제 페이지 원장으로 생성한다. 번호 역순 최대 50개이며 실제 수정일 순이라고 주장하지 않고 날짜를 만들지 않는다.
  GUID는 canonical URL과 동일하다. HTML head에 feed 자동발견 링크를 추가한다.
  원본 생성기에 이미 `rss.xml`이 있다면 덮어쓰지 않고 충돌로 중단한다.
- 원본 전화·상품 주문 링크는 그대로 유지한다. 다른 도메인의 `/assets/` 주문 주소도 변경하지 않는다.
- 이미지·CSS·JS는 해시 경로의 공개 정적 자산이다. 의도적으로 여러 호스트에서 접근 가능한 공용 자산이며
  HTML이나 비공개 자료는 허용하지 않는다. 외부 링크를 다르게 처리하는 CSS는 해시도 달라져 덮어쓰지 않는다.
- `/__v5_event`는 비활성화되어 있다. HTML·robots·sitemap·RSS·검색 인덱스·일반 404 요청은 Worker 실행을 사용한다.

## 산출물과 원본 복구

`public/`만 Worker 정적 자산 디렉터리다. 아래 보관 자료는 공개 디렉터리 밖이다.

- `source-builds/<id>/`: 기존 생성기의 원본 출력 그대로.
- `source-inputs/<id>/`: 입력 JSON 원장, 확장 후 검증된 입력, 원본 build manifest.
- `release.json`: 모든 산출물 파일의 SHA-256와 릴리스 해시, Worker/호스트 식별 정보.
- `release.zip`: 위 파일을 복원할 수 있는 스냅샷. 자체 ZIP을 반복 포함하지 않는다.
- `snapshot.json`: 복구 ZIP 자체의 SHA-256와 릴리스 식별 정보. verify는 ZIP 존재·해시·내부 파일까지 검사한다.
- `deployment-plan.json`: 정확한 호스트별 custom domain 연결 **제안**, 계정 확인·edge 검증·복구의 미완료 항목.
- `wrangler.json`: 운영용 코드·정적 자산 설정. `workers_dev: false`, `preview_urls: false`, 실제 `routes` 없음.

```console
python -m v5.shared_release restore dist/shared-fwith-r1/release.zip --output dist/shared-fwith-restored
python -m v5.shared_release verify dist/shared-fwith-restored
python -m v5.shared_release prepare --site <new-a> --site <new-b> --worker sfv5-new-sites-fwith --previous dist/shared-fwith-r1 --output dist/shared-fwith-r2
```

ZIP 복원은 명시된 파일과 해시를 확인하며 경로 이탈·중복 항목·추가 파일을 거부한다.
복원 결과에도 같은 ZIP과 hash record를 보존한다. 다음 `--previous`는 이를 필수 확인하므로
복원한 폴더를 사용해도 이전 ZIP 해시가 null로 끊기지 않는다.
초기 실험 버전의 폴더에 snapshot.json이 없다면 새 verify는 거부한다. 원래 ZIP을 새 폴더로 restore하면
내부 파일을 검증한 후 hash record를 만들어 이력을 이어갈 수 있다.
이전 릴리스를 지정한 업데이트는 기존 호스트/URL 삭제·호스트 재할당·Worker 이동을 거부한다.
캐시된 옛 HTML에서 참조하는 이전 해시 자산도 보존한다. 보존 후 **전체** 자산 18,000개를 넘으면 중단한다.
옛 자산의 자동 삭제는 하지 않는다. 이전 전체 ZIP과 새 계획의 이전 릴리스 해시·ZIP 해시를 함께 보관한다.
Cloudflare 이전 배포 버전 ID는 실제 배포 전에 별도로 확인해야 하며 임의로 채우지 않는다.
최초 배포는 아직 사용하지 않는 새 Worker여야 한다. 운영 rollback을 실행하거나 검증한 상태가 아니다.

## 안전한 edge 검증 후보

```console
python -m v5.shared_release probe dist/shared-fwith-r1 --output dist/shared-fwith-edge-probe
```

릴리스와 분리된 `sfv5-new-sites-probe-<releaseHash 앞 12자>` 후보 설정을 생성한다.
모든 응답과 정적 파일에 noindex를 강제하고 robots를 차단한다. 정확히 허용된
`X-SFV5-Probe-Host` 헤더로 호스트 선택을 시험하므로 **실제 custom domain이나 DNS가 필요하지 않다**.
이 테스트 헤더 처리 코드는 운영 패키지에 들어가지 않는다. routes·secrets·cron·서비스 바인딩도 없다.

이번 가상 자료의 정확한 후보 이름은 **`sfv5-new-sites-probe-a3bbebd671b6`**다.
이전 준비 시점의 새 이름 후보이며 그 산출물에는 `workerNameAvailabilityVerified: false`가 기록되어 있다.
후속 조사에서는 기존 Wrangler OAuth 세션으로 관리 API를 조회했다. 새 Worker 생성보다 기존 테스트 Worker
재사용을 우선하며, 현재 판단은 [서비스형·복구·기존 테스트 Worker 후속 검증](SHARED_SERVICE_AND_RECOVERY_20261103.md)에 기록한다.
이번 지시에서 새 Worker 생성 및 실제 배포는 실행하지 않았다.

진행 조건은 그 정확한 이름의 미사용 확인, 해당 새 Worker만의 별도 실행 승인, 운영 호스트 연결 없음,
최대 12회 제한 요청, 링크 추적·상품 호출·IndexNow 제출 없음이다. HTML·정적 자산 요청을 분리하여
Workers 로그와 계정 통계를 각각 확인해야 한다. 이는 로컬 테스트로 대체할 수 없다.
현재 준비한 probe는 zone Transform Rules 순서를 검증하는 도구가 아니다.

## 오프라인 검증 자료

`tests/test_shared_release.py`는 publish 생성기 실제 실행 조합, SEO·RSS, 출처 거부,
기존 단일 사이트 배포 차단, 소스 해시, ZIP 복원과 변조·경로 이탈 거부, 호스트 삭제 거부와
옛 자산 보존을 검사한다. 테스트 자료의 승인 플래그와 출처 mock은 가상 자료에만 적용하며 실제 사업 승인이 아니다.
`worker/shared-static.test.mjs`는 운영 모드의 SEO 헤더와 미등록/오류 호스트 noindex도 검사한다.

`scripts.verify_shared_static_local`은 localhost에서 미리보기·대조·운영 준비 모드 22개 결과를 저장한다.
운영 모드에서도 HTML·robots·sitemap·RSS는 각 1회, CSS는 0회 진입이었다.
[저장 증거](shared-static-local-evidence-20261103.json)의 `productionRequests: 0`은 운영 서버에 보낸 요청이 없다는 뜻이다.
`edgeBillingVerified: false`이며 실제 비용 절감은 확인하지 않았다.

로컬 `dist/shared-production-release-proof-20261103/`와 `dist/shared-edge-probe-proof-20261103/`는
`new-a.example.test`, `new-b.example.test` 가상 자료의 검토용 산출물이다. 실제 사이트 제작 완료로 취급하지 않는다.
Wrangler `deploy --dry-run`은 번들 컴파일만 수행하며 Worker를 업로드·배포하지 않는다.
`--outdir` 상대 경로는 config 폴더 기준이므로 보관 패키지 밖의 **절대 경로**를 사용한다.
이번 검사에서 패키지 안에 생긴 dry-run 출력도 무결성 검사가 추가 파일로 거부했다.
원본 ZIP으로 새 폴더에 복원한 후 외부 출력 경로로 컴파일했고 보관 파일은 변하지 않았다.
dev의 `.wrangler` 상태 파일도 보관 원본이 아닌 별도 작업 복사본에 생성한다.

검사 결과: Python 3.12 UTF-8 전체 95개 통과 후 자산 변경 시 옛 해시 파일 보존 검사도 통과,
최종 신규 release 검사 8개 통과, Node 검사 10개 통과. 로컬 호출 검사 22개 통과.
운영 및 probe 패키지의 dry-run 컴파일도 통과했다 (업로드 예정 번들 2.75 KiB / gzip 1.13 KiB,
probe 3.47 KiB / gzip 1.26 KiB; 가상 자료 크기이며 실제 대형 사이트 용량 보장이 아님).
[가상 운영 준비·복구 증거](shared-production-fixture-evidence-20261103.json)에 릴리스와 ZIP 해시를 보관했다.
계정 자원 생성·배포는 0회다.
