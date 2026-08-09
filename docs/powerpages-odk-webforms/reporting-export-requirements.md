# Reporting, Export, and Power BI Requirements

## Goal

Add a Monitoring Tool data area where authenticated users can view submitted TACATDP records, create/download governed exports, and connect Power BI to Dataverse reporting tables without relying on developer-run scripts.

## Functional Requirements

- Add a user-facing **Data** area to the Monitoring Tool.
- Show submitted records from Dataverse in a tabular, filterable, searchable view.
- Page reporting rows with a Power Pages-supported query mechanism. Do not use
  Dataverse `$skip`; use FetchXML `count` and `page` with deterministic ordering.
- Preserve the existing saved-card workflow for field editing; the Data area is for review/reporting, not primary field entry.
- Display record detail using latest current submission data, including key metadata and flattened answer values.
- Keep canonical source-of-truth in `Submissions`, `SubmissionVersions`, `SubmissionAttachments`, and submitted XML/JSON payloads.
- Add reporting projection tables for BI and export:
  - one root reporting row per latest current submission version;
  - one repeat-row reporting table or generic repeat-row table for repeat group instances;
  - one answer-level table for flexible analysis where field-level normalization is required.
- Preserve stable join keys between root submissions and repeat rows.
- Preserve form identity, form version, ODK `instanceId`, Dataverse submission id, Dataverse version id, submitter, timestamps, lifecycle status, and review state in reporting rows.
- Store export configuration as named export settings, including selected form, columns, labels/language choice, filters, repeat handling, media URL inclusion, and output format.
- Generate the export setting and CSV filename from the selected form name plus
  export timestamp. Replace spaces with underscores and use the format
  `<Form_Name>_YYYYMMDD_HHMMSS`.
- Support portal downloads for at least CSV for root records and XLSX for root plus repeat sheets.
- For forms with repeat groups, warn that CSV root export does not include repeat rows unless a repeat-specific export is selected.
- Provide a **Power BI** panel that shows:
  - target Dataverse environment;
  - reporting tables to select;
  - recommended Import or DirectQuery mode;
  - required Dataverse read permissions;
  - refresh notes and known limits.
- Prefer Power BI connection through the official Dataverse connector to reporting projection tables.
- Keep any downloadable file export as a secondary workflow for users who need files.
- Do not expose client secrets, Dataverse app credentials, bearer tokens, or raw environment credentials in portal code.
- Do not make reporting tables public or anonymous.
- Respect Dataverse and Power Pages table permissions for all portal views and exports.
- Package each reporting table's `Webapi/<logical-name>/enabled` and
  `Webapi/<logical-name>/fields` site settings and its Authenticated Users table
  permission in the governed managed solution. Whole-site inclusion alone is not
  sufficient evidence that existing Power Pages child components are solution-owned.

## Non-Functional Requirements

- Reporting surfaces must be deterministic from the latest current submission version.
- Projection refresh must be idempotent for create and edit submit paths.
- Export output must include a generated-at timestamp, form id, form version, and export configuration name.
- Column names must be stable across refreshes unless the source form schema changes.
- The user-facing table must support empty, loading, error, and permission-denied states.
- The Data area must remain usable at laptop and tablet widths. Phone width may show a reduced table/card layout, but controls must not overlap.
- Large exports must use a server-side or Dataverse-side projection; browser code must not attempt to parse all XML payloads client-side for production export.
- Prototype implementation may start with one TACATDP form, but table/schema names must leave a path to per-form reporting projections or generic multi-form projections.

## Out of Scope for First Slice

- Embedded Power BI reports inside Power Pages.
- Full OData service implementation with `$metadata`.
- Public anonymous export links.
- Production-grade data warehouse or Azure Synapse Link.
- Cross-project report builder UI.

## Open Decisions

- Whether first implementation uses form-specific Dataverse reporting tables or generic reporting tables with `form_version_id` and `field_path` columns.
- Whether XLSX generation runs through a Power Automate flow, Dataverse custom API/plugin, or a portal-compatible server-side endpoint.
- Whether CRDB environment policy allows Power BI DirectQuery to Dataverse or requires Import mode.
