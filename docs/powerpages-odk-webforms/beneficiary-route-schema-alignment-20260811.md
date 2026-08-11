# Beneficiary Route Schema Alignment — 2026-08-11

Status: prototype UI refinement. No deployment or Dataverse environment write is included.

## Purpose

Align the Beneficiaries detail drawer with the reviewed beneficiary Dataverse schema plan.

## Scope

- Replace stale future-mapping wording with reviewed Dataverse mapping language.
- Show the actual reviewed Dataverse targets:
  - `mp_TrackedEntity`
  - `mp_BeneficiaryProfile`
  - `mp_BeneficiaryProgrammeParticipation`
  - `mp_BeneficiaryFinanceLink`
  - `mp_BeneficiaryTechnologyAdoption`
  - `mp_BeneficiaryTrainingParticipation`
  - `mp_BeneficiaryOutcomeSnapshot`
  - `mp_BeneficiarySubmissionLink`
- Add a compact Data lineage section for latest submission, reporting period, completeness, and verification state.
- Extend `scripts/validate-beneficiaries-material-list.mjs` so stale “Future Dataverse mapping” wording cannot return.

## References

- `docs/powerpages-odk-webforms/beneficiary-dataverse-schema-plan-20260811.md`
- `schemas/dataverse/beneficiary-entity-extension-schema.json`
- `powerpages/webforms-spa/src/views/BeneficiariesView.vue`

## Verification

Run from `powerpages/webforms-spa`:

```bash
npm run test:material
npm run typecheck
```

Run from the repository root:

```bash
node scripts/validate-beneficiary-entity-schema.mjs
git diff --check
```
