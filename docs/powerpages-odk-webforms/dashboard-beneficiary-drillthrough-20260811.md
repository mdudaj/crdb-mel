# Dashboard-to-beneficiary drill-through

Date: 2026-08-11

## Scope

This slice adds prototype navigation from TACATDP dashboard summary visuals into the beneficiary registry. It is client-side only and uses demonstration data. It does not write to Dataverse, Power Pages, or any external service.

## Implemented entry points

- Active Borrowers KPI opens Beneficiaries filtered to `Active borrower`.
- Farmers Trained KPI opens Beneficiaries filtered to trained records.
- Selected regional summary opens Beneficiaries filtered to the selected region.
- Technology chart clicks open Beneficiaries filtered to the selected technology.
- Recent Data Submissions rows open Beneficiaries filtered by region and submission status.

## Filter behavior

Dashboard drill-through state is encoded in the hash URL, for example:

```text
#/beneficiaries?source=dashboard&region=Morogoro
```

Beneficiaries parses the URL on route entry and hash changes, shows active filter chips, and keeps non-search filters synchronized back to the URL when the reviewer changes or clears filters.

## Verification

Run from `powerpages/webforms-spa`:

```bash
npm run test:material
npm run typecheck
```

The material validation suite includes `scripts/validate-dashboard-beneficiary-drillthrough.mjs` so this behavior remains checked with future UI changes.
