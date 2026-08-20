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
import html
import hashlib
import importlib.util
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
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
    "identifier_customer_id": 100000006,
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
    parser.add_argument("--mode", choices=["dry-run", "execute", "package-asset"], default="dry-run")
    parser.add_argument("--env-file", default=".env", help="Environment file for execute mode.")
    parser.add_argument("--limit", type=int, help="Limit rows processed. Use for smoke tests.")
    parser.add_argument("--summary-json", help="Optional sanitized execution summary path.")
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


def load_deploy_module(repo_root: Path):
    path = repo_root / "scripts/dataverse-schema-deploy.py"
    spec = importlib.util.spec_from_file_location("dataverse_schema_deploy", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load Dataverse deploy helper from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_settings(deploy: Any, env_file: str) -> Any:
    path = Path(env_file).resolve()
    if path.exists():
        return deploy.build_settings(
            argparse.Namespace(env_file=env_file, schema_dir=None, schema_file=None, execute=False, no_publish=False)
        )
    env = os.environ
    required = [
        "POWER_PLATFORM_TENANT_ID",
        "POWER_PLATFORM_ENVIRONMENT_URL",
    ]
    missing = [key for key in required if not env.get(key)]
    if missing:
        raise SystemExit(f"Missing required environment values: {', '.join(missing)}")
    solution_unique_name = env.get("POWER_PLATFORM_SOLUTION_UNIQUE_NAME") or "tacatdp_prototype"
    publisher_prefix = env.get("POWER_PLATFORM_PUBLISHER_PREFIX") or "mp"
    deploy_target = env.get("TACATDP_DEPLOY_TARGET") or "dev"
    return deploy.Settings(
        tenant_id=env["POWER_PLATFORM_TENANT_ID"],
        client_id=env.get("POWER_PLATFORM_CLIENT_ID", ""),
        client_secret=env.get("POWER_PLATFORM_CLIENT_SECRET", ""),
        environment_url=env["POWER_PLATFORM_ENVIRONMENT_URL"].rstrip("/"),
        solution_unique_name=solution_unique_name,
        solution_display_name=env.get("POWER_PLATFORM_SOLUTION_DISPLAY_NAME") or solution_unique_name,
        publisher_name=env.get("POWER_PLATFORM_PUBLISHER_NAME") or "TACATDP",
        publisher_prefix=publisher_prefix,
        deploy_target=deploy_target,
        schema_dir=Path(env.get("TACATDP_DATAVERSE_SCHEMA_DIR") or "schemas/dataverse").resolve(),
        schema_file=Path(env.get("TACATDP_DATAVERSE_SCHEMA_FILE") or "schemas/dataverse/mvp-schema-definition.json").resolve(),
    )


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


def escape_odata(value: str) -> str:
    return value.replace("'", "''")


def parse_guid_from_entity_id(value: str) -> str:
    return value.rsplit("(", 1)[-1].rstrip(")")


def safe_xml_tag(raw: str, fallback: str) -> str:
    text = re.sub(r"[^0-9A-Za-z_]+", "_", raw.strip()).strip("_")
    if not text:
        text = fallback
    if text[0].isdigit():
        text = f"f_{text}"
    return text[:80]


def row_to_label_payload(row: dict[int, str], headers: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for index, raw in row.items():
        if index < len(headers) and headers[index]:
            result[headers[index]] = raw
    return result


def build_repeats_by_parent(sheets: dict[str, Any], root_sheet_name: str) -> dict[str, dict[str, list[dict[str, str]]]]:
    grouped: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for name, sheet in sheets.items():
        if name == root_sheet_name:
            continue
        if "_parent_index" not in sheet.headers:
            continue
        for row in sheet.rows:
            parent_index = value(row, sheet.headers, "_parent_index")
            if not parent_index:
                continue
            grouped[parent_index][name].append(row_to_label_payload(row, sheet.headers))
    return grouped


def build_submission_json(
    row: dict[int, str],
    headers: list[str],
    parent_index: str,
    repeats_by_parent: dict[str, dict[str, list[dict[str, str]]]],
    form_id: str,
    form_version: str,
) -> str:
    payload = {
        "source": "kobotoolbox_baseline_import",
        "xmlFormId": form_id,
        "formVersion": form_version,
        "root": row_to_label_payload(row, headers),
        "repeats": repeats_by_parent.get(parent_index, {}),
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def build_xform_xml(row: dict[int, str], headers: list[str], instance_id: str, form_version: str) -> str:
    fields: list[str] = []
    seen: Counter[str] = Counter()
    for index, raw in row.items():
        if index >= len(headers):
            continue
        header = headers[index]
        if not header or header.startswith("_"):
            continue
        tag = safe_xml_tag(header, f"field_{index}")
        seen[tag] += 1
        if seen[tag] > 1:
            tag = f"{tag}_{seen[tag]}"
        fields.append(f"<{tag}>{html.escape(raw, quote=False)}</{tag}>")
    instance = html.escape(instance_id, quote=False)
    return (
        f'<data id="{FORM_ID}" version="{html.escape(form_version, quote=True)}">'
        + "".join(fields)
        + f"<meta><instanceID>{instance}</instanceID></meta></data>"
    )


def build_package_asset(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    reader = load_workbook_reader(repo_root)
    xlsform_sheets = reader.read_xlsx(Path(args.xlsform).resolve())
    data_sheets = reader.read_xlsx(Path(args.workbook).resolve())
    form_summary = reader.xlsform_summary(xlsform_sheets)
    form_version = form_summary["settings"].get("version", "")
    if not form_version:
        raise RuntimeError("XLSForm version missing; refusing package asset generation.")

    root_sheet_name = next(iter(data_sheets.keys()), "")
    root_sheet = data_sheets[root_sheet_name]
    rows = root_sheet.rows[: args.limit] if args.limit else root_sheet.rows
    repeats_by_parent = build_repeats_by_parent(data_sheets, root_sheet_name)

    asset_rows = []
    identifier_counts: Counter[str] = Counter()
    for row_number, row in enumerate(rows, start=1):
        uuid = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["uuid"])
        customer_id = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["customer_id"])
        customer_name = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["customer_name"])
        phone = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["phone"])
        submission_time = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["submission_time"])
        start = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["start"])
        end = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["end"])
        region = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["region"])
        district = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["district"])
        parent_index = value(row, root_sheet.headers, "_index") or str(row_number)

        source_key = f"{args.project_code}:kobo:{uuid}" if uuid else f"{args.project_code}:kobo-row:{row_number}"
        instance_id = f"kobo:{uuid}" if uuid else f"kobo-row:{row_number}"
        version_key = f"{instance_id}:baseline:{form_version}"
        link_key = f"{source_key}:{instance_id}:baseline"
        if uuid:
            identifier_counts["source_uuid"] += 1
        if customer_id:
            identifier_counts["customer_id"] += 1
        if phone:
            identifier_counts["phone"] += 1

        asset_rows.append(
            {
                "rowNumber": row_number,
                "uuid": uuid,
                "customerId": customer_id,
                "customerName": customer_name,
                "phone": phone,
                "region": region,
                "district": district,
                "startedAt": parse_datetime(start),
                "submittedAt": parse_datetime(submission_time) or parse_datetime(end),
                "sourceKey": source_key,
                "instanceId": instance_id,
                "versionKey": version_key,
                "linkKey": link_key,
                "submissionJson": build_submission_json(
                    row,
                    root_sheet.headers,
                    parent_index,
                    repeats_by_parent,
                    FORM_ID,
                    form_version,
                ),
                "xformXml": build_xform_xml(row, root_sheet.headers, instance_id, form_version),
            }
        )

    duplicate_groups = [
        *duplicate_queue(root_sheet.rows, root_sheet.headers, "Customer ID", "customer_id"),
        *duplicate_queue(root_sheet.rows, root_sheet.headers, "Farmer's Phone Number", "phone"),
    ]

    return {
        "assetType": "tacatdp-baseline-bridge-import",
        "projectCode": args.project_code,
        "formId": form_summary["settings"].get("id_string", FORM_ID),
        "formVersion": form_version,
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": {
            "xlsformFile": Path(args.xlsform).name,
            "workbookFile": Path(args.workbook).name,
            "rootSheet": root_sheet_name,
        },
        "counts": {
            "rows": len(asset_rows),
            "sourceUuidIdentifiers": identifier_counts["source_uuid"],
            "customerIdIdentifiers": identifier_counts["customer_id"],
            "phoneIdentifiers": identifier_counts["phone"],
            "duplicateReviewGroups": len(duplicate_groups),
            "duplicateReviewRows": sum(group["row_count"] for group in duplicate_groups),
        },
        "duplicatePolicy": "review_only_no_auto_merge",
        "rows": asset_rows,
    }


