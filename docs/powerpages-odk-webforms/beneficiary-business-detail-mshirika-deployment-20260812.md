# Beneficiary Business Detail Mshirika Deployment — 2026-08-12

Status: deployed to Mshirika for visual review. No CRDB deployment and no Dataverse schema write were performed.

## Scope

- Reorder the Beneficiaries detail drawer so operational business sections appear before governance/technical review sections:
  - Profile
  - Finance
  - Technology
  - Training
  - Outcomes
  - Data lineage
  - Record matching
  - Group/member links
  - Location history
  - Technical mapping
- Move Dataverse table names, relationship notes, and model-target details behind `Technical mapping`.
- Keep one visible Material section container per detail block.
- Keep no left shade accent rails.
- Update the validator so the section order and technical-disclosure boundary are enforced.
- Update the Power Pages cache marker to `beneficiary-business-detail-20260812-027`.

## Target

- Environment: `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- PAC user: `john.mduda@mshirikacorp.onmicrosoft.com`

## Verification

Passed before upload:

```bash
node scripts/validate-beneficiary-entity-schema.mjs
npm run test:material
npm run typecheck
npm run build:mshirika-runtime
git diff --check
python3 scripts/stage-powerpages-spa-build.py
node scripts/verify-powerpages-spa-assets.mjs
python3 scripts/validate-powerpages-package-hygiene.py --repair-manifest
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-fW7GL7MP.mjs
```

Known upstream `@getodk/web-forms` direct-eval and large-chunk Vite warnings appeared during build; they are not introduced by this drawer hierarchy correction.

## Upload

```bash
pac pages upload \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool \
  --modelVersion Enhanced \
  --forceUploadAll
```

PAC reported:

```text
Power Pages website upload succeeded in 253.87 secs.
```

## Post-upload verification

Downloaded the Mshirika site back to `/tmp` and verified both Home fragments reference:

```html
<script type="module" crossorigin src="/assets/index-fW7GL7MP.mjs?v=beneficiary-business-detail-20260812-027"></script>
<link rel="stylesheet" crossorigin href="/assets/index-CR-0etaJ.css?v=beneficiary-business-detail-20260812-027">
```

Verified the downloaded site contains:

- `web-files/index-fW7GL7MP.mjs`
- `web-files/index-CR-0etaJ.css`
- `web-files/program-impact-farmer-U4dPWmM1.png`

`node --check` passed for the downloaded `index-fW7GL7MP.mjs`.

## Review instructions

Open the Mshirika portal and review the Beneficiaries detail drawer:

1. Confirm the visible drawer body reads as business/operational content first.
2. Confirm Dataverse `mp_` table names appear only after opening `Technical mapping`.
3. Confirm one visible container per section and no left shade.
4. Confirm `Technical mapping` remains collapsed by default.
