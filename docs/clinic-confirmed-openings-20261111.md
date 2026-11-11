# Clinic official opening/relocation verification — 2026-11-11

## Outcome
- **2 historic opening records corroborated by institution/municipality materials.**
- **0 verified currently upcoming openings or confirmed relocations** in the searched scope.
- **2 records deferred** rather than assigned to a marketing intent.
- Offline prototype: `prototypes/clinic-confirmed-openings-20261111`, exactly 2 event-case HTMLs plus index.
- Operating site HTML, DNS, permissions, robots, IndexNow, workers and redirects untouched.

## Verified historic openings
1. **Suwon, Yeonmu-dong — 어울림건강생활지원센터**. The institution's official 2026-06-02 notice states it commenced operation **2026-03-26**; the municipality's 2026-04-14 press release gives **장안구 경수대로744번길 55, 연무마을 어울림터 3~4층** and confirms it opened. Sources:
   - https://health.suwon.go.kr/board_view.asp?bd_gubn=&no=5&page_code=sub051103
   - https://www.suwon.go.kr/web/board/BD_board.view.do?bbsCd=1043&seq=20260414092346075
   - https://council.suwon.go.kr/viewer/minutes.do?mem_sch=01009&schwrd=&uid=14521
   - Note: the healthcare center's official bulletin was indexed but opening the source in this search returned a cache miss. The municipality source and council's post-event account also confirm the opening. No evidence on gift-delivery admission.
2. **Seoul, Jongno-gu — 서울대학교병원 대한외래**. Direct official article dated **2019-04-05** says its opening celebration occurred **2019-04-03**. Official hospital history distinguishes the start of outpatient care **2019-02-25**. This is not a 2026 event.
   - https://www.snuh.org/board/B003/view.do?bbs_no=4782&pageIndex=1&searchKey=&searchWord=
   - https://dept.snuh.org/dept/HHCC/content.do?menuId=003013
   - https://www.snuh.org/content/E003002007.do
   - No proof wreath installation or gift reception was permitted.

## Deferred / not qualified
- **Ansan Danwon-gu 구강보건센터**. Official municipality January 2023 newsletter, published **2022-12-29**, listed a *future proposed* 2023-07-01 opening date. A dated post-opening completion confirmation was not recovered; treated as a historical announcement **not** proof the actual event occurred.
  - https://www.ansan.go.kr/ansantalktalk/UPDIR/newsletter/3547469391_TBcCwyNo_c53451fe1e6e52193db71ddda7cb569fb46c08b1.pdf
- **Current healthcare relocation**. No specific institution with verified recent relocation date, new address and notice was confirmed in this research set. Exclude.

## Actual offline technical verification
- Workflow `clinic-confirmed-openings-offline-20261111.yml`, GitHub Actions run **43022661073** passed.
- Exactly 3 HTMLs (index + 2 historic event examples), 4 screenshots (two cases at 390px and 1440px), 2 reproduced matching legacy region HTMLs.
- Exact old comparisons: `clinicopen.nalmada.net/r/00547.html` Suwon Yeonmu-dong, `clinicpresent.nalmada.net/r/03222.html` Seoul Jongno-gu Yeongeon-dong. These were reproduced from a pinned **previous candidate generator**, **not** verified current live bytes.
- Source URLs and event dates included directly on each page.
- SKU original links, price snapshot **2026-11-05 only**, phone `tel:1844-0644`, browser navigation, Korean typography and width verified. No actual outside URL purchase click or phone call.
- `noindex,nofollow` in every prototype HTML. No sitemap, redirect or deployment.
- ZIP artifact `clinic-historical-opening-evidence-20261111`, run 43022661073, archive digest sha256 `aecdc6336c8d34d2d992cb3cc0b92620ae92b3ab7afa8a492c132a96ae32fe78`.

## Editorial/sales interpretation
These two cases demonstrate **source-to-page evidence mapping**, but they are **not current conversion-oriented regional product pages** because their events ended in 2019 and March 2026. The facilities' location and event history does not imply gift acceptance, available shipments or currently applicable orders. Do not publish or treat as complete business outcomes. Prior 324 repetitive sample paths remain intact.

## Privacy and permissions
No patient data, contact submissions, outside outreach, credentials, DNS changes, SEO submissions or production deployments.
