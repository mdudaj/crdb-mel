# Power Pages Bundle Package Hygiene - 2026-07-21

## Purpose

Keep the Power Pages source package reviewable after repeated Vite bundle uploads.

## Rule

- Keep only the current `powerpages/webforms-spa/dist/assets` runtime bundle in the source-controlled Power Pages package.
- Preserve real portal assets such as `bootstrap.min.css`, `portalbasictheme.css`, `theme.css`, CRDB logo assets, and image files.
- Remove obsolete generated bundle files and generated bundle directories named like `.mjs` or `.css` files.
- The ignored upload package may be regenerated from the source package and current build output, but should not be committed.

## Current Bundle Set

- `ActionsInfoDialog-B8AZQOuY-B_ARqT-G.mjs`
- `CanvasBlock-DWoXGSW9-CvwGR8gR.mjs`
- `MapBlock-BTX9u64V-CNidbrSB.mjs`
- `index-CYGW669e.mjs`
- `index-Cg9qvMI9-CFIDWHu8.mjs`
- `index-DALgcSQx.css`
- `runtime-core.esm-bundler-sjoBfEhY.mjs`
- `strings_es-C8xkQaZj-KYNBMnTd.mjs`
- `strings_fr-C0vLmCzP-Bi34LuTN.mjs`
- `strings_id-BE0G3I_d-B0dO9nQF.mjs`
- `vue-konva-D0sZ6RWk-De_G96cE.mjs`

## Verification

- `python3 scripts/validate-webforms-spa-foundation.py` passed after cleanup.
- `node --check powerpages/tacatdp-monitoring-tool/.powerpages-site/web-files/index-CYGW669e.mjs` passed.
- Home page fragments reference `index-CYGW669e.mjs?v=access-route-gating-20260721-001` and `index-DALgcSQx.css?v=access-route-gating-20260721-001`.

