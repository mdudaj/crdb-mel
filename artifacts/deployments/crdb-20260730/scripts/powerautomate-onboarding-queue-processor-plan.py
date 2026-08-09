#!/usr/bin/env python3
"""Generate the TACATDP Dataverse-triggered onboarding queue processor plan.

This script does not call Power Platform. It writes a deterministic JSON plan
that the maker can use to build the solution-aware Power Automate cloud flow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


STATUS = {
    "Pending": 100000000,
    "Processing": 100000001,
    "Completed": 100000002,
    "Failed": 100000003,
    "Cancelled": 100000004,
    "NeedsReview": 100000005,
}

REQUEST_TYPE = {
    "NewUser": 100000000,
    "ExistingUser": 100000001,
    "Unresolved": 100000002,
}

INVITATION_STATUS = {
    "Pending": 100000000,
    "ManualDeliveryRequired": 100000001,
    "EmailSent": 100000002,
    "Redeemed": 100000003,
    "Expired": 100000004,
    "Replaced": 100000005,
}

INVITATION_DELIVERY_MODE = {
    "Email": 100000000,
    "ManualCode": 100000001,
    "AssignmentNotification": 100000002,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write the onboarding queue processor plan JSON.")
    parser.add_argument(
        "--output",
        default="artifacts/powerautomate/tacatdp-onboarding-queue-processor-plan.json",
        help="Output JSON path.",
    )
    return parser.parse_args()


def step(step_id: int, name: str, kind: str, purpose: str, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "id": step_id,
        "name": name,
        "kind": kind,
        "purpose": purpose,
        "inputs": inputs or {},
    }


def build_plan() -> dict[str, Any]:
    return {
        "name": "TACATDP - Onboarding Queue Processor",
        "status": "planned",
        "generated_on": "2026-07-24",
        "solution_aware": True,
        "writes_performed": False,
        "official_references": [
            "https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger",
            "https://learn.microsoft.com/en-us/connectors/commondataserviceforapps/",
            "https://learn.microsoft.com/en-us/power-automate/dataverse/create",
            "https://learn.microsoft.com/en-us/power-automate/dataverse/bound-unbound",
        ],
        "trigger": {
            "connector": "Microsoft Dataverse",
            "operation": "When a row is added, modified or deleted",
            "operation_id": "SubscribeWebhookTrigger",
            "table": "mp_onboardingrequest",
            "change_type": "Added or modified",
            "scope": "Organization",
            "filter_rows": f"mp_status eq {STATUS['Pending']}",
            "select_columns": "mp_status",
            "required_privileges": [
                "Create/read/write/delete on Callback Registration for the flow owner",
                "Read/update on mp_onboardingrequest",
                "Create/read/update on contact",
                "Create/read adx_invitation and execute native Send Invitation workflow",
                "Create/read/update on mp_accessauditlog",
                "Create/read on mp_formassignment",
                "Read/append-to on mp_formversion",
                "Create/send Dataverse email for assignment notifications",
            ],
        },
        "status_codes": STATUS,
        "request_type_codes": REQUEST_TYPE,
        "invitation_status_codes": INVITATION_STATUS,
        "invitation_delivery_mode_codes": INVITATION_DELIVERY_MODE,
        "idempotency": {
            "request_key": "mp_requestkey alternate key prevents duplicate request rows.",
            "assignment_key": "mp_assignmentkey = lower(email) + ':' + formVersionId prevents duplicate form assignments.",
            "audit_key": "mp_auditkey uses request id, action, affected email, and form version where applicable.",
        },
        "steps": [
            step(1, "Guard_Pending_Status", "condition", "Exit without mutation unless request status is Pending."),
            step(2, "Set_Request_Processing", "update-row", "Set status to Processing, increment attempts, set LastAttemptAt.", {
                "table": "mp_onboardingrequests",
                "status": STATUS["Processing"],
            }),
            step(3, "Parse_Form_Scope", "parse-json", "Parse mp_formscopejson into selected form-version entries."),
            step(4, "Find_Contact_By_Email", "list-rows", "Find existing active Power Pages contact by emailaddress1.", {
                "table": "contacts",
                "filter": "emailaddress1 eq @{triggerOutputs()?['body/mp_email']}",
            }),
            step(5, "Create_Contact_When_Missing", "conditional-create-row", "Create contact only when no matching contact is found.", {
                "table": "contacts",
                "fields": ["fullname", "lastname", "emailaddress1"],
            }),
            step(6, "Update_Request_Contact", "update-row", "Write resolved contact id back to the onboarding request."),
            step(7, "Create_Request_Audit", "create-row", "Create high-level InviteUser or AssignProject access audit before downstream mutation.", {
                "table": "mp_accessauditlogs",
                "result_status": "Requested",
            }),
            step(8, "Apply_Form_Assignments", "apply-to-each", "For each selected form version, create assignment audit and assignment if missing.", {
                "idempotent_lookup": "mp_useremail eq lower(email) and _mp_formversion_value eq formVersionId",
                "create_assignment_when_missing": True,
                "assignment_key": "lower(email) + ':' + formVersionId",
            }),
            step(9, "Find_Notification_Delivery_Setting", "list-rows", "Load singleton onboarding delivery configuration from NotificationDeliverySettings.", {
                "table": "mp_notificationdeliverysettings",
                "filter": "mp_settingkey eq 'onboarding-delivery'",
                "fallback": "manual-code when missing or not tested",
            }),
            step(10, "Route_Email_Delivery", "condition", "New users receive native Power Pages invitation; existing users receive Dataverse email notification when a mailbox sender is configured."),
            step(11, "Create_Native_Power_Pages_Invitation", "conditional-create-row", "For NewUser requests, create adx_invitation bound to contact and site.", {
                "table": "adx_invitations",
                "request_type": REQUEST_TYPE["NewUser"],
                "fields": ["adx_invitationcode", "adx_expirydate", "adx_inviteContact", "mspp_websiteid"],
            }),
            step(12, "Determine_Email_Delivery_Readiness", "compose", "Email mode is allowed only when configuration says Email and mailbox status is TestedAndEnabled with a sender mailbox.", {
                "delivery_mode_required": INVITATION_DELIVERY_MODE["Email"],
                "mailbox_status_required": "TestedAndEnabled",
            }),
            step(13, "Run_Native_Send_Invitation_When_Ready", "condition", "Call native Send Invitation workflow only when delivery configuration is email-ready."),
            step(14, "Run_Native_Send_Invitation_Workflow", "optional-perform-bound-action", "Execute the native Power Pages Send Invitation workflow only when mailbox delivery is configured.", {
                "action": "Microsoft.Dynamics.CRM.ExecuteWorkflow",
            }),
            step(15, "Update_Request_Invitation_Result", "update-row", "Write invitation id, code, redeem URL, expiry, status, and delivery mode back to the admin-only queue row.", {
                "table": "mp_onboardingrequests",
                "invitation_status": INVITATION_STATUS["ManualDeliveryRequired"],
                "delivery_mode": INVITATION_DELIVERY_MODE["ManualCode"],
                "redeem_url_pattern": "https://<portal>/register/?returnurl=%2f&invitation=<Invitation Code>",
            }),
            step(16, "Create_Dataverse_Assignment_Email", "conditional-create-row", "For ExistingUser requests, create Dataverse email activity when a mailbox sender is configured.", {
                "table": "emails",
                "request_type": REQUEST_TYPE["ExistingUser"],
            }),
            step(17, "Update_Request_Assignment_Notification_Result", "update-row", "Write assignment notification delivery mode back to the queue row for existing-user requests.", {
                "table": "mp_onboardingrequests",
                "delivery_mode": INVITATION_DELIVERY_MODE["AssignmentNotification"],
            }),
            step(18, "Send_Dataverse_Assignment_Email", "optional-perform-bound-action", "Send existing-user assignment notification through Dataverse SendEmail only when mailbox send is approved.", {
                "action": "Microsoft.Dynamics.CRM.SendEmail",
            }),
            step(19, "Set_Request_Needs_Review", "update-row", "Set status NeedsReview after server-side writes when email delivery, manual code handoff, or invitation redemption cannot be confirmed automatically.", {
                "status": STATUS["NeedsReview"],
                "new_user_message": "Invitation created. If mailbox delivery is not configured, issue the invitation code through an approved internal channel.",
                "existing_user_message": "Assignment completed. Dataverse notification email was created but requires mailbox send approval/review.",
            }),
            step(20, "Set_Request_Failed_On_Error", "failure-scope", "On any processing failure, write Failed status, sanitized error category, and result message.", {
                "status": STATUS["Failed"],
                "must_not_store": ["tokens", "connector credentials", "passwords"],
            }),
        ],
        "failure_policy": {
            "failed_request_status": STATUS["Failed"],
            "store_sanitized_error_only": True,
            "retry": "Administrator explicitly sets a retry-approved Pending state after reviewing the error.",
            "no_delete": "Requests are never deleted during failure handling.",
        },
        "mshirika_smoke_tests": [
            "Create a NewUser request from the portal and confirm one queue row starts Pending.",
            "Confirm the Dataverse-triggered flow run appears for the request.",
            "Confirm status changes to Processing and then NeedsReview or Failed.",
            "Confirm NeedsReview NewUser has contact, invitation, audit, and assignments, then verify email delivery or invitation redemption.",
            "Create an ExistingUser request and confirm Dataverse email notification path.",
            "Retry a failed request and confirm no duplicate assignments are created.",
            "Confirm Data Collector cannot read or create mp_onboardingrequest rows.",
        ],
    }


def main() -> int:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build_plan(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
