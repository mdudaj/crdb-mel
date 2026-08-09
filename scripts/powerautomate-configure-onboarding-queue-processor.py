#!/usr/bin/env python3
"""Configure the TACATDP Dataverse-triggered onboarding queue processor.

This replaces the failed direct Power Pages cloud-flow trigger route. The
processor consumes Pending mp_onboardingrequest rows and performs the governed
server-side contact, audit, assignment, and notification work.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FLOW_ID_DEFAULT = "f2144020-8c86-f111-ab0e-70a8a52eccae"
SEND_INVITATION_WORKFLOW_ID = "15c03c8d-754f-4386-a62c-cf7e91337ebd"
POWERPAGES_SITE_ID = "fccc0cc6-7f5e-4885-aeb8-2272e68130a3"
DATAVERSE_CONNECTION = "shared_commondataserviceforapps"

STATUS_PENDING = 100000000
STATUS_PROCESSING = 100000001
STATUS_COMPLETED = 100000002
STATUS_FAILED = 100000003
STATUS_NEEDS_REVIEW = 100000005
REQUEST_TYPE_NEW_USER = 100000000
REQUEST_TYPE_EXISTING_USER = 100000001
INVITATION_STATUS_MANUAL_DELIVERY_REQUIRED = 100000001
INVITATION_DELIVERY_MODE_EMAIL = 100000000
INVITATION_DELIVERY_MODE_MANUAL_CODE = 100000001
INVITATION_DELIVERY_MODE_ASSIGNMENT_NOTIFICATION = 100000002
NOTIFICATION_DELIVERY_MODE_EMAIL = 100000001
MAILBOX_STATUS_TESTED_AND_ENABLED = 100000003

AUDIT_ACTION_INVITE_USER = 100000000
AUDIT_ACTION_ASSIGN_FORM = 100000002
AUDIT_RESULT_REQUESTED = 100000000
AUDIT_RESULT_SUCCEEDED = 100000001
AUDIT_SCOPE_PLATFORM = 100000000
AUDIT_SCOPE_FORM_VERSION = 100000003
ASSIGNMENT_LIFECYCLE_ACTIVE = 100000000


def load_deploy_module() -> Any:
    module_path = Path(__file__).resolve().parent / "dataverse-schema-deploy.py"
    spec = importlib.util.spec_from_file_location("dataverse_schema_deploy", module_path)
    if not spec or not spec.loader:
        raise SystemExit(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["dataverse_schema_deploy"] = module
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Patch the TACATDP onboarding queue processor flow definition.")
    parser.add_argument("--env-file", default=".env", help="Environment file containing Power Platform settings.")
    parser.add_argument("--flow-id", default=FLOW_ID_DEFAULT, help="Existing solution-aware cloud flow workflowid to patch.")
    parser.add_argument("--sender-system-user-id", default=None, help="Dataverse systemuser id to use as assignment notification sender. Defaults to the flow owner.")
    parser.add_argument("--send-invitation-workflow-id", default=SEND_INVITATION_WORKFLOW_ID, help="Native Power Pages Send Invitation workflow id.")
    parser.add_argument("--powerpages-site-id", default=POWERPAGES_SITE_ID, help="Power Pages site id to bind native invitations.")
    parser.add_argument("--powerpages-base-url", default="https://tacatdp.powerappsportals.com", help="Public Power Pages base URL used to build manual invitation redemption links.")
    parser.add_argument("--invitation-expiry-days", type=int, default=14, help="Number of days before a created invitation expires.")
    parser.add_argument("--invitation-delivery-mode", choices=("email", "manual-code"), default="manual-code", help="New-user invitation delivery mode to write back to the queue row.")
    parser.add_argument("--artifact-dir", default="artifacts/powerautomate", help="Directory for before/after flow snapshots.")
    parser.add_argument("--execute", action="store_true", help="Patch the live Dataverse flow. Without this flag, write only the planned snapshot.")
    return parser.parse_args()


def normalize_guid(value: str, label: str) -> str:
    value = (value or "").strip().strip("{}")
    if len(value) != 36 or value.count("-") != 4:
        raise SystemExit(f"{label} must be a GUID.")
    return value


def normalize_base_url(value: str) -> str:
    value = (value or "").strip().rstrip("/")
    if not value.startswith(("https://", "http://")):
        raise SystemExit("--powerpages-base-url must start with https:// or http://.")
    return value


def normalize_expiry_days(value: int) -> int:
    if value < 1 or value > 90:
        raise SystemExit("--invitation-expiry-days must be between 1 and 90.")
    return value


def parse_clientdata(flow: dict[str, Any]) -> dict[str, Any]:
    raw = flow.get("clientdata") or "{}"
    data = json.loads(raw)
    data.setdefault("schemaVersion", "1.0.0.0")
    data.setdefault("properties", {})
    data["properties"].setdefault("connectionReferences", {})
    data["properties"].setdefault("definition", {})
    return data


def dataverse_host(operation_id: str) -> dict[str, str]:
    return {
        "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
        "connectionName": DATAVERSE_CONNECTION,
        "operationId": operation_id,
    }


def dataverse_auth() -> str:
    return "@parameters('$authentication')"


def openapi_action(operation_id: str, parameters: dict[str, Any], run_after: dict[str, list[str]] | None = None) -> dict[str, Any]:
    return {
        "runAfter": run_after or {},
        "type": "OpenApiConnection",
        "inputs": {
            "host": dataverse_host(operation_id),
            "parameters": parameters,
            "authentication": dataverse_auth(),
        },
    }


def update_request_action(item: dict[str, Any], run_after: dict[str, list[str]] | None = None) -> dict[str, Any]:
    return openapi_action(
        "UpdateRecord",
        {
            "entityName": "mp_onboardingrequests",
            "recordId": "@triggerOutputs()?['body/mp_onboardingrequestid']",
            "item": item,
        },
        run_after,
    )


def create_record_action(entity_name: str, item: dict[str, Any], run_after: dict[str, list[str]] | None = None) -> dict[str, Any]:
    return openapi_action("CreateRecord", {"entityName": entity_name, "item": item}, run_after)


def list_rows_action(entity_name: str, select: str, filter_expr: str, run_after: dict[str, list[str]] | None = None) -> dict[str, Any]:
    return openapi_action(
        "ListRecords",
        {
            "entityName": entity_name,
            "$select": select,
            "$filter": filter_expr,
            "$top": 1,
        },
        run_after,
    )


def perform_bound_action(entity_name: str, action_name: str, record_id: str, item: dict[str, Any], run_after: dict[str, list[str]]) -> dict[str, Any]:
    return openapi_action(
        "PerformBoundAction",
        {
            "entityName": entity_name,
            "actionName": action_name,
            "recordId": record_id,
            "item": item,
        },
        run_after,
    )


def compose(inputs: Any, run_after: dict[str, list[str]] | None = None) -> dict[str, Any]:
    return {
        "runAfter": run_after or {},
        "type": "Compose",
        "inputs": inputs,
    }


def parse_form_scope() -> dict[str, Any]:
    return {
        "runAfter": {"Set_Request_Processing": ["Succeeded"]},
        "type": "ParseJson",
        "inputs": {
            "content": "@triggerOutputs()?['body/mp_formscopejson']",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "formId": {"type": ["string", "null"]},
                        "formName": {"type": ["string", "null"]},
                        "formVersionId": {"type": "string"},
                    },
                    "required": ["formVersionId"],
                },
            },
        },
    }


def create_contact_condition() -> dict[str, Any]:
    return {
        "runAfter": {"Find_Contact_By_Email": ["Succeeded"]},
        "type": "If",
        "expression": {
            "equals": [
                "@length(outputs('Find_Contact_By_Email')?['body/value'])",
                0,
            ],
        },
        "actions": {
            "Create_Contact_When_Missing": create_record_action(
                "contacts",
                {
                    "fullname": "@triggerOutputs()?['body/mp_fullname']",
                    "lastname": "@coalesce(triggerOutputs()?['body/mp_fullname'], triggerOutputs()?['body/mp_email'])",
                    "emailaddress1": "@triggerOutputs()?['body/mp_email']",
                },
            ),
        },
        "else": {"actions": {}},
    }


def create_request_audit_action() -> dict[str, Any]:
    return create_record_action(
        "mp_accessauditlogs",
        {
            "mp_auditkey": "@concat('access:', utcNow(), ':', triggerOutputs()?['body/mp_actoremail'], ':InviteUser:', triggerOutputs()?['body/mp_email'], ':', triggerOutputs()?['body/mp_requestid'])",
            "mp_action": AUDIT_ACTION_INVITE_USER,
            "mp_resultstatus": AUDIT_RESULT_REQUESTED,
            "mp_actoremail": "@triggerOutputs()?['body/mp_actoremail']",
            "mp_actorrolesjson": "@triggerOutputs()?['body/mp_actorrolesjson']",
            "mp_affectedemail": "@triggerOutputs()?['body/mp_email']",
            "mp_AffectedContact@odata.bind": "@concat('/contacts(', outputs('Resolve_Contact_Id'), ')')",
            "mp_targetrole": "@triggerOutputs()?['body/mp_targetrole']",
            "mp_scopetype": AUDIT_SCOPE_PLATFORM,
            "mp_newstatejson": "@string(triggerOutputs()?['body'])",
            "mp_reason": "@triggerOutputs()?['body/mp_reason']",
            "mp_sourceroute": "@triggerOutputs()?['body/mp_sourceroute']",
            "mp_requestid": "@triggerOutputs()?['body/mp_requestid']",
            "mp_occurredat": "@utcNow()",
            "mp_resultmessage": "Onboarding request accepted for server-side processing.",
        },
        {"Resolve_Contact_Id": ["Succeeded"]},
    )


def create_assignment_loop() -> dict[str, Any]:
    return {
        "runAfter": {
            "Create_Request_Audit": ["Succeeded"],
            "Parse_Form_Scope": ["Succeeded"],
        },
        "type": "Foreach",
        "foreach": "@body('Parse_Form_Scope')",
        "actions": {
            "Find_Existing_Form_Assignment": list_rows_action(
                "mp_formassignments",
                "mp_formassignmentid,mp_assignmentkey,mp_useremail,_mp_formversion_value",
                "@concat('mp_useremail eq ''', triggerOutputs()?['body/mp_email'], ''' and _mp_formversion_value eq ', items('Apply_Form_Assignments')?['formVersionId'])",
            ),
            "Create_Assign_Form_Audit": create_record_action(
                "mp_accessauditlogs",
                {
                    "mp_auditkey": "@concat('access:', utcNow(), ':', triggerOutputs()?['body/mp_actoremail'], ':AssignForm:', triggerOutputs()?['body/mp_email'], ':', items('Apply_Form_Assignments')?['formVersionId'], ':', triggerOutputs()?['body/mp_requestid'])",
                    "mp_action": AUDIT_ACTION_ASSIGN_FORM,
                    "mp_resultstatus": AUDIT_RESULT_REQUESTED,
                    "mp_actoremail": "@triggerOutputs()?['body/mp_actoremail']",
                    "mp_actorrolesjson": "@triggerOutputs()?['body/mp_actorrolesjson']",
                    "mp_affectedemail": "@triggerOutputs()?['body/mp_email']",
                    "mp_AffectedContact@odata.bind": "@concat('/contacts(', outputs('Resolve_Contact_Id'), ')')",
                    "mp_targetrole": "@triggerOutputs()?['body/mp_targetrole']",
                    "mp_scopetype": AUDIT_SCOPE_FORM_VERSION,
                    "mp_FormVersion@odata.bind": "@concat('/mp_formversions(', items('Apply_Form_Assignments')?['formVersionId'], ')')",
                    "mp_newstatejson": "@string(items('Apply_Form_Assignments'))",
                    "mp_reason": "@triggerOutputs()?['body/mp_reason']",
                    "mp_sourceroute": "@triggerOutputs()?['body/mp_sourceroute']",
                    "mp_requestid": "@concat(triggerOutputs()?['body/mp_requestid'], ':', items('Apply_Form_Assignments')?['formVersionId'])",
                    "mp_occurredat": "@utcNow()",
                    "mp_resultmessage": "Form assignment requested.",
                },
                {"Find_Existing_Form_Assignment": ["Succeeded"]},
            ),
            "Create_Form_Assignment_When_Missing": {
                "runAfter": {"Create_Assign_Form_Audit": ["Succeeded"]},
                "type": "If",
                "expression": {
                    "equals": [
                        "@length(outputs('Find_Existing_Form_Assignment')?['body/value'])",
                        0,
                    ],
                },
                "actions": {
                    "Create_Form_Assignment": create_record_action(
                        "mp_formassignments",
                        {
                            "mp_useremail": "@triggerOutputs()?['body/mp_email']",
                            "mp_assignmentkey": "@concat(triggerOutputs()?['body/mp_email'], ':', items('Apply_Form_Assignments')?['formVersionId'])",
                            "mp_lifecyclestatus": ASSIGNMENT_LIFECYCLE_ACTIVE,
                            "mp_FormVersion@odata.bind": "@concat('/mp_formversions(', items('Apply_Form_Assignments')?['formVersionId'], ')')",
                        },
                    ),
                },
                "else": {"actions": {}},
            },
        },
    }


def create_invitation_action(site_id: str, expiry_days: int) -> dict[str, Any]:
    return create_record_action(
        "adx_invitations",
        {
            "adx_name": "@concat('Impact Monitoring invitation - ', triggerOutputs()?['body/mp_email'])",
            "adx_type": 756150000,
            "adx_maximumredemptions": 1,
            "adx_invitationcode": "@guid()",
            "adx_expirydate": f"@addDays(utcNow(), {expiry_days})",
            "adx_inviteContact@odata.bind": "@concat('/contacts(', outputs('Resolve_Contact_Id'), ')')",
            "mspp_websiteid@odata.bind": f"/powerpagesites({site_id})",
        },
    )


def email_delivery_ready_expression() -> str:
    row = "first(outputs('Find_Notification_Delivery_Setting')?['body/value'])"
    return (
        "@and("
        "greater(length(outputs('Find_Notification_Delivery_Setting')?['body/value']), 0),"
        f"equals({row}?['mp_deliverymode'], {NOTIFICATION_DELIVERY_MODE_EMAIL}),"
        f"equals({row}?['mp_mailboxstatus'], {MAILBOX_STATUS_TESTED_AND_ENABLED}),"
        f"not(empty({row}?['mp_sendermailbox']))"
        ")"
    )


def update_invitation_result_action(base_url: str, run_after: dict[str, list[str]]) -> dict[str, Any]:
    return update_request_action(
        {
            "mp_invitationid": "@outputs('Create_Native_Power_Pages_Invitation')?['body/adx_invitationid']",
            "mp_invitationcode": "@outputs('Create_Native_Power_Pages_Invitation')?['body/adx_invitationcode']",
            "mp_invitationexpiresat": "@outputs('Create_Native_Power_Pages_Invitation')?['body/adx_expirydate']",
            "mp_invitationstatus": INVITATION_STATUS_MANUAL_DELIVERY_REQUIRED,
            "mp_invitationdeliverymode": f"@if(outputs('Determine_Email_Delivery_Readiness'), {INVITATION_DELIVERY_MODE_EMAIL}, {INVITATION_DELIVERY_MODE_MANUAL_CODE})",
            "mp_invitationredeemurl": f"@concat('{base_url}/register/?returnurl=%2f&invitation=', outputs('Create_Native_Power_Pages_Invitation')?['body/adx_invitationcode'])",
            "mp_resultmessage": "@if(outputs('Determine_Email_Delivery_Readiness'), 'Invitation created and native Send Invitation workflow was requested. Confirm email delivery or redemption before treating onboarding as complete.', 'Invitation created. Mailbox delivery is not configured; issue the invitation code through an approved internal channel.')",
        },
        run_after,
    )


def create_assignment_email_action(sender_system_user_id: str) -> dict[str, Any]:
    return create_record_action(
        "emails",
        {
            "subject": "@concat('Impact Monitoring access updated - ', coalesce(triggerOutputs()?['body/mp_projectname'], 'Project assignment'))",
            "description": "@concat('<p>Hello ', coalesce(triggerOutputs()?['body/mp_fullname'], triggerOutputs()?['body/mp_email']), ',</p><p>Your Impact Monitoring access has been updated.</p><p><strong>Project:</strong> ', coalesce(triggerOutputs()?['body/mp_projectname'], 'Assigned project'), '</p><p><strong>Role:</strong> ', coalesce(triggerOutputs()?['body/mp_targetrole'], 'Assigned user'), '</p><p>Please sign in to the portal using your Microsoft account.</p>')",
            "email_activity_parties": [
                {
                    "partyid_systemuser@odata.bind": f"/systemusers({sender_system_user_id})",
                    "participationtypemask": 1,
                },
                {
                    "partyid_contact@odata.bind": "@concat('/contacts(', outputs('Resolve_Contact_Id'), ')')",
                    "participationtypemask": 2,
                },
            ],
        },
    )


def route_notification_action(send_invitation_workflow_id: str, site_id: str, sender_system_user_id: str, base_url: str, expiry_days: int) -> dict[str, Any]:
    invitation_actions = {
        "Create_Native_Power_Pages_Invitation": create_invitation_action(site_id, expiry_days),
        "Determine_Email_Delivery_Readiness": compose(
            email_delivery_ready_expression(),
            {"Create_Native_Power_Pages_Invitation": ["Succeeded"]},
        ),
        "Run_Native_Send_Invitation_When_Ready": {
            "runAfter": {"Determine_Email_Delivery_Readiness": ["Succeeded"]},
            "type": "If",
            "expression": {
                "equals": [
                    "@outputs('Determine_Email_Delivery_Readiness')",
                    True,
                ],
            },
            "actions": {
                "Run_Native_Send_Invitation_Workflow": perform_bound_action(
                    "workflows",
                    "Microsoft.Dynamics.CRM.ExecuteWorkflow",
                    send_invitation_workflow_id,
                    {
                        "EntityId": "@outputs('Create_Native_Power_Pages_Invitation')?['body/adx_invitationid']",
                    },
                    {},
                ),
            },
            "else": {"actions": {}},
        },
        "Update_Request_Invitation_Result": update_invitation_result_action(base_url, {"Run_Native_Send_Invitation_When_Ready": ["Succeeded"]}),
    }
    return {
        "runAfter": {"Find_Notification_Delivery_Setting": ["Succeeded"]},
        "type": "If",
        "expression": {
            "equals": [
                "@triggerOutputs()?['body/mp_requesttype']",
                REQUEST_TYPE_NEW_USER,
            ],
        },
        "actions": invitation_actions,
        "else": {
            "actions": {
                "Create_Dataverse_Assignment_Email": create_assignment_email_action(sender_system_user_id),
                "Update_Request_Assignment_Notification_Result": update_request_action(
                    {
                        "mp_invitationstatus": INVITATION_STATUS_MANUAL_DELIVERY_REQUIRED,
                        "mp_invitationdeliverymode": INVITATION_DELIVERY_MODE_ASSIGNMENT_NOTIFICATION,
                        "mp_resultmessage": "Assignment completed. Dataverse notification email was created but requires mailbox send approval/review.",
                    },
                    {"Create_Dataverse_Assignment_Email": ["Succeeded"]},
                ),
            },
        },
    }


def build_triggers() -> dict[str, Any]:
    return {
        "When_an_onboarding_request_is_pending": {
            "type": "OpenApiConnectionWebhook",
            "inputs": {
                "host": dataverse_host("SubscribeWebhookTrigger"),
                "parameters": {
                    "subscriptionRequest/message": 4,
                    "subscriptionRequest/entityname": "mp_onboardingrequest",
                    "subscriptionRequest/scope": 4,
                    "subscriptionRequest/filteringattributes": "mp_status",
                    "subscriptionRequest/filterexpression": f"mp_status eq {STATUS_PENDING}",
                },
                "authentication": dataverse_auth(),
            },
        },
    }


def build_actions(send_invitation_workflow_id: str, site_id: str, sender_system_user_id: str, base_url: str, expiry_days: int, delivery_mode: str) -> dict[str, Any]:
    return {
        "Set_Request_Processing": update_request_action(
            {
                "mp_status": STATUS_PROCESSING,
                "mp_processingattempts": "@add(coalesce(triggerOutputs()?['body/mp_processingattempts'], 0), 1)",
                "mp_lastattemptat": "@utcNow()",
                "mp_resultmessage": "Processing onboarding request.",
                "mp_errorcategory": None,
                "mp_errorjson": None,
            },
        ),
        "Parse_Form_Scope": parse_form_scope(),
        "Find_Contact_By_Email": list_rows_action(
            "contacts",
            "contactid,fullname,emailaddress1,statecode",
            "@concat('emailaddress1 eq ''', triggerOutputs()?['body/mp_email'], ''' and statecode eq 0')",
            {"Set_Request_Processing": ["Succeeded"]},
        ),
        "Create_Contact_Route": create_contact_condition(),
        "Resolve_Contact_Id": compose(
            "@if(greater(length(outputs('Find_Contact_By_Email')?['body/value']), 0), first(outputs('Find_Contact_By_Email')?['body/value'])?['contactid'], actions('Create_Contact_When_Missing')?['outputs']?['body/contactid'])",
            {"Create_Contact_Route": ["Succeeded"]},
        ),
        "Update_Request_Contact": update_request_action(
            {"mp_contactid": "@outputs('Resolve_Contact_Id')"},
            {"Resolve_Contact_Id": ["Succeeded"]},
        ),
        "Create_Request_Audit": create_request_audit_action(),
        "Apply_Form_Assignments": create_assignment_loop(),
        "Find_Notification_Delivery_Setting": list_rows_action(
            "mp_notificationdeliverysettings",
            "mp_notificationdeliverysettingid,mp_settingkey,mp_deliverymode,mp_sendermailbox,mp_mailboxstatus",
            "mp_settingkey eq 'onboarding-delivery'",
            {"Apply_Form_Assignments": ["Succeeded"]},
        ),
        "Route_Email_Delivery": route_notification_action(send_invitation_workflow_id, site_id, sender_system_user_id, base_url, expiry_days),
        "Set_Request_Needs_Review": update_request_action(
            {
                "mp_status": STATUS_NEEDS_REVIEW,
                "mp_completedat": "@utcNow()",
                "mp_resultmessage": "Onboarding server-side writes completed. Review invitation or notification delivery before treating onboarding as complete.",
                "mp_auditkey": "@outputs('Create_Request_Audit')?['body/mp_auditkey']",
            },
            {"Route_Email_Delivery": ["Succeeded"]},
        ),
        "Set_Request_Failed_On_Error": update_request_action(
            {
                "mp_status": STATUS_FAILED,
                "mp_resultmessage": "Onboarding request failed during server-side processing. Review the flow run history.",
                "mp_errorcategory": "processor-failed",
                "mp_errorjson": "@json(concat('{\"failedAt\":\"', utcNow(), '\",\"message\":\"Review Power Automate run history for this request.\"}'))",
            },
            {
                "Set_Request_Processing": ["Failed", "TimedOut"],
                "Parse_Form_Scope": ["Failed", "TimedOut"],
                "Find_Contact_By_Email": ["Failed", "TimedOut"],
                "Create_Contact_Route": ["Failed", "TimedOut"],
                "Resolve_Contact_Id": ["Failed", "TimedOut"],
                "Update_Request_Contact": ["Failed", "TimedOut"],
                "Create_Request_Audit": ["Failed", "TimedOut"],
                "Apply_Form_Assignments": ["Failed", "TimedOut"],
                "Find_Notification_Delivery_Setting": ["Failed", "TimedOut"],
                "Route_Email_Delivery": ["Failed", "TimedOut"],
            },
        ),
    }


def build_definition(send_invitation_workflow_id: str, site_id: str, sender_system_user_id: str, base_url: str, expiry_days: int, delivery_mode: str) -> dict[str, Any]:
    return {
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "$authentication": {"defaultValue": {}, "type": "SecureObject"},
            "$connections": {"defaultValue": {}, "type": "Object"},
        },
        "triggers": build_triggers(),
        "actions": build_actions(send_invitation_workflow_id, site_id, sender_system_user_id, base_url, expiry_days, delivery_mode),
    }


def write_snapshot(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    flow_id = normalize_guid(args.flow_id, "--flow-id")
    send_invitation_workflow_id = normalize_guid(args.send_invitation_workflow_id, "--send-invitation-workflow-id")
    site_id = normalize_guid(args.powerpages_site_id, "--powerpages-site-id")
    base_url = normalize_base_url(args.powerpages_base_url)
    expiry_days = normalize_expiry_days(args.invitation_expiry_days)

    deploy = load_deploy_module()
    settings = deploy.build_settings(argparse.Namespace(env_file=args.env_file, schema_dir=None, schema_file=None, execute=False, no_publish=False))
    dv = deploy.Dataverse(settings, deploy.get_token(settings))

    flow = dv.get_json(f"workflows({flow_id})?$select=workflowid,name,category,statecode,statuscode,clientdata,_ownerid_value")
    if not flow:
        raise SystemExit(f"Flow not found: {flow_id}")
    sender_system_user_id = normalize_guid(args.sender_system_user_id or flow.get("_ownerid_value") or "", "--sender-system-user-id")

    clientdata = parse_clientdata(flow)
    before = deepcopy(clientdata)
    clientdata["properties"]["connectionReferences"] = {
        DATAVERSE_CONNECTION: {
            "runtimeSource": "embedded",
            "connection": {},
            "api": {"name": DATAVERSE_CONNECTION},
        },
    }
    clientdata["properties"]["definition"] = build_definition(send_invitation_workflow_id, site_id, sender_system_user_id, base_url, expiry_days, args.invitation_delivery_mode)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    artifact_dir = Path(args.artifact_dir)
    before_path = artifact_dir / f"tacatdp-onboarding-queue-processor-before-{stamp}.json"
    planned_path = artifact_dir / f"tacatdp-onboarding-queue-processor-planned-{stamp}.json"
    write_snapshot(before_path, before)
    write_snapshot(planned_path, clientdata)

    if args.execute:
        response = dv.request(
            "PATCH",
            f"workflows({flow_id})",
            payload={
                "name": "TACATDP - Onboarding Queue Processor",
                "primaryentity": "mp_onboardingrequest",
                "clientdata": json.dumps(clientdata, separators=(",", ":")),
            },
        )
        if response.status_code >= 400:
            raise RuntimeError(f"PATCH flow failed: HTTP {response.status_code} {deploy.safe_error(response)}")
        print("updated: TACATDP onboarding queue processor flow definition")
    else:
        print("planned: TACATDP onboarding queue processor patch written")
    print(f"flow-id: {flow_id}")
    print(f"planned-snapshot: {planned_path}")
    print(f"sender-system-user-id: {sender_system_user_id}")
    print(f"powerpages-base-url: {base_url}")
    print(f"invitation-expiry-days: {expiry_days}")
    print(f"invitation-delivery-mode: {args.invitation_delivery_mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
