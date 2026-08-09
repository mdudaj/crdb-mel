#!/usr/bin/env python3
"""Export latest TACATDP Dataverse submissions to a Power BI-friendly CSV."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import requests

API_VERSION = "v9.2"
TOKEN_URL_TEMPLATE = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
SUBMITTED_STATUS = 100000001

CORE_COLUMNS = [
    "submission_id",
    "submission_version_id",
    "instance_id",
    "display_name",
    "user_email",
    "submitted_at",
    "updated_at",
    "lifecycle_status",
    "review_state",
    "version_number",
    "form_version_id",
    "assignment_key",
    "xml_form_id",
    "payload_status",
    "payload_type",
    "attachment_count",
    "attachment_names",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default=".env", help="Environment file with Dataverse app settings.")
    parser.add_argument("--output", default="artifacts/exports/tacatdp-submissions-powerbi.csv", help="CSV output path.")
    parser.add_argument("--top", type=int, default=5000, help="Maximum submitted records to export.")
    parser.add_argument("--include-all-statuses", action="store_true", help="Export all lifecycle statuses, not only submitted records.")
    parser.add_argument("--include-xml", action="store_true", help="Include full submission XML in the CSV.")
    parser.add_argument("--check-instance", help="Print saved-list-style details for one ODK instance id.")
    return parser.parse_args()


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def require(env: dict[str, str], key: str) -> str:
    value = env.get(key, "").strip()
    if not value:
        raise SystemExit(f"Missing required env value: {key}")
    return value


def safe_error(response: requests.Response) -> str:
    try:
        data = response.json()
        error = data.get("error") or data
        if isinstance(error, dict):
            return str(error.get("message") or error.get("code") or error)[:1000]
        return str(error)[:1000]
    except Exception:
        return response.text[:1000]


class DataverseClient:
    def __init__(self, env: dict[str, str]) -> None:
        self.environment_url = require(env, "POWER_PLATFORM_ENVIRONMENT_URL").rstrip("/")
        self.base = f"{self.environment_url}/api/data/{API_VERSION}"
        token = self._get_token(env)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0",
            }
        )

    def _get_token(self, env: dict[str, str]) -> str:
        response = requests.post(
            TOKEN_URL_TEMPLATE.format(tenant=require(env, "POWER_PLATFORM_TENANT_ID")),
            data={
                "client_id": require(env, "POWER_PLATFORM_CLIENT_ID"),
                "client_secret": require(env, "POWER_PLATFORM_CLIENT_SECRET"),
                "scope": f"{self.environment_url}/.default",
                "grant_type": "client_credentials",
            },
            timeout=30,
        )
        if response.status_code >= 400:
            raise SystemExit(f"Token request failed: HTTP {response.status_code} {safe_error(response)}")
        return response.json()["access_token"]

    def get_json(self, path_or_url: str) -> dict[str, Any]:
        url = path_or_url if path_or_url.startswith("https://") else f"{self.base}/{path_or_url.lstrip('/')}"
        response = self.session.get(url, timeout=60)
        if response.status_code in {429, 500, 502, 503, 504}:
            time.sleep(3)
            response = self.session.get(url, timeout=60)
        if response.status_code >= 400:
            raise RuntimeError(f"GET failed: HTTP {response.status_code} {safe_error(response)}")
        return response.json()

    def list_submissions(self, top: int, submitted_only: bool) -> list[dict[str, Any]]:
        select = ",".join(
            [
                "mp_submissionid",
                "mp_instanceid",
                "mp_useremail",
                "mp_submittedat",
                "mp_updatedat",
                "mp_lifecyclestatus",
                "mp_reviewstate",
            ]
        )
        path = f"mp_submissions?$select={select}&$orderby=mp_updatedat desc&$top={min(top, 5000)}"
        if submitted_only:
            path += f"&$filter=mp_lifecyclestatus eq {SUBMITTED_STATUS}"
        return self._collect(path, top)

    def latest_version(self, instance_id: str) -> dict[str, Any] | None:
        escaped_instance_id = escape_odata_string(instance_id)
        select = ",".join(
            [
                "mp_submissionversionid",
                "mp_versionnumber",
                "mp_instanceid",
                "mp_xformsubmissionxml",
                "mp_submissionjson",
            ]
        )
        data = self.get_json(
            "mp_submissionversions?"
            f"$select={select}&$filter=mp_instanceid eq '{escaped_instance_id}'"
            "&$orderby=mp_versionnumber desc&$top=1"
        )
        rows = data.get("value") or []
        return rows[0] if rows else None

    def _collect(self, path: str, limit: int) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        data = self.get_json(path)
        while True:
            rows.extend(data.get("value") or [])
            if len(rows) >= limit:
                return rows[:limit]
            next_link = data.get("@odata.nextLink")
            if not next_link:
                return rows
            data = self.get_json(next_link)


def escape_odata_string(value: str) -> str:
    return value.replace("'", "''")


def parse_metadata(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"metadata_parse_error": True}
    return parsed if isinstance(parsed, dict) else {}


def flatten_xml(xml: str | None) -> dict[str, str]:
    if not xml:
        return {}
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError:
        return {"xform_parse_error": "true"}

    flattened: dict[str, list[str]] = {}

    def visit(node: ElementTree.Element, path: list[str]) -> None:
        children = list(node)
        text = (node.text or "").strip()
        if text and not children:
            key = "xform_" + sanitize_column("_".join(path))
            flattened.setdefault(key, []).append(text)
        for child in children:
            visit(child, [*path, strip_namespace(child.tag)])

    for child in list(root):
        visit(child, [strip_namespace(child.tag)])
    return {key: " | ".join(values) for key, values in flattened.items()}


def strip_namespace(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def sanitize_column(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z_]+", "_", value).strip("_").lower()
    return value or "value"


def build_row(submission: dict[str, Any], version: dict[str, Any] | None, include_xml: bool) -> dict[str, Any]:
    metadata = parse_metadata(version.get("mp_submissionjson") if version else None)
    attachments = metadata.get("attachmentNames")
    if not isinstance(attachments, list):
        attachments = []

    row: dict[str, Any] = {
        "submission_id": submission.get("mp_submissionid"),
        "submission_version_id": version.get("mp_submissionversionid") if version else None,
        "instance_id": submission.get("mp_instanceid"),
        "display_name": metadata.get("instanceName"),
        "user_email": submission.get("mp_useremail"),
        "submitted_at": submission.get("mp_submittedat"),
        "updated_at": submission.get("mp_updatedat"),
        "lifecycle_status": submission.get("mp_lifecyclestatus"),
        "review_state": submission.get("mp_reviewstate"),
        "version_number": version.get("mp_versionnumber") if version else None,
        "form_version_id": metadata.get("formVersionId"),
        "assignment_key": metadata.get("assignmentKey"),
        "xml_form_id": metadata.get("xmlFormId"),
        "payload_status": metadata.get("status"),
        "payload_type": metadata.get("payloadType"),
        "attachment_count": len(attachments),
        "attachment_names": "; ".join(str(name) for name in attachments),
    }
    xml = version.get("mp_xformsubmissionxml") if version else None
    row.update(flatten_xml(xml))
    if include_xml:
        row["xform_submission_xml"] = xml
    return row


def write_csv(path: Path, rows: list[dict[str, Any]], include_xml: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dynamic_columns = sorted({key for row in rows for key in row if key not in CORE_COLUMNS})
    columns = [*CORE_COLUMNS, *dynamic_columns]
    if include_xml and "xform_submission_xml" not in columns:
        columns.append("xform_submission_xml")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    env = load_env(Path(args.env_file))
    client = DataverseClient(env)
    submissions = client.list_submissions(args.top, submitted_only=not args.include_all_statuses)
    rows = [build_row(submission, client.latest_version(submission["mp_instanceid"]), args.include_xml) for submission in submissions]
    write_csv(Path(args.output), rows, args.include_xml)

    print(f"Exported {len(rows)} rows to {args.output}")
    if args.check_instance:
        match = next((row for row in rows if row.get("instance_id") == args.check_instance), None)
        if not match:
            print(f"Instance not found in export: {args.check_instance}", file=sys.stderr)
            return 2
        print(json.dumps({key: match.get(key) for key in CORE_COLUMNS}, indent=2, ensure_ascii=True))
    elif rows:
        print(json.dumps({key: rows[0].get(key) for key in CORE_COLUMNS}, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
