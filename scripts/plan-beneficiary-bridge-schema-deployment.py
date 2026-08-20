#!/usr/bin/env python3
"""Plan the minimal beneficiary bridge Dataverse schema slice.

This is a local dry-run planner. It reads repository schema artifacts, emits a
reviewable deployment plan, and performs no network calls or Dataverse writes.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


CORE_PLATFORM_TABLES = ["mp_TrackedEntity", "mp_EntityIdentifier"]
CORE_EXTENSION_TABLES = ["mp_BeneficiaryProfile", "mp_BeneficiarySubmissionLink"]
OPTIONAL_EXTENSION_TABLES = ["mp_BeneficiaryIdentityMatch"]
EXISTING_CRDB_PREREQUISITES = [
    "mp_project",
    "mp_submission",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--output-json", required=True, help="Plan output path. Use /tmp for runtime output.")
    parser.add_argument(
        "--include-identity-match",
        action="store_true",
        help="Include optional identity-match review table in the planned schema slice.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def platform_tables(repo_root: Path) -> dict[str, dict[str, Any]]:
    data = load_json(repo_root / "schemas/dataverse/platform-tables.json")
    return {row["logical_name"]: row for row in data.get("tables", [])}


def platform_columns(repo_root: Path) -> dict[str, list[dict[str, str]]]:
    rows = read_csv(repo_root / "schemas/dataverse/platform-columns.csv")
    result: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        table = row.get("table_logical_name") or row.get("table")
        if table:
            result.setdefault(table, []).append(row)
    return result


def platform_relationships(repo_root: Path) -> list[dict[str, str]]:
    return read_csv(repo_root / "schemas/dataverse/platform-relationships.csv")


def platform_alternate_keys(repo_root: Path) -> list[dict[str, str]]:
    return read_csv(repo_root / "schemas/dataverse/platform-alternate-keys.csv")


def extension_schema(repo_root: Path) -> dict[str, Any]:
    return load_json(repo_root / "schemas/dataverse/beneficiary-entity-extension-schema.json")


def extension_tables(repo_root: Path) -> dict[str, dict[str, Any]]:
    schema = extension_schema(repo_root)
    return {row["name"]: row for row in schema.get("tables", [])}


def selected_tables(include_identity_match: bool) -> list[str]:
    tables = [*CORE_PLATFORM_TABLES, *CORE_EXTENSION_TABLES]
    if include_identity_match:
        tables.extend(OPTIONAL_EXTENSION_TABLES)
    return tables


def operation_create_table(table: str, definition: dict[str, Any], source: str) -> dict[str, Any]:
    return {
        "operation": "create_table",
        "target": table,
        "source_artifact": source,
        "display_name": definition.get("display_name"),
        "primary_name_column": definition.get("primary_name_column"),
        "ownership": definition.get("ownership") or definition.get("ownership_type"),
        "notes": definition.get("purpose", ""),
    }


def operation_create_column(table: str, column: dict[str, Any], source: str) -> dict[str, Any]:
    name = column.get("name") or column.get("column_logical_name")
    column_type = column.get("type") or column.get("column_type")
    return {
        "operation": "create_lookup_relationship" if str(column_type).startswith("Lookup:") else "create_column",
        "target": f"{table}.{name}",
        "source_artifact": source,
        "type": column_type,
        "required": str(column.get("required", "")).lower() in {"true", "yes", "1"},
        "notes": column.get("notes") or column.get("description") or "",
    }


def operation_create_relationship(row: dict[str, Any], source: str) -> dict[str, Any]:
    return {
        "operation": "create_relationship",
        "target": f"{row['referenced_table']} -> {row['referencing_table']}.{row['lookup_column']}",
        "source_artifact": source,
        "referenced_table": row["referenced_table"],
        "referencing_table": row["referencing_table"],
        "lookup_column": row["lookup_column"],
        "required": str(row.get("required", "")).lower() in {"true", "yes", "1"},
        "notes": row.get("notes", ""),
    }


def operation_create_key(row: dict[str, Any], source: str) -> dict[str, Any]:
    table = row.get("table") or row.get("table_logical_name")
    name = row.get("name") or row.get("key_name")
    columns = row.get("columns", [])
    if isinstance(columns, str):
        columns = [item.strip() for item in columns.split(",") if item.strip()]
    return {
        "operation": "create_alternate_key",
        "target": f"{table}.{name}",
        "source_artifact": source,
        "table": table,
        "columns": columns,
        "notes": row.get("notes", ""),
    }


def build_plan(repo_root: Path, include_identity_match: bool) -> dict[str, Any]:
    selected = selected_tables(include_identity_match)
    platform_table_defs = platform_tables(repo_root)
    platform_column_defs = platform_columns(repo_root)
    extension_table_defs = extension_tables(repo_root)
    extension = extension_schema(repo_root)

    missing_artifacts: list[str] = []
    operations: list[dict[str, Any]] = []

    for table in CORE_PLATFORM_TABLES:
        definition = platform_table_defs.get(table)
        if not definition:
            missing_artifacts.append(f"{table} in schemas/dataverse/platform-tables.json")
            continue
        operations.append(operation_create_table(table, definition, "schemas/dataverse/platform-tables.json"))
        for column in platform_column_defs.get(table, []):
            operations.append(operation_create_column(table, column, "schemas/dataverse/platform-columns.csv"))

    for table in selected:
        if table in CORE_PLATFORM_TABLES:
            continue
        definition = extension_table_defs.get(table)
        if not definition:
            missing_artifacts.append(f"{table} in schemas/dataverse/beneficiary-entity-extension-schema.json")
            continue
        operations.append(operation_create_table(table, definition, "schemas/dataverse/beneficiary-entity-extension-schema.json"))
        for column in definition.get("columns", []):
            operations.append(operation_create_column(table, column, "schemas/dataverse/beneficiary-entity-extension-schema.json"))

    platform_relation_rows = [
        row
        for row in platform_relationships(repo_root)
        if row.get("referencing_table") in selected
    ]
    extension_relation_rows = [
        row
        for row in extension.get("relationships", [])
        if row.get("referencing_table") in selected
    ]
    for row in platform_relation_rows:
        operations.append(operation_create_relationship(row, "schemas/dataverse/platform-relationships.csv"))
    for row in extension_relation_rows:
        operations.append(operation_create_relationship(row, "schemas/dataverse/beneficiary-entity-extension-schema.json"))

    platform_key_rows = [
        row
        for row in platform_alternate_keys(repo_root)
        if (row.get("table") or row.get("table_logical_name")) in selected
    ]
    extension_key_rows = [
        row
        for row in extension.get("alternate_keys", [])
        if row.get("table") in selected
    ]
    for row in platform_key_rows:
        operations.append(operation_create_key(row, "schemas/dataverse/platform-alternate-keys.csv"))
    for row in extension_key_rows:
        operations.append(operation_create_key(row, "schemas/dataverse/beneficiary-entity-extension-schema.json"))

    return {
        "status": "dry_run_no_write",
        "scope": "minimal_beneficiary_bridge_schema",
        "selected_tables": selected,
        "existing_crdb_prerequisites": EXISTING_CRDB_PREREQUISITES,
        "optional_tables_excluded": [] if include_identity_match else OPTIONAL_EXTENSION_TABLES,
        "missing_artifacts": missing_artifacts,
        "operation_count": len(operations),
        "operations": operations,
        "safety": {
            "dataverse_writes_performed": False,
            "network_calls_performed": False,
            "approval_required_before_execution": True,
        },
    }


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    output = Path(args.output_json).expanduser().resolve()
    plan = build_plan(repo_root, args.include_identity_match)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")

    print("Beneficiary bridge schema deployment plan written.")
    print(f"Output: {output}")
    print(f"Selected tables: {', '.join(plan['selected_tables'])}")
    print(f"Operations: {plan['operation_count']}")
    print("No Dataverse writes performed.")
    if plan["missing_artifacts"]:
        print("Missing artifacts detected.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
