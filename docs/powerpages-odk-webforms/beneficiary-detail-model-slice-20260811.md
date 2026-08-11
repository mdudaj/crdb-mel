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
- identity governance state for future match/deduplication review;
- group membership context for individual, group, AMCOS, and SACCOS beneficiaries;
- location history context so current dashboard geography does not overwrite audit evidence;
- monitored outcome snapshot;
- future Dataverse mapping notes.

The future production direction is a central `mp_TrackedEntity` beneficiary identity with additive beneficiary extension tables related to submissions, loans, trainings, financed technologies, outcome/indicator records, identity matching, group membership, and location history.

## User experience

The Beneficiaries route keeps the summary metrics and searchable list. Each desktop row and mobile card now has a clear `View details` action. The detail opens in a right-side dialog drawer with explicit demonstration-data wording so prototype values are not mistaken for official CRDB Bank or Green Climate Fund statistics.

The detail drawer includes compact governance sections for:

- `Record matching`: candidate match state, matching signals, and reviewer decision. This previews `mp_BeneficiaryIdentityMatch` without enabling automatic fuzzy-match merges.
- `Group/member links`: beneficiary type, member linkage, and membership state. This previews `mp_BeneficiaryGroupMembership` while keeping group beneficiaries valid as entities in their own right.
- `Location history`: current location, source, effective date, and history state. This previews `mp_BeneficiaryLocationHistory` so location corrections remain auditable.

After Mshirika review, the technical Dataverse table mapping was moved behind a compact `Technical mapping` disclosure so business users see the operational sections first. The drawer uses one visible Material section container per detail block and does not add extra segment wrappers or left shade accent rails. Business-facing sections are ordered as profile, finance, technology, training, outcomes, data lineage, record matching, group/member links, and location history. Dataverse table names, relationship notes, and model-target details stay inside `Technical mapping`; visible business sections avoid implementation table names. The global `SurfaceCard` metric-card accent rule remains unchanged and stays limited to metric/summary cards.

## Verification

Run from `powerpages/webforms-spa`:

```bash
npm run test:material
npm run typecheck
npm run build:mshirika-runtime
node ../../scripts/validate-beneficiary-entity-schema.mjs
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
