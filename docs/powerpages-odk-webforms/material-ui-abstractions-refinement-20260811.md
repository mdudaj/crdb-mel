# Material UI Abstractions Refinement — August 11, 2026

## Scope

This slice consolidates the repeated Material-style surface, header, count-chip, table, row, and card-footer patterns introduced across Projects, Reporting, Project detail, System Activity, and Users.

The intent is to reduce page-local UI drift before adding more routes or dashboard modules.

## Delivered behavior

- Added shared CSS primitives:
  - `material-surface`
  - `material-list-surface`
  - `material-surface-header`
  - `material-count-chip`
  - `material-table`
  - `material-row`
  - `material-card-footer`
- Migrated the recently refined routes to use the shared primitives while retaining route-specific aliases for scoped layout and validator readability.
- Preserved existing route behavior, data loading, authorization checks, actions, and status-chip text.
- Kept metric-card accent rails unchanged and limited to metric/summary cards.
- Updated route validators to assert shared primitives instead of only page-local class contracts.
- Added a shared abstraction validator so future UI slices do not recreate the same local surface/header/count/table rules.

## Non-goals

- No Dataverse, Power Pages Web API, authorization, reporting, onboarding, submission, or export logic changed.
- No dependency was added.
- No route was visually redesigned beyond class consolidation.
- No deployment was performed as part of this slice.

## Verification

Run from `powerpages/webforms-spa`:

```bash
npm run test:material
npm run typecheck
npm run build:mshirika-runtime
npm run test:powerpages-assets
```

The focused shared abstraction validator is:

```bash
node ../../scripts/validate-material-ui-abstractions.mjs
```
