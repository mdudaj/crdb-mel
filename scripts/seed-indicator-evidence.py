#!/usr/bin/env python3
"""Seed TACATDP indicator definitions and source mappings.

This command is intentionally narrow:
- Mshirika/dev target only by default;
- explicit --execute required for writes;
- writes only mp_IndicatorDefinition and mp_DataSourceMapping;
- no indicator result, observation, evidence, Power Pages setting, or table-permission writes.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shlex
import subprocess
import sys
from collections import Counter
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote


CHOICE = {
    "indicator_type": {
        "Financial": 100000000,
        "Output": 100000001,
        "Outcome": 100000002,
        "ClimateImpactEstimate": 100000003,
        "OperationalDataQuality": 100000004,
    },
    "result_level": {
        "Programme": 100000000,
        "Component": 100000001,
        "Outcome": 100000002,
        "Output": 100000003,
        "Activity": 100000004,
        "Operational": 100000005,
    },
    "reporting_frequency": {
        "OnDemand": 100000000,
        "Weekly": 100000001,
        "Monthly": 100000002,
        "Quarterly": 100000003,
        "Seasonal": 100000004,
        "Annual": 100000005,
        "Baseline": 100000006,
        "Endline": 100000007,
    },
    "definition_status": {
        "Draft": 100000000,
        "Active": 100000001,
        "Retired": 100000002,
    },
    "source_type": {
        "XFormField": 100000000,
        "ImportedFileColumn": 100000001,
        "DataverseTable": 100000002,
        "PowerAutomateFlow": 100000003,
        "PowerBIModel": 100000004,
        "ExternalIntegration": 100000005,
    },
    "yes_no_choice": {
        False: 100000000,
        True: 100000001,
    },
}


TABLE_LOGICAL = {
    "Project": "mp_project",
    "IndicatorDefinition": "mp_indicatordefinition",
    "DataSourceMapping": "mp_datasourcemapping",
}

RELATIONSHIPS = {
    ("Project", "IndicatorDefinition", "Project"): "mp_Project_mp_IndicatorDefinition_mp_Project",
    ("Project", "DataSourceMapping", "Project"): "mp_Project_mp_DataSourceMapping_mp_Project",
    (
        "IndicatorDefinition",
        "DataSourceMapping",
        "IndicatorDefinition",
    ): "mp_IndicatorDefinition_mp_DataSourceMapping_mp_IndicatorDefinition",
}


def load_deploy_module(repo_root: Path) -> Any:
    module_path = repo_root / "scripts/dataverse-schema-deploy.py"
    spec = importlib.util.spec_from_file_location("dataverse_schema_deploy", module_path)
    if not spec or not spec.loader:
        raise SystemExit(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["dataverse_schema_deploy"] = module
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-file", default="schemas/dataverse/indicator-evidence-seed.json")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--project-code", default=None)
    parser.add_argument("--output-json", default=None, help="Optional sanitized summary output path.")
    parser.add_argument("--execute", action="store_true", help="Perform live writes. Without this flag only validates and prints a plan.")
    parser.add_argument("--allow-non-mshirika", action="store_true", help="Permit non-Mshirika dev targets for local admin testing.")
    return parser.parse_args()


def load_settings(deploy: Any, env_file: str, repo_root: Path) -> Any:
    env_path = Path(env_file).expanduser()
    if not env_path.is_absolute():
        env_path = repo_root / env_path
    env: dict[str, str] = {}
    if env_path.exists():
        env = deploy.load_env(env_path)

    environment_url = (env.get("POWER_PLATFORM_ENVIRONMENT_URL") or os.environ.get("POWER_PLATFORM_ENVIRONMENT_URL") or "").rstrip("/")
    tenant_id = env.get("POWER_PLATFORM_TENANT_ID") or os.environ.get("POWER_PLATFORM_TENANT_ID") or os.environ.get("TACATDP_POWERPLATFORM_TENANT_ID") or ""
    if not environment_url:
        raise SystemExit("Missing POWER_PLATFORM_ENVIRONMENT_URL. Source scripts/use-powerplatform-env.sh mshirika first.")
    if not tenant_id:
        raise SystemExit("Missing POWER_PLATFORM_TENANT_ID. Source scripts/use-powerplatform-env.sh mshirika first.")

    return deploy.Settings(
        tenant_id=tenant_id,
        client_id=env.get("POWER_PLATFORM_CLIENT_ID") or os.environ.get("POWER_PLATFORM_CLIENT_ID", ""),
        client_secret=env.get("POWER_PLATFORM_CLIENT_SECRET") or os.environ.get("POWER_PLATFORM_CLIENT_SECRET", ""),
        environment_url=environment_url,
        solution_unique_name=env.get("POWER_PLATFORM_SOLUTION_UNIQUE_NAME") or os.environ.get("POWER_PLATFORM_SOLUTION_UNIQUE_NAME") or "tacatdp_prototype",
        solution_display_name=env.get("POWER_PLATFORM_SOLUTION_DISPLAY_NAME") or os.environ.get("POWER_PLATFORM_SOLUTION_DISPLAY_NAME") or "tacatdp_prototype",
        publisher_name=env.get("POWER_PLATFORM_PUBLISHER_NAME") or os.environ.get("POWER_PLATFORM_PUBLISHER_NAME") or "TACATDP",
        publisher_prefix=env.get("POWER_PLATFORM_PUBLISHER_PREFIX") or os.environ.get("POWER_PLATFORM_PUBLISHER_PREFIX") or "mp",
        deploy_target=env.get("TACATDP_DEPLOY_TARGET") or os.environ.get("TACATDP_DEPLOY_TARGET") or "dev",
        schema_dir=Path(env.get("TACATDP_DATAVERSE_SCHEMA_DIR") or os.environ.get("TACATDP_DATAVERSE_SCHEMA_DIR") or "schemas/dataverse").resolve(),
        schema_file=Path(env.get("TACATDP_DATAVERSE_SCHEMA_FILE") or os.environ.get("TACATDP_DATAVERSE_SCHEMA_FILE") or "schemas/dataverse/mvp-schema-definition.json").resolve(),
    )


def get_token(deploy: Any, settings: Any) -> str:
    token_command = os.environ.get("POWER_PLATFORM_ACCESS_TOKEN_COMMAND", "").strip()
    if token_command:
        result = subprocess.run(shlex.split(token_command), check=True, capture_output=True, text=True)
        token = result.stdout.strip()
        if not token:
            raise SystemExit("POWER_PLATFORM_ACCESS_TOKEN_COMMAND returned an empty token.")
        return token

    if settings.client_id and settings.client_secret:
        return deploy.get_token(settings)

    auth_mode = os.environ.get("POWER_PLATFORM_AUTH_MODE", "").strip().lower()
    if auth_mode == "azurecli":
        result = subprocess.run(
            [
                "az",
                "account",
                "get-access-token",
                "--resource",
                settings.environment_url,
                "--query",
                "accessToken",
                "-o",
                "tsv",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        token = result.stdout.strip()
        if not token:
            raise SystemExit("Azure CLI returned an empty Dataverse access token.")
        return token

    raise SystemExit("No Dataverse token source configured. Use Azure CLI login, POWER_PLATFORM_ACCESS_TOKEN_COMMAND, or client credentials.")


def escape_odata(value: str) -> str:
    return value.replace("'", "''")


def parse_guid_from_entity_id(value: str) -> str:
    return value.rsplit("(", 1)[-1].rstrip(")")


class SeedClient:
    def __init__(self, deploy: Any, settings: Any, token: str) -> None:
        self.deploy = deploy
        self.settings = settings
        self.dv = deploy.Dataverse(settings, token)
        self.entity_sets: dict[str, str] = {}
        self.primary_ids: dict[str, str] = {}
        self.nav_properties: dict[str, str] = {}
        self.attribute_types: dict[tuple[str, str], str] = {}

    def entity_set(self, table: str) -> str:
        if table not in self.entity_sets:
            logical = TABLE_LOGICAL[table]
            data = self.dv.get_json(f"EntityDefinitions(LogicalName='{logical}')?$select=EntitySetName,PrimaryIdAttribute")
            if not data:
                raise RuntimeError(f"Missing table metadata: {logical}")
            self.entity_sets[table] = data["EntitySetName"]
            self.primary_ids[table] = data["PrimaryIdAttribute"]
        return self.entity_sets[table]

    def primary_id(self, table: str) -> str:
        self.entity_set(table)
        return self.primary_ids[table]

    def column(self, name: str) -> str:
        return name.lower()

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
            if not data:
                raise RuntimeError(f"Missing relationship navigation metadata: {relationship_schema}")
            self.nav_properties[relationship_schema] = data["ReferencingEntityNavigationPropertyName"]
        return self.nav_properties[relationship_schema]

    def bind(self, referenced: str, referencing: str, lookup: str, record_id: str) -> tuple[str, str]:
        schema = RELATIONSHIPS[(referenced, referencing, lookup)]
        return f"{self.nav_property(schema)}@odata.bind", f"/{self.entity_set(referenced)}({record_id})"

    def attribute_type(self, table: str, attribute: str) -> str:
        key = (table, attribute)
        if key not in self.attribute_types:
            logical = TABLE_LOGICAL[table]
            data = self.dv.get_json(
                f"EntityDefinitions(LogicalName='{logical}')/Attributes(LogicalName='{attribute}')?$select=AttributeType"
            )
            if not data:
                raise RuntimeError(f"Missing attribute metadata: {logical}.{attribute}")
            self.attribute_types[key] = data["AttributeType"]
        return self.attribute_types[key]

    def yes_no(self, table: str, attribute: str, value: bool) -> bool | int:
        attr_type = self.attribute_type(table, attribute)
        if attr_type == "Boolean":
            return bool(value)
        if attr_type in {"Picklist", "Virtual"}:
            return CHOICE["yes_no_choice"][bool(value)]
        raise RuntimeError(f"Unsupported yes/no attribute type for {table}.{attribute}: {attr_type}")

    def find_one(self, table: str, filter_expr: str, select_extra: str = "") -> dict[str, Any] | None:
        primary = self.primary_id(table)
        select = primary if not select_extra else f"{primary},{select_extra}"
        data = self.dv.get_json(f"{self.entity_set(table)}?$select={select}&$filter={filter_expr}&$top=1")
        rows = (data or {}).get("value") or []
        return rows[0] if rows else None

    def create(self, table: str, payload: dict[str, Any]) -> str:
        response = self.dv.post(self.entity_set(table), payload)
        return parse_guid_from_entity_id(response.headers.get("OData-EntityId", ""))

    def update(self, table: str, record_id: str, payload: dict[str, Any]) -> None:
        response = self.dv.request("PATCH", f"{self.entity_set(table)}({record_id})", payload=payload)
        if response.status_code >= 400:
            raise RuntimeError(f"PATCH {table} failed: HTTP {response.status_code} {self.deploy.safe_error(response)}")

    def ensure(self, table: str, filter_expr: str, payload: dict[str, Any], *, execute: bool, label: str) -> tuple[str | None, str]:
        primary = self.primary_id(table)
        existing = self.find_one(table, filter_expr)
        if existing:
            record_id = existing[primary]
            if execute:
                self.update(table, record_id, payload)
                print(f"updated: {label}")
                return record_id, "updated"
            print(f"would update: {label}")
            return record_id, "would_update"
        if execute:
            record_id = self.create(table, payload)
            print(f"created: {label}")
            return record_id, "created"
        print(f"would create: {label}")
        return None, "would_create"

    def required_project_id(self, project_code: str) -> str:
        row = self.find_one("Project", f"mp_projectcode eq '{escape_odata(project_code)}'")
        if not row:
            raise RuntimeError(f"Project not found by mp_projectcode: {project_code}")
        return row[self.primary_id("Project")]

    def count_by_codes(self, codes: list[str]) -> int:
        if not codes:
            return 0
        clauses = " or ".join([f"mp_code eq '{escape_odata(code)}'" for code in codes])
        data = self.dv.get_json(f"{self.entity_set('IndicatorDefinition')}?$select=mp_code&$filter={clauses}")
        return len((data or {}).get("value") or [])

    def count_by_mapping_keys(self, mapping_keys: list[str]) -> int:
        if not mapping_keys:
            return 0
        clauses = " or ".join([f"mp_mappingkey eq '{escape_odata(key)}'" for key in mapping_keys])
        data = self.dv.get_json(f"{self.entity_set('DataSourceMapping')}?$select=mp_mappingkey&$filter={clauses}")
        return len((data or {}).get("value") or [])


def definition_payload(client: SeedClient, definition: dict[str, Any], project_id: str) -> dict[str, Any]:
    payload = {
        "mp_name": definition["name"],
        "mp_code": definition["code"],
        "mp_description": definition.get("description") or None,
        "mp_indicatortype": CHOICE["indicator_type"][definition["indicator_type"]],
        "mp_resultlevel": CHOICE["result_level"][definition["result_level"]],
        "mp_unit": definition["unit"],
        "mp_formula": definition.get("formula") or None,
        "mp_numerator": definition.get("numerator") or None,
        "mp_denominator": definition.get("denominator") or None,
        "mp_reportingfrequency": CHOICE["reporting_frequency"][definition["reporting_frequency"]],
        "mp_disaggregationjson": json.dumps(definition.get("disaggregation") or [], ensure_ascii=False),
        "mp_datasourcemappingjson": json.dumps(
            [
                {
                    "mapping_key": item["mapping_key"],
                    "source_type": item["source_type"],
                    "source_table": item.get("source_table") or "",
                    "source_column": item.get("source_column") or "",
                    "source_path": item.get("source_path") or "",
                }
                for item in definition.get("mappings", [])
            ],
            ensure_ascii=False,
        ),
        "mp_verificationmethod": definition.get("verification_method") or None,
        "mp_responsibleunit": definition.get("responsible_unit") or None,
        "mp_reportingframework": definition.get("reporting_framework") or None,
        "mp_status": CHOICE["definition_status"][definition["status"]],
    }
    key, value = client.bind("Project", "IndicatorDefinition", "Project", project_id)
    payload[key] = value
    return {key: value for key, value in payload.items() if value is not None}


def mapping_payload(client: SeedClient, mapping: dict[str, Any], definition_id: str, project_id: str) -> dict[str, Any]:
    payload = {
        "mp_mappingkey": mapping["mapping_key"],
        "mp_sourcetype": CHOICE["source_type"][mapping["source_type"]],
        "mp_sourcetable": mapping.get("source_table") or None,
        "mp_sourcecolumn": mapping.get("source_column") or None,
        "mp_sourcepath": mapping.get("source_path") or None,
        "mp_transformrule": mapping.get("transform_rule") or None,
        "mp_required": client.yes_no("DataSourceMapping", "mp_required", bool(mapping.get("required"))),
        "mp_active": client.yes_no("DataSourceMapping", "mp_active", bool(mapping.get("active"))),
        "mp_notes": mapping.get("notes") or None,
    }
    key, value = client.bind("Project", "DataSourceMapping", "Project", project_id)
    payload[key] = value
    key, value = client.bind("IndicatorDefinition", "DataSourceMapping", "IndicatorDefinition", definition_id)
    payload[key] = value
    return {key: value for key, value in payload.items() if value is not None}


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    seed_path = Path(args.seed_file)
    if not seed_path.is_absolute():
        seed_path = repo_root / seed_path
    seed = json.loads(seed_path.read_text(encoding="utf-8"))

    deploy = load_deploy_module(repo_root)
    settings = load_settings(deploy, args.env_file, repo_root)
    project_code = args.project_code or seed["target_project_code"]
    target_name = os.environ.get("TACATDP_POWERPLATFORM_TARGET", "")

    print("# Indicator evidence seed")
    print(f"Mode: {'execute' if args.execute else 'dry-run'}")
    print(f"Target: {target_name or settings.deploy_target}")
    print(f"Environment: {settings.environment_url}")
    print(f"Project code: {project_code}")
    print(f"Seed file: {seed_path.relative_to(repo_root)}")

    if settings.deploy_target.lower() != "dev":
        raise SystemExit(f"Refusing non-dev deployment target: {settings.deploy_target}")
    if target_name and target_name != "mshirika" and not args.allow_non_mshirika:
        raise SystemExit(f"Refusing non-Mshirika target without --allow-non-mshirika: {target_name}")
    if not args.execute:
        print("Dry-run only. Re-run with --execute to seed Dataverse rows.")

    token = get_token(deploy, settings)
    client = SeedClient(deploy, settings, token)
    project_id = client.required_project_id(project_code)

    counts: Counter[str] = Counter()
    actions: Counter[str] = Counter()
    indicator_ids: dict[str, str] = {}

    for definition in seed["indicator_definitions"]:
        code = definition["code"]
        payload = definition_payload(client, definition, project_id)
        record_id, action = client.ensure(
            "IndicatorDefinition",
            f"_mp_project_value eq {project_id} and mp_code eq '{escape_odata(code)}'",
            payload,
            execute=args.execute,
            label=f"indicator {code}",
        )
        counts["mp_IndicatorDefinition"] += 1
        actions[f"mp_IndicatorDefinition.{action}"] += 1
        indicator_ids[code] = record_id or f"DRY-RUN-{code}"

    for definition in seed["indicator_definitions"]:
        definition_id = indicator_ids[definition["code"]]
        if definition_id.startswith("DRY-RUN-"):
            continue
        for mapping in definition["mappings"]:
            payload = mapping_payload(client, mapping, definition_id, project_id)
            _, action = client.ensure(
                "DataSourceMapping",
                f"mp_mappingkey eq '{escape_odata(mapping['mapping_key'])}'",
                payload,
                execute=args.execute,
                label=f"mapping {mapping['mapping_key']}",
            )
            counts["mp_DataSourceMapping"] += 1
            actions[f"mp_DataSourceMapping.{action}"] += 1

    codes = [definition["code"] for definition in seed["indicator_definitions"]]
    mapping_keys = [mapping["mapping_key"] for definition in seed["indicator_definitions"] for mapping in definition["mappings"]]
    readback = {
        "indicator_definitions_found": client.count_by_codes(codes),
        "data_source_mappings_found": client.count_by_mapping_keys(mapping_keys),
    }

    summary = {
        "status": "executed" if args.execute else "dry_run",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "target": target_name or settings.deploy_target,
        "environment_url": settings.environment_url,
        "project_code": project_code,
        "seed_file": str(seed_path.relative_to(repo_root)),
        "counts": dict(sorted(counts.items())),
        "actions": dict(sorted(actions.items())),
        "readback": readback,
        "writes_performed": bool(args.execute),
        "raw_pii_in_output": False,
    }

    if args.output_json:
        output_path = Path(args.output_json).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Summary: {output_path}")

    print(f"Indicator definitions matched: {readback['indicator_definitions_found']} / {len(codes)}")
    print(f"Data source mappings matched: {readback['data_source_mappings_found']} / {len(mapping_keys)}")
    print("Raw PII not printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
