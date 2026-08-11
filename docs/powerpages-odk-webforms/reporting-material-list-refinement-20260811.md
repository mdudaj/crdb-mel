# Reporting Material List Refinement — August 11, 2026

## Scope

This slice refines the global Reporting route after the Projects, Users, and Project detail Material passes. The intent is to make the Reporting workspace list follow the same Material-style list/table contract while preserving existing reporting navigation and data behavior.

## Delivered behavior

- The Reporting route keeps its metric summary strip.
- Reporting workspaces now sit inside one `reporting-list-surface`.
- The surface has a visible heading, support text, and workspace count chip.
- The desktop reporting workspace table remains semantic and now includes:
  - accessible caption,
  - scoped column headers,
  - keyboard-reachable rows,
  - numeric alignment for Forms and Records,
  - text-labelled projection status chips.
- Existing row actions are preserved:
  - Open project data,
  - Open exports,
  - Open Power BI.
- The no-workspaces state is scoped to the Reporting surface.

## Non-goals

- No reporting query, Dataverse table permission, Power BI, export, or project navigation logic changed.
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
node ../../scripts/validate-reporting-material-list.mjs
```
