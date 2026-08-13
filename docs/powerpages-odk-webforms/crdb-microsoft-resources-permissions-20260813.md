# CRDB Microsoft resources and permissions — scalable MEL platform

Date: 2026-08-13

## Purpose

This artifact explains which CRDB Microsoft resources and permissions are required to move from the current TACATDP prototype to a scalable Sustainable Finance MEL Platform.

The current prototype proves the product direction. A scalable platform needs a governed resource, infrastructure, and permission model so CRDB can own, secure, operate, audit, and extend the system without depending on one developer profile, one temporary environment, or ad hoc permission fixes.

## Why this matters

The platform handles programme monitoring, beneficiary information, financing context, field evidence, submissions, audit trails, and reporting outputs. These are institutional data assets, not just UI screens.

Clear CRDB Microsoft resource ownership matters because it controls:

1. **Data protection** — Dataverse records, field evidence, user identities, and reporting outputs must be protected by least-privilege roles.
2. **Operational continuity** — the platform must not depend on one individual's laptop, PAC profile, tenant account, or developer environment.
3. **Environment correctness** — Power Pages, Dataverse schema, Power Automate flows, and Power BI reports must live in the intended CRDB environment, not a mismatched tenant or preview environment.
4. **Access troubleshooting** — Power Pages private-site access, invitation redemption, external identity binding, web roles, table permissions, and Dataverse roles are separate gates.
5. **ALM and auditability** — solutions, environment variables, managed deployments, and release records are needed so CRDB can review, approve, import, roll back, and support changes.
6. **Future scalability** — multi-programme MEL needs stable environments, groups, service identities, DLP/data policies, reporting workspaces, and clear ownership before more modules are added.

## Architecture position

The target should be treated as a **CRDB Enterprise Monitoring, Evaluation and Learning Information System**. TACATDP is the first configured programme, not the permanent application boundary.

The central design rule is:

> Configure the MEL framework for each programme; do not hard-code the programme into the software.

This matters because CRDB may later need to monitor sustainable finance programmes, guarantee facilities, insurance-linked products, ESG initiatives, donor-funded programmes, lending schemes, customer segments, branches, or normal bank operations. Each may have different beneficiaries, indicators, reporting frequencies, evidence rules, workflows, and stakeholders.

The platform should therefore separate:

```text
CRDB Enterprise MEL Platform
  -> Programme / scheme / product configuration
    -> Operational data, field observations, indicator results, evidence, reports, and learning actions
```

## Enterprise MEL architecture layers

| Layer | Purpose | Examples |
|---|---|---|
| Programme configuration | Defines each programme without code changes. | Programme, scheme, component, outcome, output, activity, reporting period. |
| Results framework | Represents the logic model/logframe. | Outcomes, outputs, activities, targets, milestones, means of verification. |
| Indicator registry | Stores KPI definitions as metadata. | Code, name, unit, numerator, denominator, formula, baseline, target, frequency, disaggregation, source, verification method. |
| Beneficiary and party registry | Gives CRDB a reusable impact-subject model. | Person, organisation, group, cooperative, AMCOS, SACCOS, SME, institution. |
| Intervention registry | Defines financed/support activities. | Climate-smart practices, eligible products, evidence rules, expected benefits, applicable indicators. |
| Field data collection | Captures baseline, monitoring, follow-up, and evaluation data. | Web forms/XForms runtime, mobile/browser collection, GPS, photos, timestamps, signatures, attachments, validation rules. |
| Data quality and verification | Prevents raw submissions from becoming official results without review. | Automated validation, duplicate checks, range checks, location checks, supervisor review, approval. |
| Monitoring schedule | Manages periodic follow-up. | Baseline, post-disbursement, quarterly, seasonal, annual, midline, endline. |
| Indicator engine | Computes reusable indicator facts outside dashboards. | Aggregation, disaggregation, formula execution, baseline/current/target comparison. |
| Evaluation management | Supports structured evaluations beyond routine monitoring. | Evaluation questions, sampling, baseline/midline/endline, findings, recommendations. |
| Learning and action tracking | Turns evidence into management action. | Finding, lesson, recommendation, response, action, owner, deadline, status. |
| GIS and climate analytics | Treats geography as core MEL data. | Country, region, district, ward, village, farm/intervention geometry, climate exposure overlays. |
| Reporting templates | Generates repeatable stakeholder reports. | CRDB internal reports, GCF reports, government reports, PDF/Excel/Power BI outputs. |
| Integration layer | Consumes selected data from authoritative systems. | Core banking, CRM, loan systems, insurance, HR, climate platforms, GIS data, external datasets. |
| Audit and compliance | Preserves defensible lineage. | User activity, data edits, approval history, indicator lineage, report generation history. |

