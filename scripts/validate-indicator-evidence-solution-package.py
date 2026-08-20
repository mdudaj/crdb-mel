#!/usr/bin/env python3
"""Validate an unpacked or zipped indicator/evidence solution package."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree


TABLES = [
    "mp_IndicatorDefinition",
    "mp_DataSourceMapping",
    "mp_Observation",
    "mp_IndicatorResult",
    "mp_Evidence",
]

RELATIONSHIPS = [
    "mp_Project_mp_IndicatorDefinition_mp_Project",
    "mp_Project_mp_DataSourceMapping_mp_Project",
    "mp_IndicatorDefinition_mp_DataSourceMapping_mp_IndicatorDefinition",
    "mp_Project_mp_Observation_mp_Project",
    "mp_TrackedEntity_mp_Observation_mp_TrackedEntity",
    "mp_Submission_mp_Observation_mp_Submission",
    "mp_SubmissionReportRow_mp_Observation_mp_SubmissionReportRow",
    "mp_DataSourceMapping_mp_Observation_mp_DataSourceMapping",
    "mp_Project_mp_Evidence_mp_Project",
    "mp_Observation_mp_Evidence_mp_Observation",
    "mp_IndicatorResult_mp_Evidence_mp_IndicatorResult",
    "mp_Submission_mp_Evidence_mp_Submission",
    "mp_Project_mp_IndicatorResult_mp_Project",
    "mp_IndicatorDefinition_mp_IndicatorResult_mp_IndicatorDefinition",
    "mp_TrackedEntity_mp_IndicatorResult_mp_TrackedEntity",
]

ALT_KEYS = {
    "mp_IndicatorDefinition": "AK_IndicatorDefinition_Project_Code",
    "mp_DataSourceMapping": "AK_DataSourceMapping_Key",
    "mp_Observation": "AK_Observation_Key",
    "mp_Evidence": "AK_Evidence_Key",
    "mp_IndicatorResult": "AK_IndicatorResult_Key",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Unpacked solution src directory or packed solution zip.")
    return parser.parse_args()


def read_from_dir(path: Path, relative: str) -> str:
    return (path / relative).read_text(encoding="utf-8-sig")


def read_from_zip(path: Path, relative: str) -> str:
    with zipfile.ZipFile(path) as archive:
        return archive.read(relative).decode("utf-8-sig")


def list_zip(path: Path) -> set[str]:
    with zipfile.ZipFile(path) as archive:
        return set(archive.namelist())


def validate_reader(path: Path, names: set[str], reader) -> list[str]:
    errors: list[str] = []
    flattened_zip = "customizations.xml" in names and "solution.xml" in names
    if flattened_zip:
        customizations_xml = reader("customizations.xml")
        for table in TABLES:
            for fragment in [table, table.lower(), ALT_KEYS[table], f"{table.lower()}id"]:
                if fragment not in customizations_xml:
                    errors.append(f"customizations.xml missing {fragment}")
        relationships_text = customizations_xml
        solution_xml = reader("solution.xml")
    else:
        for table in TABLES:
            entity_path = f"Entities/{table}/Entity.xml"
            if entity_path not in names:
                errors.append(f"missing entity xml: {table}")
                continue
            text = reader(entity_path)
            for fragment in [table, table.lower(), ALT_KEYS[table], f"{table.lower()}id"]:
                if fragment not in text:
                    errors.append(f"{entity_path} missing {fragment}")

        solution_xml = reader("Other/Solution.xml")
        relationships_text = ""
        for name in names:
            if name.startswith("Other/Relationships/") and name.endswith(".xml"):
                relationships_text += "\n" + reader(name)

    for table in TABLES:
        if f'schemaName="{table.lower()}"' not in solution_xml:
            errors.append(f"Solution.xml missing root component for {table}")

    relationships_index = relationships_text if flattened_zip else reader("Other/Relationships.xml")
    for relationship in RELATIONSHIPS:
        if relationship not in relationships_index:
            errors.append(f"Relationships.xml missing {relationship}")
        if relationship not in relationships_text:
            errors.append(f"relationship file missing {relationship}")

    for forbidden in [
        "mp_TACATDPIndicator",
        "mp_TACATDPEvidence",
        "Webapi/mp_evidence/fields=*",
    ]:
        if forbidden in solution_xml or forbidden in relationships_text:
            errors.append(f"forbidden package fragment: {forbidden}")

    return errors


def main() -> int:
    path = Path(parse_args().path).resolve()
    if path.is_dir():
        names = {str(item.relative_to(path)) for item in path.rglob("*") if item.is_file()}
        errors = validate_reader(path, names, lambda relative: read_from_dir(path, relative))
    elif path.is_file() and path.suffix.lower() == ".zip":
        names = list_zip(path)
        errors = validate_reader(path, names, lambda relative: read_from_zip(path, relative))
    else:
        raise SystemExit(f"Expected solution src directory or zip: {path}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Indicator/evidence solution package validation passed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
