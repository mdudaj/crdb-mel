# Beneficiaries Material Abstraction Alignment — August 11, 2026

## Scope

This slice aligns the Beneficiaries route with the shared Material UI abstractions introduced for Projects, Reporting, Project detail, System Activity, and Users.

The route keeps its existing `SurfaceCard` component usage and scoped visual styling. The change adds shared `material-*` classes as behavior and consistency hooks so Beneficiaries no longer sits outside the common surface/list/table/row contract.

## Delivered behavior

- Beneficiary list `SurfaceCard` now also uses `material-list-surface`.
- Beneficiary list header now uses `material-surface-header`.
- Beneficiary count chip now uses `material-count-chip`.
- Beneficiary desktop table wrapper now uses `material-table`.
- Beneficiary desktop rows and mobile record cards now use `material-row`.
- Beneficiary mobile card footer now uses `material-card-footer`.
- Scoped component CSS now includes lightweight support for the shared row/header/footer hooks.
- Existing beneficiary filters, drill-through context, detail drawer, prototype data disclaimer, and Dataverse mapping content are unchanged.

## Non-goals

- No beneficiary data, filter, URL sync, dashboard drill-through, drawer, or Dataverse mapping behavior changed.
- No new dependency was added.
- No deployment was performed as part of this slice.

## Verification

Run from `powerpages/webforms-spa`:

```bash
npm run test:material
npm run typecheck
npm run build:mshirika-runtime
npm run test:powerpages-assets
```

The focused validators updated by this slice are:

```bash
node ../../scripts/validate-beneficiaries-material-list.mjs
node ../../scripts/validate-material-ui-abstractions.mjs
```
