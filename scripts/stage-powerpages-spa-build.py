#!/usr/bin/env python3
"""Stage the Vite SPA build into the Power Pages package."""

from __future__ import annotations

import re
import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "powerpages/webforms-spa/dist"
DIST_ASSETS = DIST / "assets"
SITE = ROOT / "powerpages/tacatdp-monitoring-tool/.powerpages-site"
UPLOAD = ROOT / "powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool"
WEB_FILES = SITE / "web-files"
HOME_FILES = [
    SITE / "web-pages/home/Home.webpage.copy.html",
    SITE / "web-pages/home/content-pages/en-US/Home.webpage.copy.html",
]
PARENT_PAGE_ID = "60efc37d-aded-4014-912d-8a1cdefa876d"
PUBLISHING_STATE_ID = "357decb2-7d20-468f-9898-1da7459f66b9"
WEBFILE_NAMESPACE = uuid.UUID("b3107b66-8078-4bfe-bd96-e84ad7e46111")
ANNOTATION_NAMESPACE = uuid.UUID("d2e9a15c-80fb-4828-b8b7-4e8646df75a8")
BUILD_MARKER = "beneficiary-kpi-map-20260809-001"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def mimetype_for(filename: str) -> str:
    if filename.endswith(".css"):
        return "text/css"
    if filename.endswith(".map"):
        return "application/json"
    if filename.endswith(".mjs") or filename.endswith(".js"):
        return "text/javascript"
    if filename.endswith(".svg"):
        return "image/svg+xml"
    if filename.endswith(".png"):
        return "image/png"
    if filename.endswith(".woff2"):
        return "font/woff2"
    return "application/octet-stream"


def metadata_for(filename: str) -> str:
    webfile_id = uuid.uuid5(WEBFILE_NAMESPACE, filename)
    annotation_id = uuid.uuid5(ANNOTATION_NAMESPACE, filename)
    return "\n".join([
        "adx_enabletracking: false",
        "adx_excludefromsearch: true",
        "adx_hiddenfromsitemap: true",
        f"adx_name: {filename}",
        f"adx_parentpageid: {PARENT_PAGE_ID}",
        f"adx_partialurl: {filename}",
        f"adx_publishingstateid: {PUBLISHING_STATE_ID}",
        f"adx_webfileid: {webfile_id}",
        f"annotationid: {annotation_id}",
        f"filename: {filename}",
        "isdocument: true",
        f"mimetype: {mimetype_for(filename)}",
        f"objectid: {webfile_id}",
        "objecttypecode: adx_webfile",
        "",
    ])


def stage_assets() -> None:
    if not DIST_ASSETS.exists():
        fail("missing Vite build assets; run npm run build:mshirika-runtime first")
    WEB_FILES.mkdir(parents=True, exist_ok=True)
    for asset in sorted(path for path in DIST_ASSETS.iterdir() if path.is_file() and not path.name.endswith(".map")):
        target = WEB_FILES / asset.name
        shutil.copy2(asset, target)
        metadata = WEB_FILES / f"{asset.name}.webfile.yml"
        if not metadata.exists():
            metadata.write_text(metadata_for(asset.name))


def build_asset_block() -> str:
    index = (DIST / "index.html").read_text()
    asset_lines = []
    for line in index.splitlines():
        stripped = line.strip()
        if 'href="/assets/' in stripped or 'src="/assets/' in stripped:
            stripped = re.sub(r'(/assets/[^"?]+)(["?])', rf'\1?v={BUILD_MARKER}\2', stripped)
            asset_lines.append(stripped)
    if not any('type="module"' in line and 'src="/assets/index-' in line for line in asset_lines):
        fail("dist/index.html did not expose a main module asset")
    if not any('rel="stylesheet"' in line and 'href="/assets/index-' in line for line in asset_lines):
        fail("dist/index.html did not expose a main stylesheet asset")
    return "\n".join(asset_lines)


def update_home_fragments() -> None:
    asset_block = build_asset_block()
    for home in HOME_FILES:
        text = home.read_text()
        text = re.sub(
            r'(?ms)<link rel="modulepreload".*?<div id="app"></div>\n<script type="module".*?</script>',
            f"{asset_block}\n<div id=\"app\"></div>",
            text,
        )
        if asset_block not in text:
            fail(f"failed to update asset block in {home.relative_to(ROOT)}")
        home.write_text(text)


def refresh_upload_mirror() -> None:
    if UPLOAD.exists():
        shutil.rmtree(UPLOAD)
    shutil.copytree(SITE, UPLOAD)


def main() -> None:
    stage_assets()
    update_home_fragments()
    refresh_upload_mirror()
    print(f"Power Pages SPA build staged with marker {BUILD_MARKER}.")


if __name__ == "__main__":
    main()
