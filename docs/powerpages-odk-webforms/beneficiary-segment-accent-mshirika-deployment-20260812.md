# Beneficiary Segment Accent Mshirika Deployment — 2026-08-12

Status: deployed to Mshirika for visual review. No CRDB deployment and no Dataverse schema write were performed.

## Scope

- Correct the Beneficiaries detail drawer accent hierarchy from individual section-card rails to larger grouped segment rails.
- Keep `Technical mapping` behind the compact disclosure.
- Preserve business-facing section labels:
  - `Record matching`
  - `Group/member links`
  - `Location history`
- Update the regression validator so `beneficiary-detail-section--accented` fails if reintroduced.
- Update the Power Pages cache marker to `beneficiary-segment-shade-20260812-024`.

This supersedes the visual treatment recorded in `beneficiary-drawer-polish-mshirika-deployment-20260812.md`: the shade belongs on grouped drawer segments, not on every individual detail item.

## Target

- Environment: `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- PAC user: `john.mduda@mshirikacorp.onmicrosoft.com`

## Pre-upload verification

```bash
node scripts/validate-beneficiary-entity-schema.mjs
npm run test:material
npm run typecheck
npm run build:mshirika-runtime
git diff --check
source scripts/use-powerplatform-env.sh mshirika
python3 scripts/stage-powerpages-spa-build.py
node scripts/verify-powerpages-spa-assets.mjs
python3 scripts/validate-powerpages-package-hygiene.py --repair-manifest
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-DOh3hI1a.mjs
```

Results:

- Beneficiary entity schema validation passed.
- Material route validators passed, including the updated beneficiary detail refinement validator.
- TypeScript check passed.
- Mshirika runtime build completed.
- Package hygiene verified.
- SPA assets verified: 32 assets, 0 duplicate partial URLs.
- Main module syntax check passed.
- Known upstream `@getodk/web-forms` direct-eval and large-chunk Vite warnings appeared; they are not introduced by this drawer accent correction.

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
Power Pages website upload succeeded in 266.36 secs.
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
<script type="module" crossorigin src="/assets/index-DOh3hI1a.mjs?v=beneficiary-segment-shade-20260812-024"></script>
<link rel="stylesheet" crossorigin href="/assets/index-CPwHMl6m.css?v=beneficiary-segment-shade-20260812-024">
```

Verified the downloaded site contains:

- `web-files/index-DOh3hI1a.mjs`
- `web-files/index-CPwHMl6m.css`
- `web-files/program-impact-farmer-U4dPWmM1.png`

`node --check` passed for the downloaded `index-DOh3hI1a.mjs`.

## Review instructions

Open the Mshirika portal and review the Beneficiaries detail drawer:

1. Confirm the left shade appears on the larger drawer segment groups only.
2. Confirm individual detail cards inside those groups are plain Material-style section cards.
3. Confirm `Technical mapping` remains collapsed by default and expands on demand.
4. Confirm the drawer is less visually noisy than the previous per-card accent treatment.

If accepted, this visual treatment should be treated as the durable Beneficiaries drawer pattern before any CRDB promotion.
