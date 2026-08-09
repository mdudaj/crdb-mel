# Access Onboarding Queue Requirements - 2026-07-24

Status: proposed for next implementation slice.

## Problem

The current **Create, invite and assign** workflow calls a Power Pages cloud flow directly from the portal through `/_api/cloudflow/v1.0/trigger/<guid>`. Repeated Mshirika tests returned generic `500 : error` while Power Automate showed no run history and Dataverse showed no contact, assignment, or audit rows for the attempted user. This means the portal-to-flow bridge can fail before the managed workflow receives a request or returns an actionable error.

Direct portal invocation of Power Pages cloud flows is therefore no longer acceptable for TACATDP onboarding. It is too opaque for a managed banking workflow where administrators need reliable status, auditability, retry behavior, and CRDB-ready deployment controls.

## Goal

Replace direct portal cloud-flow invocation with a Dataverse-backed onboarding request queue. The portal will create an onboarding request row through the normal Power Pages Web API. A Dataverse-triggered automation will process that request server-side, create or reuse the Power Pages contact, create/send the invitation or notification, assign project/form access, and update the request with a business-readable status.

## Evidence

- User-reported browser failures on 2026-07-23 and 2026-07-24 remained `500 : error`.
- Dataverse inspection found zero contact, assignment, and access-audit rows for `j.mduda@hotmail.com` after the failed attempts.
- Power Automate flow details screenshot on 2026-07-24 showed no run history for the flow being tested.
- Power Automate flow details also showed no connections on the manually created registration-test flow.
- Microsoft Power Pages cloud-flow documentation requires solution-aware flows to be added to the site, assigned web roles, and invoked through the Power Pages cloud-flow API.
- Microsoft ALM documentation says cloud flows moved with Power Pages components must be registered in the target environment; unregistered flows fail when invoked from the site.
- Project governance requires repeated Power Platform failures to become durable artifacts and executable checks before further delivery.

References:

- Microsoft Learn: Configure Power Automate cloud flows in Power Pages: https://learn.microsoft.com/en-us/power-pages/configure/cloud-flow-integration
- Microsoft Learn: Integrate Power Automate cloud flow with a Power Pages site: https://learn.microsoft.com/en-us/power-pages/configure/power-automate-how-to

## Users

- Platform Administrator: creates onboarding requests, monitors status, resolves failures, and retries or cancels requests.
- Project Manager: may create onboarding requests for assigned projects only when later authorized.
- New Power Pages user: receives an invitation and gains access only to assigned project/forms after activation.
- Existing Power Pages user: receives assignment notification and gains updated project/form visibility.
- CRDB/DAMAX technical administrator: monitors queue processing and flow run history without modifying portal code.

## Functional Requirements

### Request Capture

- The portal must create an `OnboardingRequest` row through Power Pages `/_api`.
- The portal must not call `/_api/cloudflow/v1.0/trigger/<guid>` for onboarding.
- The request must include full name, primary email, requested role, project id/name, selected forms/form versions, business reason, actor email, actor roles, source route, and a client request id.
- The request must classify the target as new user, existing user, or unresolved at submission time.
- The portal must create the request before any contact, invitation, notification, or assignment mutation is attempted.
- The portal must show the created request id and a `Pending` status immediately after submission.

### Processing

- A Dataverse-triggered cloud flow must process newly created `OnboardingRequest` rows.
- The automation must run server-side using approved Dataverse connection references.
- The automation must create or reuse a contact by primary email.
- For new users, the automation must create/send a Power Pages invitation through the native approved invitation path.
- For existing users, the automation must send an assignment notification through Dataverse-native email or a later approved Office 365 connector.
- The automation must create project/form assignment rows only after request/audit creation succeeds.
- The automation must be idempotent by `RequestId`, `RequestKey`, or alternate key.
- The automation must write step-level status and failure details back to Dataverse without exposing secrets.

### Portal Status UX

- The portal must show request status values: `Pending`, `Processing`, `Completed`, `Failed`, `Cancelled`, and `Needs Review`.
- The portal must allow administrators to refresh status.
- The portal must show business-readable failure messages and next actions.
- The portal must not report invitation/assignment success until the request row is marked `Completed` or a `Needs Review` request has confirmed email delivery or invitation redemption.
- The portal must keep the user on the result/status surface after submission; no silent redirect to project list is allowed.

### Retry and Recovery

- A failed request must not create duplicate assignments on retry.
- Retry must be explicit and administrator-initiated.
- Retry must create a new audit event or append retry metadata to the request.
- Cancellation must mark the request as cancelled without deleting the record.
- Manual resolution must be recorded as an audited status change.

### Audit

- The queue must integrate with `AccessAuditLogs`.
- Each request must preserve actor, affected user, target role, project/form scope, reason, source route, request id, result status, and before/after state where available.
- Failed processing must store sanitized error category and message.
- No request, audit, or status row may store secrets, bearer tokens, anti-forgery tokens, raw invitation codes, passwords, client secrets, or credential-bearing URLs.

## Non-Functional Requirements

- The portal must continue to use Power Pages `/_api` with CSRF handling and table permissions.
- The queue table must have narrow Web API field exposure.
- Ordinary Data Collector users must not create or read onboarding requests.
- The solution package must include the queue schema, choice values, table permissions, cloud flow, connection references, and environment variables where required.
- CRDB deployment must not require editing portal JavaScript to change flow endpoints.
- Processing must be observable through Dataverse rows and Power Automate run history.
- The first Mshirika slice must use the existing Material-style Add User wizard and result panel; major UI redesign is out of scope.

## Out of Scope

- Microsoft Graph user lookup.
- Entra group synchronization.
- Full mailbox/licensing configuration for Office 365 Outlook.
- Public self-registration.
- Password management or local account credential workflows.
- Bulk onboarding upload.

## Acceptance Criteria

- Creating a new user request from the portal creates exactly one Dataverse request row visible to administrators.
- The request row status starts as `Pending` and includes the submitted email, role, project/form scope, reason, and actor.
- A Dataverse-triggered flow run appears when a request row is created.
- On successful processing, the request row becomes `Completed`, the contact exists, assignments exist, and the portal shows success.
- On processing failure, the request row becomes `Failed`, the portal shows the failure message, and no duplicate assignments are created.
- The portal no longer calls `/_api/cloudflow/v1.0/trigger/` for onboarding.
- Hosted verification checks table schema, Web API settings, table permissions, and at least one queue request smoke scenario in Mshirika before CRDB packaging.
