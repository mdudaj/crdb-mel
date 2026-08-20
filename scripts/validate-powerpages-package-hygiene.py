#!/usr/bin/env python3
"""Validate Power Pages Enhanced upload package hygiene.

This catches the PAC failure class where `.portalconfig/manifest.yml` marks an
`adx_webfile` record as deleted while the same web file and metadata are still
present in `web-files/`. PAC can process the manifest delete first, then fail
the later file-content upload with `PortalFileContentUploadFailed` /
`ObjectDoesNotExist`.

It also verifies that Home page `/assets/...` references have matching web-file
binaries and `.webfile.yml` metadata in the upload package.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from urllib.parse import urlparse
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = ROOT / "powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool"
SOURCE_SITE = ROOT / "powerpages/tacatdp-monitoring-tool/.powerpages-site"
DIST_ASSETS = ROOT / "powerpages/webforms-spa/dist/assets"
ASSET_REF_RE = re.compile(r"""(?:href|src)=["']/assets/([^"'?#]+)(?:[?#][^"']*)?["']""")
GENERATED_SPA_ASSET_RE = re.compile(r""".+-[A-Za-z0-9_-]{6,}(?:\.[A-Za-z0-9_-]+)?\.(?:mjs|css|png|svg|woff2)(?:\.webfile\.yml)?$""")


@dataclass(frozen=True)
class ManifestRecord:
    entity: str
    record_id: str
    display_name: str
    is_deleted: bool
    start_line: int
    end_line: int


@dataclass(frozen=True)
class WebFileRecord:
    metadata_path: Path
    binary_path: Path
    values: dict[str, str]

    @property
    def identifiers(self) -> set[str]:
        return {
            value.lower()
            for key in ("adx_webfileid", "objectid")
            if (value := self.values.get(key, "")).strip()
        }

    @property
    def names(self) -> set[str]:
        return {
            value.lower()
            for key in ("adx_name", "adx_partialurl", "filename")
            if (value := self.values.get(key, "")).strip()
        } | {self.binary_path.name.lower()}


@dataclass(frozen=True)
class ManifestSection:
    entity: str
    start_line: int
    end_line: int
    has_records: bool


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def parse_scalar(line: str, key: str) -> str:
    prefix = f"{key}:"
    stripped = line.strip()
    if not stripped.startswith(prefix):
        return ""
    return stripped[len(prefix) :].strip().strip('"').strip("'")


def read_simple_yaml_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def parse_manifest(path: Path) -> list[ManifestRecord]:
    if not path.exists():
        fail(f"manifest not found: {path}")

    lines = path.read_text(encoding="utf-8-sig").splitlines(keepends=True)
    records: list[ManifestRecord] = []
    entity = ""
    current: dict[str, object] | None = None

    def finish(end_line: int) -> None:
        nonlocal current
        if current is None:
            return
        records.append(
            ManifestRecord(
                entity=str(current.get("entity", "")),
                record_id=str(current.get("record_id", "")),
                display_name=str(current.get("display_name", "")),
                is_deleted=bool(current.get("is_deleted", False)),
                start_line=int(current.get("start_line", end_line)),
                end_line=end_line,
            )
        )
        current = None

    for index, line in enumerate(lines):
        if line and not line.startswith((" ", "-")) and line.rstrip().endswith(":"):
            finish(index)
            entity = line.strip()[:-1]
            continue
        if line.startswith("- "):
            finish(index)
            current = {"entity": entity, "start_line": index}
            record_id = parse_scalar(line[2:], "RecordId")
            if record_id:
                current["record_id"] = record_id
            continue
        if current is None:
            continue
        record_id = parse_scalar(line, "RecordId")
        display_name = parse_scalar(line, "DisplayName")
        is_deleted = parse_scalar(line, "IsDeleted")
        if record_id:
            current["record_id"] = record_id
        if display_name:
            current["display_name"] = display_name
        if is_deleted:
            current["is_deleted"] = is_deleted.lower() == "true"

    finish(len(lines))
    return records


def parse_manifest_sections(path: Path) -> list[ManifestSection]:
    if not path.exists():
        fail(f"manifest not found: {path}")

    lines = path.read_text(encoding="utf-8-sig").splitlines(keepends=True)
    sections: list[ManifestSection] = []
    current: dict[str, object] | None = None

    def finish(end_line: int) -> None:
        nonlocal current
        if current is None:
            return
        sections.append(
            ManifestSection(
                entity=str(current["entity"]),
                start_line=int(current["start_line"]),
                end_line=end_line,
                has_records=bool(current["has_records"]),
            )
        )
        current = None

    for index, line in enumerate(lines):
        if line and not line.startswith((" ", "-")) and line.rstrip().endswith(":"):
            finish(index)
            current = {
                "entity": line.strip()[:-1],
                "start_line": index,
                "has_records": False,
            }
            continue
        if current is not None and line.startswith("- "):
            current["has_records"] = True

    finish(len(lines))
    return sections


