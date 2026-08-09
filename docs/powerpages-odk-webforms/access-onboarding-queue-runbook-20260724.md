# Access Onboarding Queue Runbook - 2026-07-24

Status: proposed operating runbook.

## Principle

Do not call `/_api/cloudflow/v1.0/trigger/<guid>` directly for User & Access onboarding. The portal creates an `OnboardingRequest` row. Dataverse automation processes the request and writes the result.

## Administrator Workflow

1. Confirm whether the Power Pages site is private or public.
2. If the site is private, add the CRDB/Microsoft Entra user under Power Pages Studio > Security > Site visibility > Grant site access before sending or retrying an invitation. This is a Microsoft site-visibility gate, separate from TACATDP Contact, Web Role, Table Permission, Invitation, and assignment records.
3. Open **User & Access**.
4. Choose **Add User**.
5. Enter name, email, role, project/form access, and business reason.
6. Review the confirmation step.
7. Submit the request.
8. Confirm the portal shows a request id and `Pending` or later status.
9. Use refresh to monitor progress.
10. Communicate access only after the request is marked `Completed` or a `NeedsReview` request has confirmed invitation delivery/redemption through the administrator review path.

## Expected System Workflow

1. Portal creates one `OnboardingRequest` row through Power Pages `/_api`.
2. Request starts as `Pending`.
3. Dataverse-triggered cloud flow starts from the row create/update event.
4. Flow sets request to `Processing`.
5. Flow creates or reuses Power Pages contact by primary email.
6. Flow creates access audit row.
7. Flow creates or requests invitation delivery for a new user, or creates assignment notification evidence for an existing user.
8. Flow creates project/form assignment rows.
9. Flow marks request `NeedsReview` when email delivery or invitation redemption still requires administrator confirmation.

## Failure Handling

If the portal shows `Failed`:

1. Open the request detail.
2. Review `mp_errorcategory` and `mp_resultmessage`.
3. Check Power Automate run history for the same request id.
4. Fix missing permission, connection reference, email setting, or data issue.
5. Retry explicitly from the portal when retry is enabled.
6. Do not create manual duplicate assignments unless the failure is formally resolved and audited.

If the request remains `Pending`:

1. Confirm the Dataverse-triggered flow is on.
2. Confirm connection references are healthy.
3. Confirm the trigger table is `mp_onboardingrequest`.
4. Confirm the row exists in the same environment as the flow.

If the request remains `Processing`:

1. Inspect the flow run for timeout or connector failure.
2. Mark as `Needs Review` or `Failed` through an approved administrator path.
3. Retry only after idempotency is confirmed.

If the request shows `NeedsReview` after server-side writes:

1. Confirm the contact, invitation, audit, and assignment rows exist.
2. For new users, open Portal Management > Security > Invitations and find the matching invitation by name/email.
3. Use the supported Portal Management command bar path to resend the invitation.
4. Confirm the recipient receives the email or redeems the invitation before treating the request as completed.
5. If no email is received, inspect the native Send Invitation workflow email template and outgoing mailbox settings.
6. Do not copy raw invitation codes or links into chat, tickets, or repository files.
7. If invitation email activities are created but remain `Pending Send` with zero delivery attempts, do not Test & Enable a synthetic application-user mailbox. Change the workflow sender to an approved licensed Microsoft 365 mailbox that passes Test & Enable for outgoing email.
8. If Test & Enable reports that the mailbox is not enabled for REST connectivity, confirm the account has an Exchange Online mailbox/license, is not disabled, and belongs to the tenant/server profile being used.
9. Preferred managed-system pattern: use a dedicated shared/service mailbox, such as `noreply@mshirikacorp.onmicrosoft.com`, rather than a personal maker account.

## CRDB Invitation Redemption Diagnostics

Do not treat a generated manual invitation URL, a prefilled invitation code, or a successful Microsoft sign-in prompt as proof that Power Pages invitation redemption completed.

Before advising a retry, verify access gates in order:

1. If the site is private, the user appears in Power Pages Studio > Security > Site visibility > People who can access the site.
2. Invitation Status Reason is no longer `New`, or the invitation is otherwise marked redeemed/used by the platform.
3. The Contact has an `adx_externalidentity` row linked to the signed-in Microsoft identity.
4. The Contact has the expected Power Pages web role.
5. The Contact email matches an active `mp_formassignment.mp_useremail` for the assigned form.
6. The user can load the portal home page after cache purge/restart.

If the user enters the code, is redirected to Microsoft sign-in, and then lands on Access Denied while the invitation remains `New` and no `adx_externalidentity` exists, redemption did not complete. Investigate the site registration/authentication settings, open-registration behavior, the actual redemption page route, provider claims mapping, and Contact/web-role linkage. Do not issue repeated invitation links without first proving which step failed.

## CRDB Deployment Checklist

- Queue schema imported.
- Status and request-type choices imported.
- Alternate key on `mp_requestkey` active.
- Power Pages Web API settings include only approved queue fields.
- Table permissions grant administrator create/read and deny ordinary collector access.
- Dataverse-triggered flow imported and turned on.
- Connection references are bound to an approved CRDB owner/service account.
- Contact, invitation, assignment, and audit table permissions are available to the flow owner.
- Portal cache purged after import.
- Private-site test users granted Site visibility access before invitation redemption testing.
- New-user and existing-user smoke tests completed.

## Escalation Data to Capture

- Request id.
- Request status.
- Affected user email.
- Actor email.
- Power Automate run id.
- Sanitized error category and message.
- Timestamp in local time and UTC where available.

Never send secrets, bearer tokens, anti-forgery tokens, raw invitation links, or connector credentials in support messages.
