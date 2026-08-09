#!/usr/bin/env python3
"""Validate disabled AssignForm access write implementation."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"
TYPES = ROOT / "powerpages/webforms-spa/src/powerpages-api/types.ts"
VIEW = ROOT / "powerpages/webforms-spa/src/views/AssignedFormsView.vue"
DOC = ROOT / "docs/powerpages-odk-webforms/access-assignform-disabled-implementation-20260721.md"

CLIENT_TERMS = (
    "VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED === 'true'",
    "VITE_TACATDP_ACCESS_ASSIGN_FORM_WRITE_ENABLED === 'true'",
    "VITE_TACATDP_ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED === 'true'",
    "areAssignFormWritesEnabled",
    "getAssignFormAccessReadiness",
    "buildAssignFormAccessCommand",
    "buildAssignFormAccessPreview",
    "submitAssignFormAccess",
    "findFormAssignmentByEmailAndVersion",
    "buildFormAssignmentKey",
    "createAccessAuditRequested",
    "createAssignFormAssignment",
    "updateAccessAuditResult",
    "toAccessAuditWebApiPayload",
    "throw new AccessWriteDisabledError(ACCESS_ASSIGN_FORM_DISABLED_MESSAGE)",
)
TYPE_TERMS = (
    "AssignFormAccessInput",
    "AssignFormAccessReadiness",
    "AssignFormAccessResult",
    "already-assigned",
)
DOC_TERMS = (
    "implemented behind disabled feature flags",
    "UI access is gated by `assignFormReadiness.enabled`",
    "Audit and assignment Web API helpers exist only behind the disabled public submit guard",
    "VITE_TACATDP_ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED",
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
    client = require_terms(CLIENT, CLIENT_TERMS)
    require_terms(TYPES, TYPE_TERMS)
    require_terms(DOC, DOC_TERMS)

    view = read(VIEW)
    if "submitAssignFormAccess" in view:
        for term in (
            "accessWorkflowCanSubmit",
            "userOnboardingReadiness.value.enabled",
            ':disabled="!accessWorkflowCanSubmit"',
            "@click=\"submitAccessWorkflow\"",
        ):
            if term not in view:
                fail(f"AssignForm UI submit reference must stay readiness gated; missing: {term}")
    if "ACCESS_AUDIT_WEB_API_PATH = '/_api/mp_accessauditlogs'" not in client:
        fail("audit endpoint constant must be explicit for package review")

    submit_start = client.find("async submitAssignFormAccess")
    submit_end = client.find("\n  async ", submit_start + 1)
    if submit_start < 0:
        fail("submitAssignFormAccess method missing")
    submit_body = client[submit_start:submit_end if submit_end > submit_start else len(client)]
    first_throw = submit_body.find("throw new AccessWriteDisabledError(ACCESS_ASSIGN_FORM_DISABLED_MESSAGE)")
    first_lookup = submit_body.find("findFormAssignmentByEmailAndVersion")
    first_audit_create = submit_body.find("createAccessAuditRequested")
    first_assignment_create = submit_body.find("createAssignFormAssignment")
    if first_throw < 0:
        fail("submitAssignFormAccess must throw disabled error before lookup/mutation")
    if first_lookup >= 0 and first_lookup < first_throw:
        fail("submitAssignFormAccess must not perform duplicate lookup before disabled guard")
    if first_audit_create >= 0 and first_audit_create < first_throw:
        fail("submitAssignFormAccess must not create audit before disabled guard")
    if first_assignment_create >= 0 and first_assignment_create < first_throw:
        fail("submitAssignFormAccess must not create assignment before disabled guard")

    helper_start = client.find("private async createAssignFormAssignment")
    if helper_start < 0 or "this.createRecord('/_api/mp_formassignments'" not in client[helper_start:helper_start + 500]:
        fail("guarded AssignForm assignment create helper missing")
    if "private async updateAccessAuditResult" not in client or "if (!ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED)" not in client:
        fail("audit result update helper must be guarded by one-row lifecycle flag")

    print("TACATDP AssignForm disabled implementation validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
