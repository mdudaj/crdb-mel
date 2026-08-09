#!/usr/bin/env python3
"""Validate the disabled User & Access write service shell.

This check ensures the frontend can prepare governed write payloads while live
Dataverse mutation endpoints remain disabled until approval.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"
TYPES = ROOT / "powerpages/webforms-spa/src/powerpages-api/types.ts"
DOC = ROOT / "docs/powerpages-odk-webforms/access-write-service-shell-20260721.md"
ASSIGN_FORM_DOC = ROOT / "docs/powerpages-odk-webforms/access-assignform-disabled-implementation-20260721.md"
ASSIGN_FORM_VALIDATOR = ROOT / "scripts/validate-access-assignform-disabled-implementation.py"

REQUIRED_CLIENT_TERMS = (
    "VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED === 'true'",
    "AccessWriteDisabledError",
    "areAccessWritesEnabled",
    "getAccessWriteReadiness",
    "buildAccessWritePreview",
    "submitAccessWrite",
    "if (!this.areAccessWritesEnabled())",
    "buildAccessRequestId",
    "buildAccessMutationPayload",
)
REQUIRED_TYPE_TERMS = (
    "AccessWriteAction",
    "AccessWriteStateSnapshot",
    "AccessWriteCommand",
    "AccessWriteReadiness",
    "AccessAuditPreviewPayload",
    "AccessWritePreview",
)
REQUIRED_DOC_TERMS = (
    "No Dataverse writes are enabled",
    "disabled by default",
    "submitAccessWrite()",
    "Activation Requirements",
)
FORBIDDEN_ENDPOINTS = (
    "/_api/mp_accessauditlogs",
    "/_api/mp_accessauditlog",
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
    client = require_terms(CLIENT, REQUIRED_CLIENT_TERMS)
    require_terms(TYPES, REQUIRED_TYPE_TERMS)
    require_terms(DOC, REQUIRED_DOC_TERMS)

    for endpoint in FORBIDDEN_ENDPOINTS:
        if endpoint in client:
            require_terms(ASSIGN_FORM_DOC, (
                "Audit and assignment Web API helpers exist only behind the disabled public submit guard",
                "VITE_TACATDP_ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED",
            ))
            require_terms(ASSIGN_FORM_VALIDATOR, (
                "submitAssignFormAccess must not create audit before disabled guard",
                "audit endpoint constant must be explicit for package review",
            ))

    submit_start = client.find("async submitAccessWrite")
    submit_end = client.find("\n  async ", submit_start + 1)
    if submit_start < 0:
        fail("submitAccessWrite method not found")
    submit_body = client[submit_start:submit_end if submit_end > submit_start else len(client)]
    if "this.send(" in submit_body or "this.createRecord(" in submit_body:
        fail("submitAccessWrite must not call live Web API helpers while the feature flag is disabled")

    print("TACATDP access write service shell validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
