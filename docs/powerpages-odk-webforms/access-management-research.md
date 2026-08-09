# User and Access Management Research

Date: 2026-07-21

## Goal

Define the platform-supported options for TACATDP authentication and authorization before building an administrator-facing user management UI in Power Pages.

## Sources Reviewed

- Microsoft Learn: Power Pages authentication overview
  - https://learn.microsoft.com/en-us/power-pages/security/authentication/
- Microsoft Learn: Set table permissions in Power Pages
  - https://learn.microsoft.com/en-ca/power-pages/security/table-permissions
- Microsoft Learn: Assign table permissions
  - https://learn.microsoft.com/en-us/power-pages/security/assign-table-permissions
- Microsoft Learn: Invite contacts to your Power Pages site
  - https://learn.microsoft.com/en-us/power-pages/security/invite-contacts
- Microsoft Learn: Create and assign web roles
  - https://learn.microsoft.com/en-us/power-pages/security/create-web-roles
- Microsoft Learn: Set up Microsoft Entra External ID with Power Pages
  - https://learn.microsoft.com/en-us/power-pages/security/authentication/entra-external-id
- Microsoft Learn: Roles required for Power Pages administration
  - https://learn.microsoft.com/en-us/power-pages/admin/admin-roles

## Findings

### Authentication

Power Pages represents authenticated site users as Dataverse `contact` rows. A Power Pages user must resolve to a unique contact email. For CRDB, authentication should be handled by Microsoft identity rather than local portal username/password accounts.

Recommended authentication posture:

- Use CRDB Microsoft identity as the primary sign-in provider.
- Prefer Microsoft Entra-backed sign-in configured by CRDB IT.
- Disable or avoid open self-registration unless CRDB explicitly approves it.
- Keep contact email matching strict and visible in the admin UI.
- Treat invitation redemption as a convenience workflow for onboarding, not as the only authorization source.

### Authorization

Power Pages authorization is not only a portal UI concern. Access is enforced through several layers:

- Power Pages web roles assign site-level capabilities to contacts.
- Power Pages table permissions restrict Dataverse access for lists, forms, Liquid, and `/_api`.
- TACATDP business assignments decide which projects and forms a user can access.

TACATDP needs all three layers. A user who can sign in should not automatically see all projects or all submissions.

### Native Administration Options

Power Pages and Portal Management can manage contacts, invitations, web roles, and table permissions, but those tools are administrator-oriented. They are not suitable as the primary CRDB business-user workflow for routine project/form assignment.

Native invitations can assign web roles when redeemed. This is useful for onboarding, but it does not replace TACATDP project/form membership. TACATDP still needs its own assignment records.

For the TACATDP business workflow, the portal UI should treat invitation as part of user creation rather than as a separate Portal Management task:

- new user: create/reuse contact, create/send Power Pages invitation, assign project/forms;
- existing user: assign project/forms and send notification;
- after invitation redemption/sign-in, show only project/form records already assigned in TACATDP.

The actual email-send mechanism needs environment confirmation. Microsoft documents the native **Send Invitation** workflow from Portal Management; portal-side automation may require table permissions plus an approved Dataverse workflow or Power Automate trigger.

### Recommended Product Option

Build a TACATDP **User & Access** UI inside the portal for authorized administrators.

The UI should be a business-facing management surface over Power Pages/Dataverse primitives:

- Contact lookup/status.
- User invitation guidance or invitation creation where permitted.
- Existing-user assignment notification where permitted.
- TACATDP project membership.
- Form assignments.
- Role assignment using controlled TACATDP roles.
- Suspension/deactivation without deleting history.
- Audit trail for access changes.

## Risks

- Changing Entra identity provider settings is a CRDB tenant/security action and requires CRDB IT approval.
- Creating or changing Power Pages web roles and table permissions affects site security and must be packaged and verified.
- Browser `/_api` writes need table permissions and CSRF handling.
- Email mismatch is a real operational risk; the portal should show the exact contact email used for assignment matching.
- If CRDB uses multiple aliases for one person, the admin UI must make the active contact email explicit.

## Research Conclusion

TACATDP should use CRDB Microsoft identity for authentication, Power Pages web roles/table permissions for platform authorization, and TACATDP project/form assignment records for business authorization. The next slice should implement a portal-based User & Access UI for routine administration while keeping high-risk identity-provider and table-permission changes under controlled deployment.
