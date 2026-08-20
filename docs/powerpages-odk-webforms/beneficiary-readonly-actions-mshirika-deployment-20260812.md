# Beneficiary read-only actions Mshirika deployment — 2026-08-12

## Status

Deployed to Mshirika for prototype review.

This slice converts the Beneficiaries detail drawer footer actions from disabled placeholders into safe read-only prototype interactions.

## Scope delivered

- `Open full profile` scrolls and focuses the Profile section in the existing drawer.
- `View submissions` scrolls and focuses the Data lineage section in the existing drawer.
- `View loan record` scrolls and focuses the Finance section in the existing drawer.
- `Export detail` shows an in-page planned-export notice only.

## Non-goals preserved

- No Dataverse writes.
- No export file generation.
- No new route or external navigation.
- No Power Pages permissions or authentication changes.
- No CRDB deployment in this slice.

## Deployment target

- Target: Mshirika
- Environment: `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- Runtime marker: `beneficiary-readonly-actions-20260812-029`

## Verification

Pre-deployment checks passed:

```bash
node scripts/validate-beneficiary-entity-schema.mjs
npm run test:material
npm run typecheck
git diff --check
npm run build:mshirika-runtime
python3 scripts/stage-powerpages-spa-build.py
node scripts/verify-powerpages-spa-assets.mjs
python3 scripts/validate-powerpages-package-hygiene.py --repair-manifest
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-D40sBNhx.mjs
```

Power Pages upload succeeded:

```text
Power Pages website upload succeeded in 273.77 secs.
```

Post-upload download verification passed:

```bash
pac pages download --environment "$POWER_PLATFORM_ENVIRONMENT_URL" --webSiteId fccc0cc6-7f5e-4885-aeb8-2272e68130a3 --path "$verify_dir" --modelVersion Enhanced --overwrite
rg -n "beneficiary-readonly-actions-20260812-029|/assets/index-D40sBNhx.mjs|/assets/index-B9ukYgOa.css" "$verify_dir"
test -f "$verify_dir/tacatdp-monitoring-tool/web-files/index-D40sBNhx.mjs"
test -f "$verify_dir/tacatdp-monitoring-tool/web-files/index-B9ukYgOa.css"
test -f "$verify_dir/tacatdp-monitoring-tool/web-files/program-impact-farmer-U4dPWmM1.png"
node --check "$verify_dir/tacatdp-monitoring-tool/web-files/index-D40sBNhx.mjs"
```

Verified deployed Home references:

- `/assets/index-D40sBNhx.mjs?v=beneficiary-readonly-actions-20260812-029`
- `/assets/index-B9ukYgOa.css?v=beneficiary-readonly-actions-20260812-029`

## Review checklist

1. Open Beneficiaries and select a beneficiary detail row.
2. Confirm `Open full profile`, `View submissions`, and `View loan record` scroll/focus within the drawer and show a status notice.
3. Confirm `Export detail` shows the planned-export notice and does not download a file.
4. Confirm no footer action navigates outside the drawer or writes data.
5. Confirm Technical mapping remains collapsed and the business detail order is unchanged.