def read_webfile_records(web_files: Path) -> list[WebFileRecord]:
    if not web_files.exists():
        fail(f"web-files directory not found: {web_files}")

    records: list[WebFileRecord] = []
    for metadata_path in sorted(web_files.glob("*.webfile.yml")):
        binary_name = metadata_path.name[: -len(".webfile.yml")]
        binary_path = web_files / binary_name
        records.append(
            WebFileRecord(
                metadata_path=metadata_path,
                binary_path=binary_path,
                values=read_simple_yaml_values(metadata_path),
            )
        )
    return records


def find_empty_manifest_section_issues(package: Path) -> list[str]:
    manifest = package / ".portalconfig/manifest.yml"
    return [
        f"Manifest section {section.entity}: has no records; PAC 2.9.3 can crash on null collection"
        for section in parse_manifest_sections(manifest)
        if not section.has_records
    ]


def environment_manifest_name(environment_url_or_host: str) -> str:
    parsed = urlparse(environment_url_or_host)
    host = parsed.netloc or parsed.path
    host = host.strip().strip("/")
    if not host:
        fail("--environment-url requires a URL or host")
    return f"{host}-manifest.yml"


def find_environment_manifest_issues(package: Path, environment_url_or_host: str | None) -> list[str]:
    if not environment_url_or_host:
        return []

    portal_config = package / ".portalconfig"
    expected = environment_manifest_name(environment_url_or_host)
    existing = sorted(path.name for path in portal_config.glob("*-manifest.yml"))
    if expected not in existing:
        return [
            f"Missing target environment manifest {expected}; found {', '.join(existing) or 'none'}"
        ]
    return []


def find_deleted_present_conflicts(package: Path) -> list[str]:
    manifest = package / ".portalconfig/manifest.yml"
    web_files = package / "web-files"
    deleted_webfiles = [
        record
        for record in parse_manifest(manifest)
        if record.entity == "adx_webfile" and record.is_deleted
    ]
    webfile_records = read_webfile_records(web_files)
    conflicts: list[str] = []

    for deleted in deleted_webfiles:
        deleted_id = deleted.record_id.lower()
        deleted_name = deleted.display_name.lower()
        for webfile in webfile_records:
            if deleted_id in webfile.identifiers or deleted_name in webfile.names:
                conflicts.append(
                    f"{deleted.display_name} ({deleted.record_id}) is marked deleted "
                    f"in manifest but present as {webfile.metadata_path.relative_to(package)}"
                )

    return conflicts


def find_manifest_delete_intent_issues(package: Path) -> list[str]:
    manifest = package / ".portalconfig/manifest.yml"
    return [
        f"{record.entity} {record.display_name or record.record_id} is marked IsDeleted: true; use the target-environment manifest before upload"
        for record in parse_manifest(manifest)
        if record.is_deleted
    ]


def find_source_map_issues(package: Path) -> list[str]:
    web_files = package / "web-files"
    if not web_files.exists():
        fail(f"web-files directory not found: {web_files}")
    return [
        f"{path.relative_to(package)} should not be uploaded"
        for path in sorted(web_files.iterdir())
        if path.is_file() and (path.name.endswith(".map") or path.name.endswith(".map.webfile.yml"))
    ]


def current_dist_assets() -> set[str]:
    if not DIST_ASSETS.exists():
        return set()
    return {
        asset.name
        for asset in DIST_ASSETS.iterdir()
        if asset.is_file() and not asset.name.endswith(".map")
    }


def find_untracked_source_spa_asset_issues() -> list[str]:
    web_files = SOURCE_SITE / "web-files"
    if not web_files.exists():
        return []

    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--", str(web_files.relative_to(ROOT))],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.SubprocessError:
        return []

    current_assets = current_dist_assets()
    issues: list[str] = []
    for line in result.stdout.splitlines():
        path = ROOT / line
        if not path.is_file() or not GENERATED_SPA_ASSET_RE.match(path.name):
            continue
        asset_name = path.name[: -len(".webfile.yml")] if path.name.endswith(".webfile.yml") else path.name
        if asset_name not in current_assets:
            issues.append(
                f"{path.relative_to(ROOT)} is an untracked obsolete generated SPA asset; rerun stage-powerpages-spa-build.py or remove it"
            )
    return issues


def home_fragment_paths(package: Path) -> list[Path]:
    candidates = [
        package / "web-pages/home/Home.webpage.copy.html",
        package / "web-pages/home/content-pages/Home.en-US.webpage.copy.html",
        package / "web-pages/home/content-pages/en-US/Home.webpage.copy.html",
    ]
    return [path for path in candidates if path.exists()]


