# CRDB deployment asset verification rule

Date: 2026-08-20

## Purpose

CRDB Power Pages deployments must be accepted based on browser-facing asset safety, not on whether the environment has historical duplicate Power Pages web-file records.

The CRDB development site currently retains managed duplicate `powerpagecomponent` / web-file records that cannot be cleaned safely from the delivery workstation. Those duplicates are a server hygiene issue. They are not by themselves proof that the current SPA bundle is broken.

## Current CRDB target

| Item | Value |
|---|---|
| Environment | `TACATDP-CRDB-Dev` |
| Environment URL | `https://org5eb0379b.crm4.dynamics.com/` |
| PAC profile | `tacatdp-crdb` |
| Website ID | `fccc0cc6-7f5e-4885-aeb8-2272e68130a3` |

## Required verification after every CRDB deployment

1. Confirm the PAC profile points to CRDB.
2. Download the live enhanced-model Power Pages site into a temporary folder.
3. Verify the current SPA assets against the downloaded web-file records.
4. Record duplicate partial URLs separately from missing or mismatched current assets.

Use:

```bash
source scripts/use-powerplatform-env.sh crdb
pac auth select --name "$PAC_AUTH_NAME"

VERIFY_DIR="$(mktemp -d /tmp/tacatdp-crdb-postdeploy-XXXXXX)"

pac pages download \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --webSiteId fccc0cc6-7f5e-4885-aeb8-2272e68130a3 \
  --path "$VERIFY_DIR" \
  --modelVersion Enhanced \
  --overwrite

node scripts/verify-powerpages-spa-assets.mjs \
  --web-files "$VERIFY_DIR/tacatdp-monitoring-tool/web-files" \
  --json

node scripts/inventory-powerpages-webfile-duplicates.mjs \
  --web-files "$VERIFY_DIR/tacatdp-monitoring-tool/web-files" \
  --json
```

## Pass and fail rules

| Condition | Result |
|---|---|
| Any current SPA asset is missing from the downloaded site | Fail deployment acceptance. |
| Any current SPA asset binary hash differs from the local build | Fail deployment acceptance. |
| Home references an asset that does not exist in the downloaded site | Fail deployment acceptance. |
| Duplicate partial URLs exist, but at least one current record has the expected binary and Home references current assets | Pass runtime safety, record server hygiene warning. |
| Duplicate partial URLs exist and no current record has the expected binary | Fail deployment acceptance. |

Do not run `--fail-on-duplicates` as the routine CRDB post-deployment acceptance gate while managed duplicates remain. Use it only after CRDB administrators complete managed-component cleanup.

## Cleanup boundary

Do not delete CRDB duplicate web-file records ad hoc.

Deletion requires a separate CRDB administrator or solution-owner cleanup action because the live classification shows mixed managed and unmanaged duplicate records. The stale current-build records are managed; deleting only unmanaged records would not remove the duplicate condition and could remove valid current binary copies.

Authoritative cleanup evidence:

- `docs/powerpages-odk-webforms/crdb-duplicate-webfile-ownership-classification-20260811.md`
- `docs/powerpages-odk-webforms/crdb-duplicate-webfile-inventory-20260811.md`

## Implementation rule for future agents

For CRDB deployment work:

- Treat asset verification failure as a release blocker.
- Treat known managed duplicate residue as an admin cleanup task unless it causes missing or mismatched current assets.
- Never infer local package drift from PAC-exported duplicate filenames alone; compare `adx_partialurl` and content hash.
- Keep the CRDB site ID explicit. Do not deploy by site name because duplicate site names have previously caused wrong-target updates.
