# Mshirika Beneficiary KPI and Map Deployment

Date: 2026-08-09

## Target

- Environment: `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- PAC user: `john.mduda@mshirikacorp.onmicrosoft.com`
- Branch: `prototype-next-delivery`
- Source commit before deployment: `07fbecc`

## Package marker

The uploaded Home fragments reference:

- `/assets/index-BYCG8iiH.mjs?v=beneficiary-kpi-map-20260809-001`
- `/assets/index-laWETBbq.css?v=beneficiary-kpi-map-20260809-001`

## Pre-upload validation

Passed:

```bash
python3 scripts/validate-webforms-spa-foundation.py
python3 scripts/validate-beneficiary-kpi-map-slice.py
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-BYCG8iiH.mjs
```

## PAC package-format issue

Direct upload of the repository package initially failed under PAC `2.9.3+ga17df1d` because `website.yml` used old keys (`id`, `name`) instead of the required `adx_websiteid` and `adx_name`.

After fixing `website.yml`, direct upload still failed because PAC rejected several older per-entity YAML files with:

```text
Expected 'SequenceStart', got 'MappingStart'
```

The safe workaround was:

1. Download a fresh package from Mshirika with the current PAC format.
2. Overlay only the new SPA asset files and the Home page fragments.
3. Upload the fresh-format package.

## Upload command

The successful upload used:

```bash
pac pages upload \
  --environment https://orga3cf4b37.crm4.dynamics.com/ \
  --path /tmp/mshirika-standard-upload.iITwnF/tacatdp-monitoring-tool \
  --modelVersion Enhanced \
  --forceUploadAll
```

Result:

```text
Power Pages website upload succeeded in 196.59 secs.
```

## Post-upload verification

A post-upload PAC download confirmed both Home fragments reference the new marker:

- `web-pages/home/Home.webpage.copy.html`
- `web-pages/home/content-pages/Home.en-US.webpage.copy.html`

The same download confirmed web-file metadata exists for:

- `index-BYCG8iiH.mjs`
- `index-laWETBbq.css`

## Notes

- No CRDB deployment was attempted.
- No Dataverse schema/data write was performed beyond the Power Pages website upload.
- If the browser still shows stale JavaScript, purge Power Pages server-side cache or restart the site, then reload with cache disabled.