def find_home_asset_reference_issues(package: Path) -> list[str]:
    web_files = package / "web-files"
    issues: list[str] = []
    referenced_assets: set[str] = set()

    for home in home_fragment_paths(package):
        text = home.read_text(encoding="utf-8-sig")
        referenced_assets.update(ASSET_REF_RE.findall(text))

    if not referenced_assets:
        issues.append("Home page fragments do not reference any /assets/ SPA files")
        return issues

    webfile_records_by_partial = {
        record.values.get("adx_partialurl", "").strip(): record
        for record in read_webfile_records(web_files)
    }
    for asset in sorted(referenced_assets):
        binary = web_files / asset
        metadata = web_files / f"{asset}.webfile.yml"
        record = webfile_records_by_partial.get(asset)
        if not binary.exists():
            issues.append(f"Home references /assets/{asset}, but web-file binary is missing")
        if not metadata.exists():
            issues.append(f"Home references /assets/{asset}, but {metadata.name} is missing")
        if record is None:
            issues.append(f"Home references /assets/{asset}, but no metadata has adx_partialurl: {asset}")

    return issues


def repair_deleted_present_manifest_records(package: Path) -> list[str]:
    manifest = package / ".portalconfig/manifest.yml"
    lines = manifest.read_text(encoding="utf-8-sig").splitlines(keepends=True)
    records = parse_manifest(manifest)
    conflicting_names = {
        conflict.split(" (", 1)[0].lower()
        for conflict in find_deleted_present_conflicts(package)
    }
    if not conflicting_names:
        manifest.write_text(
            remove_empty_manifest_sections("".join(lines)),
            encoding="utf-8",
        )
        return []

    remove_ranges = [
        (record.start_line, record.end_line, record.display_name)
        for record in records
        if record.entity == "adx_webfile"
        and record.is_deleted
        and record.display_name.lower() in conflicting_names
    ]
    keep = [True] * len(lines)
    removed: list[str] = []
    for start, end, display_name in remove_ranges:
        for index in range(start, end):
            keep[index] = False
        removed.append(display_name)

    repaired = "".join(line for index, line in enumerate(lines) if keep[index])
    manifest.write_text(remove_empty_manifest_sections(repaired), encoding="utf-8")
    return removed


def remove_empty_manifest_sections(text: str) -> str:
    lines = text.splitlines(keepends=True)
    sections: list[tuple[int, int, bool]] = []
    current: dict[str, object] | None = None

    def finish(end_line: int) -> None:
        nonlocal current
        if current is None:
            return
        sections.append((int(current["start_line"]), end_line, bool(current["has_records"])))
        current = None

    for index, line in enumerate(lines):
        if line and not line.startswith((" ", "-")) and line.rstrip().endswith(":"):
            finish(index)
            current = {"start_line": index, "has_records": False}
            continue
        if current is not None and line.startswith("- "):
            current["has_records"] = True

    finish(len(lines))
    keep = [True] * len(lines)
    for start, end, has_records in sections:
        if has_records:
            continue
        for index in range(start, end):
            keep[index] = False

    return "".join(line for index, line in enumerate(lines) if keep[index])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package",
        default=DEFAULT_PACKAGE,
        type=Path,
        help=f"Power Pages Enhanced upload package root. Default: {DEFAULT_PACKAGE}",
    )
    parser.add_argument(
        "--repair-manifest",
        action="store_true",
        help="Remove conflicting adx_webfile deleted entries from manifest.yml.",
    )
    parser.add_argument(
        "--environment-url",
        help="Target Dataverse environment URL or host; validates matching .portalconfig/<host>-manifest.yml.",
    )
    args = parser.parse_args()
    package = args.package.resolve()
    if not package.exists():
        fail(f"package root not found: {package}")

    if args.repair_manifest:
        removed = repair_deleted_present_manifest_records(package)
        if removed:
            print("Repaired manifest deleted-present web-file conflicts:")
            for name in removed:
                print(f"- {name}")

    conflicts = find_deleted_present_conflicts(package)
    section_issues = find_empty_manifest_section_issues(package)
    environment_issues = find_environment_manifest_issues(package, args.environment_url)
    delete_intent_issues = find_manifest_delete_intent_issues(package)
    source_map_issues = find_source_map_issues(package)
    untracked_source_spa_asset_issues = find_untracked_source_spa_asset_issues()
    asset_issues = find_home_asset_reference_issues(package)
    if conflicts or section_issues or environment_issues or delete_intent_issues or source_map_issues or untracked_source_spa_asset_issues or asset_issues:
        for conflict in conflicts:
            print(f"Deleted-present conflict: {conflict}")
        for issue in section_issues:
            print(f"Manifest structure issue: {issue}")
        for issue in environment_issues:
            print(f"Environment manifest issue: {issue}")
        for issue in delete_intent_issues:
            print(f"Manifest delete intent issue: {issue}")
        for issue in source_map_issues:
            print(f"Source map issue: {issue}")
        for issue in untracked_source_spa_asset_issues:
            print(f"Source package issue: {issue}")
        for issue in asset_issues:
            print(f"Asset reference issue: {issue}")
        fail("Power Pages package hygiene validation failed")

    print(f"Power Pages package hygiene verified: {package}")


if __name__ == "__main__":
    main()
