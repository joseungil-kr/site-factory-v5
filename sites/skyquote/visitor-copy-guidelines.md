# Skyquote visitor copy rules — applied to production generators

This is the source-level writing brief for every Skyquote HTML page and the RSS generated from it. The same rules are enforced in the base, Ansan and official-region generators.

## Visitor task
Help a person request a useful sky-lift quotation. In the first screen, explain what information helps the operator advise on equipment and cost, and make the verified phone contact easy to use.

## Say what helps the customer do next
- Ask for the job address/date/start time, actual work-point height in metres, horizontal distance from the truck parking position, occupants on the platform, tools/material weight, task type, expected duration and site photos.
- Explain the verified published price table: 1-ton half-day 4h ₩300,000 / day 8h ₩500,000; 3.5-ton ₩400,000 / ₩600,000; 5-ton ₩500,000 / ₩700,000. VAT is separate. Driver labour, fuel and basic equipment insurance are included. Night work after 18:00, holidays and long-distance transport may incur a surcharge after prior consultation. The published page does not specify an overtime hourly rate; say to confirm excess/waiting charges during consultation rather than inventing a figure.
- Use clear actions: prepare the site photo, share the measurements, call the verified operator.
- Use region names only as the page's search/navigation label. Do not invent local traffic, terrain, buildings, dispatch hubs, completed jobs, local stock or guaranteed arrival times.
- A real service area is only what the operator's current published directory supports. A page name does not itself prove local dispatch.

## Image handling
- Keep the five original 1536×1024 generated images, PNG sources, prompts, timestamps, tool output and hashes unchanged.
- Keep descriptive alt text and meaningful placement. Do not call illustrations completed work or owned equipment.
- Do not repeat a long defensive AI disclaimer under each image. Use no caption unless it helps the reader understand the illustration.

## Prohibited writing patterns
Do not use defensive or admonishing phrases such as:
- “업계 최저가를 주장하지 않습니다”
- “차량 톤수만으로 작업 가능성을 보장하지 않습니다”
- “실수를 피할 수 있습니다”
- “단정하지 마세요”, “기재합니다”
- “실제 환경을 조사한 결과가 아닌 견적용 가정”
- “AI 생성 설명 이미지 — 실제 시공·장비 보유 증명이 아닙니다”

Do not replace these with synonyms that keep the same defensive tone. Preserve material price, VAT, overtime/waiting, night/holiday/long-distance cost information in a useful customer-oriented form.

## QA policy
- The presence of a disclaimer is never a pass condition.
- Positive checks: the rate table and billing basis are visible; height, horizontal reach, people/material load and time are requested in plain language; contact is actionable; image alt and dimensions are correct; the content reads naturally.
- Negative checks are only safeguards against fabricated lowest-price, guaranteed dispatch, fake branches/jobs, unsupported price and local service claims.
- Build QA checks all 310 pages and the generated RSS item bodies. Human review reads home, district, dong and national samples. Chromium screenshots at 390px and 1440px verify actual rendering; a sample review is not reported as a full manual read of every page.