## Enterprise infrastructure view

The Microsoft prototype path is a valid near-term delivery path, but the long-term enterprise system should be documented independently of a single product stack. CRDB architecture should decide the final deployment standards.

Recommended enterprise infrastructure capabilities:

| Capability | Microsoft-first option | Enterprise/long-term option to evaluate |
|---|---|---|
| Identity and SSO | Microsoft Entra ID, Power Pages authentication, Dataverse users/contacts | CRDB enterprise IdP federation and bank-wide access governance. |
| Portal/application UI | Power Pages hosted portal for prototype and Microsoft-managed pilot | Bank-approved web/mobile portal stack if Power Pages cannot meet scale, UX, integration, or governance needs. |
| Form runtime | Web forms/XForms runtime hosted in the portal | Dedicated form/assessment engine supporting offline mobile, browser, versioning, GPS, media, signatures, and multilingual forms. |
| Operational database | Dataverse for Microsoft-managed prototype and pilot | PostgreSQL/PostGIS or another CRDB-approved operational database if enterprise scale/spatial needs exceed Dataverse fit. |
| Spatial data | Dataverse location fields and GeoJSON visualisation for prototype | PostGIS-backed spatial model for country/region/district/ward/village/farm/intervention analytics. |
| Workflow | Power Automate / Dataverse automation | Dedicated workflow engine for configurable review, approval, data quality, and learning-action processes. |
| Integration | Power Platform connectors / Dataverse APIs | API gateway, integration services, queues, and controlled ingestion from core banking, CRM, insurance, climate, and GIS systems. |
| Async processing | Power Automate / plug-ins where approved | Queue and worker architecture for indicator computation, ingestion, report generation, and scheduled jobs. |
| Object/evidence storage | Dataverse file columns or approved Microsoft storage | CRDB-approved object storage for photos, files, evidence, hashes, retention, and audit. |
| Analytics | Power BI over Dataverse/reporting projections | Dimensional warehouse/lakehouse when data volume, history, refresh, and cross-system analytics require it. |
| Observability | Power Platform admin center, Dataverse auditing, Power BI monitoring | Central logs, metrics, tracing, SIEM integration, alerting, and operational dashboards. |
| ALM | Power Platform solutions, environment variables, managed imports | Bank release pipeline with CI/CD, approvals, rollback, environment promotion, and change records. |

The current repository documents the Microsoft-first path. The enterprise architecture exercise should next decide whether production remains fully Microsoft-managed or moves selected layers to CRDB-approved enterprise infrastructure.

## Core enterprise domain model

The long-term data model should be metadata-driven:

```text
Programme
  -> Results Framework
    -> Outcome / Output / Activity
      -> Indicator Definition
        -> Target
        -> Measurement / Observation
          -> Evidence
          -> Verification
          -> Indicator Result
```

Recommended reusable entity groups:

| Group | Candidate entities |
|---|---|
| Configuration | Organisation, Programme, Scheme, Product, ProgrammeComponent, ResultFramework, Outcome, Output, Activity, Indicator, IndicatorTarget, ReportingPeriod. |
| Parties and beneficiaries | Party, Person, Organisation, Group, Beneficiary, BeneficiaryProgrammeParticipation, AccountReference, LoanReference, Facility, Guarantee, Insurance. |
| Interventions | Intervention, InterventionCategory, EligibilityCriteria, ClimateRationale, ExpectedBenefit, EvidenceRequirement, VerificationMethodology. |
| Collection | Form, FormVersion, Section, Question, Constraint, SkipLogic, Calculation, Assignment, Submission, SubmissionVersion, Attachment. |
| MEL evidence | Observation, Measurement, Assessment, IndicatorValue, Evidence, Verification, Evaluation, Feedback, Learning, Action. |
| Geography | Country, Region, District, Ward, Village, Site/Farm/Facility, Geometry, ClimateExposure. |
| Reporting | ReportTemplate, ReportSection, ReportPeriod, ReportRun, GeneratedReport, DashboardDefinition. |
| Security/audit | User, Role, AccessScope, AuditEvent, DataChangeLog, ConsentRecord, PrivacyClassification. |

