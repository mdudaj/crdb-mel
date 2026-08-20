#!/usr/bin/env python3
"""Generate the minimal beneficiary bridge Dataverse solution source.

This generator patches an exported/unpacked Power Platform solution source by
adding the four approved beneficiary bridge tables, relationships, alternate
keys, and solution root components. It performs no Dataverse network calls.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from copy import deepcopy
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


TABLES = [
    "mp_TrackedEntity",
    "mp_EntityIdentifier",
    "mp_BeneficiaryProfile",
    "mp_BeneficiarySubmissionLink",
]

RELATIONSHIPS = [
    {
        "referenced_table": "mp_Project",
        "referencing_table": "mp_TrackedEntity",
        "lookup_column": "mp_project",
        "schema_name": "mp_Project_TrackedEntity_Project",
        "notes": "Project boundary for tracked entities.",
        "delete": "RemoveLink",
    },
    {
        "referenced_table": "mp_TrackedEntity",
        "referencing_table": "mp_EntityIdentifier",
        "lookup_column": "mp_trackedentity",
        "schema_name": "mp_TrackedEntity_EntityIdentifier_TrackedEntity",
        "notes": "Identifiers belong to a tracked entity.",
        "delete": "Cascade",
    },
    {
        "referenced_table": "mp_TrackedEntity",
        "referencing_table": "mp_BeneficiaryProfile",
        "lookup_column": "mp_trackedentity",
        "schema_name": "mp_TrackedEntity_BeneficiaryProfile_TrackedEntity",
        "notes": "Current beneficiary profile belongs to a tracked entity.",
        "delete": "RemoveLink",
    },
    {
        "referenced_table": "mp_Project",
        "referencing_table": "mp_BeneficiaryProfile",
        "lookup_column": "mp_project",
        "schema_name": "mp_Project_BeneficiaryProfile_Project",
        "notes": "Project boundary for beneficiary profile.",
        "delete": "RemoveLink",
    },
    {
        "referenced_table": "mp_TrackedEntity",
        "referencing_table": "mp_BeneficiarySubmissionLink",
        "lookup_column": "mp_trackedentity",
        "schema_name": "mp_TrackedEntity_BeneficiarySubmissionLink_TrackedEntity",
        "notes": "Submission lineage belongs to a tracked entity.",
        "delete": "RemoveLink",
    },
    {
        "referenced_table": "mp_Submission",
        "referencing_table": "mp_BeneficiarySubmissionLink",
        "lookup_column": "mp_submission",
        "schema_name": "mp_Submission_BeneficiarySubmissionLink_Submission",
        "notes": "Bridge link traces to the original submitted record.",
        "delete": "RemoveLink",
    },
]

CHOICES = {
    "mp_entitytype": ["Beneficiary", "Farmer", "Farmer group", "AMCOS", "SACCOS", "Organization", "Facility", "Other"],
    "mp_status": ["Active", "Inactive", "Merged"],
    "mp_identifiertype": ["Source record", "Customer name", "Phone", "National ID", "Loan reference", "Other", "Customer ID"],
    "mp_beneficiarycategory": ["Individual farmer", "Farmer group", "AMCOS", "SACCOS", "Cooperative", "Institution", "Other"],
    "mp_verificationstatus": ["Under review", "Verified", "Incomplete", "Returned", "Inactive"],
    "mp_relationshiptype": ["Baseline submission", "Follow-up submission", "Correction", "Imported record"],
    "mp_reviewstatus": ["Under review", "Approved", "Returned", "Rejected"],
}

TEXT_LENGTHS = {
    "mp_entitykey": 200,
    "mp_displayname": 300,
    "mp_identifiervalue": 300,
    "mp_linkkey": 200,
    "mp_name": 300,
    "mp_region": 120,
    "mp_district": 120,
    "mp_datasource": 200,
}

ALT_KEYS = {
    "mp_TrackedEntity": ("AK_TrackedEntity_Project_Type_Key", ["mp_project", "mp_entitytype", "mp_entitykey"]),
    "mp_EntityIdentifier": ("AK_EntityIdentifier_Entity_Type_Value", ["mp_trackedentity", "mp_identifiertype", "mp_identifiervalue"]),
    "mp_BeneficiaryProfile": ("AK_BeneficiaryProfile_TrackedEntity", ["mp_trackedentity"]),
    "mp_BeneficiarySubmissionLink": ("AK_BeneficiarySubmissionLink_Key", ["mp_linkkey"]),
}

PHYSICAL_NAME_OVERRIDES = {
    "mp_trackedentity": "mp_TrackedEntity",
    "mp_trackedentityid": "mp_TrackedEntityId",
    "mp_entityidentifierid": "mp_EntityIdentifierId",
    "mp_beneficiaryprofileid": "mp_BeneficiaryProfileId",
    "mp_beneficiarysubmissionlinkid": "mp_BeneficiarySubmissionLinkId",
    "mp_beneficiarycategory": "mp_BeneficiaryCategory",
    "mp_verificationstatus": "mp_VerificationStatus",
    "mp_identifiertype": "mp_IdentifierType",
    "mp_identifiervalue": "mp_IdentifierValue",
    "mp_lastupdatedat": "mp_LastUpdatedAt",
    "mp_relationshiptype": "mp_RelationshipType",
    "mp_reviewstatus": "mp_ReviewStatus",
    "mp_linkkey": "mp_LinkKey",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Existing unpacked solution source folder.")
    parser.add_argument("--output", required=True, help="Output unpacked solution source folder.")
    parser.add_argument("--repo-root", default=".", help="Repository root for schema artifacts.")
    parser.add_argument("--version", default="0.2.4.0", help="Solution version to write.")
    return parser.parse_args()


def table_lower(table: str) -> str:
    return table.lower()


def schema_part(logical: str) -> str:
    if logical in PHYSICAL_NAME_OVERRIDES:
        return PHYSICAL_NAME_OVERRIDES[logical]
    if logical.startswith("mp_"):
        body = logical[3:]
        return "mp_" + "".join(part.capitalize() for part in re.split(r"[_\s]+", body) if part)
    return "".join(part.capitalize() for part in re.split(r"[_\s]+", logical) if part)


def pluralize(display: str) -> str:
    return display if display.endswith("s") else f"{display}s"


def read_platform_table_defs(repo_root: Path) -> dict[str, dict[str, Any]]:
    data = json.loads((repo_root / "schemas/dataverse/platform-tables.json").read_text(encoding="utf-8"))
    return {row["logical_name"]: row for row in data["tables"]}


def read_platform_columns(repo_root: Path) -> dict[str, list[dict[str, Any]]]:
    with (repo_root / "schemas/dataverse/platform-columns.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    result: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        result.setdefault(row["table_logical_name"], []).append(
            {
                "name": row["column_logical_name"],
                "display_name": row["display_name"],
                "type": row["data_type"],
                "required": row["required"].lower() == "yes",
                "notes": row["notes"],
            }
        )
    return result


def read_extension_table_defs(repo_root: Path) -> dict[str, dict[str, Any]]:
    data = json.loads((repo_root / "schemas/dataverse/beneficiary-entity-extension-schema.json").read_text(encoding="utf-8"))
    return {row["name"]: row for row in data["tables"]}


def pick_template_attributes(template_entity: Path) -> dict[str, ET.Element]:
    root = ET.parse(template_entity).getroot()
    attrs = root.find("./EntityInfo/entity/attributes")
    if attrs is None:
        raise RuntimeError(f"No attributes found in {template_entity}")
    templates: dict[str, ET.Element] = {}
    for attr in attrs.findall("attribute"):
        logical = attr.findtext("LogicalName")
        typ = attr.findtext("Type")
        if logical == "mp_name":
            templates["primary_name"] = deepcopy(attr)
        elif typ == "primarykey":
            templates["primary_key"] = deepcopy(attr)
        elif logical == "mp_projectcode":
            templates["text"] = deepcopy(attr)
        elif logical == "mp_lifecyclestatus":
            templates["choice"] = deepcopy(attr)
        elif logical == "createdon":
            templates["datetime"] = deepcopy(attr)
    submission_root = ET.parse(template_entity.parent.parent / "mp_Submission" / "Entity.xml").getroot()
    for attr in submission_root.findall("./EntityInfo/entity/attributes/attribute"):
        if attr.findtext("LogicalName") == "mp_formversion":
            templates["lookup"] = deepcopy(attr)
            break
    decimal_root = ET.parse(template_entity.parent.parent / "mp_SubmissionAnswer" / "Entity.xml").getroot()
    for attr in decimal_root.findall("./EntityInfo/entity/attributes/attribute"):
        if attr.findtext("LogicalName") == "mp_valuedecimal":
            templates["decimal"] = deepcopy(attr)
            break
    missing = {"primary_name", "primary_key", "text", "choice", "datetime", "lookup", "decimal"} - templates.keys()
    if missing:
        raise RuntimeError(f"Missing entity XML templates: {', '.join(sorted(missing))}")
    return templates


def set_child_text(parent: ET.Element, name: str, value: str) -> None:
    child = parent.find(name)
    if child is None:
        child = ET.SubElement(parent, name)
    child.text = value


def set_label(attr: ET.Element, display: str, description: str) -> None:
    for displayname in attr.findall("./displaynames/displayname"):
        displayname.set("description", display)
    for desc in attr.findall("./Descriptions/Description"):
        desc.set("description", description or display)
    opt = attr.find("optionset")
    if opt is not None:
        for displayname in opt.findall("./displaynames/displayname"):
            displayname.set("description", display)
        for desc in opt.findall("./Descriptions/Description"):
            desc.set("description", description or display)


def make_attribute(templates: dict[str, ET.Element], table: str, column: dict[str, Any], primary_name: str) -> ET.Element:
    logical = column["name"]
    raw_type = column["type"]
    col_type = str(raw_type).split(":", 1)[0].lower()
    key = {
        "text": "text",
        "choice": "choice",
        "lookup": "lookup",
        "datetime": "datetime",
        "dateonly": "datetime",
        "decimal": "decimal",
    }.get(col_type, "text")
    attr = deepcopy(templates["primary_name" if logical == primary_name else key])
    attr.set("PhysicalName", schema_part(logical))
    set_child_text(attr, "PhysicalName", schema_part(logical))
    set_child_text(attr, "Name", logical)
    set_child_text(attr, "LogicalName", logical)
    set_child_text(attr, "RequiredLevel", "required" if column.get("required") else "none")
    if logical == primary_name:
        set_child_text(attr, "DisplayMask", "PrimaryName|ValidForAdvancedFind|ValidForForm|ValidForGrid|RequiredForForm")
    if col_type == "dateonly":
        set_child_text(attr, "Format", "date")
    if col_type == "datetime":
        set_child_text(attr, "Format", "datetime")
    if key in {"text", "primary_name"}:
        max_length = TEXT_LENGTHS.get(logical, 200)
        set_child_text(attr, "MaxLength", str(max_length))
        set_child_text(attr, "Length", str(max_length * 2))
    if key == "lookup":
        lookup_types = attr.find("LookupTypes")
        if lookup_types is None:
            lookup_types = ET.SubElement(attr, "LookupTypes")
        lookup_types.clear()
    if key == "choice":
        opt = attr.find("optionset")
        if opt is None:
            raise RuntimeError("Choice template has no optionset")
        opt.set("Name", f"{table_lower(table)}_{logical}")
        opts = opt.find("options")
        if opts is None:
            opts = ET.SubElement(opt, "options")
        opts.clear()
        for index, label in enumerate(CHOICES.get(logical, ["Active", "Inactive"])):
            option = ET.SubElement(opts, "option", {"value": str(100000000 + index), "ExternalValue": "", "IsHidden": "0"})
            labels = ET.SubElement(option, "labels")
            ET.SubElement(labels, "label", {"description": label, "languagecode": "1033"})
    set_label(attr, column.get("display_name") or logical, column.get("notes") or column.get("display_name") or logical)
    return attr


def build_entity_xml(source: Path, output: Path, table: str, definition: dict[str, Any], columns: list[dict[str, Any]]) -> None:
    templates = pick_template_attributes(source / "Entities" / "mp_Project" / "Entity.xml")
    source_root = ET.parse(source / "Entities" / "mp_Project" / "Entity.xml").getroot()
    root_name = source_root.find("Name")
    entity = source_root.find("./EntityInfo/entity")
    attrs = entity.find("attributes") if entity is not None else None
    if root_name is None or entity is None or attrs is None:
        raise RuntimeError("Source Project entity XML has unexpected shape")

    display = definition.get("display_name") or table.removeprefix("mp_")
    primary_name = definition.get("primary_name_column") or "mp_name"
    if not str(primary_name).startswith("mp_"):
        primary_name = "mp_" + str(primary_name).lower()

    root_name.text = table
    root_name.set("LocalizedName", display)
    root_name.set("OriginalName", display)
    entity.set("Name", table)
    for node in entity.findall("./LocalizedNames/LocalizedName"):
        node.set("description", display)
    for node in entity.findall("./LocalizedCollectionNames/LocalizedCollectionName"):
        node.set("description", pluralize(display))
    for node in entity.findall("./Name"):
        entity.remove(node)
    for node in entity.findall("./ObjectTypeCode"):
        entity.remove(node)
    for node in entity.findall("./EntityInfoCode"):
        entity.remove(node)
    for node in entity.findall("./LocalizedName"):
        entity.remove(node)
    for node in entity.findall("./LocalizedCollectionName"):
        entity.remove(node)
    for node in entity.findall("./CollectionName"):
        entity.remove(node)
    for node in entity.findall("./PrimaryIdAttribute"):
        entity.remove(node)
    for node in entity.findall("./PrimaryNameAttribute"):
        entity.remove(node)
    set_child_text(entity, "IntroducedVersion", "0.2.4.0")
    set_child_text(entity, "EntitySetName", table_lower(pluralize(table)))
    for desc in entity.findall("./Descriptions/Description"):
        desc.set("description", definition.get("purpose") or display)

    attrs.clear()
    for column in columns:
        attrs.append(make_attribute(templates, table, column, primary_name))
    pk = deepcopy(templates["primary_key"])
    pk.set("PhysicalName", schema_part(f"{table_lower(table)}id"))
    set_child_text(pk, "PhysicalName", schema_part(f"{table_lower(table)}id"))
    set_child_text(pk, "Name", f"{table_lower(table)}id")
    set_child_text(pk, "LogicalName", f"{table_lower(table)}id")
    set_label(pk, pluralize(display), "Unique identifier for entity instances")
    attrs.append(pk)

    existing_keys = entity.find("EntityKeys")
    if existing_keys is not None:
        entity.remove(existing_keys)
    keys = ET.Element("EntityKeys")
    key_name, key_cols = ALT_KEYS[table]
    entity_key = ET.SubElement(keys, "EntityKey")
    set_child_text(entity_key, "Name", f"mp_{key_name}")
    set_child_text(entity_key, "LogicalName", f"mp_{key_name}".lower())
    set_child_text(entity_key, "IntroducedVersion", "0.2.4.0")
    set_child_text(entity_key, "IsCustomizable", "0")
    key_attrs = ET.SubElement(entity_key, "EntityKeyAttributes")
    for col in key_cols:
        child = ET.SubElement(key_attrs, "AttributeName")
        child.text = col
    dnames = ET.SubElement(entity_key, "displaynames")
    ET.SubElement(dnames, "displayname", {"description": key_name, "languagecode": "1033"})
    insert_before = entity.find("EntitySetName")
    index = list(entity).index(insert_before) if insert_before is not None else len(list(entity))
    entity.insert(index, keys)

    target_dir = output / "Entities" / table
    target_dir.mkdir(parents=True, exist_ok=True)
    ET.indent(source_root, space="  ")
    ET.ElementTree(source_root).write(target_dir / "Entity.xml", encoding="utf-8", xml_declaration=True)


def relationship_element(row: dict[str, str]) -> ET.Element:
    rel = ET.Element("EntityRelationship", {"Name": row["schema_name"]})
    for name, value in [
        ("EntityRelationshipType", "OneToMany"),
        ("IsCustomizable", "1"),
        ("IntroducedVersion", "0.2.4.0"),
        ("IsHierarchical", "0"),
        ("ReferencingEntityName", row["referencing_table"]),
        ("ReferencedEntityName", row["referenced_table"]),
        ("CascadeAssign", "NoCascade"),
        ("CascadeDelete", row["delete"]),
        ("CascadeArchive", row["delete"]),
        ("CascadeReparent", "NoCascade"),
        ("CascadeShare", "NoCascade"),
        ("CascadeUnshare", "NoCascade"),
        ("CascadeRollupView", "NoCascade"),
        ("IsValidForAdvancedFind", "1"),
        ("ReferencingAttributeName", schema_part(row["lookup_column"])),
    ]:
        set_child_text(rel, name, value)
    desc = ET.SubElement(rel, "RelationshipDescription")
    descriptions = ET.SubElement(desc, "Descriptions")
    ET.SubElement(descriptions, "Description", {"description": row["notes"], "languagecode": "1033"})
    roles = ET.SubElement(rel, "EntityRelationshipRoles")
    role1 = ET.SubElement(roles, "EntityRelationshipRole")
    for name, value in [
        ("NavPaneDisplayOption", "UseCollectionName"),
        ("NavPaneArea", "Details"),
        ("NavPaneOrder", "10000"),
        ("NavigationPropertyName", schema_part(row["lookup_column"])),
        ("RelationshipRoleType", "1"),
    ]:
        set_child_text(role1, name, value)
    role0 = ET.SubElement(roles, "EntityRelationshipRole")
    set_child_text(role0, "NavigationPropertyName", row["schema_name"])
    set_child_text(role0, "RelationshipRoleType", "0")
    return rel


def patch_relationship_files(output: Path) -> None:
    relationships_dir = output / "Other" / "Relationships"
    relationships_dir.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in RELATIONSHIPS:
        grouped.setdefault(row["referenced_table"], []).append(row)
    for referenced, rows in grouped.items():
        target = relationships_dir / f"{referenced}.xml"
        if target.exists():
            root = ET.parse(target).getroot()
        else:
            root = ET.Element("EntityRelationships", {"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"})
        existing = {node.attrib.get("Name") for node in root.findall("EntityRelationship")}
        for row in rows:
            if row["schema_name"] not in existing:
                root.append(relationship_element(row))
        ET.indent(root, space="  ")
        ET.ElementTree(root).write(target, encoding="utf-8", xml_declaration=True)
    index_path = output / "Other" / "Relationships.xml"
    index_root = ET.parse(index_path).getroot()
    existing = {node.attrib.get("Name") for node in index_root.findall("EntityRelationship")}
    for row in RELATIONSHIPS:
        if row["schema_name"] not in existing:
            ET.SubElement(index_root, "EntityRelationship", {"Name": row["schema_name"]})
    ET.indent(index_root, space="  ")
    ET.ElementTree(index_root).write(index_path, encoding="utf-8", xml_declaration=True)


def patch_solution_xml(output: Path, version: str) -> None:
    path = output / "Other" / "Solution.xml"
    root = ET.parse(path).getroot()
    version_node = root.find("./SolutionManifest/Version")
    if version_node is not None:
        version_node.text = version
    components = root.find("./SolutionManifest/RootComponents")
    if components is None:
        raise RuntimeError("Solution.xml has no RootComponents")
    existing = {node.attrib.get("schemaName") for node in components.findall("RootComponent")}
    for table in TABLES:
        logical = table_lower(table)
        if logical not in existing:
            ET.SubElement(components, "RootComponent", {"type": "1", "schemaName": logical, "behavior": "0"})
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def copy_source(source: Path, output: Path) -> None:
    if output.exists():
        if not str(output).startswith("/tmp/"):
            raise RuntimeError(f"Refusing to replace non-/tmp output path: {output}")
        shutil.rmtree(output)
    shutil.copytree(source, output)


def validate_output(output: Path) -> list[str]:
    errors: list[str] = []
    solution_xml = (output / "Other" / "Solution.xml").read_text(encoding="utf-8")
    for table in TABLES:
        entity_xml = output / "Entities" / table / "Entity.xml"
        if not entity_xml.exists():
            errors.append(f"missing entity xml: {table}")
            continue
        text = entity_xml.read_text(encoding="utf-8")
        key_name = ALT_KEYS[table][0]
        if key_name not in text:
            errors.append(f"missing alternate key: {table}.{key_name}")
        if f'schemaName="{table_lower(table)}"' not in solution_xml:
            errors.append(f"missing root component: {table}")
    relationships_text = "\n".join(path.read_text(encoding="utf-8") for path in (output / "Other" / "Relationships").glob("*.xml"))
    relationships_index_text = (output / "Other" / "Relationships.xml").read_text(encoding="utf-8")
    for row in RELATIONSHIPS:
        if row["schema_name"] not in relationships_text:
            errors.append(f"missing relationship: {row['schema_name']}")
        if row["schema_name"] not in relationships_index_text:
            errors.append(f"missing relationship index entry: {row['schema_name']}")
    return errors


def main() -> int:
    args = parse_args()
    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    repo_root = Path(args.repo_root).resolve()
    if not (source / "Other" / "Solution.xml").exists():
        raise SystemExit(f"Source is not an unpacked solution source: {source}")

    platform_tables = read_platform_table_defs(repo_root)
    platform_columns = read_platform_columns(repo_root)
    extension_tables = read_extension_table_defs(repo_root)

    copy_source(source, output)
    for table in TABLES:
        if table in platform_tables:
            definition = platform_tables[table]
            columns = platform_columns[table]
        else:
            definition = extension_tables[table]
            columns = definition["columns"]
        build_entity_xml(source, output, table, definition, columns)

    patch_relationship_files(output)
    patch_solution_xml(output, args.version)
    errors = validate_output(output)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(json.dumps({"status": "generated", "output": str(output), "tables": TABLES, "relationships": len(RELATIONSHIPS)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
