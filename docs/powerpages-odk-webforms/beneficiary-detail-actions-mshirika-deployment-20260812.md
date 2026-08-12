# Beneficiary Detail Actions Mshirika Deployment — 2026-08-12

Status: deployed to Mshirika for visual review. No CRDB deployment, Dataverse schema write, permission change, or Power Pages write-path activation was performed.

## Scope

- Add a compact Beneficiaries detail drawer action footer after `Technical mapping`.
- Add four non-mutating prototype actions:
  - `Open full profile`
  - `View submissions`
  - `View loan record`
  - `Export detail`
- Keep all four actions disabled in this prototype build.
- Mark each action visibly as `Planned`.
- Preserve the existing business-first drawer section order, one-container-per-section structure, and no left shade.
- Update the validator so the footer, planned state, disabled action count, and footer placement are enforced.
- Update the Power Pages cache marker to `beneficiary-detail-actions-20260812-028`.

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
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-FTgHVuKB.mjs
```

Known upstream `@getodk/web-forms` direct-eval and large-chunk Vite warnings appeared during build; they are not introduced by this drawer action-footer slice.

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
Power Pages website upload succeeded in 279.63 secs.
```

## Post-upload verification

The first post-upload download attempt hit a transient network error while downloading Power Pages file content:

```text
Network is unreachable (orga3cf4b37.crm4.dynamics.com:443)
```

The retry succeeded. Downloaded the Mshirika site back to `/tmp` and verified both Home fragments reference:

```html
<script type="module" crossorigin src="/assets/index-FTgHVuKB.mjs?v=beneficiary-detail-actions-20260812-028"></script>
<link rel="stylesheet" crossorigin href="/assets/index-CtT9ZxmN.css?v=beneficiary-detail-actions-20260812-028">
```

Verified the downloaded site contains:

- `web-files/index-FTgHVuKB.mjs`
- `web-files/index-CtT9ZxmN.css`
- `web-files/program-impact-farmer-U4dPWmM1.png`

`node --check` passed for the downloaded `index-FTgHVuKB.mjs`.

## Review instructions

Open the Mshirika portal and review the Beneficiaries detail drawer:

1. Confirm the action footer appears after `Technical mapping`.
2. Confirm the four planned actions are visible and disabled.
3. Confirm each disabled action is marked `Planned`.
4. Confirm no action performs navigation or Dataverse writes in this prototype build.
