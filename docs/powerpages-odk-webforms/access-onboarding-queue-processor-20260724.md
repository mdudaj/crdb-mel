# Access Onboarding Queue Processor - 2026-07-24

Status: Mshirika processor flow configured and smoke-tested for queue processing. New-user invitation row creation works, but recipient email delivery is not yet confirmed. The active fallback is admin-only manual invitation code delivery when no approved mailbox is configured.

## Purpose

Define the Dataverse-triggered processor that consumes `mp_onboardingrequest` rows created by the portal. The processor replaces the failed direct Power Pages cloud-flow trigger route.

## Authoritative References

- Microsoft Learn: Dataverse flows can use the **When a row is added, modified or deleted** trigger.
- Microsoft Learn: The Dataverse trigger uses callback registration records; the flow owner needs the required Callback Registration privileges.
- Microsoft Learn: Dataverse flows can add rows, update rows, and perform bound/unbound actions.

## Trigger

Use Microsoft Dataverse connector:

- Operation: `When a row is added, modified or deleted`
- Operation id: `SubscribeWebhookTrigger`
- Table: `mp_onboardingrequest`
- Change type: added or modified
- Scope: organization
- Filter rows: `mp_status eq 100000000`
- Select columns: `mp_status`

This means only `Pending` onboarding requests should start processor work.

## Processing Contract

1. Guard that request status is still `Pending`.
2. Set request status to `Processing`.
3. Parse `mp_formscopejson`.
4. Find contact by normalized `mp_email`.
5. Create contact only when no matching contact exists.
6. Write resolved contact id to the request row.
7. Create an `AccessAuditLogs` request audit before assignment mutation.
8. For each selected form version:
   - find an existing `mp_formassignment` by email and form version;
   - create an `AssignForm` audit row;
   - create assignment only when missing;
   - use `mp_assignmentkey = lower(email) + ':' + formVersionId`.
9. If request type is `NewUser`, create a native Power Pages invitation with `adx_invitationcode` and `adx_expirydate`.
10. If mailbox delivery is configured, run the native Send Invitation workflow through Dataverse `Microsoft.Dynamics.CRM.ExecuteWorkflow`.
11. If mailbox delivery is not configured, skip the send workflow and write the invitation id, manual invitation code, redemption URL, expiry, status, and delivery mode back to the admin-only queue row.
12. If request type is `ExistingUser`, create a Dataverse email/notification record when a mailbox sender is configured and write assignment-notification delivery mode back to the queue row.
13. Set request status to `NeedsReview` with contact id, audit key, completed timestamp, and result message until email delivery, manual code handoff, or invitation redemption is confirmed.
14. On failure, set status to `Failed` with sanitized `mp_errorcategory`, `mp_errorjson`, and `mp_resultmessage`.

## Required Privileges

The flow owner or service account needs:

- create/read/write/delete on Callback Registration for the Dataverse trigger;
- read/update on `mp_onboardingrequest`;
- create/read/update on `contact`;
- create/read on `adx_invitation`;
- execute the native Power Pages Send Invitation workflow;
- create/read/update on `mp_accessauditlog`;
- create/read on `mp_formassignment`;
- read/append-to on `mp_formversion`;
- create/send Dataverse email for existing-user assignment notifications.

## Security Rules

- Do not store bearer tokens, anti-forgery tokens, connector credentials, passwords, or credential-bearing links.
- Invitation codes and redemption URLs may be written only to `mp_onboardingrequest` for the approved admin-only manual fallback. Treat them as single-use activation material and pair them with expiry.
- Store sanitized failure category and message only.
- Do not delete failed requests.
- Retry must be explicit and must preserve idempotency.

## Mshirika Smoke

1. Create a new-user request from Add User.
2. Confirm one `mp_onboardingrequest` row starts `Pending`.
3. Confirm a Dataverse-triggered flow run appears.
4. Confirm status changes to `Processing`.
5. Confirm status changes to `NeedsReview` or `Failed`.
6. On `NeedsReview`, confirm contact, invitation, audit, and assignment rows, then verify recipient email delivery or invitation redemption before treating onboarding as complete.
7. Create an existing-user request and confirm Dataverse SendEmail notification path.
8. Retry a failed request and confirm no duplicate assignments.
9. Confirm a Data Collector cannot read or create queue rows.

## Generated Plan

Run:

```bash
python3 scripts/powerautomate-onboarding-queue-processor-plan.py
python3 scripts/validate-onboarding-queue-processor-plan.py
```

The generated plan is written to:

```text
artifacts/powerautomate/tacatdp-onboarding-queue-processor-plan.json
```

## 2026-07-24 Mshirika Delivery Evidence

Runtime setup completed in the Mshirika development environment:

- Deployed `mp_accessauditlog` through `schemas/dataverse/access-audit-schema.json`.
- Corrected the schema deployer so system `Contacts` relationships map to Dataverse `contact`, not `mp_contact`.
- Configured Power Pages Web API settings and administrator create/read table permission for `mp_accessauditlog`.
- Patched existing solution-aware flow `f2144020-8c86-f111-ab0e-70a8a52eccae`.
- Renamed that flow to `TACATDP - Onboarding Queue Processor`.
- Saved trigger:
  - type: `OpenApiConnectionWebhook`
  - operation id: `SubscribeWebhookTrigger`
  - table: `mp_onboardingrequest`
  - filter: `mp_status eq 100000000`
  - selected column: `mp_status`
