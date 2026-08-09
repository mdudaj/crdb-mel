# Reporting, Export, and Power BI Delivery Plan

## Evidence to Inspect First

- `docs/powerpages-odk-webforms/reporting-export-research.md`
- `docs/powerpages-odk-webforms/reporting-export-requirements.md`
- `docs/powerpages-odk-webforms/adr-0003-reporting-export-powerbi.md`
- `schemas/dataverse/odk-central-inspired-mvp-schema.json`
- `schemas/dataverse/platform-tables.json`
- `powerpages/webforms-spa/src/powerpages-api/client.ts`
- `powerpages/webforms-spa/src/views/AssignedFormsView.vue`
- Microsoft Dataverse connector docs
- Power Pages Web API and table permission docs

## Implementation Slices

### Slice 1: Reporting Schema Plan

1. Add schema artifacts for reporting projection tables.
2. Use additive Dataverse schema only; do not modify canonical submission tables except relationships if needed.
3. Include root submission report rows, repeat rows, answer rows, and export settings.
4. Define alternate keys for idempotent projection refresh:
   - root: `ReportKey`;
   - repeat row: `RepeatRowKey`;
   - answer row: `AnswerKey`;
   - export setting: `ExportKey`.
5. Run schema plan dry-run before any live Dataverse write.
6. Review `schemas/dataverse/reporting-projection-schema.json` and `schemas/dataverse/reporting-projection-schema.md` before requesting CRDB import/admin action.

### Slice 2: Projection Builder

1. Parse latest `SubmissionVersions.XFormSubmissionXml` server-side or in a trusted deploy script/flow. Delivered in `scripts/build-reporting-projections.py`.
2. Write or upsert derived reporting records. The builder uses alternate-key upserts and requires `--execute`.
3. Mark projections with source submission version lookup, `projected_at`, and `projection_status`.
4. Ensure edit submit replaces/updates the current projection for the canonical `instance_id` by rebuilding from the latest version.
5. Add a rebuild command or admin action to rebuild projections from all current versions. Delivered as a script-level rebuild command.
6. Before solution export, deploy `reporting-projection-schema.json`, run `scripts/build-reporting-projections.py --execute`, then verify reporting row counts.

### Slice 3: Data UX

1. Add a **Data** tab/area to the Monitoring Tool project workspace.
2. Show metrics: total submitted records, latest update, selected form/version, and projection status.
3. Show a dense table for desktop/tablet and a compact record list for narrow widths.
4. Add search, date range, submitter, review state, and form version filters.
5. Add record detail with metadata and answers.
6. Keep edit/open field workflow separate from reporting detail.

### Slice 4: Export UX

1. Add named export settings.
2. Support root CSV export.
3. Support XLSX export with separate sheets for root and repeat data.
4. Preserve field labels/language choices where available.
5. Include generated timestamp, export name, filters, form id, and form version in the output.
6. Show export status and clear errors when generation fails.

### Slice 5: Power BI UX

1. Add a **Power BI** panel under Data.
2. Show the Dataverse environment name/URL in a non-secret form.
3. List the reporting tables to select.
4. Explain required Dataverse read permissions and TDS/connector prerequisites.
5. Provide recommended model relationships between root and repeat tables.
6. Defer embedded reports until workspace/licensing/security decisions are made.

## Verification Gates

- Schema dry-run shows only additive tables, columns, relationships, and alternate keys.
- Projection builder can rebuild from existing smoke submissions without changing canonical submission rows.
- Submit and edit create/update reporting projection rows.
- Data view loads through Power Pages `/_api` with table permissions.
- CSV export downloads the filtered root dataset.
- XLSX export includes root and repeat sheets when repeat data exists.
- Power BI Desktop can connect to Dataverse reporting tables with an organizational account that has read permission.
- No client-side code contains secrets, bearer tokens, OAuth client secrets, or raw app credentials.

## Required Approval Before Implementation

- Dataverse reporting schema write.
- Power Pages table permission changes for reporting/export tables.
- Power Pages upload of any UX changes.
- Any Power Automate/custom API/plugin used for export generation.