The key separation is:

- indicator definitions are metadata;
- observations are raw or reviewed measurements;
- indicator results are computed facts;
- dashboards and reports consume computed results, not raw submissions directly.

## Enterprise functional modules

The scalable product should be documented around reusable modules:

1. Programme Management
2. Results Framework
3. Indicator Registry
4. Beneficiary / Party Registry
5. Product and Intervention Registry
6. Questionnaire and Assessment Designer
7. Field Data Collection
8. Monitoring Plans
9. Data Quality and Verification
10. Indicator Calculation
11. Evaluation Management
12. GIS and Climate Monitoring
13. Feedback and Grievances
14. Learning and Action Tracking
15. Dashboards and Analytics
16. Reports and Reporting Templates
17. Integration Management
18. Document and Evidence Repository
19. Users, Roles, and Access
20. Audit and Compliance
21. System Administration

This is broader than the current prototype. It should guide the future product vision and client discussion, not silently expand the current prototype scope.

## External systems and data ownership

The MEL platform should not become CRDB's core banking system, CRM, HR system, insurance system, or climate-data platform. Those systems remain authoritative for their domains.

The MEL platform should consume selected data through governed integration:

```text
Core banking / loan systems
CRM / customer systems
Insurance / guarantee systems
HR / branch structures
GIS / climate data
Field data collection
        -> Integration layer
          -> MEL operational data platform
            -> Data quality / indicator engine
              -> Analytics, dashboards, reports, and learning actions
```

This reduces duplication, reconciliation problems, and unclear ownership.

## Security, privacy, and regulatory posture

Security and privacy must be foundational for a bank-wide MEL platform.

Minimum controls to design for:

- TLS in transit.
- Encryption at rest.
- Secrets management.
- MFA / enterprise SSO.
- RBAC and scoped access by programme, organisation, branch, region, dataset, and function.
- Row-level and field-level access where sensitive data requires it.
- Audit logging and immutable security events.
- Consent management where personal data collection requires it.
- Data classification and PII masking.
- Data retention and disposal rules.
- Backup and disaster recovery.
- Security monitoring and incident response.
- Report/export approval controls.

Current external reference points:

- GCF uses results-based management and the IRMF establishes a results architecture and measurement/reporting approach for projects/programmes and portfolio-level assessment.
- Tanzania's Personal Data Protection Act No. 11 of 2022 establishes minimum requirements for collection and processing of personal data and establishes the Personal Data Protection Commission.
- PDPC publishes 2023 personal data protection regulations, including personal data collection and processing regulations.
- CRDB's privacy notice states that the bank is committed to protecting personal information and explains collection, use, sharing, protection, and rights.
- Bank of Tanzania maintains current acts, regulations, circulars, and guidelines for supervised financial institutions, including recent sustainability- and climate-related guidelines.

The final control matrix must be reviewed by CRDB legal, risk, compliance, IT security, and enterprise architecture teams before production deployment.

## Current prototype state

The active implementation path is:

- Power Pages hosted Vue SPA.
- Web forms/XForms runtime for field data collection.
- Dataverse tables for forms, assignments, submissions, submission versions, attachments, reporting projections, onboarding, and access audit.
- Power Pages `/_api` for browser-to-Dataverse access.
- ECharts dashboard with demonstration TACATDP data for visualisation.
- Mshirika as the current preview environment for latest UI review.
- CRDB as the intended client environment, with access and deployment verification handled separately.

The current prototype can continue as a proof-of-concept, but scalable delivery needs CRDB-owned environments, roles, identities, policies, and ALM.

## Microsoft platform layers for the current delivery path

