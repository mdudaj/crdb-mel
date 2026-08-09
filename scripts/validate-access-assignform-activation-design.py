#!/usr/bin/env python3
"""Validate AssignForm first-live-write activation design artifacts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "docs/powerpages-odk-webforms/access-assignform-activation-design-20260721.md"
CONTRACT = ROOT / "docs/powerpages-odk-webforms/access-write-path-contract-20260721.md"
PERMISSIONS = ROOT / "docs/powerpages-odk-webforms/access-webapi-permission-package-plan-20260721.md"
CLIENT = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"
TYPES = ROOT / "powerpages/webforms-spa/src/powerpages-api/types.ts"
DISABLED_IMPLEMENTATION = ROOT / "docs/powerpages-odk-webforms/access-assignform-disabled-implementation-20260721.md"
DISABLED_IMPLEMENTATION_VALIDATOR = ROOT / "scripts/validate-access-assignform-disabled-implementation.py"

DESIGN_TERMS = (
    "First live action: `AssignForm`",
    "Platform Administrator only",
    "Project Manager write access remains deferred",
    "ChangeRole, SuspendAccess, ReactivateAccess, RemoveAssignment, InviteUser, AssignProject, and RollbackAccessChange remain disabled",
    "If audit create fails, stop before assignment create",
    "Duplicate assignment detection is a successful no-op",
    "mp_FormVersion@odata.bind",
    "Access already existed",
    "Implementation Gate",
)
CONTRACT_TERMS = (
    "Assignment create must search by affected user email",
    "If an equivalent active assignment already exists",
    "Audit create fails",
)
PERMISSION_TERMS = (
    "For the first activation, use Platform Administrator only",
    "mp_formassignment",
    "mp_formversion",
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
    require_terms(DESIGN, DESIGN_TERMS)
    require_terms(CONTRACT, CONTRACT_TERMS)
    require_terms(PERMISSIONS, PERMISSION_TERMS)

    types = read(TYPES)
    if "'AssignForm'" not in types:
        fail("AccessWriteAction must include AssignForm")

    client = read(CLIENT)
    if "VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED === 'true'" not in client:
        fail("access write activation must remain disabled by default unless an explicit build flag is set")
    if "submitAssignFormAccess" in client:
        require_terms(DISABLED_IMPLEMENTATION, ("implemented behind disabled feature flags", "UI access is gated by `assignFormReadiness.enabled`"))
        require_terms(DISABLED_IMPLEMENTATION_VALIDATOR, ("submitAssignFormAccess must throw disabled error before lookup/mutation", "createRecord('/_api/mp_formassignments'"))
    if "createFormAssignment" in client:
        fail("AssignForm create mutation must not be added before approval")
    if "/_api/mp_accessauditlog" in client or "/_api/mp_accessauditlogs" in client:
        require_terms(DISABLED_IMPLEMENTATION, (
            "Audit and assignment Web API helpers exist only behind the disabled public submit guard",
            "VITE_TACATDP_ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED",
        ))
        require_terms(DISABLED_IMPLEMENTATION_VALIDATOR, (
            "ACCESS_AUDIT_WEB_API_PATH = '/_api/mp_accessauditlogs'",
            "audit endpoint constant must be explicit for package review",
        ))

    print("TACATDP AssignForm activation design validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
