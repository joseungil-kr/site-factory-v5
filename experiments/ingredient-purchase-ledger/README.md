# 식당 식자재 매입 장부 (독립 시험판)

> 2026-11-05 / Google Apps Script + Google Sheets + Google Drive. **실제 Google 계정 배포 및 OAuth/OCR 실물 검수 전**의 시험판입니다. 기존 Site Factory·재고관리 시스템과 연결하지 않습니다.

## 지원 기능

- 휴대폰 사진 보관함에서 JPG/PNG/WEBP/GIF 원본 1개 업로드 (8MB 이내), 브라우저에서 미리보기
- Google Drive 이미지→Google Docs 변환 OCR로 텍스트 인식 후 **참고용** 한국어 날짜·거래처·품목·수량·단가·금액 추출
- OCR 원문/사진을 보면서 거래일·거래처·문서종류·결제상태·금액·메모, 품목 행을 직접 수정 후 저장
- Google Sheets `Documents` 문서 원장 및 `Items` 품목별 원장, Drive 비공개 `영수증 원본` 폴더
- 날짜/월별 매입, 거래처별 합계, 품목별 가격 변동(품명+규격+단위가 **모두 동일한 경우만**), 원본 재확인
- 같은 날짜·거래처·유사 금액 중복 경고 및 원장 간 수동 연결. 자동 병합·삭제 금지.
- 품목의 수량×단가 불일치, 품목 합계↔공급가액, 공급가액+부가세↔합계 불일치 경고. 원값 자동 변경 없음.
- CSV(한글 UTF-8 BOM, 수식 주입 완화) 내보내기, JSON **메타데이터** 내보내기
- Google Sheet 사본 백업·복구. **사진 파일은 시트 백업에 포함되지 않으므로 Drive 폴더를 별도로 보관**해야 합니다.
- 문서 숨김 처리(소프트 삭제); 기존 원본 삭제하지 않음.

## 설치·배포: 사용자 계정 권한 승인 후에만 진행