class DataverseImportClient:
    TABLE_LOGICAL = {
        "Projects": "mp_project",
        "FormVersions": "mp_formversion",
        "Submissions": "mp_submission",
        "SubmissionVersions": "mp_submissionversion",
        "TrackedEntities": "mp_trackedentity",
        "EntityIdentifiers": "mp_entityidentifier",
        "BeneficiaryProfiles": "mp_beneficiaryprofile",
        "BeneficiarySubmissionLinks": "mp_beneficiarysubmissionlink",
    }

    RELATIONSHIPS = {
        ("FormVersions", "Submissions", "FormVersion"): "mp_FormVersion_Submission_FormVersion",
        ("Submissions", "SubmissionVersions", "Submission"): "mp_Submission_SubmissionVersion_Submission",
        ("Projects", "TrackedEntities", "Project"): "mp_Project_TrackedEntity_Project",
        ("TrackedEntities", "EntityIdentifiers", "TrackedEntity"): "mp_TrackedEntity_EntityIdentifier_TrackedEntity",
        ("TrackedEntities", "BeneficiaryProfiles", "TrackedEntity"): "mp_TrackedEntity_BeneficiaryProfile_TrackedEntity",
        ("Projects", "BeneficiaryProfiles", "Project"): "mp_Project_BeneficiaryProfile_Project",
        ("TrackedEntities", "BeneficiarySubmissionLinks", "TrackedEntity"): "mp_TrackedEntity_BeneficiarySubmissionLink_TrackedEntity",
        ("Submissions", "BeneficiarySubmissionLinks", "Submission"): "mp_Submission_BeneficiarySubmissionLink_Submission",
    }

    def __init__(self, deploy: Any, settings: Any, token: str) -> None:
        self.deploy = deploy
        self.settings = settings
        self.dv = deploy.Dataverse(settings, token)
        self.entity_sets: dict[str, str] = {}
        self.primary_ids: dict[str, str] = {}
        self.nav_properties: dict[str, str] = {}

    def table_logical(self, table: str) -> str:
        return self.TABLE_LOGICAL[table]

    def column(self, name: str) -> str:
        return f"{self.settings.publisher_prefix}_{name[0].lower()}{name[1:]}".lower()

    def entity_set(self, table: str) -> str:
        if table not in self.entity_sets:
            logical = self.table_logical(table)
            data = self.dv.get_json(f"EntityDefinitions(LogicalName='{logical}')?$select=EntitySetName,PrimaryIdAttribute")
            if not data:
                raise RuntimeError(f"Missing table metadata: {logical}")
            self.entity_sets[table] = data["EntitySetName"]
            self.primary_ids[table] = data["PrimaryIdAttribute"]
        return self.entity_sets[table]

    def primary_id(self, table: str) -> str:
        self.entity_set(table)
        return self.primary_ids[table]

    def nav_property(self, relationship_schema: str) -> str:
        if relationship_schema not in self.nav_properties:
            encoded = quote(relationship_schema, safe="")
            base = self.dv.get_json(f"RelationshipDefinitions(SchemaName='{encoded}')?$select=MetadataId")
            if not base:
                raise RuntimeError(f"Missing relationship metadata: {relationship_schema}")
            metadata_id = base["MetadataId"]
            data = self.dv.get_json(
                f"RelationshipDefinitions({metadata_id})/Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata"
                "?$select=ReferencingEntityNavigationPropertyName"
            )
            self.nav_properties[relationship_schema] = data["ReferencingEntityNavigationPropertyName"]
        return self.nav_properties[relationship_schema]

    def bind(self, referenced: str, referencing: str, lookup: str, record_id: str) -> tuple[str, str]:
        schema = self.RELATIONSHIPS[(referenced, referencing, lookup)]
        return f"{self.nav_property(schema)}@odata.bind", f"/{self.entity_set(referenced)}({record_id})"

    def find_one(self, table: str, filter_expr: str, select_extra: str = "") -> dict[str, Any] | None:
        entity_set = self.entity_set(table)
        primary = self.primary_id(table)
        select = primary if not select_extra else f"{primary},{select_extra}"
        # Do not delegate this query to Dataverse.get_json. Some filters contain
        # approved-but-sensitive identifiers such as phone numbers and customer
        # IDs. Dataverse.get_json includes the request path in failure messages,
        # which would leak those values into terminal output.
        response = self.dv.request("GET", f"{entity_set}?$select={select}&$filter={filter_expr}&$top=1")
        if response.status_code >= 400:
            raise RuntimeError(f"GET {table} query failed: HTTP {response.status_code} {self.deploy.safe_error(response)}")
        data = response.json()
        rows = (data or {}).get("value") or []
        return rows[0] if rows else None

    def create(self, table: str, payload: dict[str, Any]) -> str:
        response = self.dv.post(self.entity_set(table), payload)
        return parse_guid_from_entity_id(response.headers.get("OData-EntityId", ""))

    def update(self, table: str, record_id: str, payload: dict[str, Any]) -> None:
        response = self.dv.request("PATCH", f"{self.entity_set(table)}({record_id})", payload=payload)
        if response.status_code >= 400:
            raise RuntimeError(f"PATCH {table} failed: HTTP {response.status_code} {self.deploy.safe_error(response)}")

    def ensure(self, table: str, filter_expr: str, payload: dict[str, Any], *, update_existing: bool = True) -> tuple[str, str]:
        primary = self.primary_id(table)
        existing = self.find_one(table, filter_expr)
        if existing:
            record_id = existing[primary]
            if update_existing:
                self.update(table, record_id, payload)
                return record_id, "updated"
            return record_id, "exists"
        return self.create(table, payload), "created"

    def required_row_id(self, table: str, filter_expr: str) -> str:
        primary = self.primary_id(table)
        row = self.find_one(table, filter_expr)
        if not row:
            raise RuntimeError(f"Required {table} row not found by filter")
        return row[primary]


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
            "choice_label": "Customer ID",
            "present": bool(customer_id),
            "fingerprint": fingerprint(customer_id),
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
        "schema_followups": [],
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


