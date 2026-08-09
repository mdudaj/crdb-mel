#!/usr/bin/env python3
"""Validate the Mshirika-gated create/invite/assign User & Access UX."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEW = ROOT / "powerpages/webforms-spa/src/views/AssignedFormsView.vue"
CLIENT = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"
TYPES = ROOT / "powerpages/webforms-spa/src/powerpages-api/types.ts"
PACKAGE = ROOT / "powerpages/webforms-spa/package.json"
STYLES = ROOT / "powerpages/webforms-spa/src/styles.css"
DOC = ROOT / "docs/powerpages-odk-webforms/access-create-invite-assign-ux-20260722.md"
MATERIAL_CONTROLS_DOC = ROOT / "docs/powerpages-odk-webforms/access-add-user-material-controls-20260722.md"
HOME = ROOT / "powerpages/tacatdp-monitoring-tool/.powerpages-site/web-pages/home/Home.webpage.copy.html"
HOME_CONTENT = ROOT / "powerpages/tacatdp-monitoring-tool/.powerpages-site/web-pages/home/content-pages/en-US/Home.webpage.copy.html"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required artifact: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require(path: Path, terms: tuple[str, ...]) -> str:
    text = read(path)
    for term in terms:
        if term not in text:
            fail(f"{path.relative_to(ROOT)} missing required text: {term}")
    return text


def main() -> int:
    view = require(VIEW, (
        "Create, invite and assign",
        "accessWorkflowFullName",
        "User details",
        "workflow-status-card--compact",
        "accessWorkflowOnboardingLabel",
        "Create contact, invite and assign",
        "Assign existing user and notify",
        "Power Pages invitation email",
        "Assignment notification",
        "Email delivery",
        "Onboarding request queued",
        "Queue record",
        "accessWorkflowOutcome",
        "access-onboarding-outcome",
        "Onboarding result",
        "userOnboardingReadiness",
        "submitUserOnboardingAccess",
        "Ready to queue",
        "Queue request {{ accessWorkflowOnboardingResult.requestId }}",
        "Complete review",
        "Create access",
        "No records are created until the onboarding queue is enabled.",
        "manualInvitationAvailable",
        "manualInvitationExpired",
        "onboardingTimeline",
        "onboardingResultTitle",
        "onboardingPrimaryInstruction",
        "onboardingTechnicalSummary",
        "copyInvitationFallback",
        "recreateExpiredInvitation",
        "refreshOnboardingRequestResult",
        "onboarding-result-panel",
        "onboarding-timeline",
        "Refresh status",
        "Code ready",
        "Create new invitation",
        "approved internal channel",
        "Technical details",
        "Invitation details pending",
    ))
    require(CLIENT, (
        "VITE_TACATDP_ACCESS_ONBOARDING_AUTOMATION_ENABLED === 'true'",
        "submitUserOnboardingAccess",
        "ACCESS_ONBOARDING_QUEUE_WEB_API_PATH",
        "'/_api/mp_onboardingrequests'",
        "createOnboardingRequest",
        "toOnboardingRequestWebApiPayload",
        "ONBOARDING_STATUS_PENDING",
        "getUserOnboardingReadiness",
        "getUserOnboardingRequestResult",
        "toUserOnboardingAccessResult",
        "mp_invitationcode",
        "mp_invitationredeemurl",
        "mp_invitationexpiresat",
        "OnboardingRequests queue table exists in the target environment",
        "Dataverse-triggered onboarding processor is registered in the same environment",
    ))
    require(TYPES, (
        "UserOnboardingAccessInput",
        "UserOnboardingAccessResult",
        "queued-for-invitation",
        "queued-for-assignment-notification",
        "queueRecordId",
        "queueStatus",
        "manual-code-required",
        "invitationCode",
        "invitationRedeemUrl",
        "invitationExpiresAt",
        "replacementOfRequestId",
    ))
    require(PACKAGE, (
        "build:mshirika-access",
        "VITE_TACATDP_ACCESS_ONBOARDING_AUTOMATION_ENABLED=true",
    ))
    require(STYLES, (
        ".access-step small",
        ".access-step::after",
        "grid-template-columns: repeat(4, minmax(0, 1fr))",
        ".access-workflow-step .filter-field input",
        "min-height: 48px",
        "font-size: 1rem",
        "line-height: 1.5rem",
        ".access-workflow-step .filter-field textarea",
        "min-height: 112px",
        "accent-color: var(--mt-color-primary)",
        ".runtime-disabled-message",
        ".access-outcome-panel",
        ".access-outcome-panel--success",
        ".access-outcome-panel--warning",
        ".access-outcome-panel--error",
        ".onboarding-result-panel",
        ".onboarding-timeline",
        ".manual-invitation-card",
        ".manual-invitation-grid",
        ".onboarding-technical-details",
    ))
    require(DOC, (
        "new user",
        "existing user",
        "create or reuse the Power Pages contact",
        "explicit Mshirika test activation path",
        "assignment notification",
        "Dataverse assignment notifications",
        "Office 365 Outlook",
        "Mshirika test build can create/reuse contacts and create audited assignment records",
        "route-level onboarding outcome panel",
        "must not be lost by an unexpected reload",
        "Do not allow this mutating workflow to finish silently",
        "/_api/cloudflow/v1.0/trigger/<guid>",
        "Power Pages cloud flow trigger",
        "triggerBody()",
        "Invalid type. Expected Object but got String",
        "missing `eventData`",
    ))
    if "/_api/cloudflow/v1.0/trigger/" in read(CLIENT):
        fail("portal onboarding must create an OnboardingRequest row and must not call the direct cloud-flow trigger")
    if "? { text: payload.eventData }" in read(CLIENT):
        fail("Power Pages cloud-flow payload must use the documented eventData JSON envelope, not raw top-level text")
    if "JSON.stringify({ text:" in read(CLIENT):
        fail("Power Pages cloud-flow payload must not nest the business payload inside an eventData.text wrapper")
    if "contentType: 'application/json'" in read(CLIENT) or "data: JSON.stringify(payload)" in read(CLIENT):
        fail("Power Pages cloud-flow ajaxSafePost must pass a data object, not a manually stringified JSON body")
    if "this.createRecord('/_api/contacts'" in read(CLIENT):
        fail("portal client must not create contacts directly through browser /_api/contacts")
    require(MATERIAL_CONTROLS_DOC, (
        "Material-style form controls",
        "16px input text",
        "minimum 48px height",
        "Material text-field guidance",
        "48dp touch targets",
    ))
    if "assignFormReadiness.value.enabled" in view and "accessWorkflowCanSubmit" in view:
        fail("final onboarding submit must not be gated only by AssignForm readiness")

    print("TACATDP create/invite/assign UX validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