1. Google Apps Script (https://script.google.com/)에서 개인 프로젝트를 생성하고 `Code.gs`, `Index.html`, `Style.html`, `Core.html`, `Client.html`을 동일한 이름으로 추가합니다. 편집기의 프로젝트 설정에서 `appsscript.json`을 활성화하고 제공 파일 내용으로 대체합니다.
2. 권한 검토: `drive.file`(앱이 만든/접근 허용받은 Drive 파일), `script.external_request`(Google Drive/Sheets REST 호출), `script.storage`(앱 고유 시트/폴더 ID). 다른 도메인·외부 OCR 사업자로 사진을 전송하지 않습니다. 대신 사진은 **Google** Drive/Docs OCR 시스템으로 전송됩니다.
3. Google Cloud Project에서 Drive API, Sheets API가 필요한 환경일 수 있습니다. API 활성화, OAuth 동의, 최초 인증은 계정 소유자 승인·직접 수행 대상입니다.
4. 배포 > 새 배포 > 웹 앱. **실행 사용자=나**, **액세스 권한=나만**. URL을 외부에 공유하지 않고 먼저 단일 사용자 로그인으로 검증합니다. 일반인 전체 공개 배포 금지. 배포 생성 시 실제 권한 화면을 확인하세요.
5. 웹앱의 설정·백업에서 `장부 저장소 초기화`를 누르면 앱 전용 Drive 폴더, 사진 폴더, Google Sheets 원장 두 탭이 생성됩니다. 기존 공유 시트·기존 Drive 폴더에는 쓰지 않습니다.
6. 실거래정보 없는 샘플 사진으로 OCR→원문 확인→품목 수정→저장→새로고침→재조회→사진 재열람→CSV/백업/복원까지 점검한 다음 실사용을 시작하세요.

실제 사용자 인증·Drive API 권한 동작을 테스트하기 전에는 개인/거래처 정보 입력 **금지**. Google Apps Script 웹 앱 접근 권한을 `ANYONE`/`ANYONE_ANONYMOUS`로 설정하면 안 됩니다.

## 자체 시연용 파일

`demo.html`은 네트워크 없이 화면과 문서 입력, OCR **원문 수동 입력** 테스트가 가능한 브라우저 로컬 시험판입니다. 브라우저의 IndexedDB에 해당 브라우저 한정으로 저장됩니다. **실계정 보안 앱이 아니므로 실거래처/개인정보를 입력하지 마세요.** Google OCR·Google Sheets 저장·백업·복원은 시연 모드에서 작동하지 않습니다. 사진은 로컬 IndexedDB에 저장되며 브라우저 저장 공간을 지우면 사라집니다.

터미널에서 `npm test`로 핵심 계산 12개 단위 테스트를 실행하고 `npm run build`로 최신 데모 HTML을 다시 생성할 수 있습니다. Node 20 이상, 외부 npm 라이브러리 없음. 실물 OCR 예시 3장/테스트 문구는 **가공된 합성 이미지**입니다. 로컬 `tesseract kor+eng` 검사만 수행했고 실제 Google Drive OCR 및 휴대폰 촬영 사진 정확도는 미검증입니다.

## 데이터 스키마

- Documents: `id,date,supplier,type,supply,tax,total,payment,memo,imageId,imageName,relatedId,createdAt,updatedAt,status`
- Items: `id,docId,name,spec,unit,quantity,unitPrice,amount,active,updatedAt`
- 결제 상태: 미확인 / 미지급 / 지급완료. **매입금액과 실제 지출을 같은 것으로 추정하지 않음**.
- 거래 명세서와 실제 결제 영수증: 서로 다른 문서로 저장 가능. `relatedId`는 수동 연결 근거이며 **매출·재고와 자동 연동하지 않음**.
- 금액·수량·날짜·결제상태 누락은 공란/미확인으로 보존.

Google Sheets는 관계형 DB가 아닙니다. 앱에 LockService와 낙관적 수정 충돌 검사를 적용했지만 다중 REST 호출(문서 저장+품목 갱신) 사이 완전한 원자적 트랜잭션을 보장하지 않습니다. 저장 실패 시 시트 원본을 확인해야 하며, 사용자 1명·낮은 건수 전제로 적합합니다. 셀별 직접 수정/삭제가 앱의 내부 ID와 활성화 상태를 망가뜨리지 않도록 **문서ID·행ID 등의 내부 열은 직접 수정하지 않는 편이 안전합니다**.

## 개인정보·권한·비용

- GitHub에 OAuth 액세스 토큰·API key·비밀번호·영수증 실물 첨부하지 않음.
- 웹앱 액세스 `MYSELF`/실행 `USER_DEPLOYING`(매니페스트 기준); **운영 배포에서 실제 설정과 타 계정 차단 동작을 재검증해야 함**.
- Cloudflare Worker, D1, R2, 신규 도메인을 만들거나 변경하지 않음. Google Sheets/Drive를 먼저 사용. 기존 재고관리 시스템 미변경.
- Google 개인 계정 Drive 무료 저장 공간(다른 Google 서비스와 공유)과 Apps Script/API 할당량에 제한이 있음. 무료 보장/무제한 OCR 아님. Google Drive OCR을 이용하므로 유료 제3자 OCR API 결제는 없음.
- 시트 복사만으로 사진 백업이 되지 않음. 앱 폴더의 사진을 별도 Drive 내보내기/동기화/백업 필요. JSON도 사진 파일을 포함하지 않음.

## 직접 확인한 것 / 못 확인한 것

- 확인: 코드 구문 검사, Node 핵심 로직 단위 테스트 12건, 한글 합성 이미지 3장의 로컬 Tesseract OCR 출력 점검(인식 누락·규격 오류 존재).
- 부분 검증: 브라우저 로컬 시연 파일 생성·정적 HTML 구조; 모의 서버 검사는 별도 테스트 스크립트에 표시.
- 미확인: Google 로그인, Apps Script 권한 적용, Drive→Docs OCR, Sheets 실저장, 사진 실보관, 실제 한국어 거래명세서 정확도, 모바일 390px 렌더링, 외부 접근 차단, Cloudflare 및 운영 URL.
- 브라우저 자동화 차단: 이 실행환경에서 Playwright 페이지 열기는 관리자 차단으로 실패하여 사용자 플로우 자동 검증 완료라고 주장할 수 없음.