def import_rows(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    reader = load_workbook_reader(repo_root)
    deploy = load_deploy_module(repo_root)
    settings = build_settings(deploy, args.env_file)
    if str(settings.deploy_target).lower() != "dev":
        raise SystemExit(f"Refusing non-dev deployment target: {settings.deploy_target}")
    token = deploy.get_token(settings)
    client = DataverseImportClient(deploy, settings, token)

    xlsform_sheets = reader.read_xlsx(Path(args.xlsform).resolve())
    data_sheets = reader.read_xlsx(Path(args.workbook).resolve())
    form_summary = reader.xlsform_summary(xlsform_sheets)
    form_version = form_summary["settings"].get("version", "")
    if not form_version:
        raise RuntimeError("XLSForm version missing; refusing import.")
    root_sheet_name = next(iter(data_sheets.keys()), "")
    root_sheet = data_sheets[root_sheet_name]
    rows = root_sheet.rows[: args.limit] if args.limit else root_sheet.rows
    repeats_by_parent = build_repeats_by_parent(data_sheets, root_sheet_name)

    project_id = client.required_row_id("Projects", f"mp_projectcode eq '{escape_odata(args.project_code)}'")
    form_version_id = client.required_row_id("FormVersions", f"mp_version eq '{escape_odata(form_version)}'")

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    counts: Counter[str] = Counter()
    actions: Counter[str] = Counter()
    duplicate_groups = [
        *duplicate_queue(root_sheet.rows, root_sheet.headers, "Customer ID", "customer_id"),
        *duplicate_queue(root_sheet.rows, root_sheet.headers, "Farmer's Phone Number", "phone"),
    ]

    for row_number, row in enumerate(rows, start=1):
        uuid = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["uuid"])
        customer_id = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["customer_id"])
        customer_name = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["customer_name"])
        phone = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["phone"])
        submission_time = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["submission_time"])
        start = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["start"])
        end = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["end"])
        region = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["region"])
        district = value(row, root_sheet.headers, REQUIRED_HEADER_MAP["district"])
        parent_index = value(row, root_sheet.headers, "_index") or str(row_number)

        source_key = f"{args.project_code}:kobo:{uuid}" if uuid else f"{args.project_code}:kobo-row:{row_number}"
        instance_id = f"kobo:{uuid}" if uuid else f"kobo-row:{row_number}"
        version_key = f"{instance_id}:baseline:{form_version}"
        link_key = f"{source_key}:{instance_id}:baseline"
        display_name = customer_name or f"Beneficiary {row_number}"
        started_at = parse_datetime(start)
        submitted_at = parse_datetime(submission_time) or parse_datetime(end) or now

        submission_payload = {
            "mp_instanceid": instance_id,
            "mp_lifecyclestatus": CHOICE["submission_lifecycle_submitted"],
            "mp_reviewstate": CHOICE["submission_review_received"],
            "mp_startedat": started_at,
            "mp_submittedat": submitted_at,
            "mp_updatedat": now,
        }
        submission_payload[client.bind("FormVersions", "Submissions", "FormVersion", form_version_id)[0]] = client.bind(
            "FormVersions", "Submissions", "FormVersion", form_version_id
        )[1]
        submission_id, action = client.ensure(
            "Submissions",
            f"mp_instanceid eq '{escape_odata(instance_id)}'",
            {k: v for k, v in submission_payload.items() if v is not None},
        )
        counts["mp_Submission"] += 1
        actions[f"mp_Submission.{action}"] += 1

        submission_json = build_submission_json(row, root_sheet.headers, parent_index, repeats_by_parent, FORM_ID, form_version)
        xform_xml = build_xform_xml(row, root_sheet.headers, instance_id, form_version)
        version_payload = {
            "mp_versionkey": version_key,
            "mp_instanceid": instance_id,
            "mp_versionnumber": 1,
            "mp_current": True,
            "mp_createdat": now,
            "mp_xformsubmissionxml": xform_xml,
            "mp_submissionjson": submission_json,
        }
        key, bind_value = client.bind("Submissions", "SubmissionVersions", "Submission", submission_id)
        version_payload[key] = bind_value
        _, action = client.ensure(
            "SubmissionVersions",
            f"mp_versionkey eq '{escape_odata(version_key)}'",
            version_payload,
        )
        counts["mp_SubmissionVersion"] += 1
        actions[f"mp_SubmissionVersion.{action}"] += 1

        tracked_payload = {
            "mp_entitytype": CHOICE["tracked_entity_type_beneficiary"],
            "mp_entitykey": source_key,
            "mp_displayname": display_name,
            "mp_status": CHOICE["tracked_entity_status_active"],
        }
        key, bind_value = client.bind("Projects", "TrackedEntities", "Project", project_id)
        tracked_payload[key] = bind_value
        tracked_id, action = client.ensure(
            "TrackedEntities",
            (
                f"_mp_project_value eq {project_id} and mp_entitytype eq {CHOICE['tracked_entity_type_beneficiary']} "
                f"and mp_entitykey eq '{escape_odata(source_key)}'"
            ),
            tracked_payload,
        )
        counts["mp_TrackedEntity"] += 1
        actions[f"mp_TrackedEntity.{action}"] += 1

        identifiers = [
            ("source_uuid", CHOICE["identifier_source_record"], uuid),
            ("customer_id", CHOICE["identifier_customer_id"], customer_id),
            ("phone", CHOICE["identifier_phone"], phone),
        ]
        for label, identifier_type, identifier_value in identifiers:
            if not identifier_value:
                continue
            identifier_payload = {
                "mp_identifiertype": identifier_type,
                "mp_identifiervalue": identifier_value,
                "mp_status": CHOICE["identifier_status_active"],
            }
            key, bind_value = client.bind("TrackedEntities", "EntityIdentifiers", "TrackedEntity", tracked_id)
            identifier_payload[key] = bind_value
            _, action = client.ensure(
                "EntityIdentifiers",
                (
                    f"_mp_trackedentity_value eq {tracked_id} and mp_identifiertype eq {identifier_type} "
                    f"and mp_identifiervalue eq '{escape_odata(identifier_value)}'"
                ),
                identifier_payload,
            )
            counts["mp_EntityIdentifier"] += 1
            counts[f"identifier.{label}"] += 1
            actions[f"mp_EntityIdentifier.{action}"] += 1

        profile_payload = {
            "mp_name": display_name,
            "mp_beneficiarycategory": CHOICE["beneficiary_category_individual_farmer"],
            "mp_region": region or None,
            "mp_district": district or None,
            "mp_verificationstatus": CHOICE["beneficiary_verification_under_review"],
            "mp_datasource": "Kobo baseline import",
            "mp_lastupdatedat": now,
        }
        key, bind_value = client.bind("TrackedEntities", "BeneficiaryProfiles", "TrackedEntity", tracked_id)
        profile_payload[key] = bind_value
        key, bind_value = client.bind("Projects", "BeneficiaryProfiles", "Project", project_id)
        profile_payload[key] = bind_value
        _, action = client.ensure(
            "BeneficiaryProfiles",
            f"_mp_trackedentity_value eq {tracked_id}",
            {k: v for k, v in profile_payload.items() if v is not None},
        )
        counts["mp_BeneficiaryProfile"] += 1
        actions[f"mp_BeneficiaryProfile.{action}"] += 1

        link_payload = {
            "mp_linkkey": link_key,
            "mp_relationshiptype": CHOICE["submission_link_relationship_baseline"],
            "mp_completeness": 100,
            "mp_reviewstatus": CHOICE["submission_link_review_under_review"],
        }
        key, bind_value = client.bind("TrackedEntities", "BeneficiarySubmissionLinks", "TrackedEntity", tracked_id)
        link_payload[key] = bind_value
        key, bind_value = client.bind("Submissions", "BeneficiarySubmissionLinks", "Submission", submission_id)
        link_payload[key] = bind_value
        _, action = client.ensure(
            "BeneficiarySubmissionLinks",
            f"mp_linkkey eq '{escape_odata(link_key)}'",
            link_payload,
        )
        counts["mp_BeneficiarySubmissionLink"] += 1
        actions[f"mp_BeneficiarySubmissionLink.{action}"] += 1

    return {
        "status": "executed",
        "target": settings.deploy_target,
        "environment_url": settings.environment_url,
        "rows_processed": len(rows),
        "limit": args.limit,
        "counts": dict(sorted(counts.items())),
        "actions": dict(sorted(actions.items())),
        "duplicate_review": {
            "policy": "review_only_no_auto_merge",
            "groups": len(duplicate_groups),
            "row_memberships": sum(group["row_count"] for group in duplicate_groups),
        },
        "safety": {
            "raw_pii_in_output": False,
            "raw_payload_rows_in_output": False,
        },
    }


