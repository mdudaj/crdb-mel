#!/usr/bin/env python3
"""Validate the TACATDP onboarding request queue schema and Web API wiring."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/dataverse/onboarding-request-schema.json"
SCHEMA_DOC = ROOT / "schemas/dataverse/onboarding-request-schema.md"
CONFIG = ROOT / "scripts/powerpages-configure-webapi.py"
CLIENT = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"

REQUIRED_COLUMNS = {
    "RequestKey": True,
    "RequestId": True,
    "Status": True,
    "RequestType": True,
    "FullName": True,
    "Email": True,
    "TargetRole": True,
    "ProjectId": False,
    "ProjectName": False,
    "FormScopeJson": True,
    "Reason": True,
    "ActorEmail": True,
    "ActorRolesJson": False,
    "SourceRoute": True,
    "ContactId": False,
    "ProcessingAttempts": True,
    "LastAttemptAt": False,
    "CompletedAt": False,
    "ResultMessage": False,
    "ErrorCategory": False,
    "ErrorJson": False,
    "AuditKey": False,
    "InvitationId": False,
    "InvitationCode": False,
    "InvitationRedeemUrl": False,
    "InvitationExpiresAt": False,
    "InvitationStatus": False,
    "InvitationDeliveryMode": False,
    "ReplacementOfRequestId": False,
}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required artifact: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    schema = json.loads(read(SCHEMA))
    tables = schema.get("tables", [])
    if len(tables) != 1:
        fail("onboarding request schema must define exactly one table")
    table = tables[0]
    if table.get("name") != "OnboardingRequests":
        fail("table name must be OnboardingRequests")
    if table.get("ownership_type") != "OrganizationOwned":
        fail("OnboardingRequests must be organization-owned for central administration")
    if table.get("primary_name_column") != "RequestKey":
        fail("OnboardingRequests primary name column must be RequestKey")

    columns = {column.get("name"): column for column in table.get("columns", [])}
    for name, required in REQUIRED_COLUMNS.items():
        if name not in columns:
            fail(f"OnboardingRequests missing required column: {name}")
        if bool(columns[name].get("required")) != required:
            fail(f"OnboardingRequests.{name} required flag must be {required}")

    keys = schema.get("alternate_keys", [])
    if not any(key.get("name") == "ak_onboarding_request_key" and key.get("columns") == ["RequestKey"] for key in keys):
        fail("schema must define ak_onboarding_request_key on RequestKey")

    config = read(CONFIG)
    for term in (
        '"logical": "mp_onboardingrequest"',
        "TACATDP OnboardingRequests Admin Queue",
        "mp_requestkey,mp_requestid,mp_status,mp_requesttype",
        "mp_invitationcode,mp_invitationredeemurl,mp_invitationexpiresat",
    ):
        if term not in config:
            fail(f"Power Pages config missing queue Web API/table permission term: {term}")

    client = read(CLIENT)
    for term in (
        "ACCESS_ONBOARDING_QUEUE_WEB_API_PATH",
        "createOnboardingRequest",
        "'/_api/mp_onboardingrequests'",
        "mp_requestkey",
        "mp_formscopejson",
    ):
        if term not in client:
            fail(f"portal client missing queue submit term: {term}")
    if "/_api/cloudflow/v1.0/trigger/" in client:
        fail("portal client must not call the Power Pages cloud-flow trigger endpoint for onboarding")

    doc = read(SCHEMA_DOC)
    for term in ("OnboardingRequests", "Choice Codes", "Portal Permission Intent", "InvitationCode", "manual fallback"):
        if term not in doc:
            fail(f"schema documentation missing required term: {term}")

    print("TACATDP onboarding request queue schema validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
