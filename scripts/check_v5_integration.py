"""Read-only integration checks. No network, build, deployment or write operations."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def validate(root, archive=None):
    required = [
        "AGENTS.md", "SITE_CREATION_PROTOCOL.md", "docs/V5_1_IMPLEMENTATION.md",
        "docs/V5_CONTROL_INDEX.md", "docs/V5_WORK_REGISTRY.md",
        "docs/V4_DEPENDENCY_MIGRATION.md",
    ]
    for name in required:
        text = (root / name).read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", text):
            if "://" not in link and not link.startswith("mailto:"):
                if not ((root / name).parent / link).is_file():
                    raise ValueError("Missing document link: " + name + " -> " + link)
    manifest = json.loads((root / "docs/v4-dependency-manifest.json").read_text())
    if manifest["migrationComplete"] is not False:
        raise ValueError("Independent migration is not verified; retain incomplete status")
    dep = manifest["dependencies"][0]
    if len(dep["ref"]) != 40 or not re.fullmatch(r"[0-9a-f]{64}", dep["sha256"]):
        raise ValueError("Source ref/digest missing")
    if archive is not None:
        data = Path(archive).read_bytes()
        if len(data) != dep["size"] or hashlib.sha256(data).hexdigest() != dep["sha256"]:
            raise ValueError("Official source archive mismatch")
        return "documents PASS; supplied archive size/digest PASS; deployment NOT performed"
    return "documents PASS; archive NOT checked; migration INCOMPLETE; deployment NOT performed"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official-archive", type=Path)
    args = parser.parse_args()
    print(validate(ROOT, args.official_archive))

if __name__ == "__main__":
    main()
