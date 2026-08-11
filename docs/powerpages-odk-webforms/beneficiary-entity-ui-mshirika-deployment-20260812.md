# Beneficiary Entity UI Mshirika Deployment — 2026-08-12

Status: deployed to Mshirika for visual review. No CRDB deployment and no Dataverse schema write were performed in this slice.

## Scope

- Deploy the Beneficiaries detail/entity-model UI from commit `afcc803`.
- Update the Power Pages staging cache marker to `beneficiary-entity-ui-20260812-022`.
- Upload the validated package to the Mshirika Power Pages site.
- Download the site after upload and verify the Home page asset references and required files.

## Target

- Environment: `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- PAC user: `john.mduda@mshirikacorp.onmicrosoft.com`

## Pre-upload verification

```bash
npm run test:material
npm run build:mshirika-runtime
source scripts/use-powerplatform-env.sh mshirika
python3 scripts/stage-powerpages-spa-build.py
node scripts/verify-powerpages-spa-assets.mjs
python3 scripts/validate-powerpages-package-hygiene.py --repair-manifest
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-Bcy4xq3u.mjs
```

Results:

- Material route validators passed.
- Mshirika runtime build completed.
- Package hygiene verified.
- SPA assets verified: 32 assets, 0 duplicate partial URLs.
- Main module syntax check passed.
- Known upstream `@getodk/web-forms` direct-eval and large-chunk Vite warnings appeared; they are not introduced by this Beneficiaries UI slice.

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
Power Pages website upload succeeded in 260.77 secs.
```

## Post-upload verification

Downloaded the Mshirika site back to `/tmp` with:

```bash
pac pages download \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --webSiteId fccc0cc6-7f5e-4885-aeb8-2272e68130a3 \
  --path "$verify_dir" \
  --modelVersion Enhanced \
  --overwrite
```

Verified both Home fragments reference:

```html
<script type="module" crossorigin src="/assets/index-Bcy4xq3u.mjs?v=beneficiary-entity-ui-20260812-022"></script>
<link rel="stylesheet" crossorigin href="/assets/index-DK5fxcYG.css?v=beneficiary-entity-ui-20260812-022">
```

Verified the downloaded site contains:

- `web-files/index-Bcy4xq3u.mjs`
- `web-files/index-DK5fxcYG.css`
- `web-files/program-impact-farmer-U4dPWmM1.png`

`node --check` passed for the downloaded `index-Bcy4xq3u.mjs`.

## Review instructions

Open the Mshirika portal and review the Beneficiaries route:

1. Open a beneficiary detail drawer.
2. Confirm the drawer still uses the Material detail surface and remains readable.
3. Confirm the new sections are visible:
   - Identity governance
   - Group membership
   - Location history
4. Confirm the technical mapping lists:
   - `mp_BeneficiaryIdentityMatch`
   - `mp_BeneficiaryGroupMembership`
   - `mp_BeneficiaryLocationHistory`

If accepted, the next slice can either update CRDB or continue model-backed UX refinement.
