# Collect Runtime Mshirika Deployment

Date: 2026-07-29

## Task Classification

Assessment plus deployment smoke for restoring the TACATDP Collect runtime on Mshirika. No schema, authentication, table-permission, or Dataverse data changes were made.

## Corrected Runtime Packaging Finding

The earlier conclusion that Collect could not be uploaded through Power Pages web files was too strict. Microsoft documents that Power Pages web-file content is stored as the attachment of the latest note on the web-file record, and supported size is determined by the target Dataverse environment note attachment setting, not a universal 1 MB Power Pages limit.

Relevant Microsoft references:

- Power Pages web files: `https://learn.microsoft.com/en-us/power-pages/configure/web-files`
- Power Pages CDN/static files: `https://learn.microsoft.com/en-us/power-pages/configure/configure-cdn`

Project history also showed a runtime-enabled upload succeeded on 2026-07-14. Therefore, the right Mshirika test was to package and upload the runtime build, not stop at the conservative access-only size guard.

## Runtime Build

Command:

```bash
npm --prefix powerpages/webforms-spa run build:mshirika-runtime
```

Result: passed.

Known upstream warnings remain:

- `@getodk/web-forms` distributed bundle uses direct `eval`.
- ODK runtime chunks exceed Vite's 500 KB warning threshold.

Important generated assets:

```text
index-D1XJZa3P.mjs                         129 KB
dist-pLvMFTNt.mjs                         1.8 MB
index-Cg9qvMI9-CaiUDr-N.mjs               2.24 MB
MapBlock-BTX9u64V-Dmmytmmp.mjs             475 KB
vendor-datepicker-DzapWs4n.mjs             287 KB
```

## Package Update

The Power Pages source and upload packages now reference:

```text
/assets/index-D1XJZa3P.mjs?v=collect-runtime-20260729-001
/assets/vendor-icons-COQr__mn.mjs?v=collect-runtime-20260729-001
/assets/preload-helper-Czpn1I53.mjs?v=collect-runtime-20260729-001
/assets/index-CfUxfRBd.css?v=collect-runtime-20260729-001
/assets/vendor-datepicker-D7vsgEFT.css?v=collect-runtime-20260729-001
```

All non-map runtime assets from the Vite build were copied into both:

- `powerpages/tacatdp-monitoring-tool/.powerpages-site/web-files`
- `powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files`

## Verification Summary

Commands run:

```bash
npm --prefix powerpages/webforms-spa run build:mshirika-runtime
python3 scripts/validate-webforms-spa-foundation.py
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-D1XJZa3P.mjs
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-Cg9qvMI9-CaiUDr-N.mjs
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/dist-pLvMFTNt.mjs
git diff --check
pac env who
pac pages list
```

Results:

- Runtime build: passed with known upstream warnings.
- Foundation validator: passed.
- Runtime bundle syntax checks: passed.
- `git diff --check`: passed.
- PAC target confirmed as Mshirika `PowerPagesDeveloper-070926-125720`.
- Site confirmed as `TACATDP Monitoring Tool`.

The access-only activation validator was intentionally not used for this package because it enforces the older access-only size guard and is not a runtime package validator.

## Mshirika Upload

Command:

```bash
pac pages upload \
  --environment "https://orga3cf4b37.crm4.dynamics.com/" \
  --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool \
  --modelVersion Enhanced \
  --forceUploadAll
```

Result:

- Upload succeeded in 71.97 seconds.
- PAC printed the familiar non-terminal `powerpagecomponent ... Does Not Exist` warnings, then completed with `Power Pages website upload succeeded`.

## Browser Review Steps

1. Purge/restart the site once.
2. Open the portal while signed in.
3. Confirm the loaded bundle marker is `collect-runtime-20260729-001`.
4. Enable timing:

```js
localStorage.setItem('TACATDP_DEBUG_PERF', 'true');
location.reload();
```

5. Open a project.
6. Click Collect.
7. Watch the browser Network tab for:
   - `index-Cg9qvMI9-CaiUDr-N.mjs`
   - `dist-pLvMFTNt.mjs`
   - `MapBlock-BTX9u64V-Dmmytmmp.mjs` only if a map/geopoint control is rendered.
8. Confirm the ODK form renders instead of staying on the loading panel.

## Remaining Risks

- The runtime-enabled package may slow initial app mount because `main.ts` installs `webFormsPlugin` before mounting the Vue app. If startup becomes unacceptable, the next slice should move ODK plugin loading closer to the Collect route without rendering `OdkWebForm` before plugin setup.
- The upstream ODK runtime uses direct `eval`; this is accepted only for Mshirika testing. CRDB production hardening must review CSP/security policy impact.
- CDN can improve static asset delivery only for production Power Pages sites and authenticated pages/files still have documented caching limits. Do not assume CDN will solve Collect startup in Mshirika developer testing.
