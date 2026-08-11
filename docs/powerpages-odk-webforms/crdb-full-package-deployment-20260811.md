# CRDB Full Package Deployment — 2026-08-11

## Target

- Environment: `TACATDP-CRDB-Dev`
- Environment URL: `https://org5eb0379b.crm4.dynamics.com/`
- User profile: `dmuroba@CRDBBANK.CO.TZ`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`

## Method

Used the same deployment path proven on Mshirika:

1. Confirmed CRDB PAC profile and target site.
2. Downloaded a fresh Enhanced-model package from CRDB.
3. Staged the current SPA bundle into the fresh CRDB package.
4. Validated package hygiene against the CRDB environment URL.
5. Uploaded the full package.
6. Downloaded the live CRDB package and verified assets.

## Pre-upload checks

```bash
cd powerpages/webforms-spa
npm run test:powerpages-assets
npm run test:material
```

```bash
python3 scripts/validate-powerpages-package-hygiene.py \
  --environment-url https://org5eb0379b.crm4.dynamics.com/
```

Result:

- SPA asset check passed.
- Material/design-system checks passed.
- Package hygiene check passed.

## Deployment result

Full package upload succeeded:

```bash
pac pages upload \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool \
  --modelVersion Enhanced
```

Result:

- 2,761 records loaded across 48 entities.
- 2,697 requests executed in three batches.
- Upload succeeded in 81.48 seconds.

## Warnings

PAC reported non-blocking delete failures for stale managed
`powerpagecomponent` records. The upload continued and completed successfully.

The affected records include stale/managed components related to prior web
pages/assets such as the `assets` pages, `Cat-PC.png`, `portalbasictheme.css`,
`theme.css`, `bootstrap.min.css`, and `Logo-sm-64.png`.

These warnings mean CRDB retains some stale managed components that cannot be
deleted by this delegated PAC upload. They did not block the current SPA asset
deployment.

## Post-upload verification

Downloaded the live CRDB site and verified:

- Home root and localized Home fragments reference marker
  `beneficiary-schema-align-20260811-021`.
- Home references current JS/CSS assets:
  - `/assets/index-CZy98nSu.mjs`
  - `/assets/index-Z-GAkbH_.css`
- `node scripts/verify-powerpages-spa-assets.mjs` passed against the live
  downloaded `web-files` directory.
- `scripts/validate-powerpages-package-hygiene.py --environment-url
  https://org5eb0379b.crm4.dynamics.com/` passed against the live download.

Known non-blocking duplicate partial URL warnings remain for historical ODK
locale chunks:

- `strings_es-C8xkQaZj-KYNBMnTd.mjs`
- `strings_fr-C0vLmCzP-Bi34LuTN.mjs`
- `strings_id-BE0G3I_d-B0dO9nQF.mjs`

## Remaining risk

Package and asset integrity are verified. Browser visual review remains the
final runtime gate because PAC download verification does not execute the site
in a browser session.
