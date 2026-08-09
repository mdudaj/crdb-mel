# Mshirika User Management Activation Test - 2026-07-22

Status: prepared for Mshirika development testing only. Not approved for CRDB activation.

## Purpose

Enable the Add User onboarding workflow in the Mshirika development environment first, then use the result to decide what is safe to package for CRDB.

## 2026-07-24 Queue Architecture Update

The direct Power Pages cloud-flow trigger path is superseded by ADR 0008. The current Mshirika activation path queues onboarding requests in Dataverse:

- The portal creates an `OnboardingRequests` row through Power Pages `/_api/mp_onboardingrequests`.
- The request starts as queued / `Pending`.
- A Dataverse-triggered processor owns contact create/reuse, native Power Pages invitation for new users, Dataverse-native assignment notification for existing users, access audit creation, and form assignment writes.
- The portal must not call the direct Power Pages cloud-flow trigger for onboarding.
- CRDB must receive this queue-based package only after Mshirika verifies request creation, processor run history, status updates, and non-admin denial.

## 2026-07-24 Queue Runtime Deployment

Mshirika now has the queue shell deployed:

- `mp_onboardingrequest` exists in the Mshirika Dataverse environment.
- Power Pages Web API is enabled for `mp_onboardingrequest`.
- `Webapi/mp_onboardingrequest/fields` uses the approved queue-field allowlist instead of `*`.
- `Administrators` has create/read permission on `mp_onboardingrequest`; the portal does not have write/delete/append for this queue table.
- The Mshirika access bundle posts Add User requests to `/_api/mp_onboardingrequests`.
- The old direct `/_api/cloudflow/v1.0/trigger/<guid>` browser path is absent from the deployed bundle.
- Hosted verification passed after the 2026-07-24 upload.

Current limitation: the existing-user path creates the Dataverse notification email activity but does not send it automatically because Mshirika returned a sender-delegation error when `SendEmail` was tested. The new-user path creates the contact, assignment, audit rows, native invitation row, and requests the native Send Invitation workflow, but recipient delivery has not been confirmed. The queue processor marks both paths `NeedsReview` with a clear message until mailbox delivery or invitation redemption is verified.

Processor delivery evidence:

- `mp_accessauditlog` is deployed and included in hosted verification.
- Flow `f2144020-8c86-f111-ab0e-70a8a52eccae` is now `TACATDP - Onboarding Queue Processor`.
- Existing-user smoke request `codex-smoke-20260724121432` processed from `Pending` to `NeedsReview`.
- Contact resolution, request audit, form-assignment audit, assignment duplicate detection, email activity creation, and request status update were verified in Dataverse.
- New-user smoke request `ONB-20260724143253-j-mduda-hotmail-com` created the contact, audit rows, form assignment, and native invitation row, and the Send Invitation workflow execution completed.
- The recipient confirmed no invitation email was received; no matching Dataverse email activity was found, so the request is `NeedsReview` with `mp_errorcategory = invitation-email-not-received`.

## Build Flags

Default builds keep User & Access writes disabled. The Mshirika test build must be produced with:

```bash
npm --prefix powerpages/webforms-spa run build:mshirika-access
```

That script sets:

- `VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED=true`
- `VITE_TACATDP_ACCESS_ASSIGN_FORM_WRITE_ENABLED=true`
- `VITE_TACATDP_ACCESS_ONBOARDING_AUTOMATION_ENABLED=true`
- `VITE_TACATDP_ODK_RUNTIME_ENABLED=false`

It intentionally does not set `VITE_TACATDP_ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED`, so audit result updates remain disabled until the one-row audit lifecycle is approved.
It intentionally disables the ODK form runner for this access-only test bundle so the Power Pages upload updates the shell and User & Access route without hitting the Enhanced model content limit on ODK runtime chunks.

## Environment Gates

Before uploading the activated test bundle to Mshirika:

1. Confirm `AccessAuditLogs` exists as `mp_accessauditlog`.
2. Confirm the Power Pages Web API entity set for audit create is `mp_accessauditlogs`.
3. Confirm `Webapi/mp_accessauditlog/enabled=true`.
4. Confirm `Webapi/mp_accessauditlog/fields` includes only approved audit fields.
5. Confirm `Webapi/mp_formassignment/enabled=true`.
6. Confirm `Webapi/mp_formassignment/fields` is either the approved narrow list or the existing Mshirika wildcard `*`. Microsoft permits `*`; table permissions remain the write-control boundary.
7. Confirm `Webapi/contact/enabled=true`.
8. Confirm `Webapi/contact/fields` includes `contactid,fullname,emailaddress1,statecode`.
9. Confirm `OnboardingRequests` exists as `mp_onboardingrequest`.
10. Confirm the Power Pages Web API entity set for queue create is `mp_onboardingrequests`.
11. Confirm `Webapi/mp_onboardingrequest/enabled=true`.
12. Confirm `Webapi/mp_onboardingrequest/fields` includes only approved queue fields.
13. Confirm Platform Administrator has create/read permission on `mp_onboardingrequest`.
14. Confirm Platform Administrator has create/read permission on `mp_accessauditlog`.
15. Confirm Platform Administrator has read/create permission on `mp_formassignment`.
16. Confirm Platform Administrator has read/create permission on `contact`.
17. Confirm `mp_formversion` has read and append-to permission for the administrator role.
18. Confirm the Dataverse-triggered onboarding processor is on and uses approved connection references.
19. Save the relevant table permissions through Power Pages Security workspace if runtime authorization does not recognize scripted relationships.

Dry-run the Power Pages configuration before executing it:

```bash
python3 scripts/powerpages-configure-webapi.py \
  --env-file .env \
  --include-access-writes \
  --access-role-name Administrators
```

After reviewing the target environment, website, role IDs, and planned writes, execute only against the Mshirika dev target:

```bash
python3 scripts/powerpages-configure-webapi.py \
  --env-file .env \
  --include-access-writes \
  --access-role-name Administrators \
  --execute
```

## Browser Test

1. Sign in to the Mshirika Power Pages site as a Platform Administrator.
2. Open User & Access.
3. Open Add User.
4. Enter an Mshirika test email.
5. Select Data Collector / Bank Officer.
6. Select the TACATDP project and one form.
7. Enter a business reason.
8. Confirm the final action is enabled only when the Mshirika access bundle is uploaded.
9. Submit and confirm the result shows an onboarding request id, queue record id, and `Pending` status.
10. Confirm a Dataverse-triggered processor run appears for the same request.
11. Confirm the request moves to `Processing`, then `NeedsReview` or `Failed`.
12. On `NeedsReview`, confirm contact, access audit, and form assignment rows exist.
13. For a new contact, confirm the recipient receives the native Power Pages invitation or redeems the invitation before closing the request.
14. For an existing contact, confirm the recipient receives the Dataverse-native assignment notification or record the mailbox/delegation blocker.
15. Refresh User & Access and confirm the user appears in the access list with the selected form assignments after processing completes.
16. For a new contact, ask the user to follow the invitation link and sign in.

## CRDB Boundary

Do not reuse the activated Mshirika bundle for CRDB. CRDB must receive a separately approved package after its audit schema, Web API site settings, table permissions, and smoke tests pass.

## Delivery Evidence

Mshirika Power Pages configuration completed against the development target on 2026-07-22:

- Target: `dev`
- Site: `TACATDP Monitoring Tool`
- Admin access role: `Administrators`
- Created/confirmed `Webapi/mp_accessauditlog/*` settings and administrator table permission.
- Created/confirmed `Webapi/contact/*` settings and administrator table permission for contact onboarding.
- Created administrator-only `mp_formassignment` table permission.
- Created administrator-only `mp_formversion` append-to table permission.
- Added `TACATDP/OnboardingFlowTriggerId` as the site setting used by the portal when the cloud flow trigger GUID is available.
- Preserved the existing `Webapi/mp_formassignment/fields=*` setting because Power Pages accepts wildcard fields and the table permission remains the write boundary.
- Latest execution created the missing baseline `mp_formversion` and `mp_formassignment` table permissions, plus the administrator-only `contact` table permission.

The first upload attempt exposed the Enhanced model content limit for generated JavaScript web files. The corrected access-only package uses `VITE_TACATDP_ODK_RUNTIME_ENABLED=false` and uploads only small shell/User & Access assets. The 2026-07-22 onboarding email update used:

- `index-D2Z2Cx8_.mjs` - 129,053 bytes
- `vendor-datepicker-B-UpImsy.mjs` - 283,043 bytes
- `vendor-icons-DA7Dp-7A.mjs` - 6,825 bytes
- `index-XGRK49U1.css` - 50,514 bytes
- `vendor-datepicker-D7vsgEFT.css` - 22,956 bytes

Onboarding email delivery package update completed on 2026-07-22:

- `npm --prefix powerpages/webforms-spa run typecheck` passed.
- `npm --prefix powerpages/webforms-spa run build` passed. The normal ODK-enabled build still emits the known third-party ODK runtime direct-`eval` and chunk-size warnings.
- `npm --prefix powerpages/webforms-spa run build:mshirika-access` passed.
- `python3 scripts/validate-access-create-invite-assign-ux.py` passed.
- `python3 scripts/validate-access-mshirika-activation.py` passed.
- `python3 scripts/validate-access-crdb-update-readiness.py` passed.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-D2Z2Cx8_.mjs` passed.
- `pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll` succeeded in 68.76 seconds.
- `python3 scripts/verify-powerpages-api-smoke-hosted.py --env-file .env` passed after upload.

Post-upload `pac pages download` verified hosted Home contains `onboardingFlowTriggerId` and references:

- `/assets/index-ojTKmmzR.mjs?v=mshirika-native-invitation-20260722-001`
- `/assets/vendor-datepicker-B-UpImsy.mjs?v=mshirika-onboarding-20260722-001`
- `/assets/vendor-icons-DA7Dp-7A.mjs?v=mshirika-onboarding-20260722-001`
- `/assets/index-XGRK49U1.css?v=mshirika-native-invitation-20260722-001`
- `/assets/vendor-datepicker-D7vsgEFT.css?v=mshirika-onboarding-20260722-001`

PAC printed stale `powerpagecomponent` update warnings for records that no longer exist, but the upload completed successfully and post-upload download verified the hosted bundle. Public anonymous GET still returned stale Home content immediately after upload; clear the Power Pages config cache or restart the site before browser acceptance testing.

Native invitation update completed on 2026-07-22:

- Created approved Dataverse connector connection `tacatdp-dataverse-service-principal`.
- Patched `TACATDP - Onboarding Email Delivery` with Dataverse `CreateRecord` for `adx_invitations`, Dataverse `PerformBoundAction` for native `ExecuteWorkflow`, and a response action.
- Re-created `TACATDP/OnboardingFlowTriggerId`.
- `npm --prefix powerpages/webforms-spa run typecheck` passed.
- `npm --prefix powerpages/webforms-spa run build:mshirika-access` passed.
- `python3 scripts/validate-access-create-invite-assign-ux.py` passed.
- `python3 scripts/validate-access-mshirika-activation.py` passed.
- `python3 scripts/validate-access-crdb-update-readiness.py` passed.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-ojTKmmzR.mjs` passed.
- `pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll` succeeded in 58.07 seconds.
- `python3 scripts/verify-powerpages-api-smoke-hosted.py --env-file .env` passed after upload.
- Post-upload `pac pages download` confirmed hosted Home references `/assets/index-ojTKmmzR.mjs?v=mshirika-native-invitation-20260722-001`.

Dataverse-native existing-user notification update completed on 2026-07-22:

- Added `scripts/powerautomate-configure-onboarding-flow.py` as the repeatable flow patcher.
- The Mshirika flow now branches on `deliveryType`.
- `PowerPagesInvitation` creates a native Power Pages invitation and runs the native `Send Invitation` workflow.
- `AssignmentNotification` creates a native Dataverse email activity and runs Dataverse `SendEmail`.
- Office 365 Outlook remains a configurable CRDB option only if its connector, mailbox, and DLP path are approved.
- Rebuilt the Mshirika access bundle as `index-DBwQ_r5R.mjs`.
- Updated package Home references to `/assets/index-DBwQ_r5R.mjs?v=mshirika-dataverse-notification-20260722-001` and `/assets/index-XGRK49U1.css?v=mshirika-dataverse-notification-20260722-001`.

