# Sustainable Finance MEL Platform Requirements Specification

## Purpose

This specification defines the prototype requirements for the Sustainable Finance MEL Platform and separates them from future-product requirements.

The current prototype uses TACATDP monitoring as the proof-of-concept use case. Future-product requirements must support a configurable platform for multiple Sustainable Finance Unit programmes/projects.

## Scope Classification

| Scope | Meaning |
|---|---|
| Prototype current | Already represented in the current prototype artifacts or deployed baseline collection flow. |
| Prototype revision | Agreed addition before final prototype documentation/delivery. |
| Future product | Required for a scalable, robust production-grade Sustainable Finance MEL Platform. |

## Prototype Functional Requirements

| ID | Requirement | Scope | Priority | Acceptance Criteria |
|---|---|---|---|---|
| PR-FR-01 | The system must provide a guided baseline data collection form derived from the TACATDP impact evaluation XLSForm. | Prototype current | Must | Users can access the form and move through structured sections. |
| PR-FR-02 | The system must preserve relevant baseline survey sections, labels, choices, required rules, and validation intent. | Prototype current | Must | Form sections and validation behavior can be traced to the XLSForm inventory and validation/save map. |
| PR-FR-03 | The system must store submitted data in structured lists/entities rather than an unstructured document. | Prototype current | Must | Submission data maps to documented schema/list artifacts. |
| PR-FR-04 | The system must support reference data for location, CRDB branch, and coded choices. | Prototype current | Must | Region, district, ward, village, branch, and coded-choice references are represented in schema/import artifacts. |
| PR-FR-05 | The system must model beneficiaries as identifiable records linked to baseline submissions. | Prototype revision | Must | A beneficiary identifier or equivalent link exists between beneficiary records and submitted baseline assessments. |
| PR-FR-06 | The system must support beneficiary segmentation for monitoring where data is collected. | Prototype revision | Should | Users/reviewers can group beneficiary counts by location, value chain, sex, youth/women/social inclusion attributes, or other available fields. |
| PR-FR-07 | The system must show basic KPI visualisation directly on the portal. | Prototype revision | Must | Portal page displays KPI cards/charts for key indicators without requiring Power BI. |
| PR-FR-08 | The system must distinguish draft, submitted, failed, and reviewed states where supported by the data model. | Prototype current/revision | Should | Submission status is visible or represented in the data model. |
| PR-FR-09 | The system must provide user-facing validation feedback for required and invalid visible fields. | Prototype current/revision | Must | Invalid visible fields block continuation/submission and show useful messages. |
| PR-FR-10 | The system must provide documentation for users and administrators. | Prototype revision | Must | User manual and deployment/admin guide exist under the submission documentation pack. |
| PR-FR-11 | The documentation must position TACATDP as the first proof-of-concept use case, not as the full platform boundary. | Prototype revision | Must | Submission documents explain the multi-programme Sustainable Finance Unit platform direction. |

## Portal KPI Requirements

| ID | KPI Requirement | Scope | Acceptance Criteria |
|---|---|---|---|
| KPI-01 | Show total baseline submissions. | Prototype revision | Dashboard displays a count based on available submission records or verified demo data. |
| KPI-02 | Show total beneficiaries captured. | Prototype revision | Dashboard displays total beneficiaries or beneficiary counts from the current data model. |
| KPI-03 | Show geographic coverage. | Prototype revision | Dashboard breaks data down by region/district where location fields exist. |
| KPI-04 | Show value-chain coverage. | Prototype revision | Dashboard summarizes beneficiaries or submissions by value chain where fields exist. |
| KPI-05 | Show social inclusion indicators where data exists. | Prototype revision | Dashboard summarizes gender, youth, women, or other inclusion indicators when captured. |
| KPI-06 | Clearly label demo or sample data if live data is unavailable. | Prototype revision | Reviewer can distinguish real submitted data from seeded/demo values. |

## Beneficiary Modeling Requirements

