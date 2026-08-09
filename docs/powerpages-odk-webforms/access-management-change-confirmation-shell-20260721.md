# User & Access Change Confirmation Shell - 2026-07-21

## Purpose

Add a confirmation-first administration pattern for existing portal users before enabling any Dataverse write operations.

## Requirements

- User detail must expose controlled actions for role change, suspension, and reactivation.
- Each action must open an explicit confirmation panel tied to the selected user.
- The panel must show the user, intended action, current state, requested change, and a reason field.
- The final apply action must remain disabled in this slice.
- The UI must clearly state that no Dataverse records are changed.

## UX Contract

- User & Access remains an administrator-only route.
- Access changes are initiated from the user detail panel, not from the table row.
- Destructive or sensitive changes use a confirmation step before any future write path.
- The confirmation panel uses the same managed-service shell styling as the add-user workflow.

## Implementation Notes

- Added `selectedAccessAction`, `accessChangeRole`, and `accessChangeReason` state.
- Added preview-only handlers for `Change role`, `Suspend access`, and `Reactivate access`.
- Added a confirmation panel with disabled `Apply change disabled` action.
- No Web API create, update, delete, or role-assignment write call was added.

## Verification

- `npm run build` passed.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check` passed for packaged `index-zcOFNAeA.mjs`.
- Power Pages upload to Mshirika environment succeeded.
- Post-upload download verified Home references:
  - `/assets/index-zcOFNAeA.mjs?v=access-confirm-shell-20260721-001`
  - `/assets/index-fmICv7Cm.css?v=access-confirm-shell-20260721-001`
- Downloaded module contains `Confirm access change`, `Apply change disabled`, and the no-write confirmation text.
