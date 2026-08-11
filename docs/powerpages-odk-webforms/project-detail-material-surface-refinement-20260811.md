# Project Detail Material Surface Refinement — August 11, 2026

## Scope

This slice refines the selected Project detail route after the Users list Material pass. The intent is to make the project workspace panels use the same Material-style surface contract without changing data access, Dataverse reads/writes, exports, or Power BI connection behavior.

## Delivered behavior

- The Project detail route keeps the selected project command card, section tabs, and metric summary cards.
- The Data tab now uses a `project-detail-surface` with:
  - a visible heading,
  - support text that states the data scope,
  - a visible reporting-record count chip,
  - the existing search control,
  - the existing reporting access note and filters.
- The reporting records table remains a semantic desktop table with:
  - accessible caption,
  - scoped column headers,
  - keyboard-reachable rows,
  - numeric alignment for version values,
  - text-labelled projection status chips with tone classes.
- Exports and Power BI tabs now share the same `project-detail-surface` card treatment as the Data tab.
- Metric-card accent rails remain limited to metric/summary cards. Project detail content surfaces do not receive left accent rails.

## Non-goals

- No Dataverse schema, Power Pages table permission, or reporting query behavior changed.
- No export-generation logic changed.
- No Power BI connection instructions changed.
- No new UI dependency was added.
- No deployment was performed as part of this slice.

## Verification

Run from `powerpages/webforms-spa`:

```bash
npm run test:material
npm run typecheck
npm run build:mshirika-runtime
npm run test:powerpages-assets
```

The focused validator is:

```bash
node ../../scripts/validate-project-detail-material-surface.mjs
```
