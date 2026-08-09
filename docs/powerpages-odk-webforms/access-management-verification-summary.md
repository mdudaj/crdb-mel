# TACATDP User & Access Verification Summary

Date: 2026-07-21

## Scope Verified

This verification covers the read-only User & Access portal shell for the TACATDP Monitoring Tool. The slice adds an administrator-only entry point, a user access overview, assignment/contact status checks, filters, a detail side panel, and a role reference panel. It does not change Dataverse schema, Power Pages table permissions, web roles, site settings, authentication configuration, or deployed CRDB site content.

## Evidence

- Local render evidence: `/tmp/tacatdp-user-access-view.png`
- Local first-screen evidence: `/tmp/tacatdp-access-shell.png`
- Build command: `npm run build`
- Build result: passed

## Build Notes

The build completed successfully with the existing upstream warnings from `@getodk/web-forms`:

- direct `eval` warning in the package bundle;
- large generated chunks warning.

These warnings are not introduced by the User & Access shell. They remain a production-hardening item for the ODK Web Forms runtime and content security policy.

## Visual Smoke Result

The local fixture rendered:

- Projects first screen with the `User & Access` action visible for local admin mode.
- User & Access header with back and refresh actions.
- Access overview with metrics.
- Role filter and search field.
- Desktop access table with icon-only view action.
- Role reference panel.

No visible overlap or blank render was observed in the captured desktop view.

## Remaining Gates

The following work is intentionally not performed in this slice because it changes authentication, authorization, Power Pages site settings, or deployed content:

- Configure the CRDB Microsoft Entra sign-in policy if not already active.
- Assign the correct Power Pages administrator role to the approved TACATDP administrators.
- Package or configure table permissions for access-management reads.
- Enable/verify Power Pages Web API site settings for any additional tables used by the access UI, especially `contacts` if contact status checks are required.
- Upload the SPA bundle to the target CRDB Power Pages site.
- Purge Power Pages cache, restart the site, and run browser runtime `/_api` smoke tests in CRDB.

## Acceptance Status

Accepted for local read-only shell delivery. Not accepted for CRDB deployment until the permission and deployment gates above are approved and executed.

## CRDB Deployment Update

Date: 2026-07-21

Approved deployment executed against:

- Environment: `TACATDP-CRDB-Dev`
- Environment URL: `https://org5eb0379b.crm4.dynamics.com/`
- PAC profile: `tacatdp-crdb-20260721`
- Site: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`

Deployment approach:

- Downloaded the current CRDB Power Pages enhanced-model package to `/tmp/tacatdp-crdb-pages`.
- Applied only the current SPA build assets, Home page role payload, and admin-scoped contact read configuration to that downloaded CRDB package.
- Uploaded `/tmp/tacatdp-crdb-pages/tacatdp-monitoring-tool` using `pac pages upload --modelVersion Enhanced --forceUploadAll`.

Deployment result:

- `pac pages upload` succeeded in 110.80 seconds.
- Post-upload PAC metadata checks confirmed `Webapi/contact/enabled = true`.
- Post-upload PAC metadata checks confirmed `Webapi/contact/fields = contactid,fullname,emailaddress1,statecode`.
- Post-upload PAC metadata checks confirmed a global read-only `contact` table permission exists.
- Post-upload download confirmed the `contact` permission is linked to the `Administrators` web role only.
- Post-upload PAC metadata checks confirmed Home includes the `roles` Liquid payload and references `index-Dx9yUGB4.mjs` / `index-ChLB0qW2.css` with version `user-access-20260721-001`.

Remaining runtime checks:

- Purge Power Pages cache and restart/sync the site from the Power Pages UI.
- Sign in as Denis and confirm the Projects screen shows **User & Access**.
- If **User & Access** is hidden, assign Denis's portal contact to the `Administrators` web role through Power Pages Security/Management UI and retest.
- Confirm a non-admin user does not see the **User & Access** action.
- Open **User & Access** and verify assigned users load; contact status should show `Contact active`, `Contact not found`, or `Contact check unavailable` without breaking the page.
