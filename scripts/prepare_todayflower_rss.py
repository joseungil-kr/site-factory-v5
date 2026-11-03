"""Reuse the exact deployed preview artifact and its existing public-host rendering."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
ORIGIN = 'https://todayflower.nalmada.net'
OLD = '<meta name="robots" content="noindex,nofollow">'
NAVER = '<meta name="naver-site-verification" content="d970eeb70abc7b36cbcc02fadd9362c5c57fcb46" />'
DIGEST = '16b52597fe77b0b4311ea21ad5daf6c5193af94346f8dc8df9834e676003a180'


def build(archive: Path, baseline: bool = False):
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == DIGEST
    assets = ROOT / 'dist/todayflower-nalmada'
    public = ROOT / 'dist/todayflower-public-view'
    for target in (assets, public):
        assert target.resolve().is_relative_to(ROOT) and target.parent == ROOT / 'dist'
        if target.exists():
            shutil.rmtree(target)
    assets.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='todayflower-pinned-', dir=ROOT) as folder:
        unpack = Path(folder).resolve()
        with zipfile.ZipFile(archive) as source:
            for item in source.infolist():
                assert (unpack / item.filename).resolve().is_relative_to(unpack)
            source.extractall(unpack)
        original = unpack / 'dist/todayflower-nalmada'
        manifest = json.loads((unpack / 'reports/todayflower-nalmada/manifest.json').read_text(encoding='utf-8'))
        assert manifest['siteId'] == 'todayflower-nalmada' and manifest['mode'] == 'preview'
        assert manifest['pageCount'] == 5070 and len(manifest['files']) == 5087
        for name, expected in manifest['files'].items():
            file = original / name
            assert file.resolve().is_relative_to(original.resolve()) and file.is_file()
            assert hashlib.sha256(file.read_bytes()).hexdigest() == expected, name
        shutil.copytree(original, assets)
    paths = ['/'] + ['/' + str(n) + '.html' for n in range(2, 5072) if n != 404]
    assert len(paths) == len(set(paths)) == 5070
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    sitemap += ''.join('<url><loc>' + ORIGIN + path + '</loc></url>' for path in paths) + '</urlset>'
    (assets / 'sitemap.xml').write_text(sitemap, encoding='utf-8', newline='\n')
    shutil.copytree(assets, public)
    for path in paths:
        file = public / ('index.html' if path == '/' else path.lstrip('/'))
        html = file.read_text(encoding='utf-8')
        assert html.count(OLD) == 1 and 'rel="canonical"' not in html, path
        replacement = '<meta name="robots" content="index,follow"><link rel="canonical" href="' + ORIGIN + path + '">'
        if path == '/':
            replacement += NAVER
        file.write_text(html.replace(OLD, replacement, 1), encoding='utf-8', newline='\n')
    result = {'pages': len(paths), 'artifactSHA256': DIGEST, 'previewAssetsPreserved': True}
    if not baseline:
        from v5.rss import generate
        result.update(generate(public, ORIGIN, '오늘꽃', body_tag='body'))
        shutil.copy2(public / 'rss.xml', assets / 'rss.xml')
    report = ROOT / 'reports/todayflower-nalmada'
    report.mkdir(parents=True, exist_ok=True)
    (report / 'rss-build.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifact', required=True, type=Path)
    parser.add_argument('--baseline', action='store_true')
    args = parser.parse_args()
    build(args.artifact, args.baseline)