| Layer | CRDB resource | Why it is needed |
|---|---|---|
| Tenant governance | Microsoft 365 / Entra tenant, Power Platform admin center, tenant policies | Controls who can create, administer, expose, and govern platform resources. |
| Environment strategy | Development, test/UAT, and production Power Platform environments with Dataverse | Separates development changes from user testing and production operation. |
| Dataverse | Custom tables, relationships, choices, alternate keys, security roles, teams, application users | Provides the system of record for forms, submissions, beneficiaries, indicators, audit, and reporting projections. |
| Power Pages | CRDB-owned site records, page/web-file metadata, site visibility, authentication, web roles, page permissions, table permissions, Web API settings | Hosts the field and review portal while enforcing Power Pages security over Dataverse access. |
| Power Automate / workflow | Environment-owned cloud flows or approved server-side processing | Processes onboarding, notifications, projection refresh, approvals, and integrations where browser-only logic is insufficient. |
| Reporting | Power BI workspace, Dataverse connector access, report ownership, refresh credentials, future warehouse/Fabric boundary if approved | Supports management reporting and future stakeholder reporting without relying only on portal charts. |
| ALM | Power Platform solution, publisher, connection references, environment variables, managed solution import path | Makes deployments repeatable, reviewable, and recoverable. |
| Security and compliance | DLP/data policies, connector allow/deny rules, audit settings, retention/export policy, environment backup policy | Prevents accidental data exposure and controls which systems can exchange business data. |

## Required roles and permissions

### 1. Tenant and platform administration

| Need | Recommended CRDB owner | Minimum permission |
|---|---|---|
| Govern Power Platform environments and policies | CRDB IT / Power Platform admin team | Power Platform administrator or Dynamics 365 administrator at tenant level where applicable. |
| Create/manage data policies and connector governance | CRDB IT governance | Power Platform administrator for tenant policies, or Environment Admin/System Administrator for scoped environment policies. |
| Delegate site visibility governance | CRDB Power Platform admin | Permission to manage Power Pages site visibility and non-production public-access governance. |

Notes:

- Tenant-level admin roles do not automatically grant Dataverse data access inside an environment. Dataverse access still requires environment-level Dataverse security roles.
- DLP/data policy changes can affect apps and flows at design time and runtime, so connector decisions must be agreed before production hardening.

### 2. Environment administration

| Need | Recommended CRDB owner | Minimum permission |
|---|---|---|
| Manage the Dataverse-backed environment | CRDB platform admin / solution owner | System Administrator Dataverse security role in the target environment. |
| Customize schema and solution components | CRDB solution architect or approved maker | System Customizer or System Administrator, depending on change scope. |
| Build maker resources without full admin power | Approved CRDB makers | Environment Maker plus appropriate Dataverse roles where a database exists. |
| Run ALM import/export | CRDB release owner | Permission to import managed solutions and manage connection references/environment variables. |

Why this matters:

- Schema writes, table permissions, Web API settings, flows, and Power Pages metadata must target the same CRDB environment.
- A developer login that can preview a page might still lack permissions to import a solution, update Dataverse schema, configure site settings, or manage visibility.

### 3. Power Pages site administration

| Need | Recommended CRDB owner | Minimum permission |
|---|---|---|
| Own/manage the Power Pages site | CRDB platform owner | Power Pages website administration rights and required environment role. |
| Grant access to private non-production site | CRDB site owner/admin | Site visibility management permission. |
| Configure web roles, page permissions, and table permissions | CRDB Power Pages admin | Ability to edit Power Pages Security settings and Portal Management app components. |
| Configure Power Pages Web API site settings | CRDB Power Pages admin / System Administrator | Ability to create/update site settings and table permissions. |

Why this matters:

- A private Power Pages site can block a user before portal invitation or Dataverse assignment logic runs.
- Power Pages `/_api` access requires enabled Web API site settings, table permissions, web role association, and CSRF handling.
- Anonymous web role access to Dataverse tables should be avoided for MEL data unless a specific public reporting page is approved.

### 4. Dataverse security and data model

| Need | Recommended CRDB owner | Minimum permission |
|---|---|---|
| Create/update MEL schema | CRDB solution owner | System Administrator/System Customizer in the target environment, with approved solution context. |
| Access operational data | MEL officers, administrators, data reviewers | Custom least-privilege Dataverse security roles. |
| Access portal data through Power Pages | Portal contacts/users | Power Pages web roles plus table permissions. |
| Run server-side automation | Application user or flow owner | Dedicated least-privilege security role for only required tables/actions. |

