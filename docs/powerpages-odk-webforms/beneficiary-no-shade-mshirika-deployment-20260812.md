# Beneficiary No-Shade Mshirika Deployment — 2026-08-12

Status: deployed to Mshirika for visual review. No CRDB deployment and no Dataverse schema write were performed.

## Scope

- Remove the Beneficiaries detail drawer left shade entirely.
- Keep the internal grouped containers:
  - `Profile and participation`
  - `Beneficiary model`
  - `Programme delivery`
  - `Evidence and location`
- Keep `Technical mapping` behind the compact disclosure.
- Update the validator so drawer section and segment accent classes fail if reintroduced.
- Update the Power Pages cache marker to `beneficiary-no-shade-20260812-025`.

This supersedes the segment-shade treatment. Drawer group containers remain, but the shade is not used on the drawer, groups, or individual detail cards.

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
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-B0vKb7_F.mjs
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
Power Pages website upload succeeded in 271.28 secs.
```

## Post-upload verification

Downloaded the Mshirika site back to `/tmp` and verified both Home fragments reference:

```html
<script type="module" crossorigin src="/assets/index-B0vKb7_F.mjs?v=beneficiary-no-shade-20260812-025"></script>
<link rel="stylesheet" crossorigin href="/assets/index-BTN1kkeM.css?v=beneficiary-no-shade-20260812-025">
```

Verified the downloaded site contains:

- `web-files/index-B0vKb7_F.mjs`
- `web-files/index-BTN1kkeM.css`
- `web-files/program-impact-farmer-U4dPWmM1.png`

`node --check` passed for the downloaded `index-B0vKb7_F.mjs`.

## Review instructions

Open the Mshirika portal and review the Beneficiaries detail drawer:

1. Confirm no left shade appears on individual cards or grouped containers.
2. Confirm internal grouping is still clear through spacing, borders, and surface background.
3. Confirm `Technical mapping` remains collapsed by default.
