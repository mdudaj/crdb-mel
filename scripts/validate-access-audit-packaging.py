#!/usr/bin/env python3
"""Validate access-audit solution packaging preparation artifacts."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/dataverse/access-audit-schema.json"
CHECKLIST = ROOT / "docs/powerpages-odk-webforms/access-audit-solution-packaging-20260721.md"
RUNBOOK = ROOT / "docs/powerpages-odk-webforms/access-audit-import-update-runbook-20260721.md"
SERVICE = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"
IMPORT_ORDER = ROOT / "schemas/dataverse/import-order.md"

CHECKLIST_TERMS = (
    "No environment write",
    "AccessAuditLogs",
    "Power Pages Web API site settings",
    "Power Pages table permissions",
    "ACCESS_WRITE_ACTIONS_ENABLED",
    "additive operation count `32`",
)
RUNBOOK_TERMS = (
    "Do not execute without explicit environment-write approval",
    "Phase 1: Schema Import",
    "Phase 2: Web API Site Settings",
    "Phase 3: Table Permissions",
    "Phase 4: Portal Upload",
    "Phase 5: Post-Import Smoke Tests",
    "no `/_api/mp_accessaudit...` calls while writes are disabled",
)
IMPORT_TERMS = (
    "access-audit-schema.json",
    "User & Access write actions",
)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required artifact: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require_terms(path: Path, terms: tuple[str, ...]) -> str:
    text = read(path)
    for term in terms:
        if term not in text:
            fail(f"{path.relative_to(ROOT)} missing required text: {term}")
    return text


def main() -> int:
    schema = json.loads(read(SCHEMA))
    if schema.get("generated_for_review_only") is not True:
        fail("access audit schema must remain generated_for_review_only=true")
    if schema.get("environment_write") is not False:
        fail("access audit schema must remain environment_write=false")
    if schema.get("write_path_policy", {}).get("portal_write_enabled") is not False:
        fail("portal write path must remain disabled in schema policy")

    tables = schema.get("tables", [])
    if len(tables) != 1 or tables[0].get("name") != "AccessAuditLogs":
        fail("packaging prep must target exactly one AccessAuditLogs table")
    if len(tables[0].get("columns", [])) != 23:
        fail("AccessAuditLogs packaging checklist expects 23 columns")
    if len(schema.get("relationships", [])) != 7:
        fail("AccessAuditLogs packaging checklist expects 7 relationships")
    if len(schema.get("alternate_keys", [])) != 2:
        fail("AccessAuditLogs packaging checklist expects 2 alternate keys")

    require_terms(CHECKLIST, CHECKLIST_TERMS)
    require_terms(RUNBOOK, RUNBOOK_TERMS)
    require_terms(IMPORT_ORDER, IMPORT_TERMS)

    service = read(SERVICE)
    if "ACCESS_WRITE_ACTIONS_ENABLED = false" not in service:
        fail("portal write service flag must remain false before audit packaging deployment")
    if "/_api/mp_accessauditlogs" in service or "/_api/mp_accessauditlog" in service:
        fail("portal audit Web API endpoint must not be wired before packaging approval")

    print("TACATDP access audit packaging validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
