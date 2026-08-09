# User Activation Diagnostics

Date: 2026-07-31

## Purpose

Add a read-only administrator diagnostic view that separates user provisioning
from Power Pages activation. On private developer/non-production sites, a user
must first be granted Power Pages Site visibility access. A user is not ready
until the Power Pages invitation has been redeemed and a Microsoft identity is
bound to the Dataverse contact. In this model, invitation redemption creates a Power Pages external identity for the contact.

## Requirements

- Show one activation row per user email in current User & Access scope.
- Show contact status, email uniqueness, invitation status, redemption status,
  external identity status, web-role status, and assignment status.
- Derive a clear next action:
  - `Send code`
  - `Await redemption`
  - `Redeemed`
  - `Ready`
  - `Needs admin review`
- Treat private-site Site visibility access as necessary but not sufficient when the site is private.
- Treat active TACATDP form assignments as necessary but not sufficient.
- Treat contact login flags as useful but not sufficient.
- Treat `adx_externalidentity` as the activation proof for Microsoft sign-in.
- Do not create contacts, invitations, assignments, or external identities from
  this view.
- If diagnostics tables are not exposed through Power Pages Web API/table
  permissions, show an explicit unavailable state instead of marking users
  active.
- Package read-only diagnostics Web API/table-permission configuration for
  Platform Administrators only:
  - extended `contact` read fields for login flags;
  - `adx_invitation` read fields needed to see active invitation state;
  - `adx_externalidentity` read fields needed to prove identity binding.

## UX

Show activation diagnostics under `System Activity > Onboarding` so user
provisioning, invitation redemption, and operational onboarding checks stay in
one administrative timeline. The page is compact and operational:

- top status note: activation means invitation redemption plus external identity;
- summary chips for ready, pending, and review counts;
- table with status chips and the derived next action;
- no raw invitation codes in the diagnostic table;
- refresh action reuses the User & Access refresh path.

## System Design Notes

The system boundary includes Power Pages authentication, Dataverse contacts,
invitations, redemption activity, external identities, web roles, and TACATDP
assignments. The key delayed feedback loop is invitation redemption: the
processor can create invitation and assignment records before the user redeems
the invite. The UI must not collapse those states into one success message.

## Verification

- Build succeeds.
- Validator checks that activation diagnostics types, API client method,
  System Activity onboarding panel, status labels, and permission packaging
  exist.
- Local render shows the System Activity onboarding panel and derived states.
- Hosted CRDB verification after deployment checks one non-admin test user:
  private-site access grant, contact, invitation, redemption, external identity, web role, and assignment.
- Before hosted verification, run the approved Power Pages configuration script
  with access writes enabled so the diagnostic tables and fields are exposed to
  the Platform Administrator web role.
