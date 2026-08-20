# Beneficiary Context Reset CRDB Deployment — August 11, 2026

## Target

- Environment: CRDB `TACATDP-CRDB-Dev`
- Environment URL: `https://org5eb0379b.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- Authenticated PAC user: `dmuroba@CRDBBANK.CO.TZ`
- Source commit: `9771e27 Clear stale beneficiary dashboard context`

## Deployed fix

Direct side-navigation to Beneficiaries clears stale dashboard drill-through query state. Dashboard drill-through still preserves `source=dashboard` and active filter query parameters.

Expected behavior after deployment:

- Dashboard drill-through to Beneficiaries shows `Opened from dashboard`.
- Side-nav Beneficiaries opens `#/beneficiaries` and does not show `Opened from dashboard`.
- `Back to Dashboard` remains available only in true dashboard-origin contexts.

## Deployment method

Used the live-base-safe Power Pages upload path to avoid the previous blank-page/missing-asset failure mode.

Steps:

1. Downloaded the current live CRDB package.
2. Confirmed Home referenced existing hosted entry filenames:
   - `index-CZs74iiI.mjs`
   - `index-AZvWgjZv.css`
3. Confirmed the intended entry imports were already present in CRDB:
   - `vendor-datepicker-JwSW3Esp.mjs`
   - `vendor-icons-Bf-R-O4S.mjs`
   - `preload-helper-Czpn1I53.mjs`
4. Replaced existing hosted entry file content with the current staged build:
   - `index-CDTd1nEP.mjs`
   - `index-CVFcCDlW.css`
5. Updated both Home fragments with cache marker:
   - `crdb-beneficiary-context-reset-20260811-001`
6. Uploaded the live-base temp package:

```bash
source scripts/use-powerplatform-env.sh crdb
pac pages upload \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --path /tmp/tacatdp-crdb-context-reset-upload-JYLZRn/tacatdp-monitoring-tool \
  --modelVersion Enhanced
```

PAC processed six records and completed:

```text
Power Pages website upload succeeded in 23.99 secs.
```

PAC reported two non-blocking stale `powerpagecomponent` update warnings where records no longer existed.

## Verification

Post-upload PAC download confirmed both Home fragments reference:

```html
<script type="module" crossorigin src="/assets/index-CZs74iiI.mjs?v=crdb-beneficiary-context-reset-20260811-001"></script>
<link rel="stylesheet" crossorigin href="/assets/index-AZvWgjZv.css?v=crdb-beneficiary-context-reset-20260811-001">
```

Hosted file hashes match the intended build:

| Intended staged file | Hosted reused file | SHA-256 |
| --- | --- | --- |
| `index-CDTd1nEP.mjs` | `index-CZs74iiI.mjs` | `40f8df71204f1f9994500f546b96cb94601a9af915e8a8a5c2b8ec65b247dbf1` |
| `index-CVFcCDlW.css` | `index-AZvWgjZv.css` | `1e04b36331ab7e468b7741ff15dd5f0a0a109f1646a3b57f9de4d5d57f408cca` |

The hosted entry imports these chunks and all are present in the post-upload CRDB package:

- `vendor-datepicker-JwSW3Esp.mjs`
- `vendor-icons-Bf-R-O4S.mjs`
- `preload-helper-Czpn1I53.mjs`
