# 04 Current Architecture

## Architecture Summary

The current Sustainable Finance MEL Platform prototype uses Microsoft Power Platform to collect TACATDP beneficiary baseline data through a guided digital form and organize the captured data into monitoring-ready records.

The active prototype architecture is Power Pages plus Dataverse. Power Pages provides the web portal/user interface, while Dataverse provides the current application data store for project/form configuration, assignments, submissions, and related monitoring records.

The current implementation is derived from the TACATDP XLSForm and related generated artifacts. TACATDP names remain in some schema/list/form artifacts for compatibility and traceability. Treat TACATDP as the first configurable programme/project use case, not as the full platform boundary.

## Current Prototype Architecture

```text
User / Enumerator
  -> Power Pages portal / hosted form runtime
  -> Power Pages Web API
  -> Dataverse tables/entities
  -> Project, form, assignment, submission, beneficiary, reference, and evidence records
  -> Portal KPI dashboard
```

## Main Components

| Component | Purpose | Current status |
|---|---|---|
| Power Pages portal | Provides browser-based access to the baseline form, authenticated user experience, and planned dashboard. | Deployed prototype site exists. |
| Baseline form | Captures beneficiary baseline data from the TACATDP-derived form. | Current prototype capability. |
| Dataverse | Current prototype data store for Power Pages configuration and application records. | Active delivery path. |
| Power Pages Web API | Browser-to-Dataverse write/read channel for authenticated portal users. | Active delivery path. |
| Submission record | Parent record for a captured baseline assessment. | Represented in Dataverse/schema/design artifacts. |
| Beneficiary model | Identifies beneficiaries separately from one-off submissions. | Agreed prototype revision. |
| Section/form response records | Store detailed responses by form section or structured payload. | Represented through generated schema and Dataverse design artifacts. |
| Reference data | Supports locations, branches, and choice lists. | Represented through import templates, schema artifacts, and Dataverse-ready design. |
| Portal KPI dashboard | Shows headline indicators without waiting for Power BI. | Agreed prototype revision. |
| Power BI analytics | Future governed analytics layer. | Future product scope. |
| Programme/project configuration | Allows the platform to support multiple Sustainable Finance Unit use cases. | Future product scope. |

## Data Model Direction

The prototype should avoid treating a submitted form as the only data object. In Dataverse, it should separate:

- programme/project;
- beneficiary identity;
- baseline submission;
- form section responses;
- repeated/multi-select answer rows;
- reference data;
- calculated or aggregated KPI values.

This keeps the prototype useful for monitoring and creates a cleaner migration path toward a production MEL platform.

The future data model should also support non-beneficiary use cases by allowing configurable monitored entities for facilities, operational processes, resources, activities, indicators, results, and evidence attachments.

## Prototype Versus Enterprise Architecture

Power Pages and Dataverse are appropriate for the proof-of-concept because they provide fast delivery, Microsoft 365/Power Platform alignment, authentication integration, and a manageable route for demonstrating data collection and portal KPIs.

For an enterprise-grade scalable product, the architecture should be reviewed beyond the current Power Pages implementation. The future platform may retain some Microsoft ecosystem components where they fit, but it should not be constrained to Power Pages as the long-term application shell.

The target architecture should evaluate:

- a dedicated web application frontend for richer UX, performance, and maintainability;
- a backend API/service layer for business rules, workflow, integration, and audit;
- an enterprise DBMS or governed data platform for transactional and analytical data;
- Dataverse where it remains appropriate for Microsoft-native workflow, configuration, or rapid business app delivery;
- an analytics layer such as Power BI or another approved BI stack;
- identity, access control, audit, monitoring, backup, and release management as first-class architecture concerns.

## Beneficiary-Linked Model

```text
Beneficiary
  -> Baseline Submission
      -> Profile / demographics section
      -> Agriculture section
      -> Resource efficiency section
      -> Social inclusion section
      -> Beneficiary quantification sections
      -> Safeguards and climate section
      -> Insurance / guarantee section
      -> GHG, water, yield, income sections
      -> Production cost lines
```

At prototype level, beneficiary modeling may be lightweight. At future-product level, it should become a governed beneficiary registry with deduplication, identity rules, audit, and lifecycle management.

## Reference Data

The source form includes large and filtered choice lists. Location and branch choices should use reference data rather than hard-coded dropdown values.

Important reference categories include:

- region;
- district;
- ward;
- village;
- CRDB branch;
- coded form choices.

Large reference lists should be filtered using stable indexed keys where supported by the selected data source.

## Portal KPI Dashboard

The prototype dashboard should display key indicators directly in the portal:

- total baseline submissions;
- total beneficiaries captured;
- beneficiaries by location;
- beneficiaries by value chain;
- social inclusion indicators where available;
- submission status or completion counts.

This is a prototype analytics layer. Power BI remains the recommended future-product analytics layer once permissions, licensing, ownership, and governance are approved.

## Authentication and Access

Authentication and deployment are governed by the target Power Platform tenant/environment.

Known operational lessons:

- PAC authentication should use verified environment IDs where possible.
- Do not assume Azure service principal or managed identity authentication unless explicitly approved.
- CRDB deployment work historically used device-code authentication with the delegated `dmuroba@crdb.co.tz` profile.
- Mshirika access must be verified against the correct tenant account and Power Pages environment.

## Current Architecture Limitations

The current prototype does not yet provide:

- full production master-data governance;
- complete Power BI analytics integration;
- enterprise-grade audit and role model;
- formal backup, monitoring, and incident management;
- integration with CRDB enterprise systems;
- full offline-first data collection.

These are future-product architecture requirements.

## Architecture Acceptance Criteria

The current architecture is acceptable for prototype submission if:

- baseline collection is demonstrable;
- data is structured and beneficiary-linked;
- portal KPIs are visible or clearly planned for the prototype revision;
- deployment/authentication constraints are documented;
- production-grade gaps are explicitly assigned to the future product roadmap.