Recommended custom roles for the scalable product:

- `SFU MEL Platform Administrator`
- `SFU MEL Manager`
- `SFU MEL Officer`
- `SFU Data Collector`
- `SFU Data Reviewer`
- `SFU Reporting Viewer`
- `SFU Automation Service`

These roles should be mapped to Microsoft Entra security groups where possible for operational administration, with Dataverse roles applied in the target environment.

### 5. Application/service identities

| Need | Recommended CRDB owner | Minimum permission |
|---|---|---|
| CI/CD or controlled ALM automation | CRDB IT / release manager | Approved service principal/application user with least-privilege Dataverse roles. |
| Projection refresh or server-side processor | CRDB platform operations | Dedicated application user or flow connection owner. |
| Email/invitation notification | CRDB approved mailbox or Dataverse-native notification path | Approved sender mailbox/flow connection, not a personal ad hoc mailbox. |

Why this matters:

- Production operations should not depend on a personal user profile.
- Service identities make ownership, audit, rotation, and support clearer.
- Email delivery and invitations require approved mailbox/connectivity; otherwise manual fallback must be documented.

### 6. Reporting resources

| Need | Recommended CRDB owner | Minimum permission |
|---|---|---|
| Power BI workspace | CRDB BI/reporting team | Workspace Admin/Member for report authors; Viewer for consumers. |
| Dataverse reporting access | CRDB BI service/user identity | Read access to reporting projection tables and approved source tables. |
| Refresh credentials | CRDB reporting operations | Governed credential/connection ownership, not a developer profile. |
| Future warehouse/Fabric path | CRDB architecture / BI governance | Separate approval and data-governance decision. |

Why this matters:

- Portal charts are useful for prototype review, but scalable MEL reporting needs governed datasets, refresh ownership, and audience permissions.
- Power BI embedding or warehouse integration should be treated as a future product decision, not an assumption in the prototype.

## Minimum CRDB Microsoft resource request

### For prototype review

Required:

- One CRDB-accessible Power Pages site or approved preview target.
- Named CRDB users granted private-site visibility if the site is private.
- Power Pages contacts/external identities/web roles for testers.
- Active form assignments for testers.
- Table permissions and Web API settings for read/submit/reporting paths.
- Confirmation of whether CRDB or Mshirika is the review authority for the current build.

Not required:

- Production environment.
- Production DLP exception.
- Power BI embedding.
- Full beneficiary master-data deployment.

### For CRDB pilot/handover

Required:

- CRDB-owned development and UAT/test environments with Dataverse.
- CRDB-owned Power Pages site in the intended environment.
- CRDB solution publisher and solution unique name.
- Named CRDB release owner and platform owner.
- System Administrator/System Customizer roles for approved platform maintainers.
- Custom Dataverse roles for MEL users.
- Power Pages web roles and table permissions reviewed by CRDB.
- DLP/data policy review for connectors used by portal, flows, and reporting.
- Approved service identity or application user for automation.
- Approved mailbox or notification mechanism if email delivery is required.
- Power BI workspace for reporting proof if Power BI is part of pilot acceptance.

### For scalable production platform on the Microsoft path

Required:

- Development, test/UAT, and production environment strategy.
- Managed solution ALM with release notes and rollback path.
- Environment variables and connection references for deployable configuration.
- Least-privilege Dataverse roles and group-based access model.
- Power Pages site visibility/public-access decision.
- Production table permissions, page permissions, and web roles.
- DLP/data policies and connector governance.
- Monitoring, audit, backup, support, incident, and change-management ownership.
- Reporting workspace/dataset ownership and refresh governance.
- Data retention, export, privacy, and stakeholder-publication rules.

Also required if CRDB chooses a non-Power-Pages or hybrid enterprise architecture:

- approved application hosting platform;
- approved operational database and spatial database;
- approved object/evidence storage;
- approved API gateway/integration layer;
- approved queue/worker platform;
- approved monitoring/logging/SIEM integration;
- approved backup, disaster recovery, and retention controls;
- approved DevSecOps pipeline and release governance.

## Permission checklist before continuing scalable work

