#!/usr/bin/env python3
"""Validate TACATDP User & Access write-path planning artifacts.

This check is local only. It does not call Dataverse or Power Pages.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/powerpages-odk-webforms/access-write-path-contract-20260721.md"
MATRIX = ROOT / "docs/powerpages-odk-webforms/access-permission-matrix-20260721.md"
REQUIREMENTS = ROOT / "docs/powerpages-odk-webforms/access-management-requirements.md"
ACCEPTANCE = ROOT / "docs/powerpages-odk-webforms/access-management-acceptance-criteria.md"
ADR = ROOT / "docs/powerpages-odk-webforms/adr-0007-portal-user-access-management.md"
CLIENT = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"
VIEW = ROOT / "powerpages/webforms-spa/src/views/AssignedFormsView.vue"

CONTRACT_TERMS = (
    "ResultStatus=Requested",
    "RequestId",
    "business reason",
    "before and after",
    "RollbackAccessChange",
    "Activation Gates",
    "Writes remain disabled",
)
MATRIX_TERMS = (
    "Platform Administrator",
    "Project Manager",
    "Data Collector / Bank Officer",
    "AccessAuditLogs",
    "FormAssignments",
    "Power Pages Web API",
    "prvCreatePluginAssembly",
)
BASELINE_TERMS = {
    REQUIREMENTS: ("AccessAuditLogs", "business reason", "before and after JSON snapshots"),
    ACCEPTANCE: ("Admin actions are auditable", "permission-denied", "CRDB Microsoft identity"),
    ADR: ("Authorization will use three layers", "append-only audit table"),
}
REQUIRED_IMPLEMENTATION_TERMS = (
    "createAccessAuditRequested",
    "updateAccessAuditResult",
    "submitManageAccessUser",
    "updateContactEmail",
    "deactivateFormAssignment",
    "mp_accessauditlogs",
    "mp_accessauditlog",
    "mp_lifecyclestatus",
    "FORM_ASSIGNMENT_LIFECYCLE_INACTIVE",
)
FORBIDDEN_IMPLEMENTATION_TERMS = (
    "mutateAccessAssignment",
)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required artifact: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def assert_contains(path: Path, terms: tuple[str, ...]) -> None:
    text = read(path)
    for term in terms:
        if term not in text:
            fail(f"{path.relative_to(ROOT)} missing required text: {term}")


def main() -> int:
    assert_contains(CONTRACT, CONTRACT_TERMS)
    assert_contains(MATRIX, MATRIX_TERMS)
    for path, terms in BASELINE_TERMS.items():
        assert_contains(path, terms)

    client = read(CLIENT)
    view = read(VIEW)
    for required in REQUIRED_IMPLEMENTATION_TERMS:
        if required not in client and required not in view:
            fail(f"approved access write-path implementation missing required guardrail: {required}")
    for forbidden in FORBIDDEN_IMPLEMENTATION_TERMS:
        if forbidden in client or forbidden in view:
            fail(f"unsupported access write-path mutation pattern found: {forbidden}")

    print("TACATDP access write-path contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
