"""Prevent internal status labels and mockup copy leaking into customer-facing HTML.

This gate is intentionally limited to visible user-facing text and accessibility
labels; it does not remove crawler directives, audit metadata or provenance.
Unverified business claims must be omitted or independently checked, not
converted into confident assertions to pass this test.
"""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import re

FORBIDDEN = (
    r"공사\s*중", r"준비\s*중", r"검수용", r"테스트용", r"미리보기\s*버전",
    r"미검증", r"미확정", r"미확인\s*상품", r"자리\s*표시자",
    r"보유\s*상품\s*사진", r"실제\s*상품\s*구성은\s*달라질\s*수\s*있습니다",
    r"공통\s*상품\s*사진", r"장례식장\s*건물\s*사진이\s*아닌",
    r"원장\s*(?:기재|기준)", r"참고\s*가(?:격)?", r"참고\s*금액",
    r"검색\s*제외", r"디자인\s*시안", r"상품\s*정보\s*준비",
    r"사진\s*사용\s*예정", r"가상\s*이미지", r"해당\s*장례식장\s*배송비를\s*보장하지"
)
PATTERNS = tuple(re.compile(p, re.I) for p in FORBIDDEN)


class _VisitorText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "template", "noscript"):
            self.skip += 1
        if not self.skip:
            for key, value in attrs:
                if key in ("alt", "title", "aria-label", "placeholder") and value:
                    self.parts.append(value)

    def handle_endtag(self, tag):
        if tag in ("script", "style", "template", "noscript") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(data)


def visible_copy_errors(markup: str) -> list[str]:
    parser = _VisitorText()
    parser.feed(markup)
    content = " ".join(parser.parts)
    return sorted({match.group(0) for p in PATTERNS for match in p.finditer(content)})


def audit_html_tree(root: Path) -> dict[str, list[str]]:
    return {str(p.relative_to(root)): problems
            for p in sorted(root.rglob("*.html"))
            if (problems := visible_copy_errors(p.read_text(encoding="utf-8")))}


def require_clean_html(root: Path) -> None:
    errors = audit_html_tree(root)
    if errors:
        example = "; ".join(f"{p}: {', '.join(matches[:3])}"
                            for p, matches in list(errors.items())[:5])
        raise ValueError("Temporary/inaccurate user-facing copy blocked: " + example)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Audit visible HTML copy for internal status labels")
    p.add_argument("directory", type=Path)
    args = p.parse_args()
    require_clean_html(args.directory)
    print("VISITOR_COPY_GATE_PASS: "+str(args.directory))
