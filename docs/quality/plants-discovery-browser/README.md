# Local browser verification — 2026-10-28

Executed using installed Google Chrome headless and bundled Playwright 1.62.1 against localhost only. Viewports: desktop 1440×1000, mobile 390×844, small mobile 320×800. Screenshots were visually inspected. Browser/server processes were closed after testing.

- Raw static directory link count matched the expected inventory.
- First and last native-details groups opened and closed through browser clicks.
- Root scrollWidth equalled viewport width at all three widths: closed, first/last expanded, and every group expanded together.
- JavaScript-disabled mobile context: native-details expansion and visible static links passed.
- Phone and shop links received real browser clicks with navigation prevented; hrefs were verified. No phone call, external order or purchase was made.
- No page JavaScript exceptions.
- No persistent layout or behavior regression was found; no site-code changes were made during this verification.

Tested source HEAD: 0f545102f271c1d682d8f4f5cf2df45fb18604a3. Served the already audited public-indexing build locally.

53 directory groups, 3,464 static detail links. Existing main navigation reached /2.html; 3 related cards remained. Calculator accepted quantity 3 and displayed 159,000원 at all widths. A first screenshot taken during scroll/hover transition looked white; after the transition the button was visibly correct, with white text on rgb(242,81,93). It was a capture timing artifact, not a lasting defect; no CSS change was made. Plants has no enabled search widget, so no search functionality was claimed.

Production branches, workflow pins and deployment state were not changed. These screenshots prove local Chromium behavior, not actual mobile-device or production readback.
