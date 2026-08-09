# Notification Delivery Settings UI - 2026-07-30

## Purpose

Give Platform Administrators a portal surface to choose and monitor onboarding delivery mode without requiring them to open code or Power Pages Management for routine operational decisions.

## Boundary

The portal may manage business configuration:

- delivery mode: `Manual invitation code` or `Mailbox email delivery`;
- sender mailbox address for display/readiness tracking;
- mailbox readiness status;
- last test timestamp and result note;
- administrator instructions.

The portal must not approve, Test & Enable, license, or create Exchange/Dataverse mailboxes. Those remain tenant/admin operations in Microsoft 365, Power Platform admin center, Dataverse mailbox settings, and Power Automate connection management.

## Microsoft Evidence

- Power Pages invitations can include invitation code, expiry date, and Send Invitation workflow delivery.
- The Send Invitation workflow sends to the invited contact primary email address.
- Dataverse mailbox email sending requires mailbox approval and Test & Enable for server-side synchronization.
- Dataverse mailbox failures include missing Microsoft 365 user/mailbox or missing Exchange REST/license readiness.

References:

- https://learn.microsoft.com/en-us/power-pages/security/invite-contacts
- https://learn.microsoft.com/en-us/troubleshoot/power-platform/dataverse/email-exchange-synchronization/troubleshooting-monitoring-server-side-synchronization
- https://learn.microsoft.com/en-us/troubleshoot/power-platform/dataverse/email-exchange-synchronization/test-enable-fails-for-unrecognized-email-address

## Requirements

- Add a `Notifications` configuration card under User & Access configuration.
- Show current active mode and mailbox readiness.
- Allow Platform Administrator to save manual-code mode without mailbox readiness.
- Disable email mode unless mailbox readiness is `Tested and enabled` and sender mailbox is present.
- Show short setup checklist for mailbox mode.
- Save configuration to Dataverse when `NotificationDeliverySettings` table is available.
- Fall back to a built-in manual-code configuration when the table is not yet deployed.
- Never store secrets, passwords, tokens, authorization headers, or credential-bearing URLs.

## UX Description

The card should feel like a bank operations configuration panel:

- one current-status strip;
- two delivery-mode options;
- a small mailbox readiness form;
- one save action;
- concise error/success feedback;
- technical setup instructions kept short and visible only as checklist rows.

## Acceptance Criteria

- User & Access configuration includes a Notifications card.
- Manual-code mode is selectable and saveable.
- Email mode cannot be selected unless mailbox readiness is `Tested and enabled` and sender mailbox is provided.
- The UI states mailbox approval/Test & Enable are admin-center tasks, not portal actions.
- Validator enforces the notification settings UI, schema, and no-browser-mailbox-admin boundary.
- Mshirika build and upload pass.

## Implementation Notes

Schema artifact: `schemas/dataverse/notification-delivery-settings-schema.json`.

Singleton config key: `onboarding-delivery`.

processor update: read `mp_notificationdeliverysettings` by `mp_settingkey = 'onboarding-delivery'` and choose manual-code or email branch from the Dataverse row. Email branch runs only when `DeliveryMode = Email`, `MailboxStatus = TestedAndEnabled`, and sender mailbox is present. Otherwise, the processor keeps manual-code fallback.

## Verification

Run:

```bash
python3 scripts/validate-notification-delivery-settings.py
python3 scripts/validate-access-create-invite-assign-ux.py
npm --prefix powerpages/webforms-spa run build:mshirika-runtime
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/<entry>.mjs
git diff --check
```

After deploying schema and Web API settings, verify that a Platform Administrator can open User & Access > Configuration, save manual-code mode, and see the saved status after refresh.

## Delivery Evidence

Implemented in:

- `schemas/dataverse/notification-delivery-settings-schema.json`
- `powerpages/webforms-spa/src/powerpages-api/types.ts`
- `powerpages/webforms-spa/src/powerpages-api/client.ts`
- `powerpages/webforms-spa/src/views/AssignedFormsView.vue`
- `powerpages/webforms-spa/src/styles.css`
- `scripts/powerpages-configure-webapi.py`
- `scripts/powerautomate-configure-onboarding-queue-processor.py`
- `scripts/powerautomate-onboarding-queue-processor-plan.py`
- `scripts/validate-notification-delivery-settings.py`
- `scripts/validate-onboarding-queue-processor-plan.py`

Mshirika environment updates completed:

- Deployed `mp_notificationdeliverysetting` table and columns.
- Created alternate key `mp_Ak_notification_delivery_setting_key`.
- Configured `Webapi/mp_notificationdeliverysetting/enabled=true`.
- Configured admin-only table permission for `mp_notificationdeliverysetting`.
- Patched live flow `TACATDP - Onboarding Queue Processor` to read notification settings.
- Seeded default `onboarding-delivery` row:
  - record: `09524109-cd8b-f111-ab10-000d3ab20cf7`
  - delivery mode: `ManualCode` (`100000000`)
  - mailbox status: `NotConfigured` (`100000000`)

Packaged bundle:

- `index-DM97LP7i.mjs?v=notification-settings-20260730-001`
- `index-DTgq76J1.css?v=notification-settings-20260730-001`

Commands run:

```bash
python3 scripts/validate-notification-delivery-settings.py
python3 scripts/powerautomate-onboarding-queue-processor-plan.py
python3 scripts/validate-onboarding-queue-processor-plan.py
python3 -m py_compile scripts/powerautomate-configure-onboarding-queue-processor.py scripts/powerautomate-onboarding-queue-processor-plan.py scripts/validate-notification-delivery-settings.py
npm --prefix powerpages/webforms-spa run build:mshirika-runtime
python3 scripts/dataverse-schema-deploy.py --schema-file schemas/dataverse/notification-delivery-settings-schema.json --execute
python3 scripts/powerpages-configure-webapi.py --include-access-writes --execute
python3 scripts/powerautomate-configure-onboarding-queue-processor.py --invitation-delivery-mode manual-code --execute
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-DM97LP7i.mjs
python3 scripts/validate-access-create-invite-assign-ux.py
git diff --check
pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
```

Runtime smoke:

- request id: `ONB-NOTIFY-SMOKE-20260730040952`
- queue record: `f8dd2682-cc8b-f111-ab10-000d3ab20cf7`
- delivery mode: `ManualCode` (`100000001` on onboarding request result)
- invitation code present: yes
- expiry: `2026-08-13T04:10:04Z`

PAC upload result:

- Mshirika Power Pages upload succeeded in 102.70 seconds.
