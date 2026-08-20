#!/usr/bin/env python3
"""Plan TACATDP Kobo baseline import without writing Dataverse or raw data.

This script inspects:
- the latest XLSForm workbook, used as the field-definition authority;
- the KoboToolbox XLSX export, used as the submitted baseline data source.

It emits a sanitized summary only. It must not print beneficiary names, phone
numbers, customer IDs, raw row values, tokens, or environment secrets.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from zipfile import ZipFile
import xml.etree.ElementTree as ET

SPREADSHEET_NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

STRUCTURAL_TYPES = {
    "begin_group",
    "end_group",
    "begin_repeat",
    "end_repeat",
    "note",
    "calculate",
    "start",
    "end",
    "deviceid",
    "phonenumber",
    "username",
    "subscriberid",
    "simserial",
}

PRIVACY_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bcustomer\b",
        r"\bphone\b",
        r"\bname\b",
        r"\bgender\b",
        r"\bage\b",
        r"\bward\b",
        r"\bvillage\b",
        r"\bgeo",
        r"\blocation\b",
    )
]

ROOT_IMPORT_TARGETS = [
    "existing mp_Project",
    "existing mp_Form",
    "existing mp_FormVersion",
    "existing mp_Submission",
    "existing mp_SubmissionVersion",
    "mp_TrackedEntity",
    "mp_EntityIdentifier",
    "mp_BeneficiaryProfile",
    "mp_BeneficiarySubmissionLink",
]


@dataclass(frozen=True)
class Sheet:
    name: str
    headers: list[str]
    rows: list[dict[int, str]]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def column_count(self) -> int:
        return len(self.headers)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xlsform", required=True, help="Latest XLSForm workbook path.")
    parser.add_argument("--workbook", required=True, help="KoboToolbox submitted-data XLSX export path.")
    parser.add_argument("--summary-json", required=True, help="Sanitized JSON summary output path. Use /tmp.")
    return parser.parse_args()


def column_index(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref)
    if not match:
        raise ValueError(f"Invalid cell reference: {cell_ref}")
    value = 0
    for char in match.group(1):
        value = value * 26 + ord(char) - 64
    return value - 1


def column_name(index: int) -> str:
    index += 1
    chars: list[str] = []
    while index:
        index, rem = divmod(index - 1, 26)
        chars.append(chr(65 + rem))
    return "".join(reversed(chars))


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).casefold()


def safe_field_key(sheet_name: str, column: int, header: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z]+", "_", header.strip()).strip("_").lower()
    return f"{sheet_name}:{column_name(column)}:{slug[:60] or 'blank'}"


def cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(text.text or "" for text in cell.findall(".//a:t", SPREADSHEET_NS)).strip()

    value = cell.find("a:v", SPREADSHEET_NS)
    if value is None:
        return ""

    raw = value.text or ""
    if cell_type == "s" and raw.isdigit() and int(raw) < len(shared_strings):
        return shared_strings[int(raw)].strip()
    return raw.strip()


def read_xlsx(path: Path) -> dict[str, Sheet]:
    with ZipFile(path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("a:si", SPREADSHEET_NS):
                shared_strings.append("".join(text.text or "" for text in item.findall(".//a:t", SPREADSHEET_NS)))

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relationship_targets = {rel.attrib["Id"]: rel.attrib["Target"] for rel in relationships}
        sheets: dict[str, Sheet] = {}

        for sheet_ref in workbook.findall("a:sheets/a:sheet", SPREADSHEET_NS):
            sheet_name = sheet_ref.attrib["name"]
            relationship_id = sheet_ref.attrib[
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            ]
            target = relationship_targets[relationship_id]
            sheet_path = f"xl/{target}" if not target.startswith("/") else target[1:]
            root = ET.fromstring(archive.read(sheet_path))
            raw_rows: list[dict[int, str]] = []

            for row in root.findall("a:sheetData/a:row", SPREADSHEET_NS):
                cells = {
                    column_index(cell.attrib["r"]): cell_value(cell, shared_strings)
                    for cell in row.findall("a:c", SPREADSHEET_NS)
                }
                raw_rows.append({key: value for key, value in cells.items() if value != ""})

            if not raw_rows:
                sheets[sheet_name] = Sheet(sheet_name, [], [])
                continue

            max_column = max((max(row.keys()) for row in raw_rows if row), default=-1)
            headers = [raw_rows[0].get(index, "") for index in range(max_column + 1)]
            sheets[sheet_name] = Sheet(sheet_name, headers, raw_rows[1:])

        return sheets


def row_value(row: dict[int, str], headers: list[str], field_name: str) -> str:
    for index, header in enumerate(headers):
        if header == field_name:
            return row.get(index, "")
    return ""


def xlsform_summary(sheets: dict[str, Sheet]) -> dict[str, Any]:
    survey = rows_by_header(sheets.get("survey"))
    choices = rows_by_header(sheets.get("choices"))
    settings_rows = rows_by_header(sheets.get("settings"))
    settings = settings_rows[0] if settings_rows else {}

    type_counts: Counter[str] = Counter()
    required_count = 0
    field_rows: list[dict[str, str]] = []
    repeats: list[dict[str, str]] = []
    label_index: dict[str, list[str]] = defaultdict(list)
    name_index: set[str] = set()

    for row in survey:
        raw_type = row.get("type", "")
        if not raw_type:
            continue
        base_type = raw_type.split()[0]
        name = row.get("name", "")
        label_en = row.get("label::English (en)", "")
        label_sw = row.get("label::Swahili (sw)", "")
        type_counts[base_type] += 1

        if row.get("required", "").casefold() == "true":
            required_count += 1

        if base_type == "begin_repeat":
            repeats.append(
                {
                    "name": name,
                    "label": label_en or label_sw,
                    "repeat_count": row.get("repeat_count", ""),
                    "relevant": row.get("relevant", ""),
                }
            )

        if name:
            name_index.add(name)
        for label in (label_en, label_sw, name):
            if label:
                label_index[normalize(label)].append(name)

        if name and base_type not in STRUCTURAL_TYPES:
            field_rows.append(
                {
                    "type": raw_type,
                    "base_type": base_type,
                    "name": name,
                    "label_en": label_en,
                    "label_sw": label_sw,
                    "required": row.get("required", ""),
                    "relevant": row.get("relevant", ""),
                }
            )

    choice_counts = Counter(row.get("list_name", "") for row in choices if row.get("list_name"))

    return {
        "settings": {
            "id_string": settings.get("id_string", ""),
            "version": settings.get("version", ""),
            "default_language": settings.get("default_language", ""),
            "background_geolocation": settings.get("background-geolocation", ""),
        },
        "survey_rows": len(survey),
        "choices_rows": len(choices),
        "type_counts": dict(sorted(type_counts.items())),
        "required_rows": required_count,
        "field_count": len(field_rows),
        "repeat_groups": repeats,
        "choice_list_count": len(choice_counts),
        "choice_rows_by_list": dict(sorted(choice_counts.items())),
        "_field_rows": field_rows,
        "_label_index": label_index,
        "_name_index": name_index,
    }


def rows_by_header(sheet: Sheet | None) -> list[dict[str, str]]:
    if sheet is None:
        return []
    rows: list[dict[str, str]] = []
    for row in sheet.rows:
        rows.append({sheet.headers[index]: value for index, value in row.items() if index < len(sheet.headers) and sheet.headers[index]})
    return rows


def export_summary(sheets: dict[str, Sheet], form: dict[str, Any]) -> dict[str, Any]:
    label_index: dict[str, list[str]] = form["_label_index"]
    name_index: set[str] = form["_name_index"]
    field_names = {row["name"] for row in form["_field_rows"]}
    mapped_field_names: set[str] = set()
    root_sheet_name = next(iter(sheets.keys()), "")

    sheet_summaries: dict[str, Any] = {}
    privacy_hits: Counter[str] = Counter()
    duplicate_header_counts: dict[str, int] = {}

    for sheet_name, sheet in sheets.items():
        header_counts = Counter(header for header in sheet.headers if header)
        duplicate_header_counts.update(
            {f"{sheet_name}:{header}": count for header, count in header_counts.items() if count > 1}
        )
        mapped_columns = 0
        ambiguous_columns = 0
        unmapped_columns = 0

        for index, header in enumerate(sheet.headers):
            if not header:
                continue

            if is_privacy_sensitive(header):
                privacy_hits[privacy_category(header)] += 1

            candidates: set[str] = set()
            if header in name_index:
                candidates.add(header)
            candidates.update(label_index.get(normalize(header), []))

            if len(candidates) == 1:
                mapped_columns += 1
                mapped_field_names.update(candidates)
            elif len(candidates) > 1:
                ambiguous_columns += 1
            else:
                # Treat ODK/Kobo system columns and one-hot choice exports as mappable to raw payload.
                if header.startswith("_") or "/" in header:
                    mapped_columns += 1
                else:
                    unmapped_columns += 1

        sheet_summaries[sheet_name] = {
            "rows": sheet.row_count,
            "columns": sheet.column_count,
            "mapped_or_raw_payload_columns": mapped_columns,
            "ambiguous_columns": ambiguous_columns,
            "unmapped_columns": unmapped_columns,
            "duplicate_header_labels": sum(1 for count in header_counts.values() if count > 1),
        }

    root_sheet = sheets.get(root_sheet_name)
    duplicate_identity = duplicate_identity_summary(root_sheet) if root_sheet else {}

    missing_form_fields = sorted(field_names - mapped_field_names)

    return {
        "root_sheet": root_sheet_name,
        "sheets": sheet_summaries,
        "mapped_form_fields": len(mapped_field_names),
        "xlsform_fields_missing_from_export": len(missing_form_fields),
        "missing_form_fields_sample": missing_form_fields[:50],
        "duplicate_header_label_instances": len(duplicate_header_counts),
        "privacy_sensitive_columns_detected": dict(sorted(privacy_hits.items())),
        "duplicate_identity_candidates": duplicate_identity,
    }


def duplicate_identity_summary(sheet: Sheet | None) -> dict[str, int]:
    if sheet is None:
        return {}
    headers = sheet.headers
    candidate_fields = {
        "customer_id": "Customer ID",
        "phone": "Farmer's Phone Number",
        "source_uuid": "_uuid",
    }
    summary: dict[str, int] = {}
    for label, header in candidate_fields.items():
        values = [row_value(row, headers, header) for row in sheet.rows]
        non_empty = [value for value in values if value]
        counts = Counter(non_empty)
        summary[f"{label}_non_empty"] = len(non_empty)
        summary[f"{label}_duplicate_values"] = sum(1 for value, count in counts.items() if value and count > 1)
        summary[f"{label}_rows_in_duplicate_groups"] = sum(count for value, count in counts.items() if value and count > 1)
    return summary


def is_privacy_sensitive(text: str) -> bool:
    return any(pattern.search(text) for pattern in PRIVACY_PATTERNS)


def privacy_category(text: str) -> str:
    lowered = text.casefold()
    if "phone" in lowered:
        return "phone"
    if "customer" in lowered:
        return "customer_identifier"
    if "name" in lowered:
        return "name"
    if "gender" in lowered:
        return "gender"
    if "age" in lowered:
        return "age"
    if "ward" in lowered or "village" in lowered or "geo" in lowered or "location" in lowered:
        return "location"
    return "other"


def build_summary(xlsform_path: Path, workbook_path: Path) -> dict[str, Any]:
    form_sheets = read_xlsx(xlsform_path)
    data_sheets = read_xlsx(workbook_path)
    form = xlsform_summary(form_sheets)
    data = export_summary(data_sheets, form)

    sanitized_form = {key: value for key, value in form.items() if not key.startswith("_")}

    return {
        "status": "dry_run_no_write",
        "inputs": {
            "xlsform_file": xlsform_path.name,
            "workbook_file": workbook_path.name,
        },
        "xlsform": sanitized_form,
        "kobo_export": data,
        "proposed_import_targets": ROOT_IMPORT_TARGETS,
        "first_slice_scope": {
            "use_existing_runtime_tables": [
                "mp_Project",
                "mp_Form",
                "mp_FormVersion",
                "mp_Submission",
                "mp_SubmissionVersion",
            ],
            "beneficiary_bridge_tables": [
                "mp_TrackedEntity",
                "mp_EntityIdentifier",
                "mp_BeneficiaryProfile",
                "mp_BeneficiarySubmissionLink",
            ],
            "deferred_projection_tables": [
                "mp_BeneficiaryFinanceLink",
                "mp_BeneficiaryTechnologyAdoption",
                "mp_BeneficiaryTrainingParticipation",
                "mp_BeneficiaryOutcomeSnapshot",
                "mp_BeneficiaryGroupMembership",
                "mp_BeneficiaryLocationHistory",
            ],
        },
        "privacy_rule": "Summary intentionally excludes raw names, phone numbers, customer IDs, and row payload values.",
    }


def main() -> int:
    args = parse_args()
    xlsform_path = Path(args.xlsform).expanduser().resolve()
    workbook_path = Path(args.workbook).expanduser().resolve()
    summary_path = Path(args.summary_json).expanduser().resolve()

    if not xlsform_path.exists():
        raise SystemExit(f"XLSForm not found: {xlsform_path}")
    if not workbook_path.exists():
        raise SystemExit(f"Workbook not found: {workbook_path}")

    summary = build_summary(xlsform_path, workbook_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    print("TACATDP baseline import dry-run summary written.")
    print(f"Summary: {summary_path}")
    print(f"Form: {summary['xlsform']['settings']['id_string']} v{summary['xlsform']['settings']['version']}")
    print(f"Root rows: {summary['kobo_export']['sheets'][summary['kobo_export']['root_sheet']]['rows']}")
    print("No Dataverse writes performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
