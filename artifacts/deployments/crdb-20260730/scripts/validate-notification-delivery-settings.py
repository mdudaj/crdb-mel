#!/usr/bin/env python3
"""Validate TACATDP notification delivery settings artifacts."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/dataverse/notification-delivery-settings-schema.json"
DOC = ROOT / "docs/powerpages-odk-webforms/notification-delivery-settings-ui-20260730.md"
VIEW = ROOT / "powerpages/webforms-spa/src/views/AssignedFormsView.vue"
CLIENT = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"
TYPES = ROOT / "powerpages/webforms-spa/src/powerpages-api/types.ts"
STYLES = ROOT / "powerpages/webforms-spa/src/styles.css"
CONFIGURE = ROOT / "scripts/powerpages-configure-webapi.py"
PROCESSOR = ROOT / "scripts/powerautomate-configure-onboarding-queue-processor.py"


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
    schema = json.loads(read(SCHEMA))
    tables = {table["name"]: table for table in schema.get("tables", [])}
    if "NotificationDeliverySettings" not in tables:
        fail("schema missing NotificationDeliverySettings table")
    columns = {column["name"] for column in tables["NotificationDeliverySettings"].get("columns", [])}
    for column in (
        "SettingKey",
        "DeliveryMode",
        "SenderMailbox",
        "MailboxStatus",
        "NativeInvitationWorkflowId",
        "LastTestedAt",
        "LastTestResult",
        "Instructions",
        "UpdatedByEmail",
        "UpdatedAt",
    ):
        if column not in columns:
            fail(f"schema missing column: {column}")
    policy = schema.get("write_path_policy", {})
    if policy.get("browser_cannot_approve_or_test_mailboxes") is not True:
        fail("schema must prohibit browser mailbox approval/testing")

    require(DOC, (
        "Notification Delivery Settings UI",
        "Manual invitation code",
        "Mailbox email delivery",
        "must not approve, Test & Enable, license, or create Exchange/Dataverse mailboxes",
        "NotificationDeliverySettings",
        "onboarding-delivery",
        "processor update",
    ))
    require(TYPES, (
        "NotificationDeliverySetting",
        "NotificationDeliverySettingInput",
        "NotificationDeliveryMode",
        "MailboxReadinessStatus",
        "manual-code",
        "tested-and-enabled",
    ))
    require(CLIENT, (
        "NOTIFICATION_DELIVERY_SETTING_WEB_API_PATH",
        "mp_notificationdeliverysettings",
        "NOTIFICATION_DELIVERY_SETTING_KEY",
        "onboarding-delivery",
        "getNotificationDeliverySetting",
        "saveNotificationDeliverySetting",
        "toNotificationDeliverySettingWebApiPayload",
        "Mailbox email delivery requires a sender mailbox with Tested and enabled readiness.",
    ))
    require(VIEW, (
        "notification-settings-card",
        "Onboarding delivery",
        "notificationDeliveryMode",
        "notificationEmailModeReady",
        "saveNotificationDeliverySetting",
        "Mailbox readiness",
        "Approve the Dataverse mailbox and run Test & Enable",
        "Manual invitation code",
        "Mailbox email delivery",
    ))
    require(STYLES, (
        ".notification-settings-card",
        ".notification-mode-options",
        ".notification-settings-form",
        ".notification-setup-checklist",
    ))
    require(CONFIGURE, (
        "mp_notificationdeliverysetting",
        "TACATDP NotificationDeliverySettings Admin Config",
        "mp_settingkey,mp_deliverymode,mp_sendermailbox,mp_mailboxstatus",
    ))
    require(PROCESSOR, (
        "Find_Notification_Delivery_Setting",
        "mp_notificationdeliverysettings",
        "onboarding-delivery",
        "Determine_Email_Delivery_Readiness",
        "Run_Native_Send_Invitation_When_Ready",
        "MAILBOX_STATUS_TESTED_AND_ENABLED",
    ))

    print("TACATDP notification delivery settings validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
