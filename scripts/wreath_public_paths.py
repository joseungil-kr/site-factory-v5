from pathlib import PurePosixPath
from urllib.parse import urljoin

def output_relative_path(url_path: str) -> str:
    if not url_path.startswith("/") or url_path.startswith("//"):
        raise ValueError("expected one root-relative URL path")
    relative=url_path.lstrip("/")
    if not relative or ".." in PurePosixPath(relative).parts:
        raise ValueError("invalid output path")
    return relative

def canonical_url(origin: str, url_path: str) -> str:
    if not origin.startswith("https://") or origin.endswith("/"):
        raise ValueError("origin must be HTTPS without trailing slash")
    if not url_path.startswith("/") or url_path.startswith("//"):
        raise ValueError("expected one root-relative URL path")
    return urljoin(origin + "/", url_path.lstrip("/"))
