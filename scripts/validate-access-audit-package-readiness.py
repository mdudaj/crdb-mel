#!/usr/bin/env python3
"""Validate AccessAuditLogs audit-schema-only package readiness artifacts."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/dataverse/access-audit-schema.json"
README = ROOT / "docs/powerpages-odk-webforms/access-audit-schema-package-readiness-20260721.md"
MANIFEST = ROOT / "docs/powerpages-odk-webforms/access-audit-schema-package-manifest-20260721.md"
RUNBOOK = ROOT / "docs/powerpages-odk-webforms/access-audit-import-update-runbook-20260721.md"
SERVICE = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"

READINESS_TERMS = (
    "No export or environment write performed",
    "managed solution update",
    "existing TACATDP solution lineage",
    "pac solution export",
    "Exclude",
    "ACCESS_WRITE_ACTIONS_ENABLED = true",
    "operation count `32`",
    "separate approved permission phase",
)
MANIFEST_TERMS = (
    "AccessAuditLogs",
    "ak_access_audit_log",
    "ak_access_audit_request",
    "No `PluginAssemblies/` payload",
    "No Data Collector audit read permission",
    "No access audit seed rows",
)
RUNBOOK_TERMS = (
    "Import the `AccessAuditLogs` schema",
    "Do not configure portal write activation",
    "Phase 2: Web API Site Settings",
    "Phase 3: Table Permissions",
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
    if schema.get("environment_write") is not False:
        fail("access audit schema readiness must not authorize environment writes")
    if schema.get("write_path_policy", {}).get("portal_write_enabled") is not False:
        fail("portal write policy must remain disabled before package export")
    table = schema.get("tables", [{}])[0]
    if table.get("name") != "AccessAuditLogs":
        fail("package readiness must target AccessAuditLogs")
    if len(table.get("columns", [])) != 23:
        fail("package manifest expects 23 AccessAuditLogs columns")
    if len(schema.get("relationships", [])) != 7:
        fail("package manifest expects 7 AccessAuditLogs relationships")
    if len(schema.get("alternate_keys", [])) != 2:
        fail("package manifest expects 2 AccessAuditLogs alternate keys")

    require_terms(README, READINESS_TERMS)
    require_terms(MANIFEST, MANIFEST_TERMS)
    require_terms(RUNBOOK, RUNBOOK_TERMS)

    service = read(SERVICE)
    if "ACCESS_WRITE_ACTIONS_ENABLED = false" not in service:
        fail("portal write activation flag must remain false")
    if "ACCESS_WRITE_ACTIONS_ENABLED = true" in service:
        fail("portal write activation must not be enabled in package readiness slice")
    if "/_api/mp_accessauditlog" in service or "/_api/mp_accessauditlogs" in service:
        fail("audit Web API endpoint must not be wired before approved activation")

    print("TACATDP access audit package readiness validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
