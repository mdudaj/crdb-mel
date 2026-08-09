# User & Access Activity Audit Preview - 2026-07-21

## Purpose

Introduce the audit-history pattern expected for a managed banking administration surface before enabling real access writes.

## Requirements

- Add an `Activity` tab under User & Access.
- Show read-only access activity derived from current assignment, contact, and access-status state.
- Add selected-user activity inside the user detail drawer.
- Clearly mark activity as audit preview, not persisted audit records.
- Do not add Dataverse create, update, delete, or audit-log write calls.

## UX Notes

- `Users` remains focused on user search and inspection.
- `Activity` previews the future review model: user, event, detail, and source.
- Drawer activity is scoped to the selected user.
- Warning events highlight contact checks and pending access states.

## Verification

- `npm run build` passed.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check` passed for packaged and downloaded `index--uRBOGBI.mjs`.
- Power Pages upload to Mshirika environment succeeded.
- Post-upload download verified Home references:
  - `/assets/index--uRBOGBI.mjs?v=access-activity-preview-20260721-001`
  - `/assets/index-MsUYfavH.css?v=access-activity-preview-20260721-001`
- Downloaded module/CSS include `Access activity`, `Read-only audit preview`, `access-activity-panel`, and `access-activity-row`.
