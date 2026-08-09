#!/usr/bin/env python3
"""Configure the TACATDP Power Pages onboarding cloud flow.

The flow is intentionally Dataverse-native:
- new users receive the native Power Pages invitation workflow;
- existing users receive a Dataverse email activity sent through SendEmail.

Office 365 Outlook remains a documented future provider option, but this script
does not add or require an Outlook connector.
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

FLOW_ID_DEFAULT = "6b315273-ba85-f111-ab0e-6045bdde781c"
SEND_INVITATION_WORKFLOW_ID = "eb467141-a276-f111-ab0e-70a8a52d4a92"
POWERPAGES_SITE_ID = "fccc0cc6-7f5e-4885-aeb8-2272e68130a3"
DATAVERSE_CONNECTION = "shared_commondataserviceforapps"
ENSURE_CONTACT_DELIVERY_TYPE = "EnsureContact"
ASSIGNMENT_NOTIFICATION_DELIVERY_TYPE = "AssignmentNotification"


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
    parser = argparse.ArgumentParser(description="Patch the TACATDP onboarding cloud flow definition.")
    parser.add_argument("--env-file", default=".env", help="Environment file containing Power Platform settings.")
    parser.add_argument("--flow-id", default=FLOW_ID_DEFAULT, help="Cloud flow workflowid.")
    parser.add_argument("--sender-system-user-id", default=None, help="Dataverse systemuser id to use as assignment notification sender. Defaults to the flow owner.")
    parser.add_argument("--send-invitation-workflow-id", default=SEND_INVITATION_WORKFLOW_ID, help="Native Power Pages Send Invitation workflow id.")
    parser.add_argument("--powerpages-site-id", default=POWERPAGES_SITE_ID, help="Power Pages site id to bind native invitations.")
    parser.add_argument("--artifact-dir", default="artifacts/powerautomate", help="Directory for before/after flow snapshots.")
    parser.add_argument("--execute", action="store_true", help="Patch the live Dataverse flow. Without this flag, write only the planned snapshot.")
    return parser.parse_args()


def normalize_guid(value: str, label: str) -> str:
    value = value.strip().strip("{}")
    if len(value) != 36 or value.count("-") != 4:
        raise SystemExit(f"{label} must be a GUID.")
    return value


def parse_clientdata(flow: dict[str, Any]) -> dict[str, Any]:
    raw = flow.get("clientdata") or "{}"
    data = json.loads(raw)
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


def create_invitation_action(site_id: str) -> dict[str, Any]:
    return {
        "runAfter": {},
        "metadata": {"operationMetadataId": "590478de-f107-4e1c-b133-d7e875a428fe"},
        "type": "OpenApiConnection",
        "inputs": {
            "host": dataverse_host("CreateRecord"),
            "parameters": {
                "entityName": "adx_invitations",
                "item": {
                    "adx_name": "@{concat('TACATDP invitation - ', body('Parse_JSON')?['email'])}",
                    "adx_type": 756150000,
                    "adx_maximumredemptions": 1,
                    "adx_invitationcode": "@{guid()}",
                    "adx_inviteContact@odata.bind": "@{concat('/contacts(', body('Parse_JSON')?['contactId'], ')')}",
                    "mspp_websiteid@odata.bind": f"/powerpagesites({site_id})",
                },
            },
            "authentication": dataverse_auth(),
        },
    }


def send_invitation_workflow_action(workflow_id: str) -> dict[str, Any]:
    return {
        "runAfter": {"Create_native_Power_Pages_invitation": ["Succeeded"]},
        "metadata": {"operationMetadataId": "d9e0e190-1075-49bf-b558-79fa7168021a"},
        "type": "OpenApiConnection",
        "inputs": {
            "host": dataverse_host("PerformBoundAction"),
            "parameters": {
                "entityName": "workflows",
                "actionName": "Microsoft.Dynamics.CRM.ExecuteWorkflow",
                "recordId": workflow_id,
                "item": {
                    "EntityId": "@outputs('Create_native_Power_Pages_invitation')?['body/adx_invitationid']",
                },
            },
            "authentication": dataverse_auth(),
        },
    }


def create_contact_action() -> dict[str, Any]:
    return {
        "runAfter": {},
        "metadata": {"operationMetadataId": "056b2317-adf6-4a16-b129-b210524b7ebd"},
        "type": "OpenApiConnection",
        "inputs": {
            "host": dataverse_host("CreateRecord"),
            "parameters": {
                "entityName": "contacts",
                "item": {
                    "fullname": "@body('Parse_JSON')?['fullName']",
                    "lastname": "@body('Parse_JSON')?['fullName']",
                    "emailaddress1": "@body('Parse_JSON')?['email']",
                },
            },
            "authentication": dataverse_auth(),
        },
    }


def response_action(
    status: str,
    message_expression: str,
    request_id_expression: str = "@body('Parse_JSON')?['requestId']",
) -> dict[str, Any]:
    return {
        "runAfter": {},
        "metadata": {"operationMetadataId": "0ee92a99-7dfe-4241-b785-25deb49ccb4a"},
        "type": "Response",
        "kind": "PowerPages",
        "inputs": {
            "statusCode": 200,
            "body": {
                "status": status,
                "message": message_expression,
                "requestId": request_id_expression,
            },
        },
    }


def ensure_contact_response_action() -> dict[str, Any]:
    return {
        "runAfter": {"Create_Dataverse_onboarding_contact": ["Succeeded"]},
        "metadata": {"operationMetadataId": "a5f59ff2-6da8-4a60-8606-4cb0d6dcf56a"},
        "type": "Response",
        "kind": "PowerPages",
        "inputs": {
            "statusCode": 200,
            "body": {
                "status": "dataverse-contact-created",
                "message": "@{concat('Dataverse contact created for ', body('Parse_JSON')?['email'])}",
                "requestId": "@body('Parse_JSON')?['requestId']",
                "contactId": "@outputs('Create_Dataverse_onboarding_contact')?['body/contactid']",
                "created": True,
            },
        },
    }


def failure_response_action(
    run_after: dict[str, list[str]],
    status: str,
    message_expression: str,
    request_id_expression: str = "@body('Parse_JSON')?['requestId']",
) -> dict[str, Any]:
    return {
        "runAfter": run_after,
        "metadata": {"operationMetadataId": "07fe6f8c-5664-4c4d-84bf-f8252d861f75"},
        "type": "Response",
        "kind": "PowerPages",
        "inputs": {
            "statusCode": 200,
            "body": {
                "status": status,
                "message": message_expression,
                "requestId": request_id_expression,
            },
        },
    }


def create_assignment_email_action(sender_system_user_id: str) -> dict[str, Any]:
    return {
        "runAfter": {},
        "metadata": {"operationMetadataId": "f3190627-c0d4-44d8-8a4c-60b43754cbe4"},
        "type": "OpenApiConnection",
        "inputs": {
            "host": dataverse_host("CreateRecord"),
            "parameters": {
                "entityName": "emails",
                "item": {
                    "subject": "@{concat('Impact Monitoring access updated - ', coalesce(body('Parse_JSON')?['projectName'], 'Project assignment'))}",
                    "description": "@{concat('<p>Hello ', coalesce(body('Parse_JSON')?['fullName'], body('Parse_JSON')?['email']), ',</p><p>Your Impact Monitoring access has been updated.</p><p><strong>Project:</strong> ', coalesce(body('Parse_JSON')?['projectName'], 'Assigned project'), '</p><p><strong>Role:</strong> ', coalesce(body('Parse_JSON')?['role'], 'Assigned user'), '</p><p>Please sign in to the portal using your Microsoft account.</p>')}",
                    "email_activity_parties": [
                        {
                            "partyid_systemuser@odata.bind": f"/systemusers({sender_system_user_id})",
                            "participationtypemask": 1,
                        },
                        {
                            "partyid_contact@odata.bind": "@{concat('/contacts(', body('Parse_JSON')?['contactId'], ')')}",
                            "participationtypemask": 2,
                        },
                    ],
                },
            },
            "authentication": dataverse_auth(),
        },
    }


def send_assignment_email_action() -> dict[str, Any]:
    return {
        "runAfter": {"Create_Dataverse_assignment_email": ["Succeeded"]},
        "metadata": {"operationMetadataId": "bb64be7e-45eb-4f7f-a5e9-b6ec6365608e"},
        "type": "OpenApiConnection",
        "inputs": {
            "host": dataverse_host("PerformBoundAction"),
            "parameters": {
                "entityName": "emails",
                "actionName": "Microsoft.Dynamics.CRM.SendEmail",
                "recordId": "@outputs('Create_Dataverse_assignment_email')?['body/activityid']",
                "item": {
                    "IssueSend": True,
                    "TrackingToken": "",
                },
            },
            "authentication": dataverse_auth(),
        },
    }


def build_actions(existing_actions: dict[str, Any], sender_system_user_id: str, send_invitation_workflow_id: str, site_id: str) -> dict[str, Any]:
    parse_json = deepcopy(existing_actions.get("Parse_JSON") or {})
    parse_json.setdefault("runAfter", {})
    parse_json.setdefault("metadata", {"operationMetadataId": "9500aa77-8300-437f-b6ed-63283e635a98"})
    parse_json.setdefault("type", "ParseJson")
    parse_json.setdefault("inputs", {})
    # Power Pages passes the browser-side eventData string through to the flow
    # trigger. Parse the serialized business payload stored in that field.
    parse_json["inputs"]["content"] = "@triggerBody()?['eventData']"
    parse_json["inputs"]["schema"] = {
        "type": "object",
        "properties": {
            "requestId": {"type": "string"},
            "deliveryType": {"type": "string"},
            "contactId": {"type": "string"},
            "email": {"type": "string"},
            "fullName": {"type": "string"},
            "role": {"type": "string"},
            "projectName": {"type": "string"},
            "reason": {"type": "string"},
            "actorEmail": {"type": "string"},
            "assignmentResults": {"type": "array"},
            "sourceRoute": {"type": "string"},
            "occurredAt": {"type": "string"},
        },
    }

    invitation_response = response_action(
        "native-invitation-requested",
        "@{concat('Native Power Pages invitation requested for ', body('Parse_JSON')?['email'])}",
    )
    invitation_response["runAfter"] = {"Run_native_Send_Invitation_workflow": ["Succeeded"]}

    assignment_response = response_action(
        "dataverse-assignment-notification-sent",
        "@{concat('Dataverse assignment notification requested for ', body('Parse_JSON')?['email'])}",
    )
    assignment_response["runAfter"] = {"Send_Dataverse_assignment_email": ["Succeeded"]}

    invitation_create_failed = failure_response_action(
        {"Create_native_Power_Pages_invitation": ["Failed", "TimedOut"]},
        "native-invitation-create-failed",
        "@{coalesce(actions('Create_native_Power_Pages_invitation')?['error']?['message'], 'Native Power Pages invitation create failed.')}",
    )
    invitation_workflow_failed = failure_response_action(
        {"Run_native_Send_Invitation_workflow": ["Failed", "TimedOut"]},
        "native-invitation-workflow-failed",
        "@{coalesce(actions('Run_native_Send_Invitation_workflow')?['error']?['message'], 'Native Power Pages Send Invitation workflow failed.')}",
    )
    assignment_email_create_failed = failure_response_action(
        {"Create_Dataverse_assignment_email": ["Failed", "TimedOut"]},
        "dataverse-assignment-email-create-failed",
        "@{coalesce(actions('Create_Dataverse_assignment_email')?['error']?['message'], 'Dataverse assignment email create failed.')}",
    )
    assignment_email_send_failed = failure_response_action(
        {"Send_Dataverse_assignment_email": ["Failed", "TimedOut"]},
        "dataverse-assignment-email-send-failed",
        "@{coalesce(actions('Send_Dataverse_assignment_email')?['error']?['message'], 'Dataverse assignment email send failed.')}",
    )

    email_route = {
        "runAfter": {},
        "metadata": {"operationMetadataId": "058e135e-3d0e-43ea-82d1-c92a969a65e9"},
        "type": "If",
        "expression": {
            "equals": [
                "@body('Parse_JSON')?['deliveryType']",
                "PowerPagesInvitation",
            ],
        },
        "actions": {
            "Create_native_Power_Pages_invitation": create_invitation_action(site_id),
            "Run_native_Send_Invitation_workflow": send_invitation_workflow_action(send_invitation_workflow_id),
            "Respond_to_Power_Pages": invitation_response,
            "Respond_to_Power_Pages_Invitation_Create_Failed": invitation_create_failed,
            "Respond_to_Power_Pages_Invitation_Workflow_Failed": invitation_workflow_failed,
        },
        "else": {
            "actions": {
                "Create_Dataverse_assignment_email": create_assignment_email_action(sender_system_user_id),
                "Send_Dataverse_assignment_email": send_assignment_email_action(),
                "Respond_to_Power_Pages_Assignment": assignment_response,
                "Respond_to_Power_Pages_Assignment_Email_Create_Failed": assignment_email_create_failed,
                "Respond_to_Power_Pages_Assignment_Email_Send_Failed": assignment_email_send_failed,
            },
        },
    }

    parse_failed = failure_response_action(
        {"Parse_JSON": ["Failed", "TimedOut"]},
        "onboarding-payload-parse-failed",
        "@{coalesce(actions('Parse_JSON')?['error']?['message'], 'Onboarding flow could not parse the Power Pages payload.')}",
        "@triggerBody()?['eventData']",
    )
    contact_create_failed = failure_response_action(
        {"Create_Dataverse_onboarding_contact": ["Failed", "TimedOut"]},
        "dataverse-contact-create-failed",
        "@{coalesce(actions('Create_Dataverse_onboarding_contact')?['error']?['message'], 'Dataverse contact create failed.')}",
    )

    return {
        "Parse_JSON": parse_json,
        "Respond_to_Power_Pages_Parse_Failed": parse_failed,
        "Route_delivery_type": {
            "runAfter": {"Parse_JSON": ["Succeeded"]},
            "metadata": {"operationMetadataId": "7c66a6f1-2d51-49be-8dbb-1f962a359e31"},
            "type": "If",
            "expression": {
                "equals": [
                    "@body('Parse_JSON')?['deliveryType']",
                    ENSURE_CONTACT_DELIVERY_TYPE,
                ],
            },
            "actions": {
                "Create_Dataverse_onboarding_contact": create_contact_action(),
                "Respond_to_Power_Pages_Contact": ensure_contact_response_action(),
                "Respond_to_Power_Pages_Contact_Create_Failed": contact_create_failed,
            },
            "else": {
                "actions": {
                    "Route_email_delivery_type": email_route,
                },
            },
        },
    }


def build_triggers(existing_triggers: dict[str, Any]) -> dict[str, Any]:
    manual = deepcopy(existing_triggers.get("manual") or {})
    manual.setdefault("metadata", {"operationMetadataId": "82d6ab24-7be7-443e-8047-cb19cf22fb7a"})
    manual["type"] = "Request"
    manual["kind"] = "PowerPages"
    manual["inputs"] = {
        "schema": {
            "type": "object",
            "properties": {
                "eventData": {
                    "type": "string",
                    "x-ms-dynamically-added": True,
                },
                "requestId": {
                    "type": "string",
                    "x-ms-dynamically-added": True,
                },
                "deliveryType": {
                    "type": "string",
                    "x-ms-dynamically-added": True,
                },
                "contactId": {
                    "type": "string",
                    "x-ms-dynamically-added": True,
                },
                "email": {
                    "type": "string",
                    "x-ms-dynamically-added": True,
                },
                "fullName": {
                    "type": "string",
                    "x-ms-dynamically-added": True,
                },
                "role": {
                    "type": "string",
                    "x-ms-dynamically-added": True,
                },
                "projectName": {
                    "type": "string",
                    "x-ms-dynamically-added": True,
                },
                "reason": {
                    "type": "string",
                    "x-ms-dynamically-added": True,
                },
                "actorEmail": {
                    "type": "string",
                    "x-ms-dynamically-added": True,
                },
                "assignmentResults": {
                    "type": "array",
                    "x-ms-dynamically-added": True,
                },
                "sourceRoute": {
                    "type": "string",
                    "x-ms-dynamically-added": True,
                },
                "occurredAt": {
                    "type": "string",
                    "x-ms-dynamically-added": True,
                },
            },
            "required": [
                "eventData",
            ],
        },
    }
    return {"manual": manual}


def write_snapshot(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    flow_id = normalize_guid(args.flow_id, "--flow-id")
    send_invitation_workflow_id = normalize_guid(args.send_invitation_workflow_id, "--send-invitation-workflow-id")
    site_id = normalize_guid(args.powerpages_site_id, "--powerpages-site-id")

    deploy = load_deploy_module()
    settings = deploy.build_settings(argparse.Namespace(env_file=args.env_file, schema_dir=None, schema_file=None))
    token = deploy.get_token(settings)
    dv = deploy.Dataverse(settings, token)

    flow = dv.get_json(f"workflows({flow_id})?$select=workflowid,name,category,statecode,statuscode,clientdata,_ownerid_value")
    if not flow:
        raise SystemExit(f"Flow not found: {flow_id}")
    sender_system_user_id = normalize_guid(args.sender_system_user_id or flow.get("_ownerid_value") or "", "--sender-system-user-id")

    clientdata = parse_clientdata(flow)
    before = deepcopy(clientdata)
    properties = clientdata["properties"]
    connection_refs = properties.setdefault("connectionReferences", {})
    connection_refs.setdefault(DATAVERSE_CONNECTION, {
        "runtimeSource": "embedded",
        "connection": {},
        "api": {"name": DATAVERSE_CONNECTION},
    })
    definition = properties.setdefault("definition", {})
    definition.setdefault("$schema", "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#")
    definition.setdefault("contentVersion", "1.0.0.0")
    parameters = definition.setdefault("parameters", {})
    parameters.setdefault("$authentication", {"defaultValue": {}, "type": "SecureObject"})
    parameters.setdefault("$connections", {"defaultValue": {}, "type": "Object"})
    definition["triggers"] = build_triggers(definition.get("triggers") or {})
    definition["actions"] = build_actions(
        definition.get("actions") or {},
        sender_system_user_id,
        send_invitation_workflow_id,
        site_id,
    )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    artifact_dir = Path(args.artifact_dir)
    write_snapshot(artifact_dir / f"tacatdp-onboarding-flow-before-ensure-contact-{stamp}.json", before)
    write_snapshot(artifact_dir / f"tacatdp-onboarding-flow-ensure-contact-planned-{stamp}.json", clientdata)

    if args.execute:
        response = dv.request("PATCH", f"workflows({flow_id})", payload={
            "clientdata": json.dumps(clientdata, separators=(",", ":")),
        })
        if response.status_code >= 400:
            raise RuntimeError(f"PATCH flow failed: HTTP {response.status_code} {deploy.safe_error(response)}")
        print("updated: TACATDP onboarding flow uses Dataverse contact creation and native notifications")
    else:
        print("planned: TACATDP onboarding flow ensure-contact patch written")
    print(f"sender-system-user-id: {sender_system_user_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