Add User Material control sizing update completed on 2026-07-22:

- Rebuilt the Mshirika access bundle as `index-BC-8uZDL.mjs`.
- Rebuilt the stylesheet bundle as `index-B7Yqis7I.css`.
- Updated package Home references to `/assets/index-BC-8uZDL.mjs?v=mshirika-material-controls-20260722-001` and `/assets/index-B7Yqis7I.css?v=mshirika-material-controls-20260722-001`.

EnsureContact flow boundary update completed on 2026-07-22:

- Browser-side contact creation returned `90040103` for `POST /_api/contacts`.
- The onboarding cloud flow now supports `EnsureContact`, creates the Dataverse contact server-side, and returns `contactId`.
- The portal no longer creates missing contacts directly through browser `/_api/contacts`.
- Rebuilt the Mshirika access bundle as `index-BRtAE5_v.mjs`.
- Updated package Home references to `/assets/index-BRtAE5_v.mjs?v=mshirika-ensure-contact-20260722-001`.

Cloud-flow trigger input correction completed on 2026-07-22:

- Browser-side onboarding submit returned a generic Power Pages 500 page from `POST /_api/cloudflow/v1.0/trigger/<guid>`.
- Dataverse inspection found no contact, invitation, or assignment rows for the attempted email, proving the failure happened before the flow actions ran.
- Live flow inspection showed the Power Pages trigger schema requires `text`, while the portal was posting `eventData` and the flow was parsing `triggerBody()?['eventData']`.
- A raw `{ "text": "..." }` browser post still returned the generic Power Pages 500.
- The portal now posts the documented outer Power Pages `eventData` envelope containing `{ "text": "<serialized business payload>" }`.
- The portal now sends the cloud-flow request through `shell.ajaxSafePost`, matching Microsoft's Power Pages cloud-flow JavaScript sample, instead of the generic JSON `fetch` helper used for Dataverse CRUD.
- The flow configurator now forces Parse JSON content to `triggerBody()?['text']`.
- Rebuilt the Mshirika access bundle as `index-BGBfr46I.mjs`.
- Updated package Home references to `/assets/index-BGBfr46I.mjs?v=mshirika-flow-text-input-20260722-001` and `/assets/index-B7Yqis7I.css?v=mshirika-flow-text-input-20260722-001`.
- Rebuilt the Mshirika access bundle again as `index-DyT1hsoT.mjs` after confirming Power Pages expects an outer `eventData` envelope.
- Updated package Home references to `/assets/index-DyT1hsoT.mjs?v=mshirika-flow-eventdata-wrapper-20260723-001` and `/assets/index-B7Yqis7I.css?v=mshirika-flow-eventdata-wrapper-20260723-001`.
- Rebuilt the Mshirika access bundle again as `index-SeclrLQg.mjs` after isolating cloud-flow transport to `shell.ajaxSafePost`.
- Updated package Home references to `/assets/index-SeclrLQg.mjs?v=mshirika-flow-ajaxsafe-20260723-001` and `/assets/index-B7Yqis7I.css?v=mshirika-flow-ajaxsafe-20260723-001`.

Onboarding feedback hardening completed on 2026-07-23:

- Browser submit appeared to return to the project list without a success or failure message.
- Dataverse inspection for `j.mduda@hotmail.com` found no contact, assignment, access audit, invitation, or Dataverse email rows, so the user was not created and no invitation email was sent.
- User & Access now shows a route-level onboarding outcome panel for success, failure, and pending/interrupted states.
- The pending state is stored before the external cloud-flow call and restored after an unexpected reload so a mutating workflow cannot fail silently.
- Next email-delivery verification must inspect Power Automate run history or Dataverse invitation/email rows after a new retry.

Cloud-flow live schema correction completed on 2026-07-23:

