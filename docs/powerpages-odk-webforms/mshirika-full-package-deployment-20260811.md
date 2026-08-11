# Mshirika Full Package Deployment — 2026-08-11

## Target

- Environment: `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- User profile: `john.mduda@mshirikacorp.onmicrosoft.com`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`

## Pre-upload issue fixed

The earlier full package failed because the upload package mixed stale metadata:

- deleted-present `adx_webfile` records in `.portalconfig/manifest.yml`;
- an empty `adx_webfile:` manifest section after repair;
- a CRDB environment manifest inside the Mshirika upload package.

The package was refreshed from Mshirika, staged with the current SPA assets, and
validated before upload.

## Commands verified

```bash
cd powerpages/webforms-spa
npm run test:powerpages-assets
```

```bash
python3 scripts/validate-powerpages-package-hygiene.py \
  --environment-url https://orga3cf4b37.crm4.dynamics.com/
```

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
- Upload succeeded in 53.71 seconds.

## Post-upload verification

Downloaded the live Mshirika site and verified:

- Home root and localized Home fragments reference marker
  `beneficiary-schema-align-20260811-021`.
- Home references current JS/CSS assets, including:
  - `/assets/index-CZy98nSu.mjs`
  - `/assets/index-Z-GAkbH_.css`
- `node scripts/verify-powerpages-spa-assets.mjs` passed against the live
  downloaded `web-files` directory.
- `scripts/validate-powerpages-package-hygiene.py --environment-url
  https://orga3cf4b37.crm4.dynamics.com/` passed against the live download.

## Remaining risk

This confirms package integrity and upload success. Browser visual review is
still a manual user gate because PAC download verification does not execute the
Power Pages runtime in a browser session.
