#!/usr/bin/env python3
"""Configure Power Pages Web API and table permissions for TACATDP ODK MVP.

Idempotent dev-only configuration for the Power Pages enhanced data model (`mspp_*`):
- creates/updates Webapi/<table>/enabled and Webapi/<table>/fields site settings;
- creates/updates Global table permissions;
- associates permissions to the Authenticated Users web role.

This uses Dataverse Web API as an admin/configuration channel. It does not use the
Power Pages `/_api`, because Microsoft documents portal configuration tables as
unsupported through the portals Web API.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

WEB_API_TABLES = [
    # metadata reads
    # Baseline import creates tracked entities that bind to an existing project.
    # Power Pages requires Append To on the referenced table for that association.
    {"logical": "mp_project", "name": "TACATDP Projects", "read": True, "create": False, "write": False, "delete": False, "append": False, "appendto": True},
    {"logical": "mp_form", "name": "TACATDP Forms", "read": True, "create": False, "write": False, "delete": False, "append": False, "appendto": False},
    # FormVersions remain read-only to portal users, but submission create binds
    # mp_submission.mp_FormVersion to an existing form version. Power Pages
    # requires Append To on the referenced table for that association.
    {"logical": "mp_formversion", "name": "TACATDP FormVersions", "read": True, "create": False, "write": False, "delete": False, "append": False, "appendto": True},
    {"logical": "mp_formassignment", "name": "TACATDP FormAssignments", "read": True, "create": False, "write": False, "delete": False, "append": False, "appendto": False},
    {"logical": "mp_formattachment", "name": "TACATDP FormAttachments", "read": True, "create": False, "write": False, "delete": False, "append": False, "appendto": False},
    # submission writes for dev POC; tighten before production with contact/self/custom access
    {"logical": "mp_submission", "name": "TACATDP Submissions", "read": True, "create": True, "write": True, "delete": False, "append": True, "appendto": True},
    {"logical": "mp_submissionversion", "name": "TACATDP SubmissionVersions", "read": True, "create": True, "write": True, "delete": False, "append": True, "appendto": True},
    {"logical": "mp_submissionattachment", "name": "TACATDP SubmissionAttachments", "read": True, "create": True, "write": True, "delete": False, "append": True, "appendto": True},
    # reporting projection reads for Data/Power BI guidance UX
    {"logical": "mp_submissionreportrow", "name": "TACATDP SubmissionReportRows", "read": True, "create": False, "write": False, "delete": False, "append": False, "appendto": False},
    {"logical": "mp_submissionrepeatrow", "name": "TACATDP SubmissionRepeatRows", "read": True, "create": False, "write": False, "delete": False, "append": False, "appendto": False},
    {"logical": "mp_submissionanswer", "name": "TACATDP SubmissionAnswers", "read": True, "create": False, "write": False, "delete": False, "append": False, "appendto": False},
    # named export settings for the upcoming export UX; dev prototype allows authenticated users to create/update settings
    {"logical": "mp_exportsetting", "name": "TACATDP ExportSettings", "read": True, "create": True, "write": True, "delete": False, "append": True, "appendto": True},
]
ACCESS_WRITE_TABLES = [
    {
        "logical": "mp_project",
        "name": "TACATDP Projects Admin Import",
        "read": True,
        "create": False,
        "write": False,
        "delete": False,
        "append": False,
        "appendto": True,
        "fields": "*",
    },
    {
        "logical": "contact",
        "name": "TACATDP Contacts Admin Onboarding",
        "read": True,
        "create": True,
        "write": True,
        "delete": False,
        "append": False,
        "appendto": False,
        "fields": "contactid,fullname,emailaddress1,statecode,adx_identity_username,adx_identity_logonenabled,adx_identity_emailaddress1confirmed",
    },
    {
        "logical": "adx_invitation",
        "name": "TACATDP Invitations Admin Diagnostics",
        "read": True,
        "create": False,
        "write": False,
        "delete": False,
        "append": False,
        "appendto": False,
        "fields": "adx_invitationid,adx_name,adx_expirydate,adx_invitecontact,statecode,statuscode,createdon,modifiedon",
    },
    {
        "logical": "adx_externalidentity",
        "name": "TACATDP ExternalIdentities Admin Diagnostics",
        "read": True,
        "create": False,
        "write": False,
        "delete": False,
        "append": False,
        "appendto": False,
        "fields": "adx_externalidentityid,adx_username,adx_contactid,createdon",
    },
    {
        "logical": "mp_accessauditlog",
        "name": "TACATDP AccessAuditLogs",
        "read": True,
        "create": True,
        "write": False,
        "delete": False,
        "append": False,
        "appendto": False,
        "fields": "mp_auditkey,mp_action,mp_resultstatus,mp_actoremail,mp_actorrolesjson,mp_affectedemail,mp_targetrole,mp_scopetype,mp_previousstatejson,mp_newstatejson,mp_reason,mp_sourceroute,mp_requestid,mp_occurredat,mp_resultmessage",
    },
    {
        "logical": "mp_formassignment",
        "name": "TACATDP FormAssignments Admin Write",
        "read": True,
        "create": True,
        "write": True,
        "delete": False,
        "append": True,
        "appendto": False,
        "fields": "mp_useremail,mp_assignmentkey,mp_formversion,mp_lifecyclestatus",
    },
    {
        "logical": "mp_formversion",
        "name": "TACATDP FormVersions Admin AppendTo",
        "read": True,
        "create": False,
        "write": False,
        "delete": False,
        "append": False,
        "appendto": True,
        "fields": "*",
    },
    {
        "logical": "mp_onboardingrequest",
        "name": "TACATDP OnboardingRequests Admin Queue",
        "read": True,
        "create": True,
        "write": True,
        "delete": False,
        "append": False,
        "appendto": False,
        "fields": "mp_requestkey,mp_requestid,mp_status,mp_requesttype,mp_fullname,mp_email,mp_targetrole,mp_projectid,mp_projectname,mp_formscopejson,mp_reason,mp_actoremail,mp_actorrolesjson,mp_sourceroute,mp_contactid,mp_processingattempts,mp_lastattemptat,mp_completedat,mp_resultmessage,mp_errorcategory,mp_errorjson,mp_auditkey,mp_invitationid,mp_invitationcode,mp_invitationredeemurl,mp_invitationexpiresat,mp_invitationstatus,mp_invitationdeliverymode,mp_replacementofrequestid",
    },
    {
        "logical": "mp_notificationdeliverysetting",
        "name": "TACATDP NotificationDeliverySettings Admin Config",
        "read": True,
        "create": True,
        "write": True,
        "delete": False,
        "append": False,
        "appendto": False,
        "fields": "mp_settingkey,mp_deliverymode,mp_sendermailbox,mp_mailboxstatus,mp_nativeinvitationworkflowid,mp_lasttestedat,mp_lasttestresult,mp_instructions,mp_updatedbyemail,mp_updatedat",
    },
]

GLOBAL_SCOPE = 756150000
SITE_SETTING_SOURCE_TABLE = 0


def load_deploy_module():
    module_path = Path(__file__).resolve().parent / "dataverse-schema-deploy.py"
    spec = importlib.util.spec_from_file_location("dataverse_schema_deploy", module_path)
    if not spec or not spec.loader:
        raise SystemExit(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["dataverse_schema_deploy"] = module
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Configure Power Pages Web API site settings and table permissions for TACATDP MVP.")
    parser.add_argument("--env-file", default=".env", help="Environment file containing Power Platform settings.")
    parser.add_argument("--website-id", default=None, help="Power Pages website id. Defaults to POWERPAGES_WEBSITE_ID or the first matching site name.")
    parser.add_argument("--site-name", default=None, help="Power Pages site name. Defaults to POWERPAGES_SITE_NAME or TACATDP Monitoring Tool.")
    parser.add_argument("--portal-user-email", default=None, help="Optional portal contact email to assign to the Authenticated Users web role.")
    parser.add_argument("--include-access-writes", action="store_true", help="Also configure administrator-only User & Access write prerequisites for Mshirika testing.")
    parser.add_argument("--access-role-name", default="Administrators", help="Power Pages web role that receives access-write permissions when --include-access-writes is set.")
    parser.add_argument("--onboarding-flow-trigger-id", default=None, help="Optional Power Pages cloud-flow trigger GUID for TACATDP onboarding email delivery.")
    parser.add_argument("--execute", action="store_true", help="Perform live writes. Without this flag only a dry-run summary is shown.")
    return parser.parse_args()


def escape_odata(value: str) -> str:
    return value.replace("'", "''")


def parse_guid_from_entity_id(value: str) -> str:
    return value.rsplit("(", 1)[-1].rstrip(")")


class PagesConfigClient:
    def __init__(self, deploy: Any, settings: Any, token: str) -> None:
        self.deploy = deploy
        self.dv = deploy.Dataverse(settings, token)

    def find_website(self, website_id: str | None, site_name: str) -> str:
        if website_id:
            data = self.dv.get_json(f"mspp_websites({website_id})?$select=mspp_websiteid,mspp_name")
            if not data:
                raise RuntimeError(f"Power Pages website not found: {website_id}")
            return data["mspp_websiteid"]
        data = self.dv.get_json(f"mspp_websites?$select=mspp_websiteid,mspp_name&$filter=mspp_name eq '{escape_odata(site_name)}'&$top=1")
        values = (data or {}).get("value") or []
        if not values:
            raise RuntimeError(f"Power Pages website not found by name: {site_name}")
        return values[0]["mspp_websiteid"]

    def find_authenticated_role(self, website_id: str) -> str:
        data = self.dv.get_json(
            "mspp_webroles?$select=mspp_webroleid,mspp_name,mspp_authenticatedusersrole"
            f"&$filter=_mspp_websiteid_value eq {website_id} and mspp_authenticatedusersrole eq true&$top=1"
        )
        values = (data or {}).get("value") or []
        if not values:
            raise RuntimeError("Authenticated Users web role not found for site")
        return values[0]["mspp_webroleid"]

    def find_role_by_name(self, website_id: str, role_name: str) -> str:
        data = self.dv.get_json(
            "mspp_webroles?$select=mspp_webroleid,mspp_name"
            f"&$filter=_mspp_websiteid_value eq {website_id} and mspp_name eq '{escape_odata(role_name)}'&$top=1"
        )
        values = (data or {}).get("value") or []
        if not values:
            raise RuntimeError(f"Power Pages web role not found for site: {role_name}")
        return values[0]["mspp_webroleid"]

    def find_contact_by_email(self, email: str) -> str | None:
        data = self.dv.get_json(
            "contacts?$select=contactid,emailaddress1,statecode"
            f"&$filter=emailaddress1 eq '{escape_odata(email)}'&$top=1"
        )
        values = (data or {}).get("value") or []
        if not values:
            return None
        if values[0].get("statecode") != 0:
            raise RuntimeError(f"Portal contact is not active: {email}")
        return values[0]["contactid"]

    def ensure_site_setting(self, website_id: str, name: str, value: str, execute: bool) -> str | None:
        data = self.dv.get_json(
            "mspp_sitesettings?$select=mspp_sitesettingid,mspp_value"
            f"&$filter=_mspp_websiteid_value eq {website_id} and mspp_name eq '{escape_odata(name)}'&$top=1"
        )
        values = (data or {}).get("value") or []
        payload = {
            "mspp_name": name,
            "mspp_value": value,
            "mspp_source": SITE_SETTING_SOURCE_TABLE,
            "mspp_websiteid@odata.bind": f"/mspp_websites({website_id})",
        }
        if values:
            record_id = values[0]["mspp_sitesettingid"]
            current_value = values[0].get("mspp_value")
            if name.endswith("/fields") and current_value == "*" and value != "*":
                print(f"exists: site setting {name}=*; preserving existing wildcard fields")
            elif current_value == value:
                print(f"exists: site setting {name}={value}")
            elif execute:
                response = self.dv.request("PATCH", f"mspp_sitesettings({record_id})", payload={"mspp_value": value})
                if response.status_code >= 400:
                    if not self.patch_enhanced_site_setting(record_id, value):
                        raise RuntimeError(f"PATCH site setting {name} failed: HTTP {response.status_code} {self.deploy.safe_error(response)}")
                print(f"updated: site setting {name}={value}")
            else:
                print(f"would update: site setting {name}={value}")
            return record_id
        if not execute:
            print(f"would create: site setting {name}={value}")
            return None
        response = self.dv.post("mspp_sitesettings", payload)
        print(f"created: site setting {name}={value}")
        return parse_guid_from_entity_id(response.headers.get("OData-EntityId", ""))

    def patch_enhanced_site_setting(self, component_id: str, value: str) -> bool:
        payload = {"content": json.dumps({"value": value, "source": SITE_SETTING_SOURCE_TABLE}, indent=2)}
        response = self.dv.request("PATCH", f"powerpagecomponents({component_id})", payload=payload)
        return response.status_code < 400

    def ensure_permission(self, website_id: str, role_id: str, table: dict[str, Any], execute: bool) -> str | None:
        logical = table["logical"]
        name = table["name"]
        data = self.dv.get_json(
            "mspp_entitypermissions?$select=mspp_entitypermissionid,mspp_entityname,mspp_entitylogicalname,mspp_scope,"
            "mspp_read,mspp_create,mspp_write,mspp_delete,mspp_append,mspp_appendto"
            f"&$filter=_mspp_websiteid_value eq {website_id} and mspp_entitylogicalname eq '{escape_odata(logical)}' and mspp_scope eq {GLOBAL_SCOPE}&$top=1"
        )
        values = (data or {}).get("value") or []
        payload = {
            "mspp_entityname": logical,
            "mspp_entitylogicalname": logical,
            "mspp_scope": GLOBAL_SCOPE,
            "mspp_read": table["read"],
            "mspp_create": table["create"],
            "mspp_write": table["write"],
            "mspp_delete": table["delete"],
            "mspp_append": table["append"],
            "mspp_appendto": table["appendto"],
            "mspp_websiteid@odata.bind": f"/mspp_websites({website_id})",
        }
        linked_values = [
            row for row in values
            if self.permission_role_exists(row["mspp_entitypermissionid"], role_id)
        ]
        if linked_values:
            permission_id = linked_values[0]["mspp_entitypermissionid"]
            current = linked_values[0]
            updates = {
                key: value
                for key, value in payload.items()
                if key != "mspp_websiteid@odata.bind" and current.get(key) != value
            }
            if updates and execute:
                privilege_payload = {
                    "mspp_read": table["read"],
                    "mspp_create": table["create"],
                    "mspp_write": table["write"],
                    "mspp_delete": table["delete"],
                    "mspp_append": table["append"],
                    "mspp_appendto": table["appendto"],
                }
                response = self.dv.request("PATCH", f"mspp_entitypermissions({permission_id})", payload=privilege_payload)
                if response.status_code >= 400:
                    if not self.patch_enhanced_permission(permission_id, table):
                        raise RuntimeError(f"PATCH table permission {logical} failed: HTTP {response.status_code} {self.deploy.safe_error(response)}")
                print(f"updated: table permission {logical}")
            elif updates:
                print(f"would update: table permission {logical}")
            else:
                print(f"exists: table permission {logical}")
        else:
            if not execute:
                print(f"would create: table permission {logical}")
                return None
            response = self.dv.post("mspp_entitypermissions", payload)
            permission_id = parse_guid_from_entity_id(response.headers.get("OData-EntityId", ""))
            print(f"created: table permission {logical}")
        self.ensure_permission_role(permission_id, role_id, execute)
        self.ensure_enhanced_permission_role(permission_id, role_id, execute)
        return permission_id

    def patch_enhanced_permission(self, permission_id: str, table: dict[str, Any]) -> bool:
        component = self.dv.get_json(f"powerpagecomponents({permission_id})?$select=content")
        if not component:
            return False
        try:
            content = json.loads(component.get("content") or "{}")
        except json.JSONDecodeError:
            content = {}
        content.update({
            "entityname": table["logical"],
            "entitylogicalname": table["logical"],
            "scope": GLOBAL_SCOPE,
            "read": table["read"],
            "create": table["create"],
            "write": table["write"],
            "delete": table["delete"],
            "append": table["append"],
            "appendto": table["appendto"],
        })
        response = self.dv.request(
            "PATCH",
            f"powerpagecomponents({permission_id})",
            payload={"content": json.dumps(content, indent=2)},
        )
        return response.status_code < 400

    def permission_role_exists(self, permission_id: str, role_id: str) -> bool:
        existing = self.dv.get_json(
            "mspp_entitypermission_webroleset?$select=mspp_entitypermission_webroleid"
            f"&$filter=mspp_entitypermissionid eq {permission_id} and mspp_webroleid eq {role_id}&$top=1"
        )
        return bool((existing or {}).get("value"))

    def ensure_permission_role(self, permission_id: str, role_id: str, execute: bool) -> None:
        if self.permission_role_exists(permission_id, role_id):
            print("exists: permission web role link")
            return
        if not execute:
            print("would create: permission web role link")
            return
        payload = {"@odata.id": f"{self.dv.base}/mspp_webroles({role_id})"}
        response = self.dv.request("POST", f"mspp_entitypermissions({permission_id})/mspp_entitypermission_webrole/$ref", payload=payload)
        if response.status_code >= 400:
            message = self.deploy.safe_error(response)
            if "already" not in message.lower() and "duplicate" not in message.lower():
                raise RuntimeError(f"Associate permission role failed: HTTP {response.status_code} {message}")
        print("created: permission web role link")

    def ensure_enhanced_permission_role(self, permission_id: str, role_id: str, execute: bool) -> None:
        if self.enhanced_permission_role_exists(permission_id, role_id):
            print("exists: enhanced permission web role component link")
            return
        if not execute:
            print("would create: enhanced permission web role component link")
            return
        payload = {"@odata.id": f"{self.dv.base}/powerpagecomponents({role_id})"}
        response = self.dv.request("POST", f"powerpagecomponents({permission_id})/powerpagecomponent_powerpagecomponent/$ref", payload=payload)
        if response.status_code >= 400:
            message = self.deploy.safe_error(response)
            if "already" not in message.lower() and "duplicate" not in message.lower():
                raise RuntimeError(f"Associate enhanced permission role failed: HTTP {response.status_code} {message}")
        if not self.enhanced_permission_role_exists(permission_id, role_id):
            raise RuntimeError("Associate enhanced permission role did not create a readable component link")
        print("created: enhanced permission web role component link")

    def enhanced_permission_role_exists(self, permission_id: str, role_id: str) -> bool:
        existing = self.dv.get_json(
            f"powerpagecomponents({permission_id})/powerpagecomponent_powerpagecomponent"
            "?$select=powerpagecomponentid&$top=50"
        )
        return any(row.get("powerpagecomponentid") == role_id for row in (existing or {}).get("value", []))

    def ensure_contact_role(self, contact_id: str | None, role_id: str, email: str, execute: bool) -> None:
        if not contact_id:
            print(f"missing: portal contact {email}; create/redeem an invitation before browser /_api testing")
            return
        existing = self.dv.get_json(
            f"powerpagecomponents({role_id})/powerpagecomponent_mspp_webrole_contact"
            "?$select=contactid&$top=100"
        )
        if any(row.get("contactid") == contact_id for row in (existing or {}).get("value", [])):
            print(f"exists: portal contact Authenticated Users role link {email}")
            return
        if not execute:
            print(f"would create: portal contact Authenticated Users role link {email}")
            return
        payload = {"@odata.id": f"{self.dv.base}/contacts({contact_id})"}
        response = self.dv.request("POST", f"powerpagecomponents({role_id})/powerpagecomponent_mspp_webrole_contact/$ref", payload=payload)
        if response.status_code >= 400:
            message = self.deploy.safe_error(response)
            if "already" not in message.lower() and "duplicate" not in message.lower():
                raise RuntimeError(f"Associate contact role failed: HTTP {response.status_code} {message}")
        print(f"created: portal contact Authenticated Users role link {email}")

    def find_cloud_flow_component(self, website_id: str, flow_id: str) -> str | None:
        data = self.dv.get_json(
            "powerpagecomponents?$select=powerpagecomponentid,name,powerpagecomponenttype,_powerpagesiteid_value"
            f"&$filter=_powerpagesiteid_value eq {website_id} and powerpagecomponenttype eq 33&$top=100"
        )
        for row in (data or {}).get("value", []):
            component_id = row["powerpagecomponentid"]
            if component_id.lower() == flow_id.lower():
                return component_id
            if row.get("name", "").strip().lower() == "tacatdp - onboarding email delivery":
                return component_id
        return None

    def ensure_cloud_flow_role(self, website_id: str, flow_id: str, role_id: str, role_name: str, execute: bool) -> None:
        flow_component_id = self.find_cloud_flow_component(website_id, flow_id)
        if not flow_component_id:
            print(f"missing: registered Power Pages cloud flow component for {flow_id}; add/register the flow in Power Pages Studio")
            return
        existing = self.dv.get_json(
            f"powerpagecomponents({flow_component_id})/powerpagecomponent_powerpagecomponent"
            "?$select=powerpagecomponentid,name,powerpagecomponenttype&$top=100"
        )
        if any(row.get("powerpagecomponentid") == role_id for row in (existing or {}).get("value", [])):
            print(f"exists: cloud flow role link {role_name}")
            return
        if not execute:
            print(f"would create: cloud flow role link {role_name}")
            return
        payload = {"@odata.id": f"{self.dv.base}/powerpagecomponents({role_id})"}
        response = self.dv.request(
            "POST",
            f"powerpagecomponents({flow_component_id})/powerpagecomponent_powerpagecomponent/$ref",
            payload=payload,
        )
        if response.status_code >= 400:
            message = self.deploy.safe_error(response)
            if "already" not in message.lower() and "duplicate" not in message.lower():
                raise RuntimeError(f"Associate cloud flow role failed: HTTP {response.status_code} {message}")
        if not self.enhanced_permission_role_exists(flow_component_id, role_id):
            raise RuntimeError("Associate cloud flow role did not create a readable component link")
        print(f"created: cloud flow role link {role_name}")


def main() -> int:
    args = parse_args()
    deploy = load_deploy_module()
    settings = deploy.build_settings(argparse.Namespace(env_file=args.env_file, schema_dir=None, schema_file=None, execute=False, no_publish=False))
    env = deploy.load_env(Path(args.env_file).resolve())
    website_id = args.website_id or env.get("POWERPAGES_WEBSITE_ID") or None
    site_name = args.site_name or env.get("POWERPAGES_SITE_NAME") or "TACATDP Monitoring Tool"
    seed_user_email = args.portal_user_email or env.get("TACATDP_SEED_USER_EMAIL") or env.get("POWER_PLATFORM_ASSIGNMENT_USER_EMAIL") or "john.mduda@mshirikacorp.onmicrosoft.com"
    onboarding_flow_trigger_id = args.onboarding_flow_trigger_id or env.get("TACATDP_ONBOARDING_FLOW_TRIGGER_ID") or ""

    print("# TACATDP Power Pages Web API Configuration")
    print(f"Mode: {'execute' if args.execute else 'dry-run'}")
    print(f"Target: {settings.deploy_target}")
    print(f"Environment: {settings.environment_url}")
    print(f"Site: {site_name}")
    print(f"Tables: {len(WEB_API_TABLES)}")
    if args.include_access_writes:
        print(f"Access write role: {args.access_role_name}")
        print(f"Access write tables: {len(ACCESS_WRITE_TABLES)}")
        print(f"Onboarding email flow: {onboarding_flow_trigger_id or 'not configured'}")
    if settings.deploy_target.lower() != "dev":
        raise SystemExit(f"Refusing non-dev deployment target: {settings.deploy_target}")

    token = deploy.get_token(settings)
    client = PagesConfigClient(deploy, settings, token)
    resolved_website_id = client.find_website(website_id, site_name)
    role_id = client.find_authenticated_role(resolved_website_id)
    access_role_id = client.find_role_by_name(resolved_website_id, args.access_role_name) if args.include_access_writes else None
    contact_id = client.find_contact_by_email(seed_user_email)
    print(f"Website ID: {resolved_website_id}")
    print(f"Authenticated Users role ID: {role_id}")
    if access_role_id:
        print(f"Access write role ID: {access_role_id}")
    print(f"Seed portal contact ID: {contact_id or 'missing'}")
    if not args.execute:
        print("Dry-run only. Re-run with --execute to configure Power Pages.")

    for table in WEB_API_TABLES:
        logical = table["logical"]
        client.ensure_site_setting(resolved_website_id, f"Webapi/{logical}/enabled", "true", args.execute)
        client.ensure_site_setting(resolved_website_id, f"Webapi/{logical}/fields", table.get("fields", "*"), args.execute)
        client.ensure_permission(resolved_website_id, role_id, table, args.execute)
    if access_role_id:
        for table in ACCESS_WRITE_TABLES:
            logical = table["logical"]
            client.ensure_site_setting(resolved_website_id, f"Webapi/{logical}/enabled", "true", args.execute)
            client.ensure_site_setting(resolved_website_id, f"Webapi/{logical}/fields", table.get("fields", "*"), args.execute)
            client.ensure_permission(resolved_website_id, access_role_id, table, args.execute)
        if onboarding_flow_trigger_id:
            client.ensure_site_setting(resolved_website_id, "TACATDP/OnboardingFlowTriggerId", onboarding_flow_trigger_id, args.execute)
            client.ensure_cloud_flow_role(resolved_website_id, onboarding_flow_trigger_id, access_role_id, args.access_role_name, args.execute)
    client.ensure_contact_role(contact_id, role_id, seed_user_email, args.execute)

    print("configuration complete" if args.execute else "dry-run complete")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
