# ADR 0003: Reporting Projection and Power BI Export Surface

Status: proposed.
Date: 2026-07-14

## Context

The Monitoring Tool now stores submitted XForm instance XML and compact JSON metadata in Dataverse. Users need to view submitted data, export it, and connect Power BI before further feature work.

Developer-run CSV scripts proved that persisted submissions can be flattened, but scripts are not an acceptable user workflow. Mature ODK-style systems separate canonical submission storage from reporting/export surfaces. ODK Central exposes form data through relational OData tables with one table per repeat group. KoboToolbox provides named export settings and synchronous export URLs for tools such as Power BI and Excel. Microsoft Power BI can connect directly to Dataverse using the Dataverse connector.

## Decision

TACATDP will keep `Submissions`, `SubmissionVersions`, and submitted XML/JSON as source-of-truth, and add Dataverse reporting projections for user data views, downloads, and Power BI.

The first implementation will provide:

- a Monitoring Tool **Data** area for browsing and filtering submitted records;
- reporting projection tables generated from latest current submission versions;
- root submission reporting rows plus repeat/answer projections where needed;
- named export settings for repeatable CSV/XLSX output;
- a Power BI guidance panel that connects users to the Dataverse reporting tables through the official Dataverse connector.

Power BI direct connection to Dataverse reporting tables is the primary BI path. CSV/XLSX download is a secondary user convenience, not the primary integration architecture.

## Consequences

- Submit/edit must refresh reporting projections after writing canonical submission/version rows.
- Reporting projections are derived data and can be rebuilt from `SubmissionVersions`.
- Repeat groups must be represented relationally; they must not be collapsed permanently into a single wide row.
- Portal export UX must respect Power Pages authentication and Dataverse permissions.
- A future production hardening slice may replace or supplement Dataverse projections with Azure Synapse Link, Fabric, or a governed warehouse if data volume grows.

## Rejected Alternatives

- **Manual developer-run CSV only**: useful for smoke verification, not acceptable as product UX.
- **Power BI directly over raw XML payloads**: preserves source data but creates brittle report logic and poor repeat handling.
- **Portal-only browser flattening**: simple for a prototype, but unsafe for large forms and inconsistent with Dataverse as the system of record.
- **Embedded Power BI first**: attractive visually, but it depends on workspace, licensing, sharing, and tenant policy decisions that should not block basic data access.
