# Users Material List Refinement — August 11, 2026

## Scope

This slice refines the Users section of the User & Access route. The intent is to align the user list with the Material-style list/table pattern already used in the prototype while preserving the existing access-management data flow.

## Delivered behavior

- Users list toolbar, table/cards, loading state, and no-results state now sit inside one `access-list-surface`.
- The list has a visible heading, explanatory support text, and filtered count chip.
- Desktop remains a semantic table with:
  - accessible caption,
  - scoped column headers,
  - keyboard-reachable rows,
  - numeric alignment for project/form counts,
  - text-labelled contact and access status chips.
- Mobile remains a stacked card list with:
  - leading user identity,
  - trailing access status,
  - contact, role, project count, and form count facts,
  - direct Manage access and Resend invitation actions.
- Loading and no-results states are scoped to the Users list surface.

## Non-goals

- No access authorization logic changed.
- No Dataverse, Power Pages table permission, web role, invitation, or assignment write behavior changed.
- No new UI dependency was added.
- Metric-card left accent rails remain limited to metric/summary cards. Users list cards do not receive decorative rails.

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
node ../../scripts/validate-users-material-list.mjs
```
