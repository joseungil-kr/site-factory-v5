"""Local immutable archives, readback validation and guarded rollback."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from .config import ConfigError,ROOT,validate_site_id
from .engine import report_dir,target_dir,sha


def archive(site_id,root=None,manifest=None):
    validate_site_id(site_id)
    output=(root or target_dir(site_id)).resolve()
    report=report_dir(site_id)
    if manifest is None:
        location=report/'manifest.json'
        if not location.is_file():raise ConfigError('No manifest to archive')
        manifest=json.loads(location.read_text(encoding='utf-8'))
    expected=manifest['files']
    actual={p.relative_to(output).as_posix():sha(p.read_bytes()) for p in output.rglob('*') if p.is_file()}
    if actual!=expected:raise ConfigError('Local archive integrity check failed')
    from .engine import stable_hash
    release_hash=manifest.get('releaseHash') or stable_hash({'sourceDigest':manifest['sourceDigest'],'files':manifest['files']})
    revision=release_hash[:16]
    dest=report/'snapshots'/f'{revision}.zip'
    dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():
        with ZipFile(dest,'w',ZIP_DEFLATED,compresslevel=6) as z:
            for name in sorted(actual):z.write(output/name,arcname='site/'+name)
            z.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,sort_keys=True))
    return {'file':str(dest),'revision':revision,'sha256':sha(dest.read_bytes()),'files':len(expected)}


def restore_local(site_id,revision,*,output=None):
    validate_site_id(site_id)
    if not revision or len(revision)>64 or not all(x in '0123456789abcdef' for x in revision):
        raise ConfigError('Snapshot revision must be lowercase hexadecimal')
    path=report_dir(site_id)/'snapshots'/f'{revision}.zip'
    if not path.is_file():raise ConfigError('Missing snapshot: '+revision)
    dest=(output or target_dir(site_id)).resolve()
    if not dest.is_relative_to(ROOT/'dist'):
        raise ConfigError('Restore output must stay in managed dist')
    import tempfile,shutil
    dest.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='restore-',dir=dest.parent) as work:
        staging=Path(work)/'restored';staging.mkdir()
        with ZipFile(path) as z:
            manifest=json.loads(z.read('manifest.json'))
            from .engine import stable_hash
            calculated=stable_hash({'sourceDigest':manifest['sourceDigest'],'files':manifest['files']})
            if manifest['siteId']!=site_id or calculated[:len(revision)]!=revision:
                raise ConfigError('Snapshot site or revision mismatch')
            expected=manifest['files']
            for name,expected_hash in expected.items():
                if '\\' in name or name.startswith(('/','../')) or '/..' in name:
                    raise ConfigError('Path traversal in archive')
                target=staging/name;target.parent.mkdir(parents=True,exist_ok=True)
                data=z.read('site/'+name)
                if sha(data)!=expected_hash:raise ConfigError('Snapshot file hash mismatch '+name)
                target.write_bytes(data)
            previous=Path(work)/'previous'
            if dest.exists():dest.rename(previous)
            try:
                staging.rename(dest)
            except Exception:
                if previous.exists() and not dest.exists():previous.rename(dest)
                raise
            report=report_dir(site_id)
            (report/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'restored':revision,'files':len(expected),'output':str(dest)}
