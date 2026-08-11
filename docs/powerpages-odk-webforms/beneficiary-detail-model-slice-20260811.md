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

## Mshirika deployment

Deployment completed on 2026-08-11 to:

- Environment: `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- PAC user: `john.mduda@mshirikacorp.onmicrosoft.com`
- Build marker: `beneficiary-detail-20260811-020`

Pre-upload checks:

```bash
npm run test:material
npm run build:mshirika-runtime
python3 scripts/stage-powerpages-spa-build.py
node scripts/verify-powerpages-spa-assets.mjs
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-qlHls_DF.mjs
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
Power Pages website upload succeeded in 263.72 secs.
```

Post-upload verification downloaded the site again and confirmed both Home fragments reference:

```html
<script type="module" crossorigin src="/assets/index-qlHls_DF.mjs?v=beneficiary-detail-20260811-020"></script>
<link rel="stylesheet" crossorigin href="/assets/index-br0G_Ug1.css?v=beneficiary-detail-20260811-020">
```

The post-upload package also contained the referenced main module, stylesheet, and `program-impact-farmer-U4dPWmM1.png`; `node --check` passed for `index-qlHls_DF.mjs`.
