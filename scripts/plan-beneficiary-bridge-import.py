#!/usr/bin/env python3
"""Plan TACATDP beneficiary bridge import without Dataverse writes.

Input is the sanitized output from plan-baseline-workbook-import.py. This script
does not read raw workbook rows, does not print PII, and does not call Dataverse.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

BENEFICIARY_BRIDGE_TABLES = [
    "mp_TrackedEntity",
    "mp_EntityIdentifier",
    "mp_BeneficiaryProfile",
    "mp_BeneficiarySubmissionLink",
]

OPTIONAL_REVIEW_TABLES = [
    "mp_BeneficiaryIdentityMatch",
]

DEFERRED_TABLES = [
    "mp_BeneficiaryProgrammeParticipation",
    "mp_BeneficiaryFinanceLink",
    "mp_BeneficiaryTechnologyAdoption",
    "mp_BeneficiaryTrainingParticipation",
    "mp_BeneficiaryOutcomeSnapshot",
    "mp_BeneficiaryGroupMembership",
    "mp_BeneficiaryLocationHistory",
]

EXISTING_RUNTIME_TABLES = [
    "mp_Project",
    "mp_Form",
    "mp_FormVersion",
    "mp_FormAttachment",
    "mp_FormAssignment",
    "mp_Submission",
    "mp_SubmissionVersion",
    "mp_SubmissionAttachment",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-summary", required=True, help="Sanitized baseline planner JSON.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--output-json", required=True, help="Sanitized dry-run output path. Use /tmp.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def platform_table_names(repo_root: Path) -> set[str]:
    data = load_json(repo_root / "schemas/dataverse/platform-tables.json")
    return {row.get("logical_name", "") for row in data.get("tables", [])}


def platform_columns(repo_root: Path) -> dict[str, list[str]]:
    rows = read_csv(repo_root / "schemas/dataverse/platform-columns.csv")
    result: dict[str, list[str]] = {}
    for row in rows:
        table = row.get("table") or row.get("table_logical_name")
        column = row.get("column") or row.get("column_logical_name")
        if table and column:
            result.setdefault(table, []).append(column)
    return result


def beneficiary_extension_table_names(repo_root: Path) -> set[str]:
    data = load_json(repo_root / "schemas/dataverse/beneficiary-entity-extension-schema.json")
    return {row.get("name", "") for row in data.get("tables", [])}


def beneficiary_columns(repo_root: Path) -> dict[str, list[str]]:
    data = load_json(repo_root / "schemas/dataverse/beneficiary-entity-extension-schema.json")
    return {
        table["name"]: [column["name"] for column in table.get("columns", [])]
        for table in data.get("tables", [])
    }


def runtime_schema_tables(repo_root: Path) -> set[str]:
    data = load_json(repo_root / "schemas/dataverse/odk-central-inspired-mvp-schema.json")
    return {f"mp_{row.get('singular_name', '')}" for row in data.get("tables", []) if row.get("singular_name")}


def runtime_schema_columns(repo_root: Path) -> dict[str, list[str]]:
    data = load_json(repo_root / "schemas/dataverse/odk-central-inspired-mvp-schema.json")
    result: dict[str, list[str]] = {}
    for table in data.get("tables", []):
        singular = table.get("singular_name")
        if not singular:
            continue
        result[f"mp_{singular}"] = [
            f"mp_{column['name'].lower()}"
            for column in table.get("columns", [])
            if column.get("name")
        ]
    return result


def table_artifact_status(repo_root: Path) -> dict[str, Any]:
    platform_tables = platform_table_names(repo_root)
    extension_tables = beneficiary_extension_table_names(repo_root)
    runtime_tables = runtime_schema_tables(repo_root)
    platform_cols = platform_columns(repo_root)
    extension_cols = beneficiary_columns(repo_root)
    runtime_cols = runtime_schema_columns(repo_root)

    def status(table: str) -> dict[str, Any]:
        if table in platform_tables:
            return {
                "artifact": "schemas/dataverse/platform-tables.json",
                "status": "defined",
                "columns": platform_cols.get(table, []),
            }
        if table in extension_tables:
            return {
                "artifact": "schemas/dataverse/beneficiary-entity-extension-schema.json",
                "status": "defined",
                "columns": extension_cols.get(table, []),
            }
        if table in runtime_tables:
            return {
                "artifact": "schemas/dataverse/odk-central-inspired-mvp-schema.json",
                "status": "defined",
                "columns": runtime_cols.get(table, []),
            }
        return {"artifact": None, "status": "missing_from_local_schema_artifacts", "columns": []}

    return {
        "runtime_tables": {table: status(table) for table in EXISTING_RUNTIME_TABLES},
        "beneficiary_bridge_tables": {table: status(table) for table in BENEFICIARY_BRIDGE_TABLES},
        "optional_review_tables": {table: status(table) for table in OPTIONAL_REVIEW_TABLES},
        "deferred_tables": {table: status(table) for table in DEFERRED_TABLES},
    }


def build_import_plan(summary: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    kobo = summary["kobo_export"]
    root_sheet = kobo["root_sheet"]
    root_rows = int(kobo["sheets"][root_sheet]["rows"])
    duplicate_identity = kobo.get("duplicate_identity_candidates", {})
    source_uuid_duplicates = int(duplicate_identity.get("source_uuid_rows_in_duplicate_groups", 0))
    customer_id_duplicate_rows = int(duplicate_identity.get("customer_id_rows_in_duplicate_groups", 0))
    phone_duplicate_rows = int(duplicate_identity.get("phone_rows_in_duplicate_groups", 0))
    identity_match_candidate_rows = max(customer_id_duplicate_rows, phone_duplicate_rows)

    return {
        "status": "dry_run_no_write",
        "form": summary["xlsform"]["settings"],
        "source": {
            "root_sheet": root_sheet,
            "root_rows": root_rows,
            "repeat_sheets": {
                name: sheet["rows"]
                for name, sheet in kobo["sheets"].items()
                if name != root_sheet
            },
        },
        "local_schema_inventory": table_artifact_status(repo_root),
        "expected_idempotent_import_actions": {
            "mp_Project": {
                "operation": "confirm_or_seed",
                "expected_rows": 1,
                "note": "Use existing TACATDP project where present.",
            },
            "mp_Form": {
                "operation": "confirm_or_seed",
                "expected_rows": 1,
                "note": "Use form id tacatdp_impact_evaluation.",
            },
            "mp_FormVersion": {
                "operation": "confirm_or_seed",
                "expected_rows": 1,
                "note": "Use latest XLSForm version 2608130924.",
            },
            "mp_Submission": {
                "operation": "create_or_match_by_instanceid",
                "expected_rows": root_rows,
                "blocked_if_duplicate_source_uuid_rows": source_uuid_duplicates,
            },
            "mp_SubmissionVersion": {
                "operation": "create_or_match_by_versionkey",
                "expected_rows": root_rows,
                "note": "Store normalized baseline payload. Do not emit raw row payload in dry-run output.",
            },
            "mp_TrackedEntity": {
                "operation": "create_or_match_candidate",
                "expected_rows_upper_bound": root_rows,
                "note": "Final count may be lower after approved duplicate review.",
            },
            "mp_EntityIdentifier": {
                "operation": "create_source_uuid_customer_id_and_phone_identifiers",
                "expected_rows_minimum": root_rows
                + int(duplicate_identity.get("customer_id_non_empty", 0))
                + int(duplicate_identity.get("phone_non_empty", 0)),
                "expected_source_uuid_rows": root_rows,
                "expected_approved_identifier_rows": {
                    "customer_id": int(duplicate_identity.get("customer_id_non_empty", 0)),
                    "phone": int(duplicate_identity.get("phone_non_empty", 0)),
                },
                "approved_identifier_fields": ["Customer ID", "Farmer's Phone Number"],
                "note": "Approved for CRDB-controlled environment import. Do not print raw values in logs/reports.",
            },
            "mp_BeneficiaryProfile": {
                "operation": "create_or_update_imported_profile_projection",
                "expected_rows_upper_bound": root_rows,
                "note": "Profile fields only; finance/training/outcome facts remain in SubmissionVersion JSON for this slice.",
            },
            "mp_BeneficiarySubmissionLink": {
                "operation": "create_lineage_link",
                "expected_rows": root_rows,
            },
            "mp_BeneficiaryIdentityMatch": {
                "operation": "optional_create_review_records",
                "expected_candidate_rows": identity_match_candidate_rows,
                "note": "Do not auto-merge duplicate customer/phone candidates.",
            },
        },
        "deferred_normalized_projection_tables": DEFERRED_TABLES,
        "privacy_findings": {
            "privacy_sensitive_columns_detected": kobo.get("privacy_sensitive_columns_detected", {}),
            "duplicate_identity_candidates": duplicate_identity,
            "approved_identifier_storage": ["Customer ID", "Farmer's Phone Number"],
            "remaining_decision": "Duplicate customer/phone candidates must be queued for review, not auto-merged.",
        },
        "blocking_checks_before_live_import": [
            "Confirm target environment has the four beneficiary bridge tables.",
            "Confirm duplicate customer/phone candidates are review-only and not auto-merged.",
            "Confirm the import should create one tracked-entity candidate per Kobo root row before duplicate adjudication.",
            "Confirm the baseline import remains schema/data-only and does not change Power Pages table permissions.",
        ],
        "safety": {
            "dataverse_writes_performed": False,
            "raw_pii_included": False,
            "raw_rows_included": False,
        },
    }


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    baseline_summary = Path(args.baseline_summary).expanduser().resolve()
    output = Path(args.output_json).expanduser().resolve()

    if not baseline_summary.exists():
        raise SystemExit(f"Baseline summary not found: {baseline_summary}")
    if not repo_root.exists():
        raise SystemExit(f"Repo root not found: {repo_root}")

    summary = load_json(baseline_summary)
    plan = build_import_plan(summary, repo_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")

    print("Beneficiary bridge import dry-run plan written.")
    print(f"Output: {output}")
    print(f"Root rows: {plan['source']['root_rows']}")
    print(f"Identity-match candidate rows: {plan['expected_idempotent_import_actions']['mp_BeneficiaryIdentityMatch']['expected_candidate_rows']}")
    print("No Dataverse writes performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
