# Beneficiary Drawer Polish Mshirika Deployment — 2026-08-12

Status: deployed to Mshirika for visual review. No CRDB deployment and no Dataverse schema write were performed.

## Scope

- Deploy Beneficiaries detail drawer polish from commit `0817c35`.
- Move the technical mapping into the compact `Technical mapping` disclosure.
- Use business-facing section labels:
  - `Record matching`
  - `Group/member links`
  - `Location history`
- Add scoped left accent rails to Beneficiary detail drawer section cards.
- Update the Power Pages cache marker to `beneficiary-drawer-polish-20260812-023`.

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
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-Cmw7aGMz.mjs
```

Results:

- Material route validators passed.
- Mshirika runtime build completed.
- Package hygiene verified.
- SPA assets verified: 32 assets, 0 duplicate partial URLs.
- Main module syntax check passed.
- Known upstream `@getodk/web-forms` direct-eval and large-chunk Vite warnings appeared; they are not introduced by this Beneficiaries drawer polish.

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
Power Pages website upload succeeded in 254.66 secs.
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
<script type="module" crossorigin src="/assets/index-Cmw7aGMz.mjs?v=beneficiary-drawer-polish-20260812-023"></script>
<link rel="stylesheet" crossorigin href="/assets/index-EMqul_oD.css?v=beneficiary-drawer-polish-20260812-023">
```

Verified the downloaded site contains:

- `web-files/index-Cmw7aGMz.mjs`
- `web-files/index-EMqul_oD.css`
- `web-files/program-impact-farmer-U4dPWmM1.png`

`node --check` passed for the downloaded `index-Cmw7aGMz.mjs`.

## Review instructions

Open the Mshirika portal and review the Beneficiaries detail drawer:

1. Confirm section labels are business-facing:
   - Record matching
   - Group/member links
   - Location history
2. Confirm drawer section cards have subtle left accent rails.
3. Confirm `Technical mapping` is collapsed by default and expands on demand.
4. Confirm the drawer remains readable and not visually crowded.

If accepted, the same package can be promoted to CRDB when CRDB review access is available.
