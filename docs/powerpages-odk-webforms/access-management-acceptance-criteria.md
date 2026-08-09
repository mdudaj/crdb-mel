# User and Access Management Acceptance Criteria

Date: 2026-07-21

- A Platform Administrator can open a **User & Access** area in the TACATDP portal.
- A non-admin user cannot see the User & Access navigation entry.
- A non-admin user cannot read or mutate access-management tables through portal `/_api` permissions.
- The Users list shows contact name, exact email, status, role, assigned projects, and assigned forms.
- The UI clearly identifies users who have not logged in or do not yet have a matching Power Pages contact.
- An administrator can assign an existing contact to a TACATDP project.
- An administrator can assign an existing contact to a form/form version.
- Assignment creation is idempotent and does not duplicate a user's access row.
- A newly assigned user sees the project/form after sign-in and cache/session refresh requirements are met.
- An administrator can suspend and reactivate project/form access.
- Suspended access hides the project/form from the user without deleting submission history.
- Role labels match the agreed TACATDP role model.
- Export/reporting capabilities are only available to roles allowed by the authorization matrix.
- All portal data calls use Power Pages `/_api` with CSRF handling for writes.
- Portal code contains no client secrets, bearer tokens, tenant secrets, or Dataverse app credentials.
- Authentication is handled by CRDB Microsoft identity; local password management is not introduced as the default.
- The UI includes loading, empty, error, permission-denied, saving, and saved states.
- Admin actions are auditable through access-change records or Dataverse audit configuration.
- Critical User & Access actions show a confirmation step with affected user, target scope, current state, proposed state, and required reason before mutation.
- Each access mutation uses a client-generated request id and prevents duplicate assignment creation on retry.
- Rollback creates a new audit event and does not edit or delete the original audit event.
- The first live write action is limited to AssignForm for Platform Administrator until a later approved slice enables additional actions.
- AssignForm live write treats an existing equivalent assignment as a successful no-op and does not create a duplicate assignment row.