- Browser-side onboarding retry showed a visible outcome panel with `IncorrectPayload` and `Required properties are missing from object: text`.
- The error proves the Power Pages cloud-flow trigger is reachable and schema-validating the request body before flow actions run.
- Live flow metadata showed the trigger had one required `text` input of type string, but Power Pages browser calls deliver the documented `eventData` envelope to the trigger.
- Microsoft Power Pages cloud-flow documentation says browser calls use an `eventData` envelope.
- The portal must send `data: { eventData: "<serialized business payload>" }` through `shell.ajaxSafePost`.
- The portal must not pass `data: JSON.stringify(...)` to `shell.ajaxSafePost`; the 2026-07-23 retry returned `Required properties are missing from object: eventData` for that shape.
- The flow trigger must accept the parsed business payload, not require `eventData` or `text`.
- The portal must not post raw top-level `text`; the 2026-07-23 retry returned `Invalid type. Expected Object but got String` for that shape.
- The flow configurator now forces Parse JSON content to `triggerBody()`.

Cloud-flow action failure diagnostics added on 2026-07-23:

- After the trigger schema correction, browser-side onboarding returned `500 : error` with no contact, assignment, audit, invitation, or Dataverse email rows created for the test user.
- Power Platform run-history API access from the Linux service-principal path was not sufficient to inspect the failed flow action directly.
- The flow configurator now adds explicit Power Pages response actions for Parse JSON, contact create, invitation create/workflow, assignment email create, and assignment email send failures.
- Failure responses return short non-secret status values such as `dataverse-contact-create-failed` or `native-invitation-workflow-failed`.
- The portal now treats any returned failure status as a failed onboarding outcome, even when the cloud-flow response itself is HTTP 200.
- The next browser retry should either create the contact and continue, or show the exact failed flow action in the result panel. A continued generic Power Pages 500 means the run history must be inspected manually in Power Automate.

Cloud-flow site role repair completed on 2026-07-23:

- A follow-up retry still returned generic `500 : error` and Dataverse inspection found no contact, assignment, or access-audit rows for `j.mduda@hotmail.com`.
- The registered Power Pages cloud-flow component existed on the Mshirika site, but it had no linked web roles through the enhanced `powerpagecomponent_powerpagecomponent` relationship.
- `scripts/powerpages-configure-webapi.py` now repairs this condition by linking the registered onboarding cloud-flow component to the configured access role.
- The Mshirika execute run created `cloud flow role link Administrators`.
- `scripts/verify-powerpages-api-smoke-hosted.py` now fails if `TACATDP/OnboardingFlowTriggerId` exists but the registered flow component is not linked to `Administrators`.
- Hosted verification now passes `onboarding cloud flow linked to Administrators`.
- Purge Power Pages cache or restart the site before retrying the browser workflow because site component authorization can be cached.

Cloud-flow eventData trigger correction completed on 2026-07-23:

- A retry after the `Administrators` role link repair still returned generic `500 : error`, proving the missing role link was necessary but not sufficient.
- The registered Power Pages cloud-flow component content includes `flowapiurl` and `processid` for `6b315273-ba85-f111-ab0e-6045bdde781c`, and its content stores the `Administrators` role id.
- The portal bundle was already posting `shell.ajaxSafePost` object data with `eventData`.
- The flow was corrected to require `eventData` as the Power Pages trigger input and parse `@triggerBody()?['eventData']`.
- Live verification confirmed `Parse_JSON.inputs.content = @triggerBody()?['eventData']` and trigger required fields equal `eventData`.
- No portal rebuild was needed for this correction because the hosted bundle already posts the documented `eventData` envelope.

Cloud-flow registration metadata failure found on 2026-07-23:

- A retry after eventData trigger correction still returned generic `500 : error`.
- Dataverse inspection still found zero contact, assignment, and access-audit records for `j.mduda@hotmail.com`.
- Service-principal run-history checks returned zero flow runs, so the flow was not reached.
- The registered Power Pages cloud-flow component content has `flowapiurl`, but `flowtriggerurl` and `metadata` are empty.
- The hosted verifier now fails with:
  - `onboarding cloud flow trigger URL registered`
  - `onboarding cloud flow metadata registered`
- Do not retry onboarding until the flow is re-registered in Power Pages Studio and the hosted verifier passes these checks.

Known limitation: this is an access-only Mshirika test build. The Collect/form-runner path shows a disabled-runtime message in this build. ODK runtime packaging needs a separate chunking or hosting decision before CRDB packaging.
