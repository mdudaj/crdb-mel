#!/usr/bin/env python3
"""Validate the TACATDP onboarding queue processor plan."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "artifacts/powerautomate/tacatdp-onboarding-queue-processor-plan.json"
GENERATOR = ROOT / "scripts/powerautomate-onboarding-queue-processor-plan.py"
RUNBOOK = ROOT / "docs/powerpages-odk-webforms/access-onboarding-queue-processor-20260724.md"
CONFIGURATOR = ROOT / "scripts/powerautomate-configure-onboarding-queue-processor.py"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required artifact: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    plan = json.loads(read(PLAN))
    if plan.get("name") != "TACATDP - Onboarding Queue Processor":
        fail("processor plan name mismatch")
    if plan.get("writes_performed") is not False:
        fail("processor plan must not perform environment writes")
    trigger = plan.get("trigger", {})
    if trigger.get("operation_id") != "SubscribeWebhookTrigger":
        fail("processor must use the current Dataverse row trigger")
    if trigger.get("table") != "mp_onboardingrequest":
        fail("processor trigger table must be mp_onboardingrequest")
    if "Callback Registration" not in " ".join(trigger.get("required_privileges", [])):
        fail("processor privileges must document Callback Registration requirement")
    steps = {step.get("name"): step for step in plan.get("steps", [])}
    for name in (
        "Set_Request_Processing",
        "Find_Contact_By_Email",
        "Create_Contact_When_Missing",
        "Create_Request_Audit",
        "Apply_Form_Assignments",
        "Find_Notification_Delivery_Setting",
        "Create_Native_Power_Pages_Invitation",
        "Determine_Email_Delivery_Readiness",
        "Run_Native_Send_Invitation_When_Ready",
        "Run_Native_Send_Invitation_Workflow",
        "Update_Request_Invitation_Result",
        "Create_Dataverse_Assignment_Email",
        "Update_Request_Assignment_Notification_Result",
        "Send_Dataverse_Assignment_Email",
        "Set_Request_Needs_Review",
        "Set_Request_Failed_On_Error",
    ):
        if name not in steps:
            fail(f"processor plan missing step: {name}")
    if plan.get("status_codes", {}).get("Pending") != 100000000:
        fail("Pending status code mismatch")
    if plan.get("request_type_codes", {}).get("ExistingUser") != 100000001:
        fail("ExistingUser request type code mismatch")
    if plan.get("invitation_status_codes", {}).get("ManualDeliveryRequired") != 100000001:
        fail("ManualDeliveryRequired invitation status code mismatch")
    if plan.get("invitation_delivery_mode_codes", {}).get("ManualCode") != 100000001:
        fail("ManualCode invitation delivery mode code mismatch")
    if "Microsoft.Dynamics.CRM.SendEmail" not in read(PLAN):
        fail("existing-user notification must use Dataverse SendEmail")
    if "Microsoft.Dynamics.CRM.ExecuteWorkflow" not in read(PLAN):
        fail("new-user invitation must use native ExecuteWorkflow")

    generator = read(GENERATOR)
    for term in ("writes_performed", "False", "SubscribeWebhookTrigger", "mp_onboardingrequest"):
        if term not in generator:
            fail(f"generator missing required term: {term}")

    configurator = read(CONFIGURATOR)
    for term in (
        "SubscribeWebhookTrigger",
        "subscriptionRequest/entityname",
        "subscriptionRequest/message",
        "15c03c8d-754f-4386-a62c-cf7e91337ebd",
        "mp_onboardingrequest",
        "Set_Request_Processing",
        "Create_Request_Audit",
        "Apply_Form_Assignments",
        "Find_Notification_Delivery_Setting",
        "mp_notificationdeliverysettings",
        "onboarding-delivery",
        "Determine_Email_Delivery_Readiness",
        "Run_Native_Send_Invitation_When_Ready",
        "Update_Request_Invitation_Result",
        "mp_invitationcode",
        "mp_invitationredeemurl",
        "mp_invitationexpiresat",
        "manual-code",
        "Run_Native_Send_Invitation_Workflow",
        "Set_Request_Needs_Review",
        "approved internal channel",
        "Set_Request_Failed_On_Error",
    ):
        if term not in configurator:
            fail(f"processor configurator missing required term: {term}")
    if 'SEND_INVITATION_WORKFLOW_ID = "eb467141-a276-f111-ab0e-70a8a52d4a92"' in configurator:
        fail("queue processor must not default to the non-executable type-2 Send Invitation workflow id")

    runbook = read(RUNBOOK)
    for term in (
        "When a row is added, modified or deleted",
        "Callback Registration",
        "mp_onboardingrequest",
        "Power Pages invitation",
        "manual invitation code",
        "Dataverse SendEmail",
        "Mshirika Smoke",
    ):
        if term not in runbook:
            fail(f"processor runbook missing required term: {term}")

    print("TACATDP onboarding queue processor plan validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
