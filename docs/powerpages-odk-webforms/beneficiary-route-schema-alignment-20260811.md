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

## Mshirika deployment

Deployment completed on 2026-08-11 to:

- Environment: `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- PAC user: `john.mduda@mshirikacorp.onmicrosoft.com`
- Build marker: `beneficiary-schema-align-20260811-021`

Pre-upload checks:

```bash
npm run test:material
npm run build:mshirika-runtime
node scripts/validate-beneficiary-entity-schema.mjs
python3 scripts/stage-powerpages-spa-build.py
node scripts/verify-powerpages-spa-assets.mjs
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-THAC16le.mjs
```

Upload command:

```bash
pac pages upload \
  --environment "https://orga3cf4b37.crm4.dynamics.com/" \
  --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool \
  --modelVersion Enhanced \
  --forceUploadAll
```

PAC reported:

```text
Power Pages website upload succeeded in 268.45 secs.
```

Post-upload verification downloaded the site again and confirmed both Home fragments reference:

```html
<script type="module" crossorigin src="/assets/index-THAC16le.mjs?v=beneficiary-schema-align-20260811-021"></script>
<link rel="stylesheet" crossorigin href="/assets/index-D8wBU9s4.css?v=beneficiary-schema-align-20260811-021">
```

The post-upload package also contained the referenced main module, stylesheet, and `program-impact-farmer-U4dPWmM1.png`; `node --check` passed for `index-THAC16le.mjs`.
