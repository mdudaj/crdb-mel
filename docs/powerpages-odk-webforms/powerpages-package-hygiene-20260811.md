# Power Pages Package Hygiene Gate — 2026-08-11

## Problem

Full Enhanced-model `pac pages upload` failed on Mshirika with
`PortalFileContentUploadFailed` while uploading `portalbasictheme.css`.

The package was internally inconsistent:

- `.portalconfig/manifest.yml` marked several `adx_webfile` records as deleted.
- The same files and `.webfile.yml` records were still present under `web-files/`.
- PAC processed the manifest delete, then later tried to upload file content for the deleted/nonexistent record.
- Dataverse returned `ObjectDoesNotExist`.

Confirmed conflict set:

- `Logo-sm-64.png`
- `bootstrap.min.css`
- `theme.css`
- `portalbasictheme.css`
- `Cat-PC.png`

## Decision

Do not delete the physical files as the default fix. Some site pages and content
snippets still reference assets such as `Cat-PC.png` and `Logo-sm-64.png`.

The safer package fix is:

1. keep the web-file binaries and metadata intact;
2. remove only the conflicting deleted `adx_webfile` entries from the upload manifest;
3. fail locally if the conflict reappears.

## Implementation

The guard is implemented in:

- `scripts/validate-powerpages-package-hygiene.py`

It checks:

- deleted-present `adx_webfile` conflicts between `.portalconfig/manifest.yml`
  and `web-files/*.webfile.yml`;
- empty manifest sections that PAC 2.9.3 can read as a null collection;
- target environment manifest presence when `--environment-url` is supplied;
- Home page `/assets/...` references have matching web-file binaries;
- Home page `/assets/...` references have matching `.webfile.yml` metadata;
- Home page asset metadata exposes the expected `adx_partialurl`.

The staging script now runs the manifest repair and validation after copying SPA
assets:

```bash
python3 scripts/stage-powerpages-spa-build.py
```

The deploy asset gate now includes package hygiene validation:

```bash
npm run test:powerpages-assets
```

## Acceptance checks

Before full package upload:

```bash
cd powerpages/webforms-spa
npm run test:powerpages-assets
```

Expected:

- SPA dist assets match the upload package web files.
- No deleted-present `adx_webfile` conflicts remain.
- No empty manifest sections remain.
- Home page JS and CSS references resolve to package files.

Before deploying to a specific environment, validate that the upload package was
downloaded from that target environment:

```bash
python3 scripts/validate-powerpages-package-hygiene.py \
  --environment-url https://orga3cf4b37.crm4.dynamics.com/
```

Duplicate partial URL warnings for historical localized/date-picker chunks remain
non-blocking unless a future upload failure proves they affect PAC or runtime
resolution.
