#!/usr/bin/env python3
"""Site Factory V5 image-origin release gate (no network, no mutation).

For NEW/CHANGED image assets, a bare AI label or a matching filename/hash is
insufficient. A real generator tool result and prompt/timestamp, or an exact
user-authorized original/photo grant, must be recorded. Unchanged legacy
images are audited as review-hold, not deleted or retroactively un-deployed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
REGISTRY_DIR=ROOT/"docs/image-governance"
IMAGE_SUFFIXES={".webp",".png",".jpg",".jpeg",".avif",".gif",".svg"}
ALLOWED_SOURCE_TYPES={"GENERATED_VERIFIED","USER_APPROVED_EXTERNAL","USER_SUPPLIED_ORIGINAL"}
BLOCKED_SOURCE_TYPES={"GENERATION_EVIDENCE_PARTIAL","SOURCE_UNVERIFIED","RESEARCH_ONLY"}
IMG_HOTLINKS=(
    re.compile(r'<(?:img|source)\b[^>]*\b(?:src|srcset)\s*=\s*["\']https?://',re.I),
    re.compile(r'url\s*\(\s*["\']?https?://[^)]*\)',re.I),
    re.compile(r'!\[[^\]]*\]\(\s*https?://',re.I),
)

def sha256(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def normalize_asset_path(path:str)->str:
    if not isinstance(path,str) or not path.startswith("assets/library/"):
        raise ValueError("Asset must have repo-local assets/library/ path")
    p=Path(path)
    if p.is_absolute() or ".." in p.parts or p.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError("Invalid image asset path: "+repr(path))
    if "//" in path or "\\" in path:
        raise ValueError("Non-normalized image asset path: "+repr(path))
    return path

def valid_sha(s:object)->bool:
    return isinstance(s,str) and re.fullmatch(r"[a-f0-9]{64}",s) is not None

def is_real_utc_timestamp(s:object)->bool:
    if not isinstance(s,str) or not s.strip():
        return False
    try:
        d=datetime.fromisoformat(s.replace("Z","+00:00"))
        return d.tzinfo is not None and d.utcoffset().total_seconds()==0
    except (ValueError,TypeError,AttributeError):
        return False

def load_registered(root=ROOT):
    records={}
    for filename in ("approved-daysky-assets.json","generated-asset-registry.json"):
        path=root/"docs/image-governance"/filename
        if not path.is_file():
            raise ValueError("Missing mandatory provenance registry "+str(path))
        data=json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data.get("records"),list):
            raise ValueError("Registry records must be an array: "+str(path))
        for rec in data["records"]:
            asset=normalize_asset_path(rec.get("assetPath"))
            if asset in records:
                raise ValueError("Duplicate provenance record: "+asset)
            records[asset]=rec
    return records

def validate_one(record:dict,root=ROOT)->list[str]:
    errors=[]
    try:
        path=normalize_asset_path(record.get("assetPath"))
    except ValueError as e:
        return [str(e)]
    target=root/path
    if not target.is_file():
        errors.append("Image is missing from repository: "+path)
    else:
        data=target.read_bytes()
        digest=sha256(data)
        if not valid_sha(record.get("finalSha256")) or record["finalSha256"]!=digest:
            errors.append("Final SHA256 missing/mismatch: "+path)
        if record.get("finalBytes") is not None and record["finalBytes"]!=len(data):
            errors.append("Final file byte size mismatch: "+path)
    source_type=record.get("sourceType")
    if source_type not in ALLOWED_SOURCE_TYPES:
        errors.append("Source type not authorized for new release: "+str(source_type))
        return errors
    if record.get("assetRole") in (None,""):
        errors.append("Image role required: "+path)
    if record.get("depictedFactRole") in (None,""):
        errors.append("Depicted fact role (illustrative or verified real photo) missing: "+path)
    if source_type=="GENERATED_VERIFIED":
        # Human-authored descriptive filenames or after-the-fact labels do
        # not establish the generation tool ever produced the actual image.
        required=("generatorTool","toolResultRef","toolPromptVerbatim",
                  "originalFilename","originalSha256","originalArchiveLocation")
        for k in required:
            if not isinstance(record.get(k),str) or not record[k].strip():
                errors.append("Missing generated-image evidence "+k+": "+path)
        if not is_real_utc_timestamp(record.get("generatedAt")):
            errors.append("Exact UTC generatedAt from tool required: "+path)
        if not valid_sha(record.get("originalSha256")):
            errors.append("Original generated file hash invalid: "+path)
        if not isinstance(record.get("transformations"),list) or not record["transformations"]:
            errors.append("Original-to-final transformations must be documented: "+path)
        elif not all(isinstance(x,dict) and x.get("operation") for x in record["transformations"]):
            errors.append("Invalid transformation audit steps: "+path)
        if record.get("depictedFactRole") != "illustration":
            errors.append("AI-generated image cannot claim a photographed real-world event: "+path)
    elif source_type=="USER_APPROVED_EXTERNAL":
        url=record.get("originalURL")
        p=urlparse(url) if isinstance(url,str) else None
        scope=record.get("permission") or {}
        if not p or p.scheme!="https" or not p.hostname:
            errors.append("Exact HTTPS photo source URL required: "+path)
        elif scope.get("scopeHostname")!=p.hostname:
            errors.append("Permission host scope mismatch: "+path)
        if not valid_sha(record.get("originalSha256")):
            errors.append("Approved source original SHA256 is required: "+path)
        if not isinstance(scope.get("userQuote"),str) or not scope["userQuote"].strip():
            errors.append("User explicit grant text is required: "+path)
        if scope.get("exactAsset") is not True:
            errors.append("Permission must be scoped to exact asset: "+path)
    elif source_type=="USER_SUPPLIED_ORIGINAL":
        info=record.get("permission") or {}
        if not info.get("userQuote") or not record.get("originalFileRef"):
            errors.append("User-provided original and explicit reuse permission required: "+path)
        if not valid_sha(record.get("originalSha256")):
            errors.append("Original user image SHA256 required: "+path)
    return errors

def changed_files(base_ref:str,root=ROOT)->list[str]:
    proc=subprocess.run(["git","-C",str(root),"diff","--name-only",
                         "--diff-filter=ACMR",base_ref+"...HEAD"],
                        capture_output=True,text=True,check=False)
    if proc.returncode!=0:
        raise RuntimeError("Git changed-image base is unavailable; cannot release: "+proc.stderr.strip()[:500])
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]

def scan_hotlinks(changed:list[str],root=ROOT)->list[str]:
    errors=[]
    for path in changed:
        p=root/path
        if not p.is_file() or p.suffix.lower() not in (".html",".css",".js",".jsx",".tsx",".astro",".vue",".md"):
            continue
        if not (path.startswith("sites/") or path.startswith("site/") or path.startswith("v5/")):
            continue
        text=p.read_text(encoding="utf-8",errors="replace")
        for pattern in IMG_HOTLINKS:
            if pattern.search(text):
                errors.append("Unapproved external image hotlink in changed source file: "+path)
                break
    return errors

def referenced_site_images(site_id:str,root=ROOT)->set[str]:
    """Find image dependencies for a newly changed V5 site, even if assets
    themselves were committed long ago. This prevents 'reusing' unknown
    historical images from bypassing the new-image-only change scanner.
    """
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}",site_id):
        raise ValueError("Unsafe site ID in image dependency audit")
    folder=root/"sites"/site_id
    paths=set()
    def load_optional(name:str):
        p=folder/name
        return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None
    site=load_optional("site.json")
    if isinstance(site,dict):
        image_library=site.get("imageLibrary")
        image_pool=site.get("imagePool",[])
        if image_pool:
            if not image_library or not isinstance(image_pool,list):
                raise ValueError("site.json imagePool must have imageLibrary: "+site_id)
            for name in image_pool:
                if not isinstance(name,str) or "/" in name or "\\" in name:
                    raise ValueError("Unsafe V5 imagePool filename: "+str(name))
                paths.add(normalize_asset_path("assets/library/"+image_library+"/"+name))
    spec=load_optional("site-spec.json")
    if isinstance(spec,dict):
        imgs=spec.get("images",{})
        if isinstance(imgs,dict):
            for name in imgs.get("assetPaths",[]):
                paths.add(normalize_asset_path(name))
            repo_path=imgs.get("repoPath")
            if repo_path and imgs.get("names"):
                for name in imgs["names"]:
                    if not isinstance(name,str) or "/" in name or "\\" in name:
                        raise ValueError("Unsafe V5 image filename: "+str(name))
                    paths.add(normalize_asset_path(repo_path.rstrip("/")+"/"+name))
    manifest=load_optional("images-manifest.json")
    if isinstance(manifest,dict):
        for record in manifest.get("assets",[]):
            name=record.get("assetPath") or record.get("path")
            if name:
                paths.add(normalize_asset_path(name))
    historical=root/"docs/site-plans"/site_id/"images-manifest.json"
    if historical.is_file():
        for record in json.loads(historical.read_text(encoding="utf-8")).get("assets",[]):
            name=record.get("assetPath") or record.get("path")
            if name:
                paths.add(normalize_asset_path(name))
    return paths

def check_changed_site_dependencies(changes:list[str],records:dict,root=ROOT):
    site_ids=sorted({name.split("/")[1] for name in changes
                     if name.startswith("sites/") and len(name.split("/"))>=3})
    errors=[]
    paths=set()
    for site_id in site_ids:
        try:
            references=referenced_site_images(site_id,root)
        except (ValueError,TypeError,KeyError) as exc:
            errors.append("Cannot safely identify image references in site "+site_id+": "+str(exc))
            continue
        paths.update(references)
    for path in sorted(paths):
        record=records.get(path)
        if record is None:
            errors.append("New/changed site refers to an existing asset without verified origin: "+path)
            continue
        errors.extend(validate_one(record,root))
    return {"changedSites":site_ids,"referencedImages":sorted(paths),
            "verified":len(paths) if not errors else 0,"errors":errors}

def check_explicit_release_assets(manifest_file:Path,records:dict,root=ROOT):
    """Release workflows can require an explicit full asset list, including
    unchanged images from legacy directories.
    """
    doc=json.loads(manifest_file.read_text(encoding="utf-8"))
    names=doc.get("assets") if isinstance(doc,dict) else doc
    if not isinstance(names,list) or not names:
        return ["Release assets manifest must contain a nonempty asset path list"]
    errors=[]
    for name in names:
        if not isinstance(name,str):
            errors.append("Invalid release image asset path value")
            continue
        try:
            path=normalize_asset_path(name)
        except ValueError as e:
            errors.append(str(e))
            continue
        rec=records.get(path)
        if rec is None:
            errors.append("Release asset has no approved provenance: "+path)
        else:
            errors.extend(validate_one(rec,root))
    return errors

def validate_changed_images(base_ref:str,root=ROOT):
    records=load_registered(root)
    changes=changed_files(base_ref,root)
    assets=[x for x in changes if x.startswith("assets/library/") and Path(x).suffix.lower() in IMAGE_SUFFIXES]
    errors=scan_hotlinks(changes,root)
    deps=check_changed_site_dependencies(changes,records,root)
    errors.extend(deps["errors"])
    accepted=[]
    for path in assets:
        record=records.get(path)
        if not record:
            errors.append("New/changed image has no exact provenance record: "+path)
            continue
        violations=validate_one(record,root)
        if violations:errors.extend(violations)
        else:accepted.append(path)
    return {"changedFiles":len(changes),"newOrChangedImages":len(assets),
            "provenanceApprovedImages":accepted,"siteDependencies":deps,
            "errors":errors,"pass":not errors,"existingLegacyFilesUnchanged":True}

def audit_legacy(root=ROOT):
    inventory=json.loads((root/"docs/image-governance/legacy-inventory-20261030.json").read_text(encoding="utf-8"))
    rows=inventory["groups"]
    by_status={}
    for row in rows:
        status=row["status"]
        by_status[status]=by_status.get(status,0)+1
    return {"groupCount":len(rows),"groupStatuses":by_status,
            "legacyReviewHold":[x["id"] for x in rows if x["status"] in
                ("SOURCE_UNVERIFIED","GENERATION_EVIDENCE_PARTIAL","PRODUCT_ORIGIN_RECORDED_PERMISSION_SCOPE_RECHECK")],
            "existingOperationalAssetsDeleted":False,
            "existingProductionReleasesModified":False}

def cli():
    p=argparse.ArgumentParser()
    p.add_argument("--changed-base",default=None,
                   help="Git base ref for NEW/CHANGED file enforcement; e.g. origin/main")
    p.add_argument("--legacy-audit",action="store_true")
    p.add_argument("--release-assets-manifest",default=None,
                   help="Full exact public image dependency list, including unchanged existing images")
    args=p.parse_args()
    errors=[]
    records=load_registered(ROOT)
    for path,record in records.items():
        errors.extend(validate_one(record))
    result={"registeredRecords":len(records),"registeredPaths":list(records),"registryErrors":errors}
    if args.changed_base:
        changed=validate_changed_images(args.changed_base,ROOT)
        result["changed"]=changed
        errors.extend(changed["errors"])
    if args.release_assets_manifest:
        release_errors=check_explicit_release_assets(Path(args.release_assets_manifest),records,ROOT)
        result["releaseImageDependencyErrors"]=release_errors
        errors.extend(release_errors)
    if args.legacy_audit:
        result["legacy"]=audit_legacy(ROOT)
    result["pass"]=not errors
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)

if __name__=="__main__":
    cli()