- Saved processor actions:
  - `Set_Request_Processing`
  - `Parse_Form_Scope`
  - `Find_Contact_By_Email`
  - `Create_Contact_Route`
  - `Resolve_Contact_Id`
  - `Update_Request_Contact`
  - `Create_Request_Audit`
  - `Apply_Form_Assignments`
  - `Route_Email_Delivery`
  - `Set_Request_Needs_Review`
  - `Set_Request_Failed_On_Error`

Existing-user smoke test:

- Created request `codex-smoke-20260724121432`.
- Processor resolved contact `f1e65863-d37b-f111-ab0e-7c1e523612eb`.
- Processor created one request audit row and one form-assignment audit row.
- Existing form assignment was detected, so no duplicate assignment was created.
- Processor created a Dataverse email activity.
- Request completed as `NeedsReview` with message: `Assignment completed. Dataverse notification email was created but requires mailbox send approval/review.`

Direct `Microsoft.Dynamics.CRM.SendEmail` testing against the created email returned:

```text
The user selected in the From field does not have the option enabled to allow other users to send the email on their behalf.
```

Therefore, the Mshirika processor intentionally does not call `SendEmail` for existing users until mailbox delegation or an approved sender account is configured. CRDB can enable that step after confirming the sender mailbox/delegation policy.

New-user invitation smoke testing on 2026-07-24 exposed two delivery issues:

- The processor initially used workflow id `eb467141-a276-f111-ab0e-70a8a52d4a92`.
- Direct `ExecuteWorkflow` returned `Workflow must be in Published state.`
- Mshirika has another `Send Invitation` workflow row, `15c03c8d-754f-4386-a62c-cf7e91337ebd`, which executed successfully against invitation `d137a8a1-6c87-f111-ab0e-70a8a57d9610`.
- The queue processor was patched to use `15c03c8d-754f-4386-a62c-cf7e91337ebd`.
- Request `ONB-20260724143253-j-mduda-hotmail-com` confirmed contact, audit rows, form assignment, native invitation row, and successful Send Invitation workflow execution.
- The recipient later confirmed no invitation email was received. Dataverse email activity search returned zero matching email activities for the recipient/invitation smoke, so the request was corrected to `NeedsReview` with `mp_errorcategory = invitation-email-not-received`.
- The queue processor now marks successful server-side writes as `NeedsReview`, not `Completed`, until invitation email delivery or invitation redemption is confirmed.
- The live Mshirika processor flow `f2144020-8c86-f111-ab0e-70a8a52eccae` was patched with this `NeedsReview` behavior; planned snapshot `artifacts/powerautomate/tacatdp-onboarding-queue-processor-planned-20260724145029.json` records the updated definition.
- Manual Portal Management `Flow > Send Invitation` attempts created Dataverse email activities for `j.mduda@hotmail.com`, but all remained `Pending Send` with `senton = null` and `deliveryattempts = 0`.
- The email sender was the non-interactive application user `# TACATDP Impact Tracking`, and relevant mailbox records showed outgoing email status `Not Run`. Mshirika invitation delivery therefore requires mailbox approval/Test & Enable or a configured licensed sender path before the workflow can be treated as delivering email.
- Testing the `# TACATDP Impact Tracking` synthetic mailbox failed with `User Not Found` because its generated address does not exist as a Microsoft 365 UPN, SMTP, or mail address. Do not use this application-user mailbox as the invitation sender. Configure the native Send Invitation workflow `From` sender to a real approved Microsoft 365 mailbox, then approve and Test & Enable that mailbox.
- Testing `john.mduda@mshirikacorp.onmicrosoft.com` also failed because the mailbox was not enabled for Exchange REST connectivity in the Microsoft 365 tenant associated with the `Microsoft Exchange Online` email server profile. This means John is not yet a usable Dataverse outgoing sender either; assign/enable an Exchange Online mailbox or use another approved mailbox whose Test & Enable result is successful.
- Chosen Mshirika sender path: create a dedicated Exchange Online shared mailbox `noreply@mshirikacorp.onmicrosoft.com`, bind the Dataverse sender mailbox record to that real address, approve it, Test & Enable it, and use it as the native invitation sender. For CRDB, use the same pattern with a CRDB-approved service mailbox.

The older `scripts/powerautomate-configure-onboarding-flow.py` belongs to the abandoned direct Power Pages trigger path and still references the non-executable workflow row. Do not use it for the queue processor path.

## 2026-07-30 Manual Code Fallback Update

The Mshirika tenant does not currently have an approved Exchange mailbox for reliable outgoing Dataverse/Power Pages invitation email. The queue processor therefore supports `--invitation-delivery-mode manual-code` as the default Mshirika path:

- create/reuse the contact;
- create audit and assignment rows idempotently;
- create a native Power Pages invitation;
- set an expiry date;
- write `mp_invitationid`, `mp_invitationcode`, `mp_invitationredeemurl`, `mp_invitationexpiresat`, `mp_invitationstatus`, and `mp_invitationdeliverymode` to the queue row;
- leave the request as `NeedsReview` so a Platform Administrator can refresh the portal result and issue the code through an approved internal channel.

The generated redemption URL uses the Power Pages registration pattern:

```text
https://<portal>/register/?returnurl=%2f&invitation=<Invitation Code>
```

For CRDB, keep `manual-code` until a CRDB-approved shared/service mailbox has been approved, tested, and enabled. After mailbox readiness is confirmed, rerun the processor configurator with `--invitation-delivery-mode email` so the native Send Invitation workflow is part of the new-user branch.
