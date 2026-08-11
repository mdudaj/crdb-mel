#!/usr/bin/env python3
"""Read-only CRDB Power Pages duplicate web-file ownership classifier.

This script uses the active PAC profile and FetchXML. It does not read .env
files, does not print tokens, and does not delete or update Dataverse records.

Run it from a CRDB-scoped shell:

    source scripts/use-powerplatform-env.sh crdb
    python3 scripts/classify-crdb-duplicate-webfiles.py --only-current-dist
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEB_FILES = ROOT / "powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files"
DEFAULT_INVENTORY_SCRIPT = ROOT / "scripts/inventory-powerpages-webfile-duplicates.mjs"
GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")


@dataclass(frozen=True)
class DownloadedDuplicate:
    partial_url: str
    local_file: str
    metadata: str
    webfile_id: str
    annotation_id: str
    sha256: str
    matches_dist: bool


@dataclass(frozen=True)
class PowerPageComponent:
    powerpagecomponentid: str
    name: str
    ismanaged: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify duplicate CRDB Power Pages web-file records without Dataverse writes.")
    parser.add_argument("--web-files", default=str(DEFAULT_WEB_FILES), help="Downloaded Power Pages web-files directory.")
    parser.add_argument("--only-current-dist", action="store_true", help="Classify only duplicates that exist in current Vite dist/assets.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    return parser.parse_args()


def run_inventory(web_files: Path) -> dict[str, Any]:
    command = [
        "node",
        str(DEFAULT_INVENTORY_SCRIPT),
        "--web-files",
        str(web_files),
        "--json",
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=ROOT)
    return json.loads(result.stdout)


def flatten_inventory(inventory: dict[str, Any], only_current_dist: bool) -> list[DownloadedDuplicate]:
    records: list[DownloadedDuplicate] = []
    for group in inventory.get("duplicateGroups", []):
        if only_current_dist and not group.get("distAssetExists"):
            continue
        dist_hash = group.get("distSha256") or ""
        for record in group.get("downloadedRecords", []):
            records.append(DownloadedDuplicate(
                partial_url=group["partialUrl"],
                local_file=record["file"],
                metadata=record["metadata"],
                webfile_id=record["webFileId"],
                annotation_id=record["annotationId"],
                sha256=record.get("binarySha256") or "",
                matches_dist=bool(dist_hash and record.get("binarySha256") == dist_hash),
            ))
    return records


def fetch_components_by_name(partial_url: str) -> list[PowerPageComponent]:
    environment_url = os.environ.get("POWER_PLATFORM_ENVIRONMENT_URL", "").strip()
    if not environment_url:
        raise SystemExit("Missing POWER_PLATFORM_ENVIRONMENT_URL; source scripts/use-powerplatform-env.sh crdb first.")
    escaped_name = html.escape(partial_url, quote=True)
    fetch_xml = (
        "<fetch>"
        "<entity name='powerpagecomponent'>"
        "<attribute name='powerpagecomponentid'/>"
        "<attribute name='name'/>"
        "<attribute name='ismanaged'/>"
        "<filter>"
        f"<condition attribute='name' operator='eq' value='{escaped_name}'/>"
        "</filter>"
        "</entity>"
        "</fetch>"
    )
    command = [
        "pac",
        "org",
        "fetch",
        "--environment",
        environment_url,
        "--xml",
        fetch_xml,
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=ROOT)
    return parse_component_table(result.stdout)


def parse_component_table(output: str) -> list[PowerPageComponent]:
    rows: list[PowerPageComponent] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not GUID_RE.match(line):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        rows.append(PowerPageComponent(
            powerpagecomponentid=parts[0],
            name=parts[1],
            ismanaged=parts[-1],
        ))
    return rows


def classify(downloaded: DownloadedDuplicate, component: PowerPageComponent | None) -> str:
    if component is None:
        return "missing-from-powerpagecomponent-query"
    if component.ismanaged == "Managed":
        return "managed-blocked"
    if downloaded.matches_dist:
        return "unmanaged-current-delete-candidate"
    return "unmanaged-stale-delete-candidate"


def classify_all(records: list[DownloadedDuplicate]) -> list[dict[str, Any]]:
    components_by_name: dict[str, list[PowerPageComponent]] = {}
    for partial_url in sorted({record.partial_url for record in records}):
        components_by_name[partial_url] = fetch_components_by_name(partial_url)

    results: list[dict[str, Any]] = []
    for record in records:
        component = next(
            (candidate for candidate in components_by_name.get(record.partial_url, []) if candidate.powerpagecomponentid.lower() == record.webfile_id.lower()),
            None,
        )
        results.append({
            "partialUrl": record.partial_url,
            "localFile": record.local_file,
            "webfileId": record.webfile_id,
            "annotationId": record.annotation_id,
            "binarySha256": record.sha256,
            "matchesCurrentDist": record.matches_dist,
            "powerpagecomponent": None if component is None else {
                "powerpagecomponentid": component.powerpagecomponentid,
                "name": component.name,
                "ismanaged": component.ismanaged,
            },
            "classification": classify(record, component),
        })
    return results


def print_text(results: list[dict[str, Any]]) -> None:
    by_partial: dict[str, list[dict[str, Any]]] = {}
    for row in results:
        by_partial.setdefault(row["partialUrl"], []).append(row)

    for partial_url, rows in by_partial.items():
        print("")
        print(partial_url)
        print("-" * len(partial_url))
        for row in rows:
            component = row.get("powerpagecomponent") or {}
            print(
                f"{row['localFile']} | class={row['classification']} | "
                f"matchesDist={'yes' if row['matchesCurrentDist'] else 'no'} | "
                f"managed={component.get('ismanaged', 'unknown')} | "
                f"component={row['webfileId']} | annotation={row['annotationId']}"
            )


def main() -> int:
    target = os.environ.get("TACATDP_POWERPLATFORM_TARGET", "")
    if target != "crdb":
        raise SystemExit(f"Refusing to run unless TACATDP_POWERPLATFORM_TARGET=crdb; current value is {target or '<empty>'}.")
    args = parse_args()
    inventory = run_inventory(Path(args.web_files).resolve())
    records = flatten_inventory(inventory, args.only_current_dist)
    results = classify_all(records)
    if args.json:
        print(json.dumps({
            "target": target,
            "environmentUrl": os.environ.get("POWER_PLATFORM_ENVIRONMENT_URL", ""),
            "recordCount": len(results),
            "results": results,
        }, indent=2))
    else:
        print(f"Target: {target}")
        print(f"Environment: {os.environ.get('POWER_PLATFORM_ENVIRONMENT_URL', '')}")
        print(f"Classified records: {len(results)}")
        print_text(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
