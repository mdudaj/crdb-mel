#!/usr/bin/env python3
"""Generate Dataverse solution source for the approved indicator/evidence schema.

This script performs no network calls. It patches an exported/unpacked
Power Platform solution source by adding the approved indicator/evidence tables,
relationships, alternate keys, and solution root components.

It intentionally reuses the XML generation conventions from
generate-beneficiary-bridge-solution-patch.py because that path has already
been validated and deployed successfully in Mshirika.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Existing unpacked solution source folder.")
    parser.add_argument("--output", required=True, help="Output unpacked solution source folder. Must be under /tmp.")
    parser.add_argument("--repo-root", default=".", help="Repository root for schema artifacts.")
    parser.add_argument("--schema-file", default="schemas/dataverse/indicator-evidence-schema.json", help="Approved schema JSON.")
    parser.add_argument("--version", default="0.2.6.0", help="Solution version to write.")
    return parser.parse_args()


def load_bridge_generator(repo_root: Path):
    module_path = repo_root / "scripts" / "generate-beneficiary-bridge-solution-patch.py"
    spec = importlib.util.spec_from_file_location("beneficiary_bridge_generator", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load generator module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_column(column: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(column)
    column_type = str(normalized.get("type", ""))
    if column_type == "TwoOptions":
        normalized["type"] = "Choice"
        normalized["choices"] = ["No", "Yes"]
        normalized["notes"] = (
            f"{normalized.get('notes', '').strip()} "
            "Implemented as a local two-value choice in the PAC solution package path; "
            "the logical schema remains a two-options flag."
        ).strip()
    return normalized


def schema_relationship_name(bridge, relationship: dict[str, Any]) -> str:
    referenced = bridge.schema_part(relationship["referenced_table"])
    referencing = bridge.schema_part(relationship["referencing_table"])
    lookup = bridge.schema_part(relationship["lookup_column"])
    return f"{referenced}_{referencing}_{lookup}"


def prepare_bridge_globals(bridge, schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tables = [table["name"] for table in schema["tables"]]
    table_defs = {table["name"]: table for table in schema["tables"]}
    bridge.PHYSICAL_NAME_OVERRIDES = {
        **bridge.PHYSICAL_NAME_OVERRIDES,
        "mp_Project": "mp_Project",
        "mp_TrackedEntity": "mp_TrackedEntity",
        "mp_Submission": "mp_Submission",
        "mp_SubmissionReportRow": "mp_SubmissionReportRow",
        "mp_IndicatorDefinition": "mp_IndicatorDefinition",
        "mp_indicatordefinition": "mp_IndicatorDefinition",
        "mp_indicatordefinitionid": "mp_IndicatorDefinitionId",
        "mp_DataSourceMapping": "mp_DataSourceMapping",
        "mp_datasourcemapping": "mp_DataSourceMapping",
        "mp_datasourcemappingid": "mp_DataSourceMappingId",
        "mp_Observation": "mp_Observation",
        "mp_observation": "mp_Observation",
        "mp_observationid": "mp_ObservationId",
        "mp_Evidence": "mp_Evidence",
        "mp_evidence": "mp_Evidence",
        "mp_evidenceid": "mp_EvidenceId",
        "mp_IndicatorResult": "mp_IndicatorResult",
        "mp_indicatorresult": "mp_IndicatorResult",
        "mp_indicatorresultid": "mp_IndicatorResultId",
        "mp_indicatortype": "mp_IndicatorType",
        "mp_resultlevel": "mp_ResultLevel",
        "mp_reportingfrequency": "mp_ReportingFrequency",
        "mp_disaggregationjson": "mp_DisaggregationJson",
        "mp_datasourcemappingjson": "mp_DataSourceMappingJson",
        "mp_verificationmethod": "mp_VerificationMethod",
        "mp_responsibleunit": "mp_ResponsibleUnit",
        "mp_reportingframework": "mp_ReportingFramework",
        "mp_mappingkey": "mp_MappingKey",
        "mp_sourcetype": "mp_SourceType",
        "mp_sourcetable": "mp_SourceTable",
        "mp_sourcecolumn": "mp_SourceColumn",
        "mp_sourcepath": "mp_SourcePath",
        "mp_transformrule": "mp_TransformRule",
        "mp_observationkey": "mp_ObservationKey",
        "mp_submissionreportrow": "mp_SubmissionReportRow",
        "mp_observedat": "mp_ObservedAt",
        "mp_reportingperiod": "mp_ReportingPeriod",
        "mp_valuedecimal": "mp_ValueDecimal",
        "mp_valuetext": "mp_ValueText",
        "mp_qualitystatus": "mp_QualityStatus",
        "mp_sourcepayloadref": "mp_SourcePayloadRef",
        "mp_evidencekey": "mp_EvidenceKey",
        "mp_evidencetype": "mp_EvidenceType",
        "mp_uriorfilereference": "mp_UriOrFileReference",
        "mp_capturedat": "mp_CapturedAt",
        "mp_capturedby": "mp_CapturedBy",
        "mp_gpslatitude": "mp_GpsLatitude",
        "mp_gpslongitude": "mp_GpsLongitude",
        "mp_resultkey": "mp_ResultKey",
        "mp_verificationstatus": "mp_VerificationStatus",
        "mp_sourcesummaryjson": "mp_SourceSummaryJson",
        "mp_calculatedat": "mp_CalculatedAt",
        "mp_calculatedby": "mp_CalculatedBy",
    }

    choices: dict[str, list[str]] = {}
    for table in schema["tables"]:
        for column in table.get("columns", []):
            if column.get("type") == "Choice":
                choices[column["name"]] = list(column.get("choices") or ["Active", "Inactive"])
            elif column.get("type") == "TwoOptions":
                choices[column["name"]] = ["No", "Yes"]

    alt_keys: dict[str, tuple[str, list[str]]] = {}
    for key in schema.get("alternate_keys", []):
        alt_keys[key["table"]] = (key["name"], list(key.get("columns") or []))

    relationships: list[dict[str, str]] = []
    for relationship in schema.get("relationships", []):
        relationships.append(
            {
                "referenced_table": relationship["referenced_table"],
                "referencing_table": relationship["referencing_table"],
                "lookup_column": relationship["lookup_column"],
                "schema_name": schema_relationship_name(bridge, relationship),
                "notes": relationship.get("notes") or relationship["lookup_column"],
                "delete": "RemoveLink",
            }
        )

    text_lengths = {
        "mp_code": 100,
        "mp_name": 300,
        "mp_unit": 80,
        "mp_reportingperiod": 80,
        "mp_geography": 160,
        "mp_responsibleunit": 160,
        "mp_reportingframework": 120,
        "mp_mappingkey": 200,
        "mp_sourcetable": 160,
        "mp_sourcecolumn": 160,
        "mp_sourcepath": 300,
        "mp_observationkey": 200,
        "mp_sourcepayloadref": 300,
        "mp_evidencekey": 200,
        "mp_title": 300,
        "mp_uriorfilereference": 500,
        "mp_hash": 160,
        "mp_capturedby": 200,
        "mp_resultkey": 250,
        "mp_calculatedby": 200,
    }

    bridge.TABLES = tables
    bridge.RELATIONSHIPS = relationships
    bridge.CHOICES = {**bridge.CHOICES, **choices}
    bridge.TEXT_LENGTHS = {**bridge.TEXT_LENGTHS, **text_lengths}
    bridge.ALT_KEYS = alt_keys
    return table_defs


def copy_source(source: Path, output: Path) -> None:
    if not str(output).startswith("/tmp/"):
        raise RuntimeError(f"Refusing to replace non-/tmp output path: {output}")
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(source, output)


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    schema_file = (repo_root / args.schema_file).resolve() if not Path(args.schema_file).is_absolute() else Path(args.schema_file)

    if not (source / "Other" / "Solution.xml").exists():
        raise SystemExit(f"Source is not an unpacked solution source: {source}")
    if not schema_file.exists():
        raise SystemExit(f"Schema file not found: {schema_file}")

    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    if schema.get("schema_name") != "indicator_evidence_schema":
        raise SystemExit(f"Unexpected schema file: {schema.get('schema_name')}")

    bridge = load_bridge_generator(repo_root)
    table_defs = prepare_bridge_globals(bridge, schema)

    copy_source(source, output)
    for table_name in bridge.TABLES:
        definition = table_defs[table_name]
        columns = [normalize_column(column) for column in definition["columns"]]
        bridge.build_entity_xml(source, output, table_name, definition, columns)

    bridge.patch_relationship_files(output)
    bridge.patch_solution_xml(output, args.version)
    errors = bridge.validate_output(output)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(
        json.dumps(
            {
                "status": "generated",
                "output": str(output),
                "schema_file": str(schema_file),
                "version": args.version,
                "tables": bridge.TABLES,
                "relationships": len(bridge.RELATIONSHIPS),
                "alternate_keys": len(bridge.ALT_KEYS),
                "writes_performed": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
