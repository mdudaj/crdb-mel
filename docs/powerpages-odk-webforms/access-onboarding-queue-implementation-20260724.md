# Access Onboarding Queue Implementation - 2026-07-24

Status: queue table, Power Pages configuration, Mshirika portal package, access audit schema, and queue processor path deployed. New-user invitation email delivery remains unresolved.

## Delivered

- Added additive `OnboardingRequests` schema artifacts:
  - `schemas/dataverse/onboarding-request-schema.json`
  - `schemas/dataverse/onboarding-request-schema.md`
- Added `mp_onboardingrequest` to the Power Pages Web API/table-permission configuration helper for administrator create/read.
- Updated the Add User submit path to create an onboarding queue row through `/_api/mp_onboardingrequests`.
- Removed the portal dependency on direct `/_api/cloudflow/v1.0/trigger/<guid>` onboarding calls.
- Updated the Add User result UX to show request id, queue record id, `Pending` status, and server-side processing expectations.
- Updated Mshirika/CRDB readiness validators and documentation to use the queue-based architecture.
- Added `scripts/validate-access-onboarding-queue-schema.py`.
- Deployed `mp_onboardingrequest` to the Mshirika Dataverse environment and published customizations.
- Configured Power Pages Web API settings and administrator-only create/read table permission for `mp_onboardingrequest`.
- Uploaded the queue-based Mshirika Power Pages access package.
- Updated hosted verification to validate the queue table, explicit Web API field allowlist, and administrator queue-create permission instead of the abandoned direct cloud-flow trigger registration.
- Deployed `mp_accessauditlog` and configured administrator create/read permission for audit writes.
- Patched Mshirika flow `f2144020-8c86-f111-ab0e-70a8a52eccae` into `TACATDP - Onboarding Queue Processor`.
- Smoke-tested the existing-user path through queue trigger, contact resolution, request audit, assignment audit, assignment duplicate detection, email activity creation, and `NeedsReview` completion.
- Smoke-tested the new-user path through queue trigger, contact creation, request audit, assignment audit, assignment creation, native Power Pages invitation creation, and native Send Invitation workflow execution. Recipient email delivery was not confirmed.

## Current Browser Submit Behavior

When the Mshirika access build is enabled, Add User creates one queue row with:

- `mp_requestkey`
- `mp_requestid`
- `mp_status = 100000000` (`Pending`)
- `mp_requesttype = 100000000` (`NewUser`) or `100000001` (`ExistingUser`)
- user name/email/role
- project and form scope JSON
- business reason
- actor email and role snapshot
- source route
- initial processing attempts and result message

The portal does not create contacts, invitations, notifications, audit rows, or form assignments directly in this path.

## Verification

Passed:

```bash
python3 scripts/validate-access-onboarding-queue-schema.py
python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/onboarding-request-schema.json
python3 scripts/validate-access-create-invite-assign-ux.py
python3 scripts/validate-access-crdb-update-readiness.py
python3 scripts/validate-access-mshirika-activation.py
python3 scripts/validate-access-onboarding-queue-artifacts.py
PYTHONPYCACHEPREFIX=/tmp/tacatdp-pycache python3 -m py_compile scripts/validate-access-onboarding-queue-schema.py scripts/validate-access-onboarding-queue-artifacts.py scripts/validate-access-create-invite-assign-ux.py scripts/validate-access-crdb-update-readiness.py scripts/validate-access-mshirika-activation.py scripts/powerpages-configure-webapi.py
npm --prefix powerpages/webforms-spa run typecheck
npm --prefix powerpages/webforms-spa run build:mshirika-access
node --check powerpages/webforms-spa/dist/assets/index-DGttGQVq.mjs
python3 scripts/validate-webforms-spa-foundation.py
git diff --check
```

Focused bundle/source check confirmed `/_api/mp_onboardingrequests` is present and `/_api/cloudflow/v1.0/trigger` is absent from the SPA source/build.

Mshirika runtime deployment verification passed on 2026-07-24:

```bash
python3 scripts/dataverse-schema-deploy.py --env-file .env --schema-file schemas/dataverse/onboarding-request-schema.json --execute
python3 scripts/powerpages-configure-webapi.py --env-file .env --include-access-writes --access-role-name Administrators --execute
npm --prefix powerpages/webforms-spa run build:mshirika-access
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-00W4I3DT.mjs
python3 scripts/validate-access-mshirika-activation.py
python3 scripts/validate-webforms-spa-foundation.py
pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
python3 scripts/verify-powerpages-api-smoke-hosted.py --env-file .env
```

