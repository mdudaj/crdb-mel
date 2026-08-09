#!/usr/bin/env python3
"""Validate the TACATDP access-audit design artifacts.

No network calls are made and no environment writes are performed.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/dataverse/access-audit-schema.json"
SCHEMA_DOC = ROOT / "schemas/dataverse/access-audit-schema.md"
REQUIREMENTS = ROOT / "docs/powerpages-odk-webforms/access-management-requirements.md"
ADR = ROOT / "docs/powerpages-odk-webforms/adr-0007-portal-user-access-management.md"
IMPORT_ORDER = ROOT / "schemas/dataverse/import-order.md"
CLIENT = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"
VIEW = ROOT / "powerpages/webforms-spa/src/views/AssignedFormsView.vue"

REQUIRED_COLUMNS = {
    "AuditKey": True,
    "Action": True,
    "ResultStatus": True,
    "ActorEmail": True,
    "ActorContact": False,
    "ActorRolesJson": False,
    "AffectedEmail": True,
    "AffectedContact": False,
    "TargetRole": False,
    "ScopeType": True,
    "Project": False,
    "Form": False,
    "FormVersion": False,
    "FormAssignment": False,
    "PreviousStateJson": False,
    "NewStateJson": False,
    "Reason": True,
    "SourceRoute": True,
    "RequestId": True,
    "CorrelationId": False,
    "RollbackOf": False,
    "OccurredAt": True,
    "ResultMessage": False,
}
REQUIRED_ACTIONS = {
    "InviteUser",
    "AssignProject",
    "AssignForm",
    "ChangeRole",
    "SuspendAccess",
    "ReactivateAccess",
    "RemoveAssignment",
    "RollbackAccessChange",
}
REQUIRED_RESULT_STATUSES = {"Requested", "Succeeded", "Failed", "Rejected", "RolledBack"}
REQUIRED_SCOPE_TYPES = {"Platform", "Project", "Form", "FormVersion", "Assignment"}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required artifact: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    schema = json.loads(read(SCHEMA))
    if schema.get("environment_write") is not False:
        fail("access audit schema must remain review-only with environment_write=false")
    if schema.get("write_path_policy", {}).get("portal_write_enabled") is not False:
        fail("access audit design must not enable portal writes in this slice")

    tables = schema.get("tables", [])
    if len(tables) != 1 or tables[0].get("name") != "AccessAuditLogs":
        fail("schema must define exactly one AccessAuditLogs table")
    table = tables[0]
    if table.get("ownership_type") != "OrganizationOwned":
        fail("AccessAuditLogs must be organization-owned for central audit administration")
    if table.get("primary_name_column") != "AuditKey":
        fail("AccessAuditLogs primary name column must be AuditKey")

    columns = {column["name"]: column for column in table.get("columns", [])}
    for column_name, required in REQUIRED_COLUMNS.items():
        column = columns.get(column_name)
        if not column:
            fail(f"AccessAuditLogs missing required column: {column_name}")
        if bool(column.get("required")) != required:
            fail(f"AccessAuditLogs.{column_name} required flag must be {required}")

    action_choices = set(columns["Action"].get("choices", []))
    if not REQUIRED_ACTIONS.issubset(action_choices):
        fail(f"Action choices missing: {', '.join(sorted(REQUIRED_ACTIONS - action_choices))}")
    result_choices = set(columns["ResultStatus"].get("choices", []))
    if not REQUIRED_RESULT_STATUSES.issubset(result_choices):
        fail(f"ResultStatus choices missing: {', '.join(sorted(REQUIRED_RESULT_STATUSES - result_choices))}")
    scope_choices = set(columns["ScopeType"].get("choices", []))
    if not REQUIRED_SCOPE_TYPES.issubset(scope_choices):
        fail(f"ScopeType choices missing: {', '.join(sorted(REQUIRED_SCOPE_TYPES - scope_choices))}")

    policy = schema.get("write_path_policy", {})
    for key in (
        "audit_before_mutation",
        "reason_required",
        "actor_required",
        "affected_user_required",
        "before_after_required_for_mutations",
        "rollback_must_create_new_audit_row",
    ):
        if policy.get(key) is not True:
            fail(f"write_path_policy.{key} must be true")

    keys = {key["name"]: set(key.get("columns", [])) for key in schema.get("alternate_keys", [])}
    if keys.get("ak_access_audit_log") != {"AuditKey"}:
        fail("alternate key ak_access_audit_log must use AuditKey")
    if keys.get("ak_access_audit_request") != {"RequestId"}:
        fail("alternate key ak_access_audit_request must use RequestId")

    for text_path, required_strings in {
        SCHEMA_DOC: ("AccessAuditLogs", "RollbackOf", "Reason", "before and after state", "no environment write"),
        REQUIREMENTS: ("AccessAuditLogs", "business reason", "before and after JSON snapshots", "Rollback"),
        ADR: ("append-only audit table", "schemas/dataverse/access-audit-schema.json", "before/after state snapshots"),
        IMPORT_ORDER: ("access-audit-schema.json", "validate-access-audit-design.py", "User & Access write actions"),
    }.items():
        text = read(text_path)
        for required in required_strings:
            if required not in text:
                fail(f"{text_path.relative_to(ROOT)} missing required access-audit text: {required}")

    client = read(CLIENT)
    view = read(VIEW)
    for forbidden in (
        "/_api/mp_accessauditlogs",
        "mp_accessauditlogs",
        "createAccessAudit",
        "AccessAuditLogs@odata.bind",
    ):
        if forbidden in client or forbidden in view:
            fail(f"portal access-audit write path must not be implemented in this design-only slice: {forbidden}")

    print("TACATDP access audit design validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
