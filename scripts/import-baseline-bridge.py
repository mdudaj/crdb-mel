#!/usr/bin/env python3
"""Build TACATDP baseline bridge import payloads.

Default mode is a sanitized dry-run. It reads the latest XLSForm and Kobo export,
constructs the intended Dataverse upsert payload plan, validates required fields
and duplicate handling, and writes only aggregate/fingerprint output.

The script intentionally does not print raw beneficiary names, phone numbers,
customer IDs, or row payloads.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


FORM_ID = "tacatdp_impact_evaluation"
DEFAULT_PROJECT_CODE = "TACATDP"

CHOICE = {
    "submission_lifecycle_submitted": 100000001,
    "submission_review_received": 100000000,
    "tracked_entity_type_beneficiary": 100000000,
    "tracked_entity_status_active": 100000000,
    "identifier_source_record": 100000000,
    "identifier_phone": 100000002,
    "identifier_other": 100000005,
    "identifier_status_active": 100000000,
    "beneficiary_category_individual_farmer": 100000000,
    "beneficiary_verification_under_review": 100000000,
    "submission_link_relationship_baseline": 100000000,
    "submission_link_review_under_review": 100000000,
}


REQUIRED_HEADER_MAP = {
    "uuid": "_uuid",
    "submission_time": "_submission_time",
    "customer_id": "Customer ID",
    "customer_name": "Customer Name",
    "phone": "Farmer's Phone Number",
    "region": "Region",
    "district": "District",
    "start": "starttime",
    "end": "endtime",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xlsform", required=True, help="Latest XLSForm workbook path.")
    parser.add_argument("--workbook", required=True, help="KoboToolbox XLSX export path.")
    parser.add_argument("--output-json", required=True, help="Sanitized dry-run report path. Use /tmp for runtime output.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--project-code", default=DEFAULT_PROJECT_CODE, help="Project code used in stable keys.")
    parser.add_argument("--mode", choices=["dry-run", "execute"], default="dry-run")
    return parser.parse_args()


def load_workbook_reader(repo_root: Path):
    path = repo_root / "scripts/plan-baseline-workbook-import.py"
    spec = importlib.util.spec_from_file_location("baseline_planner_reader", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load workbook reader from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def value(row: dict[int, str], headers: list[str], header: str) -> str:
    for index, candidate in enumerate(headers):
        if candidate == header:
            return row.get(index, "").strip()
    return ""


def fingerprint(raw: str) -> str:
    if not raw:
        return ""
    digest = hashlib.sha256(f"tacatdp-baseline:{raw}".encode("utf-8")).hexdigest()
    return digest[:16]


def parse_datetime(raw: str) -> str | None:
    if not raw:
        return None
    text = raw.strip()
    try:
        serial = float(text)
    except ValueError:
        serial = None
    if serial is not None and 1 <= serial <= 100000:
        # Excel serial date. 1899-12-30 handles Excel's 1900 leap-year bug in
        # the same way common spreadsheet tooling does.
        return (datetime(1899, 12, 30, tzinfo=timezone.utc) + timedelta(days=serial)).isoformat()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M:%S"):
        try:
            return datetime.strptime(text[:19], fmt).replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            pass
    return None


def row_payload_summary(row: dict[int, str], headers: list[str], row_number: int, project_code: str, form_version: str) -> dict[str, Any]:
    uuid = value(row, headers, REQUIRED_HEADER_MAP["uuid"])
    customer_id = value(row, headers, REQUIRED_HEADER_MAP["customer_id"])
    customer_name = value(row, headers, REQUIRED_HEADER_MAP["customer_name"])
    phone = value(row, headers, REQUIRED_HEADER_MAP["phone"])
    submission_time = value(row, headers, REQUIRED_HEADER_MAP["submission_time"])
    start = value(row, headers, REQUIRED_HEADER_MAP["start"])
    end = value(row, headers, REQUIRED_HEADER_MAP["end"])
    region = value(row, headers, REQUIRED_HEADER_MAP["region"])
    district = value(row, headers, REQUIRED_HEADER_MAP["district"])

    source_key = f"{project_code}:kobo:{uuid}" if uuid else f"{project_code}:kobo-row:{row_number}"
    submission_instance_id = f"kobo:{uuid}" if uuid else f"kobo-row:{row_number}"
    version_key = f"{submission_instance_id}:baseline:{form_version or 'unknown'}"
    link_key = f"{source_key}:{submission_instance_id}:baseline"

    identifiers = [
        {
            "type": "source_uuid",
            "choice_label": "Source record",
            "present": bool(uuid),
            "fingerprint": fingerprint(uuid),
        },
        {
            "type": "customer_id",
            "choice_label": "Other",
            "present": bool(customer_id),
            "fingerprint": fingerprint(customer_id),
            "schema_note": "Current choice set lacks Customer ID; dry-run maps this identifier to Other.",
        },
        {
            "type": "phone",
            "choice_label": "Phone",
            "present": bool(phone),
            "fingerprint": fingerprint(phone),
        },
    ]

    return {
        "row_number": row_number,
        "stable_key_fingerprints": {
            "tracked_entity_key": fingerprint(source_key),
            "submission_instance_id": fingerprint(submission_instance_id),
            "submission_version_key": fingerprint(version_key),
            "beneficiary_submission_link_key": fingerprint(link_key),
        },
        "field_presence": {
            "uuid": bool(uuid),
            "customer_id": bool(customer_id),
            "customer_name": bool(customer_name),
            "phone": bool(phone),
            "region": bool(region),
            "district": bool(district),
            "submission_time": bool(submission_time),
        },
        "timestamps": {
            "started_at_parseable": bool(parse_datetime(start)),
            "submitted_at_parseable": bool(parse_datetime(submission_time) or parse_datetime(end)),
        },
        "payload_shapes": {
            "mp_Submission": {
                "alternate_key": "mp_instanceid",
                "columns": ["mp_instanceid", "mp_lifecyclestatus", "mp_reviewstate", "mp_startedat", "mp_submittedat"],
                "choice_labels": {
                    "mp_lifecyclestatus": "Submitted",
                    "mp_reviewstate": "Received",
                },
            },
            "mp_SubmissionVersion": {
                "alternate_key": "mp_versionkey",
                "columns": [
                    "mp_versionkey",
                    "mp_instanceid",
                    "mp_versionnumber",
                    "mp_current",
                    "mp_createdat",
                    "mp_xformsubmissionxml",
                    "mp_submissionjson",
                ],
                "contains_raw_payload_at_execute_time": True,
            },
            "mp_TrackedEntity": {
                "alternate_key": "AK_TrackedEntity_Project_Type_Key",
                "columns": ["mp_project", "mp_entitytype", "mp_entitykey", "mp_displayname", "mp_status"],
                "choice_labels": {
                    "mp_entitytype": "Beneficiary",
                    "mp_status": "Active",
                },
            },
            "mp_EntityIdentifier": {
                "alternate_key": "AK_EntityIdentifier_Entity_Type_Value",
                "identifier_count": sum(1 for item in identifiers if item["present"]),
                "identifier_types": [item["type"] for item in identifiers if item["present"]],
            },
            "mp_BeneficiaryProfile": {
                "alternate_key": "AK_BeneficiaryProfile_TrackedEntity",
                "columns": [
                    "mp_name",
                    "mp_trackedentity",
                    "mp_project",
                    "mp_beneficiarycategory",
                    "mp_region",
                    "mp_district",
                    "mp_verificationstatus",
                    "mp_datasource",
                    "mp_lastupdatedat",
                ],
            },
            "mp_BeneficiarySubmissionLink": {
                "alternate_key": "AK_BeneficiarySubmissionLink_Key",
                "columns": [
                    "mp_linkkey",
                    "mp_trackedentity",
                    "mp_submission",
                    "mp_relationshiptype",
                    "mp_completeness",
                    "mp_reviewstatus",
                ],
            },
        },
        "identifier_fingerprints": identifiers,
    }


def duplicate_queue(rows: list[dict[int, str]], headers: list[str], header: str, label: str) -> list[dict[str, Any]]:
    values: dict[str, list[str]] = defaultdict(list)
    for index, row in enumerate(rows, start=1):
        raw = value(row, headers, header)
        uuid = value(row, headers, REQUIRED_HEADER_MAP["uuid"])
        if raw:
            values[raw].append(fingerprint(uuid) or f"row-{index}")
    groups = []
    for raw, source_fingerprints in values.items():
        if len(source_fingerprints) > 1:
            groups.append(
                {
                    "identifier_type": label,
                    "identifier_fingerprint": fingerprint(raw),
                    "row_count": len(source_fingerprints),
                    "source_uuid_fingerprints": sorted(source_fingerprints)[:20],
                }
            )
    return sorted(groups, key=lambda item: (-item["row_count"], item["identifier_fingerprint"]))


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    reader = load_workbook_reader(repo_root)
    xlsform_sheets = reader.read_xlsx(Path(args.xlsform).resolve())
    data_sheets = reader.read_xlsx(Path(args.workbook).resolve())
    form_summary = reader.xlsform_summary(xlsform_sheets)
    root_sheet_name = next(iter(data_sheets.keys()), "")
    root_sheet = data_sheets[root_sheet_name]
    headers = root_sheet.headers

    missing_headers = [header for header in REQUIRED_HEADER_MAP.values() if header not in headers]
    rows = root_sheet.rows
    row_summaries = [
        row_payload_summary(row, headers, index, args.project_code, form_summary["settings"].get("version", ""))
        for index, row in enumerate(rows, start=1)
    ]

    missing_counts = Counter()
    parse_counts = Counter()
    identifier_counts = Counter()
    for item in row_summaries:
        for field, present in item["field_presence"].items():
            if not present:
                missing_counts[field] += 1
        for field, parseable in item["timestamps"].items():
            if parseable:
                parse_counts[field] += 1
        for identifier in item["identifier_fingerprints"]:
            if identifier["present"]:
                identifier_counts[identifier["type"]] += 1

    duplicate_groups = [
        *duplicate_queue(rows, headers, "Customer ID", "customer_id"),
        *duplicate_queue(rows, headers, "Farmer's Phone Number", "phone"),
    ]

    table_counts = {
        "mp_Submission": len(rows),
        "mp_SubmissionVersion": len(rows),
        "mp_TrackedEntity": len(rows),
        "mp_EntityIdentifier": sum(identifier_counts.values()),
        "mp_BeneficiaryProfile": len(rows),
        "mp_BeneficiarySubmissionLink": len(rows),
        "duplicate_review_groups": len(duplicate_groups),
        "duplicate_review_rows": sum(group["row_count"] for group in duplicate_groups),
    }

    sample_shapes = [row_summaries[index] for index in range(min(3, len(row_summaries)))]
    return {
        "status": "dry_run_no_write",
        "mode": args.mode,
        "inputs": {
            "xlsform_file": Path(args.xlsform).name,
            "workbook_file": Path(args.workbook).name,
            "root_sheet": root_sheet_name,
        },
        "form": {
            "id_string": form_summary["settings"].get("id_string", ""),
            "version": form_summary["settings"].get("version", ""),
        },
        "payload_counts": table_counts,
        "identifier_counts": dict(sorted(identifier_counts.items())),
        "missing_required_input_counts": dict(sorted(missing_counts.items())),
        "timestamp_parse_counts": dict(sorted(parse_counts.items())),
        "duplicate_review": {
            "policy": "review_only_no_auto_merge",
            "groups": duplicate_groups,
        },
        "schema_followups": [
            "Add a dedicated Customer ID option to mp_EntityIdentifier.mp_identifiertype; current dry-run maps Customer ID to Other.",
        ],
        "sample_payload_shapes": sample_shapes,
        "validation": {
            "missing_required_headers": missing_headers,
            "source_uuid_duplicate_groups": len(duplicate_queue(rows, headers, "_uuid", "source_uuid")),
            "execute_allowed": False,
        },
        "safety": {
            "dataverse_writes_performed": False,
            "raw_pii_in_output": False,
            "raw_payload_rows_in_output": False,
            "notes": [
                "Customer ID and phone are approved identifiers for CRDB-controlled Dataverse storage.",
                "Dry-run output includes only fingerprints and aggregate counts.",
                "Raw values must not be printed or committed.",
            ],
        },
    }


def main() -> int:
    args = parse_args()
    if args.mode == "execute":
        raise SystemExit("Live execute mode is intentionally blocked in this slice. Run dry-run and review first.")
    report = build_report(args)
    output = Path(args.output_json).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print("Baseline bridge import payload dry-run written.")
    print(f"Output: {output}")
    print(f"Root rows: {report['payload_counts']['mp_Submission']}")
    print(f"EntityIdentifier rows planned: {report['payload_counts']['mp_EntityIdentifier']}")
    print(f"Duplicate review groups: {report['payload_counts']['duplicate_review_groups']}")
    print("No Dataverse writes performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