Hosted verifier evidence:

- Entity set `mp_onboardingrequest` resolves to `mp_onboardingrequests`.
- `Webapi/mp_onboardingrequest/enabled=true`.
- `Webapi/mp_onboardingrequest/fields` is the approved queue-field allowlist, not `*`.
- `Administrators` has create/read-only queue table permission for `mp_onboardingrequest`.
- Entity set `mp_accessauditlog` resolves to `mp_accessauditlogs`.
- `Webapi/mp_accessauditlog/enabled=true`.
- `Webapi/mp_accessauditlog/fields` is the approved audit-field allowlist.
- `Administrators` has create/read-only audit table permission for `mp_accessauditlog`.
- Baseline project, form, assignment, submission, reporting, export, contact, and XForm seed checks still pass.
- The test contact `john.mduda@mshirikacorp.onmicrosoft.com` exists, is active, has `Authenticated Users`, and has redeemed an external identity.

Processor smoke evidence:

- Existing-user smoke request `codex-smoke-20260724121432` reached status `NeedsReview`.
- The processor wrote contact id, audit key, completed timestamp, and a business-readable result message.
- Two audit rows were created for the request: request-level audit and form-assignment audit.
- One Dataverse email activity was created.
- Dataverse `SendEmail` is not yet enabled because direct testing returned a sender delegation error for the flow sender account.
- New-user request `ONB-20260724143253-j-mduda-hotmail-com` created contact `f103749b-6c87-f111-ab0e-70a8a57d9610`, one native Power Pages invitation, access audit rows, and one form assignment.
- Native Send Invitation workflow execution completed for the new-user invitation, but the recipient confirmed no email was received.
- Dataverse email activity search returned zero matching email activities for that new-user invitation smoke, so the request is `NeedsReview` with `mp_errorcategory = invitation-email-not-received`.
- The live Mshirika processor flow was patched after this finding so future requests keep `NeedsReview` until delivery or redemption is confirmed. Snapshot: `artifacts/powerautomate/tacatdp-onboarding-queue-processor-planned-20260724145029.json`.
- Two manual Portal Management resend attempts created recipient email activities, but all invitation email activities remained `Pending Send` with no sent timestamp and zero delivery attempts. The sender mailbox path must be approved and Test & Enable must succeed before automatic invitation email delivery can pass acceptance.
- Testing the synthetic `# TACATDP Impact Tracking` mailbox failed with `User Not Found`; it is an application-user address, not a real Microsoft 365 mailbox. The native Send Invitation workflow must use a real approved sender mailbox.
- Testing `john.mduda@mshirikacorp.onmicrosoft.com` failed because the mailbox is not enabled for Exchange REST connectivity. John cannot be used as the Dataverse sender until Exchange Online mailbox/licensing/connectivity is fixed.
- The selected Mshirika fix is a dedicated Exchange Online shared mailbox: `noreply@mshirikacorp.onmicrosoft.com`.

## Pending Runtime Work

1. Verify native Power Pages invitation email delivery from Portal Management for `Impact Monitoring invitation - j.mduda@hotmail.com`; do not expose the raw invitation code in chat or docs.
2. Create `noreply@mshirikacorp.onmicrosoft.com` as a dedicated Exchange Online shared mailbox.
3. Bind the Dataverse sender mailbox record to `noreply@mshirikacorp.onmicrosoft.com`, approve email, and Test & Enable until outgoing email status is `Success`.
4. Switch the native Send Invitation workflow sender away from `# TACATDP Impact Tracking` to the approved `noreply@mshirikacorp.onmicrosoft.com` mailbox.
5. Inspect the native Send Invitation workflow email/template/mailbox configuration if Portal Management resend still produces no sent email.
6. Configure mailbox delegation or an approved sender identity if existing-user notification must be sent automatically from Dataverse.
7. Confirm non-admin users cannot create onboarding requests through the portal.
8. Package for CRDB only after Mshirika confirms queue create, processor run history, status update, invitation/notification delivery or redemption, audit, assignment, and non-admin denial.
