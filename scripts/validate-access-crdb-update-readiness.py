#!/usr/bin/env python3
"""Validate CRDB User Management delivery gates and UI separation."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEW = ROOT / "powerpages/webforms-spa/src/views/AssignedFormsView.vue"
STYLES = ROOT / "powerpages/webforms-spa/src/styles.css"
CLIENT = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"
DOC = ROOT / "docs/powerpages-odk-webforms/access-crdb-update-readiness-20260722.md"

VIEW_TERMS = (
    "userOnboardingReadiness",
    "getUserOnboardingReadiness",
    "accessWorkflowFullName",
    "accessWorkflowReason",
    "Business reason",
    "accessWorkflowCanSubmit",
    "submitAccessWorkflow",
    "submitUserOnboardingAccess",
    "Access creation results",
)
STYLE_TERMS = (
    "assignform-readiness-panel",
)
FORBIDDEN_UI_TERMS = (
    "accessCrdbUpdateItems",
    "crdbReadyItemCount",
    "CRDB update package",
    "Update gates",
    "crdb-update-readiness",
    "crdb-update-grid",
    "crdb-update-card",
)
DOC_TERMS = (
    "implemented for portal package readiness",
    "Mshirika write activation",
    "CRDB update package",
    "Create, invite and assign confirmation captures a business reason",
    "UI access is gated by `userOnboardingReadiness.enabled`",
    "OnboardingRequests",
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
    view = require_terms(VIEW, VIEW_TERMS)
    styles = require_terms(STYLES, STYLE_TERMS)
    require_terms(DOC, DOC_TERMS)
    client = read(CLIENT)

    for term in FORBIDDEN_UI_TERMS:
        if term in view or term in styles:
            fail(f"deployment gate wording must stay out of normal portal UI: {term}")

    for term in (
        "VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED === 'true'",
        "VITE_TACATDP_ACCESS_ASSIGN_FORM_WRITE_ENABLED === 'true'",
        "VITE_TACATDP_ACCESS_ONBOARDING_AUTOMATION_ENABLED === 'true'",
        "VITE_TACATDP_ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED === 'true'",
    ):
        if term not in client:
            fail(f"access write flag must default to disabled unless explicitly enabled: {term}")
    for term in (
        "userOnboardingReadiness.value.enabled",
        ':disabled="!accessWorkflowCanSubmit"',
        "@click=\"submitAccessWorkflow\"",
    ):
        if term not in view:
            fail(f"onboarding submit path must remain readiness gated; missing: {term}")
    print("TACATDP CRDB access update gate validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
