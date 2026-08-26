#!/usr/bin/env python3
"""Normalize cleaned TACATDP Stata data into the browser baseline import asset.

Default mode is a sanitized dry-run. It reports counts, identity quality,
child-table linkage quality, and KPI-relevant aggregates without writing raw
beneficiary rows. `package-asset` mode writes the raw import JSON expected by
the Power Pages browser importer and must be written outside the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any

try:
    import pandas as pd
    import pyreadstat
except ModuleNotFoundError as exc:  # pragma: no cover - exercised by operator environment
    missing = exc.name or "pandas/pyreadstat"
    raise SystemExit(
        f"Missing dependency: {missing}. Install local tooling with: .venv/bin/pip install pandas pyreadstat"
    ) from exc


ROOT_DTA = "TACATDP_Impact_Data_Tracking_for_Financed_Beneficiarie_Dataset.dta"
LOAN_DTA = "Loan and value chains invested in.dta"
COST_DTA = "Stages of Value Chain Cost Quantification Dataset.dta"
SUMMARY_XLSX = "DAP_TACADPT_share.xlsx"
FORM_ID = "tacatdp_impact_evaluation"
DEFAULT_FORM_VERSION = "2608130924"
DEFAULT_PROJECT_CODE = "TACATDP"

ROOT_FIELD_MAP = {
    "uuid": "_uuid",
    "submission_time": "_submission_time",
    "customer_id": "Customer_ID",
    "customer_name": "Customer_Name",
    "phone": "Farmer_Phone",
    "region": "region",
    "district": "district",
    "start": "starttime",
    "end": "endtime",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dta-folder", required=True, help="Folder containing cleaned TACATDP .dta files.")
    parser.add_argument("--output-json", required=True, help="Output path. Use /tmp for package assets.")
    parser.add_argument("--mode", choices=["dry-run", "package-asset"], default="dry-run")
    parser.add_argument("--project-code", default=DEFAULT_PROJECT_CODE)
    parser.add_argument("--form-id", default=FORM_ID)
    parser.add_argument("--form-version", default=DEFAULT_FORM_VERSION)
    parser.add_argument("--limit", type=int, help="Limit root rows for smoke package generation.")
    return parser.parse_args()


def require_file(folder: Path, name: str) -> Path:
    path = folder / name
    if not path.is_file():
        raise SystemExit(f"Required cleaned data file not found: {path}")
    return path


def load_dta(path: Path) -> tuple[pd.DataFrame, Any]:
    return pyreadstat.read_dta(path, apply_value_formats=True)


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return datetime.combine(value, time.min, tzinfo=timezone.utc).isoformat()
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def parse_datetime(value: Any) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    if isinstance(value, datetime):
        dt = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return dt.replace(microsecond=0).isoformat()
    if isinstance(value, date):
        return datetime.combine(value, time.min, tzinfo=timezone.utc).isoformat()
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:19], fmt).replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
    return None


def safe_xml_tag(raw: str, fallback: str) -> str:
    text = re.sub(r"[^0-9A-Za-z_]+", "_", raw.strip()).strip("_")
    if not text:
        text = fallback
    if text[0].isdigit():
        text = f"f_{text}"
    return text[:80]


def row_payload(row: pd.Series) -> dict[str, str]:
    result: dict[str, str] = {}
    for column, value in row.items():
        text = safe_text(value)
        if text:
            result[str(column)] = text
    return result


def build_xform_xml(root: dict[str, str], instance_id: str, form_id: str, form_version: str) -> str:
    fields: list[str] = []
    seen: Counter[str] = Counter()
    for index, (column, raw) in enumerate(root.items(), start=1):
        if column.startswith("_"):
            continue
        tag = safe_xml_tag(column, f"field_{index}")
        seen[tag] += 1
        if seen[tag] > 1:
            tag = f"{tag}_{seen[tag]}"
        fields.append(f"<{tag}>{html.escape(raw, quote=False)}</{tag}>")
    instance = html.escape(instance_id, quote=False)
    return (
        f'<data id="{form_id}" version="{html.escape(form_version, quote=True)}">'
        + "".join(fields)
        + f"<meta><instanceID>{instance}</instanceID></meta></data>"
    )


def fingerprint(value: str) -> str:
    if not value:
        return ""
    return hashlib.sha256(f"tacatdp-cleaned:{value}".encode("utf-8")).hexdigest()[:16]


def duplicate_summary(df: pd.DataFrame, column: str, identifier_type: str) -> dict[str, int | str]:
    values = df[column].map(safe_text) if column in df else pd.Series(dtype=str)
    values = values[values != ""]
    counts = values.value_counts()
    duplicate_groups = counts[counts > 1]
    return {
        "identifier_type": identifier_type,
        "column": column,
        "non_empty": int(values.count()),
        "unique": int(values.nunique()),
        "duplicate_groups": int(duplicate_groups.count()),
        "duplicate_rows": int(duplicate_groups.sum()),
    }


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def yes_count(df: pd.DataFrame, column: str) -> int:
    if column not in df:
        return 0
    values = df[column].map(safe_text).str.casefold()
    return int(values.isin({"1", "yes", "true", "selected"}).sum())


def aggregate_summary(root: pd.DataFrame, loans: pd.DataFrame, costs: pd.DataFrame) -> dict[str, Any]:
    loan_total = numeric(root["total_loan_amount"]) if "total_loan_amount" in root else pd.Series(dtype=float)
    loan_child_amount = numeric(loans["loan_amount"]) if "loan_amount" in loans else pd.Series(dtype=float)
    loan_count = numeric(root["loan_count"]) if "loan_count" in root else pd.Series(dtype=float)
    land_baseline = numeric(root["land_baseline"]) if "land_baseline" in root else pd.Series(dtype=float)
    land_after = numeric(root["land_after"]) if "land_after" in root else pd.Series(dtype=float)
    land_both = pd.DataFrame({"baseline": land_baseline, "after": land_after}).dropna()
    total_trained = numeric(root["total_trained"]) if "total_trained" in root else pd.Series(dtype=float)
    subtotal = numeric(costs["subtotal"]) if "subtotal" in costs else pd.Series(dtype=float)
    return {
        "beneficiary_rows": int(len(root)),
        "loan_child_rows": int(len(loans)),
        "cost_child_rows": int(len(costs)),
        "loan_count_sum": float(loan_count.sum()) if not loan_count.empty else 0,
        "root_total_loan_amount": float(loan_total.sum()) if not loan_total.empty else 0,
        "loan_child_amount_total": float(loan_child_amount.sum()) if not loan_child_amount.empty else 0,
        "regions": int(root["region"].dropna().nunique()) if "region" in root else 0,
        "districts": int(root["district"].dropna().nunique()) if "district" in root else 0,
        "wards": int(root["ward"].dropna().nunique()) if "ward" in root else 0,
        "gps_rows": int(
            root[["_Georeference_latitude", "_Georeference_longitude"]].dropna().shape[0]
            if {"_Georeference_latitude", "_Georeference_longitude"}.issubset(root.columns)
            else 0
        ),
        "ara_training_yes": yes_count(root, "ara_training"),
        "ara_training_no": int((root["ara_training"].map(safe_text).str.casefold() == "no").sum())
        if "ara_training" in root
        else 0,
        "total_trained_sum": float(total_trained.sum()) if not total_trained.empty else 0,
        "land_baseline_acres": float(land_baseline.sum()) if not land_baseline.empty else 0,
        "land_after_acres": float(land_after.sum()) if not land_after.empty else 0,
        "land_delta_acres": float((land_both["after"] - land_both["baseline"]).sum()) if not land_both.empty else 0,
        "cost_subtotal_sum_unverified": float(subtotal.sum()) if not subtotal.empty else 0,
    }


def top_counts(df: pd.DataFrame, column: str, limit: int = 12) -> list[dict[str, Any]]:
    if column not in df:
        return []
    counts = df[column].map(safe_text).replace("", pd.NA).dropna().value_counts().head(limit)
    return [{"value": str(value), "count": int(count)} for value, count in counts.items()]


def child_linkage(root: pd.DataFrame, loans: pd.DataFrame, costs: pd.DataFrame) -> dict[str, Any]:
    root_uuid = set(root["_uuid"].map(safe_text)) if "_uuid" in root else set()
    loan_uuid = loans["_submission__uuid"].map(safe_text) if "_submission__uuid" in loans else pd.Series(dtype=str)
    cost_pid = costs["PID"].map(safe_text) if "PID" in costs else pd.Series(dtype=str)
    return {
        "loan_rows": int(len(loans)),
        "loan_uuid_non_empty": int((loan_uuid != "").sum()),
        "loan_uuid_unique": int(loan_uuid[loan_uuid != ""].nunique()),
        "loan_rows_matching_root_uuid": int(loan_uuid.isin(root_uuid).sum()),
        "loan_link_status": "ready",
        "cost_rows": int(len(costs)),
        "cost_pid_non_empty": int((cost_pid != "").sum()),
        "cost_pid_unique": int(cost_pid[cost_pid != ""].nunique()),
        "cost_rows_matching_root_uuid": int(cost_pid.isin(root_uuid).sum()),
        "cost_link_status": "deferred_pid_mapping_required",
    }


def root_rows_by_uuid(root: pd.DataFrame) -> dict[str, pd.Series]:
    result: dict[str, pd.Series] = {}
    for _, row in root.iterrows():
        uuid = safe_text(row.get("_uuid"))
        if uuid:
            result[uuid] = row
    return result


def grouped_loan_repeats(loans: pd.DataFrame) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    if "_submission__uuid" not in loans:
        return grouped
    for _, row in loans.iterrows():
        uuid = safe_text(row.get("_submission__uuid"))
        if uuid:
            grouped[uuid].append(row_payload(row))
    return grouped


def build_asset_rows(
    root: pd.DataFrame,
    loans: pd.DataFrame,
    *,
    project_code: str,
    form_id: str,
    form_version: str,
    limit: int | None,
) -> list[dict[str, Any]]:
    rows = root.head(limit) if limit else root
    loan_repeats = grouped_loan_repeats(loans)
    asset_rows: list[dict[str, Any]] = []
    for row_number, (_, row) in enumerate(rows.iterrows(), start=1):
        uuid = safe_text(row.get(ROOT_FIELD_MAP["uuid"]))
        customer_id = safe_text(row.get(ROOT_FIELD_MAP["customer_id"]))
        customer_name = safe_text(row.get(ROOT_FIELD_MAP["customer_name"]))
        phone = safe_text(row.get(ROOT_FIELD_MAP["phone"]))
        region = safe_text(row.get(ROOT_FIELD_MAP["region"]))
        district = safe_text(row.get(ROOT_FIELD_MAP["district"]))
        # Keep the same tracked-entity identity namespace used by the first
        # Kobo baseline bridge import. The cleaned DTA file is a cleaned export
        # of the same baseline collection, so changing this to a new namespace
        # would append duplicate beneficiary entities instead of updating the
        # existing registry records during a replace import.
        source_key = f"{project_code}:kobo:{uuid}" if uuid else f"{project_code}:kobo-row:{row_number}"
        instance_id = f"kobo:{uuid}" if uuid else f"kobo-row:{row_number}"
        version_key = f"{instance_id}:baseline:{form_version}"
        link_key = f"{source_key}:{instance_id}:baseline"
        root_payload = row_payload(row)
        submission_json = {
            "source": "tacatdp_cleaned_dap_stata_import",
            "xmlFormId": form_id,
            "formVersion": form_version,
            "root": root_payload,
            "repeats": {
                "loan_value_chain": loan_repeats.get(uuid, []),
            },
            "lineage": {
                "rootFile": ROOT_DTA,
                "loanFile": LOAN_DTA,
                "loanRepeatLink": "_submission__uuid -> _uuid",
                "costFile": COST_DTA,
                "costRepeatLink": "deferred: PID mapping not proven",
            },
        }
        asset_rows.append(
            {
                "rowNumber": row_number,
                "uuid": uuid,
                "customerId": customer_id,
                "customerName": customer_name,
                "phone": phone,
                "region": region,
                "district": district,
                "startedAt": parse_datetime(row.get(ROOT_FIELD_MAP["start"])),
                "submittedAt": parse_datetime(row.get(ROOT_FIELD_MAP["submission_time"]))
                or parse_datetime(row.get(ROOT_FIELD_MAP["end"])),
                "sourceKey": source_key,
                "instanceId": instance_id,
                "versionKey": version_key,
                "linkKey": link_key,
                "submissionJson": json.dumps(submission_json, ensure_ascii=False, separators=(",", ":")),
                "xformXml": build_xform_xml(root_payload, instance_id, form_id, form_version),
            }
        )
    return asset_rows


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    folder = Path(args.dta_folder).expanduser().resolve()
    root_path = require_file(folder, ROOT_DTA)
    loan_path = require_file(folder, LOAN_DTA)
    cost_path = require_file(folder, COST_DTA)
    summary_path = folder / SUMMARY_XLSX
    root, _ = load_dta(root_path)
    loans, _ = load_dta(loan_path)
    costs, _ = load_dta(cost_path)

    missing_root_fields = [field for field in ROOT_FIELD_MAP.values() if field not in root.columns]
    if missing_root_fields:
        raise SystemExit(f"Main cleaned DTA is missing required root fields: {', '.join(missing_root_fields)}")

    selected_root = root.head(args.limit) if args.limit else root
    duplicate_groups = [
        duplicate_summary(root, "Customer_ID", "customer_id"),
        duplicate_summary(root, "Farmer_Phone", "phone"),
    ]
    identifier_counts = {
        "sourceUuidIdentifiers": int((selected_root["_uuid"].map(safe_text) != "").sum()),
        "customerIdIdentifiers": int((selected_root["Customer_ID"].map(safe_text) != "").sum()),
        "phoneIdentifiers": int((selected_root["Farmer_Phone"].map(safe_text) != "").sum()),
    }
    base = {
        "assetType": "tacatdp-baseline-bridge-import",
        "projectCode": args.project_code,
        "formId": args.form_id,
        "formVersion": args.form_version,
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": {
            "rootFile": root_path.name,
            "loanValueChainFile": loan_path.name,
            "valueChainCostFile": cost_path.name,
            "summaryWorkbook": summary_path.name if summary_path.exists() else None,
            "sourceFormat": "stata_dta_cleaned_dap",
        },
        "counts": {
            "rows": int(min(len(root), args.limit) if args.limit else len(root)),
            **identifier_counts,
            "duplicateReviewGroups": int(sum(group["duplicate_groups"] for group in duplicate_groups)),
            "duplicateReviewRows": int(sum(group["duplicate_rows"] for group in duplicate_groups)),
        },
        "duplicatePolicy": "review_only_no_auto_merge",
        "importPlan": {
            "recommendedMode": "replace",
            "rootRows": "ready",
            "loanValueChainRows": "preserved_in_submission_json_repeats",
            "valueChainCostRows": "deferred_until_pid_mapping_is_verified",
        },
        "quality": {
            "identifiers": {
                "_uuid": duplicate_summary(root, "_uuid", "source_uuid"),
                "Customer_ID": duplicate_groups[0],
                "Farmer_Phone": duplicate_groups[1],
            },
            "childLinkage": child_linkage(root, loans, costs),
        },
        "aggregates": aggregate_summary(root, loans, costs),
        "distributions": {
            "regions": top_counts(root, "region"),
            "districts": top_counts(root, "district"),
            "gender": top_counts(root, "Gender"),
            "ageGroup": top_counts(root, "age_group"),
            "araTraining": top_counts(root, "ara_training"),
            "loanYear": top_counts(loans, "loan_year"),
            "valueChainStage": top_counts(loans, "other_stage"),
        },
    }

    if args.mode == "package-asset":
        if not str(Path(args.output_json).expanduser().resolve()).startswith("/tmp/"):
            raise SystemExit("Package assets contain raw beneficiary data and must be written under /tmp.")
        return {
            **base,
            "rows": build_asset_rows(
                root,
                loans,
                project_code=args.project_code,
                form_id=args.form_id,
                form_version=args.form_version,
                limit=args.limit,
            ),
        }

    return {
        "status": "dry_run_no_write",
        **base,
        "rows": "omitted_in_dry_run",
        "safety": {
            "raw_pii_in_output": False,
            "raw_payload_rows_in_output": False,
            "dataverse_writes_performed": False,
        },
    }


def main() -> int:
    args = parse_args()
    report = build_report(args)
    output = Path(args.output_json).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print("Cleaned TACATDP DTA import normalization complete.")
    print(f"Mode: {args.mode}")
    print(f"Output: {output}")
    print(f"Root rows: {report['counts']['rows']}")
    print(f"Duplicate review groups: {report['counts']['duplicateReviewGroups']}")
    print(f"Recommended import mode: {report['importPlan']['recommendedMode']}")
    if args.mode == "dry-run":
        print("No raw rows or Dataverse writes produced.")
    else:
        print("Raw import asset produced under /tmp; do not commit it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
