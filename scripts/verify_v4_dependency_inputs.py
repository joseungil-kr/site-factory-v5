"""Read pinned local inputs only; never download, extract, build, patch or deploy."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def verify_digest(path, expected, size=None):
    data = Path(path).read_bytes()
    if digest(data) != expected or (size is not None and len(data) != size):
        raise ValueError('Input digest/size mismatch: ' + str(path))
    return data

def safe_members(archive):
    names = archive.namelist()
    if len(names) != len(set(names)):
        raise ValueError('Duplicate archive paths')
    for name in names:
        p = PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or '\\' in name:
            raise ValueError('Unsafe archive path')
    return names

def verify_official(path, dep, upper_path):
    data = verify_digest(path, dep['sha256'], dep['size'])
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = safe_members(archive)
        if len(names) != 1:
            raise ValueError('Unexpected government archive members')
        rows = list(csv.reader(io.StringIO(archive.read(names[0]).decode('cp949')), delimiter='\t'))
    if rows[0] != ['법정동코드', '법정동명', '폐지여부']:
        raise ValueError('Unexpected source columns')
    active = {r[0]: r[1].strip() for r in rows[1:] if len(r) == 3 and r[2].strip() == '존재'}
    lower = [name for name in active.values() if name.split()[-1].endswith(('읍', '면', '동'))]
    upper = json.loads(Path(upper_path).read_text())['entries']
    if (len(rows)-1, len(active), len(lower), len(upper)) != (53403, 20560, 4632, 284):
        raise ValueError('Unexpected official region counts')
    if any(active.get(x['code']) != x['fullName'] for x in upper):
        raise ValueError('Upper-region source mismatch')
    if any(not any(name.startswith(x['fullName']+' ') for x in upper) for name in lower):
        raise ValueError('Unmatched lower-region parent')
    return {'sourceRows':len(rows)-1, 'activeRows':len(active), 'matchedLowerRows':len(lower), 'upperRows':len(upper)}

def verify_todayflower(path, dep):
    data = verify_digest(path, dep['sha256'])
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = safe_members(archive)
        manifest = json.loads(archive.read('reports/todayflower-nalmada/manifest.json'))
        if (manifest.get('siteId'), manifest.get('mode'), manifest.get('pageCount'), len(manifest.get('files',{}))) != ('todayflower-nalmada','preview',5070,5087):
            raise ValueError('Unexpected artifact manifest')
        for name, sha in manifest['files'].items():
            p = PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts:
                raise ValueError('Unsafe manifest path')
            if digest(archive.read('dist/todayflower-nalmada/'+name)) != sha:
                raise ValueError('Artifact member digest mismatch: '+name)
        return {'contentPages':5070, 'verifiedManifestFiles':5087, 'archiveBytes':len(data), 'archiveMembers':len(names)}

def verify_sources(inputs, dep):
    for item in dep['sourceFiles']:
        verify_digest(Path(inputs)/item['localPath'], item['sha256'])
    return {'sourceFilesVerified':len(dep['sourceFiles']), 'siteRegenerated':False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--official-archive', type=Path)
    parser.add_argument('--todayflower-artifact', type=Path)
    args = parser.parse_args()
    manifest=json.loads((ROOT/'docs/v4-dependency-manifest.json').read_text())
    deps={d['id']:d for d in manifest['dependencies']}
    results={'deploymentPerformed':False,'migrationComplete':False}
    for key in ('skyquote-official-regions','clinic-rss-composite'):
        results[key]=verify_sources(args.inputs,deps[key])
    if args.official_archive:
        results['officialArchive']=verify_official(args.official_archive,deps['skyquote-official-regions'],args.inputs/'skyquote/sites/skyquote/official-upper-regions-20261022.json')
    else:
        results['officialArchive']='NOT_CHECKED'
    if args.todayflower_artifact:
        results['todayflowerArtifact']=verify_todayflower(args.todayflower_artifact,deps['todayflower-artifact'])
    else:
        results['todayflowerArtifact']='NOT_CHECKED'
    print(json.dumps(results,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
