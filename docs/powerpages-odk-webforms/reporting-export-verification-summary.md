# Reporting, Export, and Power BI Verification Summary

Date: 2026-07-14

## Current Status

Planning artifacts, additive reporting schema, projection builder, deployed reporting tables, populated projection rows, and Power Pages reporting permissions are complete in the development environment. Portal reporting reads, named CSV export UX, and Power BI guidance are the active implementation slice.

## Evidence Established

- Existing Dataverse persistence smoke proved submitted records and latest versions can be read.
- Developer-only CSV export proved XML flattening is technically possible, but it is not the product approach.
- ODK Central research supports relational reporting projection with root and repeat tables.
- KoboToolbox research supports user-facing named exports and Power BI/Excel connection workflows.
- Microsoft documentation supports Power BI connection to Dataverse through the Dataverse connector.
- `schemas/dataverse/reporting-projection-schema.json` validates as JSON.
- `scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/reporting-projection-schema.json` produces a no-write dry-run that includes reporting tables, columns/lookups, relationships, and alternate keys.
- `scripts/build-reporting-projections.py --top 10` dry-ran against the dev Dataverse environment and projected 5 canonical submissions into 5 report rows and 145 answer rows with no failed projections and no writes.
- `scripts/validate-reporting-projection-builder.py` validates root answer, repeat-row, and repeat-answer projection behavior without network access.
- Power Pages Web API settings and table permissions were configured for reporting/export tables on 2026-07-14:
  `mp_submissionreportrow`, `mp_submissionrepeatrow`, `mp_submissionanswer`, and `mp_exportsetting`.
- Hosted verifier passed with 12 table permissions and 24 Web API settings.
- Managed solution `0.2.3.0` explicitly includes the 8 reporting Web API site
  settings and 4 reporting table permissions after `0.2.2.0` omitted them.
- Package validation now rejects releases missing any reporting Power Pages
  component or any Authenticated Users role association. See
  `crdb-reporting-webapi-9004010c-20260716.md`.

## Verification Still Required After Implementation

- Hosted browser `/_api` read of reporting tables from the implemented UI.
- Submit/edit projection refresh.
- Rebuild projection from canonical versions.
- Data UX browser test across desktop/tablet/phone.
- CSV and XLSX download tests.
- Power BI Desktop connection test with non-admin reporting user.

## Completed Environment Verification

- Reporting schema deployed after explicit approval: 4 tables, 58 columns, 13 relationships, and 4 alternate keys.
- Projection rebuild wrote 5 report rows and 145 answer rows with 0 failures.
- Reporting Power Pages configuration passed the hosted verifier with 12 table permissions and 24 Web API settings.

## Completed Local Portal Verification

- Data reads use `/_api/mp_submissionreportrows` with server-side page, filter, order, and count parameters.
- Record detail reads normalized answers from `/_api/mp_submissionanswers`.
- Named CSV settings write through `/_api/mp_exportsettings`; browser CSV generation is bounded to 100 filtered root rows for the prototype.
- CSV download includes export name, generated timestamp, form version, applied filters, reporting metadata, and flattened root answers.
- Power BI panel exposes the non-secret Dataverse environment URL, reporting logical table names, recommended relationships, and the separate Dataverse security-role requirement.
- TypeScript typecheck, production build, SPA source validator, and projection builder validator pass.
- Headless browser checks pass at 1440 px and 390 px with no page overflow or JavaScript errors.
- Local named export test saved one reusable setting and downloaded a two-row CSV with stable metadata and answer columns.
