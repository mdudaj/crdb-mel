# Upstream Deployment Summary: 2026-07-14

## Target

- Environment: `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- Public URL recorded in repository docs: `https://tacatdp.powerappsportals.com/`

## Deployed Package

- Source SPA: `powerpages/webforms-spa/`
- Upload package: `powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/`
- Home page cache marker: `project-tabs-20260714-001`
- Main module: `/assets/index-CKcLk8G5.mjs`
- Main stylesheet: `/assets/index-DniLTH1I.css`

## Verification

- `npm run typecheck` passed.
- `npm run build` passed.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-CKcLk8G5.mjs` passed.
- `node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-Cg9qvMI9-B1UfK9zv.mjs` passed.
- `pac env who` confirmed `PowerPagesDeveloper-070926-125720`.
- `pac pages list` confirmed website ID `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`.
- `pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll` succeeded in 125.42 seconds.
- `python3 scripts/verify-powerpages-api-smoke-hosted.py --website-id fccc0cc6-7f5e-4885-aeb8-2272e68130a3 --site-name "TACATDP Monitoring Tool"` passed.
- Dataverse `mspp_webpages` Home rows contain `index-CKcLk8G5.mjs`, `index-DniLTH1I.css`, and `project-tabs-20260714-001`.

## Notes

- Public unauthenticated curl redirects to Microsoft sign-in, so browser-level visual verification still requires an authenticated session.
- PAC logged missing `powerpagecomponent` update warnings for records that no longer exist, but the upload completed successfully and hosted-state verification passed.
- Build warnings remain the known upstream ODK Web Forms direct `eval` and large chunk warnings.
