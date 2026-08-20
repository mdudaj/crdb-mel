# Beneficiary Detail Mshirika Deployment — August 11, 2026

## Target

- Environment: Mshirika `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- Authenticated PAC user: `john.mduda@mshirikacorp.onmicrosoft.com`
- Source commit: `326c53a Refine beneficiary detail drill-through`

## Intended frontend build

- Built and staged package entry:
  - `index-BCA4e2ST.mjs`
  - `index-CVFcCDlW.css`
- Cache marker from normal staging:
  - `beneficiary-schema-align-20260811-021`

## Normal upload result

The normal source-package upload was attempted with:

```bash
source scripts/use-powerplatform-env.sh mshirika
pac pages upload \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool \
  --modelVersion Enhanced \
  --forceUploadAll
```

It repeatedly stopped at:

```text
Uploading - [##########----------] 49.6%  ETA: ~01:00 (Events: 70/141) [Threads: 1]
```

The visible `pac`/`dotnet` process then disappeared while the PTY session stayed open. A post-attempt download showed hosted Home still referenced the previous bundle:

- `index-CZs74iiI.mjs`
- `index-AZvWgjZv.css`

The same stall occurred with non-forced upload and with a repository-source temp package that removed the newly generated entry files. This indicates the blocker is probably stale package manifest/history or PAC handling of a fixed batch, not the new beneficiary detail bundle itself.

## Successful workaround

A temporary deployment package was created from the freshly downloaded live Mshirika package, not from the repository source package. The workaround:

1. Reused existing hosted entry filenames:
   - `index-CZs74iiI.mjs`
   - `index-AZvWgjZv.css`
2. Replaced their file content with the newly built content from:
   - `index-BCA4e2ST.mjs`
   - `index-CVFcCDlW.css`
3. Updated Home copy references to use cache marker:
   - `beneficiary-detail-refinement-20260811-001`
4. Uploaded the live-base temp package:

```bash
source scripts/use-powerplatform-env.sh mshirika
pac pages upload \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --path /tmp/tacatdp-mshirika-livebase-Y34bsB/tacatdp-monitoring-tool \
  --modelVersion Enhanced
```

PAC processed six records and completed:

```text
Power Pages website upload succeeded in 12.19 secs.
```

PAC also reported two non-blocking stale `powerpagecomponent` update warnings where records no longer existed.

## Verification

A post-upload download from Mshirika confirmed hosted Home references:

```html
<script type="module" crossorigin src="/assets/index-CZs74iiI.mjs?v=beneficiary-detail-refinement-20260811-001"></script>
<link rel="stylesheet" crossorigin href="/assets/index-AZvWgjZv.css?v=beneficiary-detail-refinement-20260811-001">
```

Hosted file hashes match the intended new build content:

| Intended staged file | Hosted reused file | SHA-256 |
| --- | --- | --- |
| `index-BCA4e2ST.mjs` | `index-CZs74iiI.mjs` | `ec14d2c3e34dd711f20aa294e4e363b664a63e52aeef635c455f9815942cb2cc` |
| `index-CVFcCDlW.css` | `index-AZvWgjZv.css` | `1e04b36331ab7e468b7741ff15dd5f0a0a109f1646a3b57f9de4d5d57f408cca` |

## Follow-up

Before the next deployment, prefer a live-base upload package or repair the repository source package manifest/historical web-file state. Do not keep retrying the full repository-source PAC upload if it stops at event 70/141 again.
