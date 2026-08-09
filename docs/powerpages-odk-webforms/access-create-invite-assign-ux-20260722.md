# Create, Invite, and Assign UX - 2026-07-22

Status: implemented as a guarded UX with an explicit Mshirika test activation path.

## Target Workflow

For a new user, an administrator enters full name, Microsoft account email, role, project, form access, and a business reason. The activated Mshirika path can create or reuse the Power Pages contact: it reads existing contacts through Power Pages Web API, but missing contact creation is delegated to the registered Dataverse cloud flow through `EnsureContact`. After the flow returns the contact id, the portal writes audited TACATDP project/form assignments and calls the same flow to create and send the native Power Pages invitation email.

For an existing user, the administrator selects the same role/project/form scope. The activated Mshirika path writes any missing assignments and calls the registered Power Pages cloud flow with `AssignmentNotification`; the flow sends a native Dataverse email through the configured Dataverse sender.

After the invited user redeems the Power Pages invitation and signs in through CRDB Microsoft identity, project/form visibility remains controlled by TACATDP assignment records.

## UX Delivered

- Renamed the Add User workflow to **Create, invite and assign**.
- Added full name capture before email validation can proceed.
- Replaced the old contact-status step with an onboarding-path step.
- Shows either **Create contact, invite and assign** or **Assign existing user and notify** based on whether the email already appears in current access data.
- Final review shows workflow, name, email, contact state, role, project, form count, reason, and expected email delivery.
- Final action remains disabled behind `getUserOnboardingReadiness()` in normal builds.
- The explicit Mshirika access build enables `submitUserOnboardingAccess()` for controlled testing.
- Result output shows whether the contact was created or reused, assignment write outcomes, email delivery status, flow response, and email request id. Existing users report `assignment-notification-sent` only after the Dataverse-native flow accepts the request.
- Create, invite, and assign now also writes a route-level onboarding outcome panel. Success, failure, and pending/interrupted states must remain visible after submit and must not be lost by an unexpected reload or return to the project list.
- A pending outcome is stored before the external cloud-flow call and replaced only after the portal receives confirmed success or failure. If the page reloads first, the user returns to User & Access with an explicit unconfirmed state.

## Implementation Boundary

Normal builds do not send email and do not create Dataverse records. The Mshirika test build can create/reuse contacts and create audited assignment records: existing contacts are read through Power Pages Web API, missing contact creation is delegated to the onboarding flow, and then the portal invokes `/_api/cloudflow/v1.0/trigger/<guid>` for new-user native invitations and existing-user Dataverse assignment notifications when `TACATDP/OnboardingFlowTriggerId` is configured on the Power Pages site.

The portal does not call Dataverse workflow actions directly. Microsoft documents that Power Pages Web API supports data operations, not actions/functions. The supported portal-side email path is a Power Pages-registered cloud flow secured by web role.

## Cloud Flow Contract

Create a solution-aware Power Automate flow with the Power Pages cloud flow trigger whose schema accepts the Power Pages `eventData` string.

The portal invokes cloud flows with Power Pages `shell.ajaxSafePost`, matching Microsoft examples for `/_api/cloudflow/v1.0/trigger/<guid>`. Microsoft documents the browser request as a data object with `eventData`. The trigger body contains `eventData`, whose value is the serialized onboarding business payload. The flow `Parse JSON` action must parse `@triggerBody()?['eventData']`. The parsed business payload contains:

- `requestId`
- `deliveryType`: `PowerPagesInvitation` or `AssignmentNotification`
- `contactId`
- `email`
- `fullName`
- `role`
- `projectName`
- `reason`
- `actorEmail`
- `assignmentResults`
- `sourceRoute`
- `occurredAt`

The flow should:

1. For `EnsureContact`, create the missing Dataverse contact and return `contactId`.
2. For `PowerPagesInvitation`, create/send the Power Pages invitation using the approved Portal Management invitation process or equivalent governed Dataverse/Power Automate steps.
3. For `AssignmentNotification`, create a native Dataverse email activity from the configured sender system user to the contact and run the Dataverse `SendEmail` action.
4. Keep Office 365 Outlook as a configurable future provider option for CRDB if its mailbox/licensing path is approved; do not require it for Mshirika.
5. Return a response body with a business-readable status where possible.
6. Avoid exposing secrets or credentials in portal code, site settings, or returned messages.

Do not create new contacts directly through browser `POST /_api/contacts`. The 2026-07-22 Mshirika test returned `90040103` for browser-side contact create even with the administrator role and contact table permission present; the supported product boundary is the role-secured cloud flow.

Do not post raw top-level `text` outside the Power Pages `eventData` envelope, do not pass a manually stringified request body to `ajaxSafePost`, and do not use the generic JSON `fetch` helper for `/_api/cloudflow`. The 2026-07-23 Mshirika retries showed four failure signatures: missing `text` when the flow trigger schema required `text`, missing `eventData` when the flow trigger schema required `eventData`, `Invalid type. Expected Object but got String` when raw `text` was posted directly, and missing `eventData` when a manually stringified JSON body was passed to `ajaxSafePost`. The concrete contract is `shell.ajaxSafePost` with `data: { eventData: "<serialized business payload>" }`, trigger schema requiring `eventData`, and flow Parse JSON content `@triggerBody()?['eventData']`.

Do not allow this mutating workflow to finish silently. It must show a page-level result with the affected email, time, result message, and actionable details. Email delivery is not confirmed until the user receives the invitation or the administrator verifies the Power Automate/Dataverse email run history.

If the cloud flow fails after the trigger accepts the request, the flow must still respond to Power Pages with a short non-secret status and message. Required failure statuses are:

- `onboarding-payload-parse-failed`
- `dataverse-contact-create-failed`
- `native-invitation-create-failed`
- `native-invitation-workflow-failed`
- `dataverse-assignment-email-create-failed`
- `dataverse-assignment-email-send-failed`

The portal must treat any returned status containing `failed`, `error`, or timeout language as a failed onboarding result, even if Power Pages delivered the flow response over HTTP 200. This prevents the UI from reporting invitation or notification success when the flow only acknowledged the request and then failed in a Dataverse action.

## Verification

- `npm --prefix powerpages/webforms-spa run typecheck`
- `python3 scripts/validate-webforms-spa-foundation.py`
- `python3 scripts/validate-access-crdb-update-readiness.py`
- `python3 scripts/validate-access-write-preview-ui.py`
- `python3 scripts/validate-access-create-invite-assign-ux.py`
