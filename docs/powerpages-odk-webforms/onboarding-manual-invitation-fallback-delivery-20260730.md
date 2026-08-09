# Onboarding Manual Invitation Fallback Delivery - 2026-07-30

## Purpose

Add a governed fallback for environments where Power Pages invitation records can be created but mailbox-based delivery is not yet configured. A Platform Administrator can refresh the queued onboarding result, copy the single-use invitation code and redemption URL, and issue them through an approved CRDB channel.

## Requirements

- New-user onboarding remains server-side queued through `mp_onboardingrequest`.
- On private developer/non-production sites, the administrator must grant Site visibility access before sharing a manual invitation link/code. Manual invitation fallback does not bypass the private-site gate.
- The portal must not create contacts, invitations, web roles, or assignments directly from browser-only elevated logic.
- If mailbox delivery is unavailable, the server-side onboarding processor may write the invitation id, invitation code, redemption URL, expiry, status, and delivery mode back to the admin-only request row.
- The admin UI must show a clear manual fallback panel only when both invitation code and redemption URL are present.
- Expired invitation codes must not be copyable as active activation material.
- The admin UI must allow an expired request to queue a replacement request linked through `ReplacementOfRequestId`.
- Existing-user assignment notifications remain configurable: Dataverse-native delivery by default, Office 365 Outlook when CRDB provides an approved mailbox/connection.

## Microsoft Reference

Microsoft documents that Power Pages invitations include an invitation code, can have an expiry date, and can assign roles during redemption. Microsoft also documents that invitation codes can be redeemed by a registering visitor and can be submitted through non-email channels when a general code submission path is used. Table permissions remain the required portal-side control for Dataverse Web API access.

References:

- https://learn.microsoft.com/en-us/power-pages/security/invite-contacts
- https://learn.microsoft.com/en-us/power-pages/security/authentication/set-authentication-identity
- https://learn.microsoft.com/en-us/power-pages/security/table-permissions

## Delivered Changes

- Extended onboarding request schema and data contract with invitation result fields:
  - `InvitationId`
  - `InvitationCode`
  - `InvitationRedeemUrl`
  - `InvitationExpiresAt`
  - `InvitationStatus`
  - `InvitationDeliveryMode`
  - `ReplacementOfRequestId`
- Extended Power Pages Web API configuration allowlist for the corresponding `mp_` columns.
- Added `getUserOnboardingRequestResult()` so the portal can refresh the queue row after server-side processing.
- Added onboarding result UX for:
  - refresh status
  - manual invitation code fallback
  - copy redemption URL
  - copy invitation code
  - expired invitation warning
  - replacement invitation request
- Packaged and uploaded Mshirika review bundle:
  - `index-Cs2188JS.mjs?v=manual-invite-fallback-20260730-001`
- Updated the Dataverse-triggered onboarding queue processor so manual-code mode:
  - creates a native Power Pages invitation;
  - sets invitation expiry;
  - skips the native Send Invitation workflow when no mailbox is configured;
  - writes invitation id, code, redeem URL, expiry, status, and delivery mode back to `mp_onboardingrequest`;
  - leaves the request in `NeedsReview` for administrator handoff.

## Security Position

Invitation codes are activation material and must stay admin-only. This fallback is acceptable only because `mp_onboardingrequest` is intended to be accessible to Platform Administrators, invitation codes are single-use, expiry is enforced by Power Pages invitation behavior, and the portal does not store passwords or bearer tokens.

The administrator must communicate the code and redemption URL only through an approved CRDB channel. For private sites, the administrator must first confirm the user is in Power Pages Site visibility > People who can access the site. This fallback is a controlled operational substitute for mailbox delivery, not a public or collector-facing feature.

## Processor Contract

The Dataverse onboarding processor must populate these fields after creating the Power Pages invitation:

- `mp_invitationid`
- `mp_invitationcode`
- `mp_invitationredeemurl`
- `mp_invitationexpiresat`
- `mp_invitationstatus`
- `mp_invitationdeliverymode`

When the admin queues a replacement, the request includes `mp_replacementofrequestid`. The processor should close or mark the old request as replaced, create a new invitation, and write the new invitation fields to the replacement request.

## Verification

Commands run:

```bash
python3 scripts/validate-access-onboarding-queue-schema.py
python3 scripts/validate-access-create-invite-assign-ux.py
python3 scripts/validate-webforms-spa-foundation.py
npm --prefix powerpages/webforms-spa run build:mshirika-runtime
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-Cs2188JS.mjs
git diff --check
pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
python3 scripts/powerautomate-onboarding-queue-processor-plan.py
python3 -m py_compile scripts/powerautomate-configure-onboarding-queue-processor.py scripts/powerautomate-onboarding-queue-processor-plan.py scripts/validate-onboarding-queue-processor-plan.py
python3 scripts/validate-onboarding-queue-processor-plan.py
python3 scripts/powerautomate-configure-onboarding-queue-processor.py --invitation-delivery-mode manual-code
python3 scripts/powerautomate-configure-onboarding-queue-processor.py --invitation-delivery-mode manual-code --execute
python3 scripts/dataverse-schema-deploy.py --schema-file schemas/dataverse/onboarding-request-schema.json --execute
python3 scripts/powerpages-configure-webapi.py --include-access-writes --execute
```

Result:

- Validators passed.
- Runtime build passed.
- Packaged bundle syntax check passed.
- Diff whitespace check passed.
- Mshirika Power Pages upload succeeded in 116.43 seconds.
- Onboarding request schema deployment created the missing invitation result columns and published customizations.
- Power Pages Web API configuration updated `Webapi/mp_onboardingrequest/fields` with the invitation result fields.
- Mshirika live processor readback passed:
  - flow: `TACATDP - Onboarding Queue Processor`
  - new-user actions: `Create_Native_Power_Pages_Invitation`, `Update_Request_Invitation_Result`
  - `Run_Native_Send_Invitation_Workflow` absent in manual-code mode.
- Mshirika controlled processor smoke passed:
  - request id: `ONB-SMOKE-20260730023047`
  - queue record: `88803fa8-be8b-f111-ab0f-7ced8d74983c`
  - queue status: `NeedsReview` (`100000005`)
  - delivery mode: `ManualCode` (`100000001`)
  - invitation status: `ManualDeliveryRequired` (`100000001`)
  - invitation code present: yes
  - redeem URL present: yes
  - expiry: `2026-08-13T02:30:52Z`

Note: `scripts/validate-access-mshirika-activation.py` is not the correct validator for the full runtime package because it validates a Mshirika-only access shell with ODK runtime disabled and enforces a no-large-ODK-assets constraint.

## CRDB Readiness

Before CRDB deployment, confirm these items:

- The governed solution includes the new onboarding request columns.
- `scripts/powerpages-configure-webapi.py --include-access-writes` has been run or equivalent site settings are present for the new fields.
- Platform Administrator web role has create/read/write permission on `mp_onboardingrequest`.
- The server-side onboarding processor writes invitation fields back to the queue row.
- If CRDB provides a shared mailbox, configure mailbox delivery; otherwise use the manual code fallback through an approved internal channel.
- If the site remains private, grant Site visibility access before asking the user to redeem the manual link/code.

## Remaining Risk

Mshirika now proves the manual fallback path end to end. CRDB still needs the same additive schema fields, Power Pages Web API allowlist, admin table permission, and processor definition update before production users can rely on manual invitation code fallback there.