Before moving beyond prototype UI refinement, confirm:

- [ ] Which CRDB environment is the future source of truth: development, UAT, or production.
- [ ] Which CRDB user or group owns the Power Pages site.
- [ ] Which CRDB user or group owns Dataverse solution imports.
- [ ] Which CRDB user or group owns table permissions and Power Pages Web API site settings.
- [ ] Which CRDB user or group owns Power Automate/cloud-flow connections.
- [ ] Which CRDB user or group owns Power BI workspace/reporting assets.
- [ ] Whether the non-production Power Pages site is private or allowed to be public.
- [ ] Which named reviewers need private-site visibility access.
- [ ] Which Dataverse roles are assigned to platform admins, MEL officers, collectors, reviewers, and reporting viewers.
- [ ] Whether DLP/data policies allow the required connectors.
- [ ] Whether any production deployment requires managed solution import rather than direct PAC page upload.

## Recommended architecture position

Use the current TACATDP prototype to prove workflow and stakeholder value, but document the scalable product as CRDB-owned resources:

```text
CRDB Microsoft Entra tenant
  -> Enterprise MEL platform governance
    -> Programme configuration and results framework
    -> Indicator registry and indicator engine
    -> Beneficiary/party and intervention registries
    -> Field data collection and verification workflow
    -> Operational database and evidence storage
    -> Integration layer and analytics warehouse
    -> Dashboards, reporting templates, learning actions
    -> ALM, DLP, audit, support, and release governance
```

This keeps TACATDP as the proof-of-concept project while positioning the Sustainable Finance MEL Platform as an extensible CRDB system.

## Official Microsoft references checked

- Power Pages site visibility: <https://learn.microsoft.com/en-us/power-pages/security/site-visibility>
- Control public access for non-production Power Pages sites: <https://learn.microsoft.com/en-us/power-pages/admin/site-visibility-governance>
- Power Pages security overview: <https://learn.microsoft.com/en-us/power-pages/security/power-pages-security>
- Power Pages Web API overview: <https://learn.microsoft.com/en-us/power-pages/configure/web-api-overview>
- Power Pages table permissions: <https://learn.microsoft.com/en-us/power-pages/security/assign-table-permissions>
- Roles required for Power Pages administration: <https://learn.microsoft.com/en-us/power-pages/admin/admin-roles>
- Dataverse role-based security roles: <https://learn.microsoft.com/en-us/power-platform/admin/database-security>
- Dataverse security roles and privileges: <https://learn.microsoft.com/en-us/power-platform/admin/security-roles-privileges>
- Power Platform governance considerations: <https://learn.microsoft.com/en-us/power-platform/admin/governance-considerations>
- Power Platform data policy strategy: <https://learn.microsoft.com/en-us/power-platform/guidance/adoption/dlp-strategy>
- Manage data policies: <https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss>
- Power Pages solutions: <https://learn.microsoft.com/en-us/power-pages/configure/power-pages-solutions>
- Power Platform ALM overview: <https://learn.microsoft.com/en-us/power-platform/alm/overview-alm>
- Organize Power Platform solutions: <https://learn.microsoft.com/en-us/power-platform/alm/organize-solutions>
- GCF results-based management: <https://www.greenclimate.fund/portfolio/results-based-management>
- GCF Integrated Results Management Framework: <https://www.greenclimate.fund/document/integrated-results-management-framework>
- Tanzania Personal Data Protection Act, 2022: <https://oagmis.oag.go.tz/portal/acts/237>
- PDPC regulations: <https://www.pdpc.go.tz/en/policies-legislations/regulations/>
- CRDB Privacy Notice: <https://crdbbank.co.tz/en/about-us/privacy-policy>
- Bank of Tanzania Acts, Regulations, Circulars, Guidelines: <https://www.bot.go.tz/Publications/Filter/38?lang=en>
- Bank of Tanzania Guidelines: <https://www.bot.go.tz/Publications/Filter/40>

## Non-goals

This artifact does not approve:

- Dataverse schema writes;
- Power Pages permission changes;
- site visibility changes;
- production deployment;
- DLP policy changes;
- service-principal creation;
- Power BI workspace creation.

Those actions require explicit CRDB/user approval and target confirmation.
