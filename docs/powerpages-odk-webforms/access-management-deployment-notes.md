# User and Access Management Deployment Notes

Date: 2026-07-21

## Purpose

Record the deployment prerequisites for the read-only **User & Access** portal shell.

## Current Slice

This slice is read-only. It does not create users, send invitations, assign roles, suspend access, or write Dataverse records.

The shell reads:

- `mp_formassignment` to identify TACATDP users in scope;
- related form/form-version records to summarize form access;
- `contact` when the Power Pages Web API and table permission allow the read, to show whether the assignment email has a matching portal contact.

If contact read is not enabled, the UI shows `Contact check unavailable` rather than failing the whole page.

## Admin Gate

The portal now expects Power Pages Liquid to expose the signed-in user's web roles in `window.__TACATDP_POWERPAGES__.roles`.

The **User & Access** entry point is visible only when the signed-in user has one of these Power Pages web roles:

- `Administrators`
- `Platform Administrator`

Local Vite development remains allowed without a portal role so the UI can be reviewed locally.

## Required Power Pages Configuration

Before deployment to CRDB, verify:

1. A web role exists for administration:
   - use the existing `Administrators` web role, or
   - create/package `Platform Administrator` if CRDB wants TACATDP-specific naming.
2. The intended administrator contact is assigned that web role.
3. Existing authenticated read access for `mp_formassignment`, `mp_formversion`, and `mp_form` remains intact.
4. If contact status should show exact active/missing state, configure:
   - `Webapi/contact/enabled = true`
   - `Webapi/contact/fields = contactid,fullname,emailaddress1,statecode`
   - a table permission that grants admin role read access to `contact`.

Do not grant broad contact read to ordinary data collectors unless CRDB approves that privacy model.

## Verification

- Signed-in administrator sees the **User & Access** button on the Projects screen.
- Signed-in non-admin does not see the **User & Access** button.
- Deep-linked non-admin sees the permission-denied state.
- Administrator can load the assigned-user list.
- The list shows `Contact active`, `Contact not found`, or `Contact check unavailable` without breaking the page.
- No browser code contains secrets or bearer tokens.

## Next Slice

After the read-only shell is deployed and verified:

1. Package a TACATDP-specific `Platform Administrator` web role if needed.
2. Add proper admin-scoped table permissions for contact/access management.
3. Add audit-backed write actions for assignment create/suspend/reactivate.
