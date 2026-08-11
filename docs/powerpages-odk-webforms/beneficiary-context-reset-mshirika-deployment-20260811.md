# Beneficiary Context Reset Mshirika Deployment — August 11, 2026

## Target

- Environment: Mshirika `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- Authenticated PAC user: `john.mduda@mshirikacorp.onmicrosoft.com`
- Source commit: `9771e27 Clear stale beneficiary dashboard context`

## Deployed fix

Direct side-navigation to Beneficiaries now clears stale dashboard drill-through query state. Dashboard drill-through still preserves `source=dashboard` and active filter query parameters.

Expected behavior after deployment:

- Dashboard drill-through to Beneficiaries shows `Opened from dashboard`.
- Side-nav Beneficiaries opens `#/beneficiaries` and does not show `Opened from dashboard`.
- `Back to Dashboard` remains available only in true dashboard-origin contexts.

## Deployment method

Used the live-base-safe Power Pages upload path because repository-source uploads had previously stalled at `49.6% / Events 70 of 141`.

Steps:

1. Downloaded the current live Mshirika package.
2. Reused existing hosted entry filenames:
   - `index-CZs74iiI.mjs`
   - `index-AZvWgjZv.css`
3. Replaced their file content with the current staged build:
   - `index-CDTd1nEP.mjs`
   - `index-CVFcCDlW.css`
4. Updated both Home fragments with cache marker:
   - `beneficiary-context-reset-20260811-001`
5. Uploaded the live-base temp package:

```bash
source scripts/use-powerplatform-env.sh mshirika
pac pages upload \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --path /tmp/tacatdp-mshirika-context-reset-upload-ZE0xib/tacatdp-monitoring-tool \
  --modelVersion Enhanced
```

PAC processed four records and completed:

```text
Power Pages website upload succeeded in 14.76 secs.
```

PAC reported one non-blocking stale `powerpagecomponent` update warning where the record no longer existed.

## Verification

Post-upload PAC download confirmed both Home fragments reference:

```html
<script type="module" crossorigin src="/assets/index-CZs74iiI.mjs?v=beneficiary-context-reset-20260811-001"></script>
<link rel="stylesheet" crossorigin href="/assets/index-AZvWgjZv.css?v=beneficiary-context-reset-20260811-001">
```

Hosted file hashes match the intended build:

| Intended staged file | Hosted reused file | SHA-256 |
| --- | --- | --- |
| `index-CDTd1nEP.mjs` | `index-CZs74iiI.mjs` | `40f8df71204f1f9994500f546b96cb94601a9af915e8a8a5c2b8ec65b247dbf1` |
| `index-CVFcCDlW.css` | `index-AZvWgjZv.css` | `1e04b36331ab7e468b7741ff15dd5f0a0a109f1646a3b57f9de4d5d57f408cca` |
