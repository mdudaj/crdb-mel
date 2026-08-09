# Existing User Access Lifecycle Delivery - 2026-07-30

## Purpose

Portal administrators need a controlled way to correct user emails and remove access after onboarding mistakes, without deleting contacts or requiring direct Dataverse table editing.

## Requirements

- Platform Administrator users can open User & Access, select an existing user, and choose a lifecycle action.
- Correct email requires a new valid email address and a business reason.
- Remove access requires a business reason and deactivates active form assignment rows instead of deleting contacts.
- Every lifecycle change creates an AccessAuditLogs request before mutation and updates that audit record with Succeeded or Failed.
- Assignment reads only return active assignment rows so removed users lose project/form visibility after cache refresh and sign-in refresh.
- Power Pages Web API must allow Platform Administrator write access to Contacts and FormAssignments for the approved fields only.

## Design Decision

Use direct audited Power Pages Web API writes for this narrow administrator lifecycle path:

- Contact email correction: PATCH contact `emailaddress1` when a matching contact exists.
- Assignment email correction: PATCH `mp_useremail` and deterministic `mp_assignmentkey` on active assignment rows.
- Access removal: PATCH `mp_lifecyclestatus` to inactive on active assignment rows.

This avoids contact deletion, preserves auditability, and gives administrators immediate recovery from email entry mistakes. The known limitation is that multiple Dataverse PATCH operations are not transactional from the browser; failed partial updates are recorded in AccessAuditLogs and should be reviewed by an administrator.

## Delivery Instructions

1. Import the latest managed solution/table metadata first.
2. Enable Power Pages Web API fields for Contacts and FormAssignments using the updated configuration script or equivalent Power Pages Management changes.
3. Upload the packaged Power Pages site bundle.
4. Purge Power Pages cache and restart/sync the site.
5. Sign in as Platform Administrator and verify User & Access is visible.
6. Correct one test user email and confirm the contact/assignment rows update.
7. Remove one test user's access and confirm they disappear from active assignment views.
8. Confirm Access activity/audit records show the request and result.

## Verification

- `npm --prefix powerpages/webforms-spa run typecheck`
- `npm --prefix powerpages/webforms-spa run build:mshirika-access`
- `python3 scripts/validate-webforms-spa-foundation.py`
- `python3 scripts/validate-access-crdb-update-readiness.py`
- `python3 scripts/validate-access-write-path-contract.py`
- `node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-CJU3GZ7F.mjs`
- `git diff --check`
