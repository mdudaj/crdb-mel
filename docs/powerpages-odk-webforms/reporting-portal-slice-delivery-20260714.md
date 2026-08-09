# Reporting Portal Slice Delivery: 2026-07-14

## Delivered

- Corrected stale reporting checklist and readiness records against deployed environment evidence.
- Added typed Power Pages Web API access for paginated/filtered report rows, normalized answers, and named export settings.
- Replaced the Data placeholder with an operational reporting table, date/submitter/review/search filters, pagination, projection state, answer detail, and canonical Edit handoff.
- Replaced the Exports placeholder with named current-filter CSV settings, bounded browser download, rerun actions, progress, empty, success, and error states.
- Replaced the Power BI placeholder with the Dataverse environment URL, connector steps, reporting tables, relationships, recommended initial Import mode, and permission guidance.
- Added deterministic local reporting fixtures for desktop/phone UI verification without environment writes.
- Fixed local Vite rendering of Power Pages Liquid session placeholders by keeping Liquid expressions inside valid JavaScript strings.

## Implementation Boundary

- CSV covers root reporting rows only and is limited to 100 filtered rows in the browser prototype.
- XLSX remains deferred until hosted repeat data exists and a governed workbook-generation mechanism is selected.
- Projection refresh remains an explicit trusted script operation; automatic submit/edit refresh is a separate server-side automation slice.
- No Power Pages upload, Dataverse schema write, permission change, package installation, or Power BI connection was performed.

## Verification

- `npm run typecheck`: passed.
- `npm run build`: passed; existing ODK dependency direct-eval and large-chunk warnings remain.
- `python3 scripts/validate-webforms-spa-foundation.py`: passed.
- `python3 scripts/validate-reporting-projection-builder.py`: passed.
- Headless Chromium desktop Data/answer detail, Exports, and Power BI renders: passed with no page errors or viewport overflow.
- Headless Chromium phone Data render: passed; all four Material tabs fit within 390 px and the table remains horizontally scrollable.
- Named export browser test: saved one setting and downloaded `current-project-data.csv` with two fixture rows and metadata/root-answer columns.
- CSV cell generation neutralizes leading spreadsheet formula characters before download.

## Deployment Instructions

1. Inspect this delivery note, `reporting-export-requirements.md`, `adr-0003-reporting-export-powerbi.md`, `reporting-powerpages-permissions-20260714.md`, and the current git diff.
2. Run the verification commands above.
3. Confirm PAC targets website ID `fccc0cc6-7f5e-4885-aeb8-2272e68130a3` in `https://orga3cf4b37.crm4.dynamics.com`.
4. After explicit upload approval, package the new Vite build into the explicit enhanced-model Power Pages site source and upload by website ID.
5. Clear Power Pages server cache, then browser-test signed-in Data reads, answer detail, named export create, CSV download, and Power BI copy guidance.
6. Verify CSV contents do not exceed the bounded scope and that no anonymous user can read reporting tables.

## Remaining Gates

- Explicit Power Pages upload approval.
- Hosted authenticated browser verification.
- Power BI Desktop connection with a non-admin Dataverse reporting user.
- Hosted repeat submission before XLSX delivery.
