# Beneficiary Detail Model Slice — 2026-08-11

## Purpose

This slice models TACATDP beneficiaries as reusable monitored entities in the prototype. It adds value because a beneficiary becomes more than a submitted form row: the UI can show profile, finance, training, technology, submission, outcome, and future Dataverse relationship context from one place.

## Scope

- Add richer prototype-only beneficiary records in `powerpages/webforms-spa/src/prototype/beneficiaries.ts`.
- Add a Beneficiaries detail drawer in `powerpages/webforms-spa/src/views/BeneficiariesView.vue`.
- Keep the existing Material-style list surface, filters, status chips, and mobile card fallback.
- Add regression checks in `scripts/validate-beneficiaries-material-list.mjs`.

No Dataverse schema, Power Pages Web API write path, or environment deployment is included in this slice.

## Prototype entity shape

Each beneficiary record now carries:

- profile and verification status;
- programme and project participation;
- finance snapshot;
- financed technology relationships;
- training summary;
- latest submission status;
- monitored outcome snapshot;
- future Dataverse mapping notes.

The future production direction is a central `mp_beneficiary`-style entity related to submissions, loans, trainings, financed technologies, and outcome/indicator records.

## User experience

The Beneficiaries route keeps the summary metrics and searchable list. Each desktop row and mobile card now has a clear `View details` action. The detail opens in a right-side dialog drawer with explicit demonstration-data wording so prototype values are not mistaken for official CRDB Bank or Green Climate Fund statistics.

## Verification

Run from `powerpages/webforms-spa`:

```bash
npm run test:material
npm run typecheck
npm run build:mshirika-runtime
```

Expected result: Material/list validation passes, TypeScript compiles, and the runtime bundle builds.
