# User & Access Detail Drawer - 2026-07-21

## Purpose

Move selected-user detail out of the main User & Access page flow so the route remains compact after the user opens a record.

## Requirements

- Selecting a user opens a right-side drawer instead of expanding an inline panel.
- The drawer must show contact state, role, access status, assigned form count, confirmation-only actions, and assigned project/form access.
- The drawer must close through the close button or outside scrim.
- Existing role change, suspend, and reactivate actions remain confirmation-only with disabled apply.
- No Dataverse write path is added.

## UX Notes

- The Users tab remains focused on finding and comparing users.
- The drawer is for inspection and review of one user.
- Assignment rows show both the project label and form details so bank administrators can understand access scope without leaving the table.
- On mobile, the drawer becomes full-width.

## Verification

- `npm run build` passed.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check` passed for packaged and downloaded `index-BVHym9H3.mjs`.
- Power Pages upload to Mshirika environment succeeded.
- Post-upload download verified Home references:
  - `/assets/index-BVHym9H3.mjs?v=access-user-drawer-20260721-001`
  - `/assets/index-DjlzOFN9.css?v=access-user-drawer-20260721-001`
- Downloaded module/CSS include `access-detail-drawer`, `access-drawer-scrim`, and `Project and form access`.