| ID | Requirement | Scope | Acceptance Criteria |
|---|---|---|---|
| BEN-01 | The prototype must represent a beneficiary separately from a one-time form submission. | Prototype revision | Beneficiary concept is documented and represented in the data model or implementation plan. |
| BEN-02 | Each baseline submission must link to a beneficiary identifier where feasible. | Prototype revision | Submission record can be associated with a beneficiary. |
| BEN-03 | Beneficiary data must support future follow-up and endline comparisons. | Prototype revision/future | Data model does not prevent multiple submissions over time for the same beneficiary. |
| BEN-04 | The future product must support central beneficiary master data and deduplication. | Future product | Roadmap includes registry governance, deduplication, and data ownership. |

## Non-Functional Requirements

| ID | Requirement | Scope | Acceptance Criteria |
|---|---|---|---|
| NFR-01 | Documentation and source artifacts must be version controlled. | Prototype current | Repository contains docs, schema, scripts, and app artifacts. |
| NFR-02 | The prototype must avoid storing secrets or credentials in source files. | Prototype current | No secrets are committed in documentation or scripts. |
| NFR-03 | Deployment and authentication steps must be documented with known tenant/profile constraints. | Prototype revision | Admin guide records PAC and environment notes. |
| NFR-04 | The prototype must not depend on Power BI permissions for basic assessment visibility. | Prototype revision | Portal KPI dashboard provides immediate monitoring visibility. |
| NFR-05 | The future product must define production-grade security, audit, backup, and support requirements. | Future product | Future-product vision and roadmap include production readiness gates. |
| NFR-06 | The future product must not be constrained to Power Pages if enterprise requirements require a more robust application architecture. | Future product | Future vision documents target frontend, backend API, DBMS/data platform, integration, hosting, and operations review. |

## Data Requirements

The prototype data model should support:

- parent submission records;
- beneficiary records or beneficiary-linked summary records;
- section-based baseline data;
- multi-select answer rows where needed for analytics;
- production cost line rows where repeated cost data exists;
- reference data for locations, branches, and choices;
- status and timestamp metadata.

Existing TACATDP list/schema names may remain unchanged for compatibility with generated artifacts and deployed components.

## User Roles

| Role | Required access |
|---|---|
| Beneficiary/respondent | Submit baseline data where portal access model allows. |
| Enumerator | Capture and save baseline data. |
| MEL reviewer | Review submissions and dashboard indicators. |
| Administrator | Configure portal, data sources, users, and deployment settings. |
| Developer | Maintain source, schema, scripts, and documentation. |

## Out of Scope for Prototype

The prototype does not include:

- guaranteed production SLA;
- full Power BI dashboard integration;
- enterprise master-data management;
- integration with CRDB core banking or customer systems;
- complete offline synchronization;
- automated approval workflow unless explicitly implemented;
- formal disaster recovery implementation.

## Future Product Requirements

If accepted, the scalable Sustainable Finance MEL Platform should include:

- configurable programme/project setup;
- governed beneficiary registry;
- configurable entities for facilities, processes, resources, activities, indicators, and evidence;
- reviewed frontend/application architecture beyond the Power Pages proof of concept;
- backend API/service layer;
- enterprise DBMS or approved governed data platform;
- advanced analytics and Power BI dashboards;
- data quality workflow;
- role-based permissions and audit trails;
- environment-separated ALM process;
- backup, monitoring, incident response, and support model;
- integration strategy for approved enterprise systems.

Future use cases should be expressed as configurable Sustainable Finance Unit operating domains, including programmes, projects, facilities, business processes, resources, activities, indicators, evidence, and institutional impact monitoring. Specific initiative examples should remain implied unless approved for inclusion in the final submission.

## Documentation Acceptance Criteria

The documentation pack is acceptable when:

- it explains the prototype clearly for technical and non-technical readers;
- it does not confuse current prototype capability with future product vision;
- beneficiary modeling and portal KPI visualisation are included;
- requirements map to architecture, testing, and traceability artifacts;
- known limitations and future work are explicit.
