# CRDB duplicate webfile inventory

Date: 2026-08-11

## Scope

This is a read-only diagnosis of duplicate Power Pages web-file records observed after the CRDB deployment of the dashboard-to-beneficiary drill-through build.

No Dataverse records were deleted. No Power Pages upload was run for this diagnosis slice.

## Evidence inspected

- Fresh CRDB PAC download:
  - `powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files`
- Committed canonical package:
  - `powerpages/tacatdp-monitoring-tool/.powerpages-site/web-files`
- Current Vite build assets:
  - `powerpages/webforms-spa/dist/assets`
- CRDB upload output from the previous deployment:
  - PAC upload succeeded.
  - PAC reported non-blocking delete failures for managed `powerpagecomponent` records.
  - The server rejected deletion during managed property evaluation: `Managed Property Name: ismanaged`.

## Commands

```bash
node scripts/inventory-powerpages-webfile-duplicates.mjs
node scripts/inventory-powerpages-webfile-duplicates.mjs --only strings_es-C8xkQaZj-KYNBMnTd.mjs
node scripts/inventory-powerpages-webfile-duplicates.mjs --only strings_fr-C0vLmCzP-Bi34LuTN.mjs
node scripts/inventory-powerpages-webfile-duplicates.mjs --only strings_id-BE0G3I_d-B0dO9nQF.mjs
node scripts/verify-powerpages-spa-assets.mjs
```

## Summary

The CRDB downloaded server package contains duplicate browser-facing `adx_partialurl` records. The committed canonical package does not contain these duplicates.

| Check | Result |
| --- | ---: |
| Downloaded CRDB web-file metadata records | 334 |
| Canonical committed web-file metadata records | 196 |
| Duplicate partial URLs in downloaded CRDB package | 17 |
| Duplicate partial URLs that overlap the current Vite dist assets | 3 |
| Missing current Vite assets | 0 |
| Current Vite assets without a matching CRDB binary | 0 |

The deployed page remains functional because the active home page references the current entry assets:

- `index-CZs74iiI.mjs`
- `index-AZvWgjZv.css`

## Current-build duplicate records

These three duplicate groups are relevant to the current build because the partial URLs exist in `dist/assets`.

| Partial URL | CRDB downloaded records | Canonical package records | Records matching current dist | Assessment |
| --- | ---: | ---: | ---: | --- |
| `strings_es-C8xkQaZj-KYNBMnTd.mjs` | 8 | 1 | 7 | Server-retained duplicates; one stale binary remains. |
| `strings_fr-C0vLmCzP-Bi34LuTN.mjs` | 8 | 1 | 7 | Server-retained duplicates; one stale binary remains. |
| `strings_id-BE0G3I_d-B0dO9nQF.mjs` | 8 | 1 | 7 | Server-retained duplicates; one stale binary remains. |

The verifier passes because at least one CRDB web-file record for each current browser partial URL has the expected current binary hash.

## Historical duplicate groups

The full CRDB downloaded package currently has 17 duplicate partial URLs. Fourteen are historical chunks that do not exist in the current Vite build.

- `ActionsInfoDialog-B8AZQOuY-B_ARqT-G.mjs`
- `ActionsInfoDialog-B8AZQOuY-DbERyGTk.mjs`
- `CanvasBlock-DWoXGSW9-CvwGR8gR.mjs`
- `CanvasBlock-DWoXGSW9-DjPauhpe.mjs`
- `index-BvFx8uy6.css`
- `index-Cg9qvMI9-B1UfK9zv.mjs`
- `index-ChLB0qW2.css`
- `index-Dx9yUGB4.mjs`
- `MapBlock-BTX9u64V-CiYAL6Wu.mjs`
- `MapBlock-BTX9u64V-CNidbrSB.mjs`
- `runtime-core.esm-bundler-5TRCMxAO.mjs`
- `runtime-core.esm-bundler-sjoBfEhY.mjs`
- `vue-konva-D0sZ6RWk-B6d3nPSD.mjs`
- `vue-konva-D0sZ6RWk-De_G96cE.mjs`

These historical duplicates are not referenced by the current home page and are not needed by the current dashboard entry bundle.

## Interpretation

The duplicate records were not reintroduced by the local package.

The likely cause is CRDB retaining stale server-side Power Pages records that PAC attempted but failed to delete. The failure is consistent with PAC's CRDB upload warnings: server-side managed `powerpagecomponent` records could not be removed because Dataverse evaluated them as managed components.

This means cleanup must not be done by deleting local files from the ignored download mirror. A safe cleanup needs a Dataverse-aware inventory of component ownership and managed state before any delete is proposed.

## Cleanup recommendation

Do not delete these records ad hoc.

Recommended next cleanup path:

1. Query CRDB Dataverse for the duplicate `adx_webfile` and related `powerpagecomponent` rows.
2. Capture solution/component ownership and managed state.
3. Classify each duplicate as:
   - canonical active record;
   - unmanaged stale record that can be deleted after approval;
   - managed stale record that must be removed through solution lifecycle;
   - harmless historical record that can remain documented.
4. Prepare an explicit delete plan only for records proven unmanaged and unused.
5. Run a fresh PAC download and `node scripts/verify-powerpages-spa-assets.mjs --fail-on-duplicates` only after cleanup approval and execution.

## Tooling added

Added:

- `scripts/inventory-powerpages-webfile-duplicates.mjs`

Updated:

- `scripts/verify-powerpages-spa-assets.mjs`

The asset verifier now prints duplicate local filenames instead of only duplicate counts. This prevents future confusion between a clean committed package and a downloaded server package containing retained duplicates.
