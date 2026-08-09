# User & Access Tabs and Footer Fix - 2026-07-21

## Issue

The User & Access route rendered too many administration panels in one vertical stack. On the portal preview, the managed footer could visually collide with long access content instead of staying as a clean bottom shell element.

## Requirements

- Keep the managed shell pattern with side navigation, sticky top bar, scrollable workspace, and bottom footer.
- Prevent the footer from overlapping or crowding route content.
- Reduce User & Access density by separating major tasks into tabs.
- Keep current write protections: user creation, role change, suspension, and reactivation remain preview/confirmation-only.

## UX Decision

Use the existing Material-style tab convention inside the User & Access route:

- `Users`: filters, user list, selected-user detail, and confirmation-only user actions.
- `Add user`: guided add-user preview workflow.
- `Roles`: role reference and expectations.

The route-level top action still exposes `Add user` as a shortcut into the `Add user` tab.

## Verification

- `npm run build` passed.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check` passed for packaged `index-BhVLJ_49.mjs`.
- Power Pages upload to Mshirika environment succeeded.
- Post-upload download verified Home references:
  - `/assets/index-BhVLJ_49.mjs?v=access-tabs-footer-20260721-001`
  - `/assets/index-Ofewpmtc.css?v=access-tabs-footer-20260721-001`
- Downloaded module/CSS include the access tab and managed footer shell changes.
