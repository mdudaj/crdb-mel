# Beneficiary Flat Detail Mshirika Deployment — 2026-08-12

Status: deployed to Mshirika for visual review. No CRDB deployment and no Dataverse schema write were performed.

## Scope

- Flatten the Beneficiaries detail drawer to one visible Material section container per detail block.
- Remove the extra `beneficiary-detail-segment` wrapper containers.
- Keep no left shade accent rails.
- Keep `Technical mapping` behind the compact disclosure.
- Update the validator so segment wrappers or section accent classes fail if reintroduced.
- Update the Power Pages cache marker to `beneficiary-flat-detail-20260812-026`.

This supersedes both prior drawer-shade treatments. The accepted rule for this slice is: no extra segment wrapper and no left shade; use the existing `material-detail-section beneficiary-detail-section` card as the single container.

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
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-CVRA8xSY.mjs
```

Known upstream `@getodk/web-forms` direct-eval and large-chunk Vite warnings appeared during build; they are not introduced by this drawer correction.

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
Power Pages website upload succeeded in 258.83 secs.
```

## Post-upload verification

Downloaded the Mshirika site back to `/tmp` and verified both Home fragments reference:

```html
<script type="module" crossorigin src="/assets/index-CVRA8xSY.mjs?v=beneficiary-flat-detail-20260812-026"></script>
<link rel="stylesheet" crossorigin href="/assets/index-CjVo0G1M.css?v=beneficiary-flat-detail-20260812-026">
```

Verified the downloaded site contains:

- `web-files/index-CVRA8xSY.mjs`
- `web-files/index-CjVo0G1M.css`
- `web-files/program-impact-farmer-U4dPWmM1.png`

`node --check` passed for the downloaded `index-CVRA8xSY.mjs`.

## Review instructions

Open the Mshirika portal and review the Beneficiaries detail drawer:

1. Confirm each detail block has only one visible container.
2. Confirm there are no extra outer segment cards around groups of details.
3. Confirm no left shade appears.
4. Confirm `Technical mapping` remains collapsed by default.
