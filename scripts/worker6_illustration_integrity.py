"""Fail-closed approved illustration validation; no product-photo substitutions."""
import hashlib
from pathlib import Path
EXPECTED={
 'a_bright_softly_lit_modern_office_desk_still_lif.webp':'6c75e9c0f5b31c200812187276f59370ea1d59d441ca3bfed1810843636a2482',
 'a_bright_softly_lit_indoor_desk_office_scene_in_a.webp':'5d9e359054e9aba0241cd8d7413099a81477e3305d6198eaebde7091caa8011f',
}
LABEL='연출 이미지 · 실제 판매 상품 사진 아님'
def verify_illustrations(directory):
    directory=Path(directory)
    missing=[];mismatched=[]
    for name,digest in EXPECTED.items():
        file=directory/name
        if not file.is_file():missing.append(name)
        elif hashlib.sha256(file.read_bytes()).hexdigest()!=digest:mismatched.append(name)
    if missing or mismatched:
        raise ValueError(f'approved raster missing={missing}, sha256 mismatch={mismatched}')
    return [directory/name for name in EXPECTED]
def require_rendered_illustrations(html):
    if html.count('<img ')<1 or LABEL not in html:
        raise ValueError('actual image element and non-product illustration label required')
    for name in EXPECTED:
        if name not in html:raise ValueError('missing approved illustration '+name)
    return True