def main() -> int:
    args = parse_args()
    if args.mode == "execute":
        report = import_rows(args)
    elif args.mode == "package-asset":
        report = build_package_asset(args)
    else:
        report = build_report(args)
    output = Path(args.output_json).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.summary_json:
        summary_path = Path(args.summary_json).expanduser().resolve()
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.mode == "dry-run":
        print("Baseline bridge import payload dry-run written.")
    elif args.mode == "package-asset":
        print("Baseline bridge package asset written.")
    else:
        print("Baseline bridge import executed.")
    print(f"Output: {output}")
    if args.mode == "dry-run":
        print(f"Root rows: {report['payload_counts']['mp_Submission']}")
        print(f"EntityIdentifier rows planned: {report['payload_counts']['mp_EntityIdentifier']}")
        print(f"Duplicate review groups: {report['payload_counts']['duplicate_review_groups']}")
        print("No Dataverse writes performed.")
    elif args.mode == "package-asset":
        print(f"Rows packaged: {report['counts']['rows']}")
        print(
            "EntityIdentifier rows packaged: "
            f"{report['counts']['sourceUuidIdentifiers'] + report['counts']['customerIdIdentifiers'] + report['counts']['phoneIdentifiers']}"
        )
        print(f"Duplicate review groups: {report['counts']['duplicateReviewGroups']}")
        print("Raw row values are stored only in the generated package asset; do not commit it.")
    else:
        print(f"Rows processed: {report['rows_processed']}")
        print(f"EntityIdentifier rows written/updated: {report['counts'].get('mp_EntityIdentifier', 0)}")
        print("Raw PII not printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
