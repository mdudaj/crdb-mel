# Reporting and Export Research

## Purpose

This note records the reporting/export patterns to copy from mature ODK-style platforms before implementing TACATDP data viewing, export, and Power BI connectivity.

## Sources Inspected

- ODK Central OData endpoints: `https://docs.getodk.org/central-api-odata-endpoints/`
- ODK Central submission management: `https://docs.getodk.org/central-api-submission-management/`
- KoboToolbox synchronous exports: `https://support.kobotoolbox.org/synchronous_exports.html`
- KoboToolbox Power BI connection: `https://support.kobotoolbox.org/pulling_data_into_powerbi.html`
- KoboToolbox export downloads: `https://support.kobotoolbox.org/export_download.html`
- Microsoft Dataverse Power Query connector: `https://learn.microsoft.com/en-us/power-query/connectors/dataverse`
- Microsoft Dataverse Analyze in Power BI: `https://learn.microsoft.com/en-us/power-apps/maker/data-platform/view-entity-data-power-bi`

OnaData was considered because it is an ODK/formhub-derived platform, but current hosted API/export docs were not reliably retrievable during this research pass. Do not treat OnaData as a governing source until its current API/export documentation is inspected directly.

## ODK Central Pattern

ODK Central keeps submitted data as canonical, versioned ODK submissions and exposes reporting data through form-specific OData services:

- One service per form.
- A root `Submissions` table for non-repeat data.
- One relational table per repeat group.
- Stable join identifiers for root-to-repeat relationships.
- A `$metadata` endpoint that describes the generated schema.
- Data endpoints with OData-style paging, filtering, counting, selected fields, ordering, and repeat expansion.
- Attachments are retrievable separately through download paths.

The important architectural lesson is that Central does not make the submission XML the analytics surface. It keeps XML as source-of-truth and projects it into relational, BI-friendly tables.

## KoboToolbox Pattern

KoboToolbox provides user-facing export workflows:

- Users configure exports from the project data/downloads area.
- Users can save named export settings.
- Synchronous export URLs expose configured CSV or XLSX output for external tools such as Power BI, Excel, and Google Sheets.
- XLSX is preferred when repeat groups exist because repeat groups become separate sheets; CSV does not include repeat groups.
- Export configuration can include question labels, language choices, filters, and media URL options.
- Synchronous exports have practical reliability limits, including refresh latency and completion time limits.

The important UX lesson is that nontechnical users need named export configurations and a visible download/connect workflow, not only raw APIs.

## Microsoft/Dataverse Pattern

Power BI can connect directly to Dataverse using the Dataverse connector. The connector supports Power BI semantic models, Import, DirectQuery, organizational account authentication, and service principal authentication in supported contexts. It requires Dataverse table read permissions and the Dataverse TDS endpoint setting. Microsoft also supports an "Analyze in Power BI" entry from Power Apps table data for users with the required maker/read privileges.

The important TACATDP lesson is to prefer Dataverse reporting tables as the Power BI source. A Power Pages CSV download is useful for users, but should not be the primary Power BI integration path.

## TACATDP Design Implications

- Keep `Submissions`, `SubmissionVersions`, and attachment records as canonical source-of-truth.
- Add reporting projections that are generated from the latest current submission version.
- Model the root form data and repeat groups as separate relational reporting surfaces.
- Provide a portal UX for browsing data and creating named export configurations.
- Provide a Power BI guidance panel that points to the Dataverse connector and the reporting tables.
- Offer CSV/XLSX downloads for user workflows, but keep Power BI connected to Dataverse when possible.
- Treat export generation as a governed reporting feature with permissions, filters, schema version, and refresh semantics.
