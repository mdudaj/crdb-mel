# User and Access Management Requirements

Date: 2026-07-21

## Goal

Add a secure, business-friendly **User & Access** area to the TACATDP Power Pages portal so authorized CRDB/DAMAX administrators can manage user visibility, project membership, and form assignments without developer-run scripts or manual Dataverse edits.

Authentication must be handled by CRDB Microsoft identity, preferably Microsoft Entra sign-in. TACATDP must not introduce local password management as the default authentication mechanism.

## Functional Requirements

- Add an administrator-only **User & Access** area in the portal.
- Show users from Power Pages contacts relevant to TACATDP.
- Display each user's:
  - full name;
  - primary email used for sign-in/contact matching;
  - status;
  - TACATDP role;
  - assigned projects;
  - assigned forms;
  - last known access/update status where available.
- Allow an authorized administrator to create or prepare a user by email and name.
- Detect whether a matching Power Pages contact already exists.
- Show a clear state when the user has not logged in, no contact exists yet, or an invitation must be sent.
- For a new user, create or reuse a Power Pages contact, create a Power Pages invitation, send the invitation email, and assign the selected project/form access.
- For an existing user, assign the selected project/form access and send an assignment notification rather than a duplicate invitation.
- After invitation redemption through CRDB Microsoft identity, the user must see only assigned projects/forms.
- Assign users to TACATDP projects.
- Assign users to forms/form versions through TACATDP assignment records.
- Suspend or reactivate project/form access without deleting historical submissions.
- Prevent ordinary data collectors from seeing the User & Access area.
- Keep project/form visibility filtered by TACATDP business assignment, not only by successful sign-in.
- Preserve the existing `mp_formassignment.mp_useremail` behavior for the prototype while adding a path to contact/project membership lookup hardening.
- Record access changes in an audit-friendly way.
- Require a confirmation step and business reason before any access-management mutation.
- Use a client-generated request id for each write action so retries do not create duplicate assignments.
- Prefer suspend/inactive status over hard deletion for access changes so historical submission context is preserved.

## Audit Requirements

- User & Access writes must not be enabled until the dedicated access audit schema is approved and deployed.
- The proposed schema is `schemas/dataverse/access-audit-schema.json` / `schemas/dataverse/access-audit-schema.md`.
- Every attempted or completed access mutation must create an `AccessAuditLogs` row.
- Required audit data:
  - signed-in administrator email and detected admin roles;
  - affected user email and contact id when available;
  - action, scope, source route, request id, result status, and UTC timestamp;
  - business reason entered by the administrator;
  - before and after JSON snapshots for mutation actions;
  - rollback reference when reversing a prior access change.
- Rollback must be append-only: create a new audit row that references the original event instead of editing or deleting the original audit row.
- The write path must stop before mutating access if the audit create step fails.
- Result messages must be business-readable and must not store secrets, bearer tokens, anti-forgery tokens, passwords, or raw credential material.

## Role Model

### Platform Administrator

Can manage all TACATDP users, projects, forms, assignments, exports, configuration, and access records. This role is for trusted administrators only.

### Project Manager

Can manage users and form assignments only for projects they administer. Can view project submissions and reporting outputs for assigned projects.

### Supervisor / Reviewer

Can view submissions for assigned projects, inspect record detail, update review state where enabled, and request corrections. Cannot manage platform configuration.

### Data Collector / Bank Officer

Can collect data for assigned forms, view their relevant submissions where permitted, and edit records only under configured lifecycle rules. Cannot manage users or exports unless explicitly granted.

### Reporting Officer

Can view assigned project data, use exports, and follow Power BI connection guidance. Cannot collect data or manage users unless combined with another role.

### Read-only Auditor

Can view assigned project records and audit/status information. Cannot edit submissions, collect data, export restricted datasets, or manage users.

## Authorization Matrix

| Capability | Platform Admin | Project Manager | Reviewer | Data Collector | Reporting Officer | Auditor |
| --- | --- | --- | --- | --- | --- | --- |
| View assigned project | Yes | Yes | Yes | Yes | Yes | Yes |
| Collect assigned form | Yes | Optional | No | Yes | No | No |
| View own submissions | Yes | Yes | Yes | Yes | Optional | Yes |
| View all project submissions | Yes | Yes, assigned projects | Yes, assigned projects | No | Yes, assigned projects | Yes, assigned projects |
| Edit unlocked submission | Yes | Optional | Optional review only | Own records only | No | No |
| Review/approve submissions | Yes | Optional | Yes | No | No | No |
| Export project data | Yes | Yes | Optional | No | Yes | Optional |
| Manage project users | Yes | Assigned projects only | No | No | No | No |
| Manage platform roles/config | Yes | No | No | No | No | No |
| Suspend/reactivate access | Yes | Assigned projects only | No | No | No | No |

## Non-Functional Requirements

- No client secrets, bearer tokens, app credentials, or tenant secrets in portal code.
- All portal Dataverse access must use Power Pages `/_api` with table permissions and CSRF handling.
- User management UI must show loading, empty, error, permission-denied, and saved states.
- Email matching must be visible and auditable.
- Role labels must use bank-worker terminology, not research-platform jargon.
- The UI must be usable at laptop/tablet widths and remain readable on mobile.
- Access changes must be reversible without deleting users or submission history.
- Access audit rows must be queryable by administrators without exposing them to ordinary data collectors by default.

## Out of Scope for First Slice

- Full Microsoft Graph group synchronization.
- Automatic Entra group-to-role provisioning.
- Embedded Power BI security model.
- Self-service public registration.
- Password reset/local account workflows.
- Fine-grained field-level authorization.

## Open Decisions

- Whether CRDB wants Microsoft Entra ID, Microsoft Entra External ID, or another approved Entra-backed provider for this site.
- Invitation creation and notification sending is resolved by ADR 0008 for the next implementation slice: the portal creates an `OnboardingRequest` queue row through `/_api`, and Dataverse-triggered automation performs contact, invitation/notification, assignment, audit, and status updates.
- Whether Project Manager can assign Reporting Officer and Reviewer roles, or only Data Collector access.
- Whether export permission should be separate from reporting view permission.
- Whether CRDB wants audit-log read access for project managers, read-only auditors, or only platform administrators.
