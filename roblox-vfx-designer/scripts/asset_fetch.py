#!/usr/bin/env python3
"""Bounded CC0/public-domain asset acquisition. Review rights BEFORE using download.
No credentials, executable extraction, Roblox upload, or automatic legal assurance.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import io
import ipaddress
import json
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
import re
import shutil
import socket
import stat
import tempfile
from urllib.parse import urljoin, urlparse, urlencode, quote
from urllib.request import Request, build_opener, HTTPRedirectHandler, ProxyHandler
import zipfile

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "RobloxVFXDesigner-AssetHelper/1.0"
# Extend only after checking the provider, license and redirect destinations.
ALLOWED_HOSTS = {
    "kenney.nl", "www.kenney.nl", "opengameart.org", "www.opengameart.org",
    "polyhaven.com", "api.polyhaven.com", "dl.polyhaven.org", "cdn.polyhaven.com",
    "ambientcg.com", "www.ambientcg.com", "docs.ambientcg.com",
}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
TEXT_EXTS = {".txt", ".md"}
MAX_DOWNLOAD = 64 * 1024 * 1024
MAX_EXTRACTED = 256 * 1024 * 1024
MAX_FILES = 5000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_url(url: str, resolve: bool = False) -> str:
    p = urlparse(url)
    if len(url) > 8192 or p.scheme != "https" or not p.hostname:
        raise ValueError("Only bounded, absolute HTTPS URLs are accepted")
    if p.username or p.password or p.port not in (None, 443):
        raise ValueError("Credentials and nonstandard ports are not permitted")
    host = p.hostname.lower()
    if host not in ALLOWED_HOSTS:
        raise ValueError(f"Unreviewed host: {host}; inspect the provider before extending the allowlist")
    if resolve:
        addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(x[4][0]).is_global for x in addresses):
            raise ValueError("Host resolves to a non-public address")
    return url


class GuardedRedirect(HTTPRedirectHandler):
    max_redirections = 4
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl, resolve=True)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url: str, limit: int = MAX_DOWNLOAD) -> tuple[bytes, str, str]:
    """Public library domains only; no ambient credentials/proxy configuration."""
    validate_url(url, resolve=True)
    opener = build_opener(ProxyHandler({}), GuardedRedirect())
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
    with opener.open(request, timeout=30) as response:
        final_url = validate_url(response.geturl())
        length = response.headers.get("Content-Length")
        if length and int(length) > limit:
            raise ValueError("Download exceeds configured byte budget")
        chunks, size = [], 0
        while True:
            chunk = response.read(min(1024 * 1024, limit + 1 - size))
            if not chunk:
                break
            size += len(chunk)
            if size > limit:
                raise ValueError("Download exceeds configured byte budget")
            chunks.append(chunk)
        return b"".join(chunks), final_url, response.headers.get("Content-Type", "")


def safe_member(name: str) -> PurePosixPath:
    if not name or "\\" in name or ":" in name or "\x00" in name:
        raise ValueError("Unsafe archive path")
    p = PurePosixPath(name)
    if p.is_absolute() or any(v in ("..", ".") for v in name.split("/")):
        raise ValueError("Unsafe archive traversal")
    reserved = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}
    for part in p.parts:
        if part.rstrip(" .") != part or part.split(".")[0].upper() in reserved:
            raise ValueError("Unsafe cross-platform archive filename")
    return p


def image_extension(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"): return ".png"
    if data.startswith(b"\xff\xd8\xff"): return ".jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP": return ".webp"
    if data.startswith(b"BM"): return ".bmp"
    return None


def safe_extract_zip(data: bytes, destination: Path) -> list[dict]:
    """Extract only images/text into a NEW directory; never execute content.
    This is a narrow acquisition helper, not a complete malware sandbox.
    """
    if destination.exists():
        raise ValueError("Extraction destination already exists")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        infos = archive.infolist()
        if len(infos) > MAX_FILES or sum(x.file_size for x in infos) > MAX_EXTRACTED:
            raise ValueError("Archive exceeds file/expanded-byte budget")
        selected, seen = [], set()
        for info in infos:
            path = safe_member(info.filename)
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError("Archive symlinks are not accepted")
            if info.flag_bits & 1:
                raise ValueError("Encrypted archives are not accepted")
            if info.file_size > MAX_DOWNLOAD or info.file_size / max(info.compress_size, 1) > 1000:
                raise ValueError("Suspicious archive expansion")
            key = str(path).casefold()
            if key in seen:
                raise ValueError("Duplicate/case-colliding archive path")
            seen.add(key)
            if not info.is_dir() and path.suffix.lower() in IMAGE_EXTS | TEXT_EXTS:
                selected.append((info, path))
        if not any(path.suffix.lower() in IMAGE_EXTS for _, path in selected):
            raise ValueError("Archive contains no supported images")
        records = []
        destination.mkdir(parents=True, exist_ok=False)
        try:
            for info, path in selected:
                content = archive.read(info)
                if path.suffix.lower() in IMAGE_EXTS and image_extension(content) is None:
                    raise ValueError(f"Non-image content in image entry: {path}")
                target = destination.joinpath(*path.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as out: out.write(content)
                records.append({"path": str(path), "sha256": sha256(content), "bytes": len(content)})
        except Exception:
            shutil.rmtree(destination)
            raise
    return records


def validate_evidence(e: dict) -> None:
    fields = ("asset_page", "creator", "license", "license_evidence_url", "verified_at", "download_url", "reviewer", "review_notes")
    if any(not isinstance(e.get(k), str) or not e[k].strip() for k in fields):
        raise ValueError("Incomplete evidence: provide nonempty provenance fields")
    if e.get("review_complete") is not True:
        raise ValueError("Review is incomplete; inspect asset-level rights before downloading")
    if e["license"] not in {"CC0-1.0", "Public-Domain"}:
        raise ValueError("This helper defaults to CC0/public-domain, not CC-BY/custom/free labels")
    date = dt.date.fromisoformat(e["verified_at"])
    if not 0 <= (dt.date.today() - date).days <= 30:
        raise ValueError("Recheck license evidence: verification must be within 30 days, not future-dated")
    for field in ("asset_page", "license_evidence_url"):
        p = urlparse(e[field])
        if p.scheme != "https" or not p.hostname or p.username or p.password:
            raise ValueError(f"Invalid evidence URL in {field}")
    validate_url(e["download_url"])


def download(evidence: dict, destination: Path) -> dict:
    validate_evidence(evidence)
    if destination.exists(): raise ValueError("Choose a fresh destination; existing files are never overwritten")
    data, final_url, content_type = fetch(evidence["download_url"])
    if not data: raise ValueError("Empty download")
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".vfx-download-", dir=destination.parent))
    try:
        is_zip = zipfile.is_zipfile(io.BytesIO(data))
        ext = ".zip" if is_zip else image_extension(data)
        if ext is None: raise ValueError("Response is not a supported image or ZIP; it may be an HTML/login page")
        raw_name = "original-download" + ext
        (stage / raw_name).write_bytes(data)
        if is_zip:
            files = safe_extract_zip(data, stage / "files")
            for f in files: f["path"] = "files/" + f["path"]
        else:
            files = [{"path": raw_name, "sha256": sha256(data), "bytes": len(data)}]
        record = {"schema_version": "1.0", "evidence": evidence, "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                  "final_download_url": final_url, "content_type": content_type, "original_file": raw_name,
                  "original_sha256": sha256(data), "files": files, "modifications": [],
                  "roblox_import": {"status": "not_imported", "owner": None, "image_content_id": None}}
        (stage / "asset-manifest.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        if destination.exists(): raise ValueError("Destination appeared during download; refusing overwrite")
        stage.rename(destination)
        return record
    finally:
        if stage.exists(): shutil.rmtree(stage)


class LinkParser(HTMLParser):
    def __init__(self): super().__init__(); self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href: self.links.append(href)


def discover(entry: dict, query: str = "", asset_id: str | None = None):
    adapter = entry["access"]["adapter"]
    if adapter == "polyhaven":
        url = "https://api.polyhaven.com/files/" + quote(asset_id, safe="") if asset_id else "https://api.polyhaven.com/assets"
        data = json.loads(fetch(url, 24 * 1024 * 1024)[0])
        if not asset_id:
            data = {k: v for k, v in data.items() if query.lower() in (k + " " + json.dumps(v)).lower()}
            data = dict(list(data.items())[:30])
        return {"provider": "Poly Haven", "credit": "Assets from Poly Haven", "source": url, "data": data}
    if adapter == "ambientcg":
        params = {"q": query, "limit": 10, "include": "title,url,downloads"}
        if asset_id: params["id"] = asset_id
        url = "https://ambientcg.com/api/v3/assets?" + urlencode(params)
        return {"provider": "ambientCG", "source": url, "data": json.loads(fetch(url, 8 * 1024 * 1024)[0])}
    data, url, _ = fetch(entry["page_url"], 4 * 1024 * 1024)
    parser = LinkParser(); parser.feed(data.decode("utf-8", errors="replace"))
    links = sorted({urljoin(url, link) for link in parser.links})
    relevant = [link for link in links if re.search(r"download|donat|license|creativecommons|\.(?:zip|png|jpg)(?:\?|$)", link, re.I)]
    return {"page": url, "candidate_links": relevant[:80], "catalog_hint": entry["access"]["direct_download_url"],
            "warning": "Discovery only. Read the asset-level license and choose the actual file, not a preview."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    d = sub.add_parser("discover"); d.add_argument("library"); d.add_argument("--query", default=""); d.add_argument("--asset-id")
    f = sub.add_parser("download"); f.add_argument("--evidence", type=Path, required=True); f.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        catalog = json.loads((ROOT / "assets/library-catalog.json").read_text(encoding="utf-8"))["libraries"]
        if args.command == "list":
            result = [{"id": e["id"], "title": e["title"], "roles": e["roles"], "page": e["page_url"]} for e in catalog]
        elif args.command == "discover":
            entry = next((e for e in catalog if e["id"] == args.library), None)
            if entry is None: raise ValueError("Unknown library; run list")
            result = discover(entry, args.query, args.asset_id)
        else:
            result = download(json.loads(args.evidence.read_text(encoding="utf-8")), args.out)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as exc:
        parser.exit(1, f"asset_fetch: {exc}\n")

if __name__ == "__main__": main()
