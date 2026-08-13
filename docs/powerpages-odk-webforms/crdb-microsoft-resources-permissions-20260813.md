# CRDB Microsoft resources and permissions — scalable MEL platform

Date: 2026-08-13

## Purpose

This artifact explains which CRDB Microsoft ecosystem resources and permissions are required to move from the current TACATDP prototype to a scalable Sustainable Finance MEL Platform.

The current prototype proves the product direction. The scalable platform must leverage CRDB's Microsoft tenant infrastructure because CRDB policy requires the enterprise MEL platform to remain within the approved Microsoft ecosystem for identity, governance, integration, security, operations, and support. The enterprise question is therefore: which CRDB Microsoft resources, environments, roles, policies, and ALM controls are required to make this platform scalable and supportable?

## Up-front CRDB Microsoft tenant asks

Before the platform moves from prototype review to pilot or enterprise delivery, CRDB needs to identify the owners and grant paths for the following Microsoft resources:

| Area | Required CRDB Microsoft resource or decision | Why it is needed |
|---|---|---|
| Tenant ownership | Named Microsoft Entra tenant owner, Power Platform administrator, and environment owner | Prevents delivery from depending on a developer laptop, personal PAC profile, or unmanaged preview environment. |
| Environments | CRDB-owned development, test/UAT, and production Power Platform environments with Dataverse | Keeps development, review, and production data separated while supporting governed release management. |
| Identity and access | Microsoft Entra groups, Conditional Access/MFA policy, Power Pages site visibility access, portal contacts, external identities, web roles, and Dataverse security roles | Allows controlled access for MEL officers, reviewers, field collectors, administrators, reporting users, and external stakeholders where approved. |
| Application surface | CRDB-owned Power Pages site and approved Power Apps/admin surfaces in the intended environment | Hosts authenticated portal, field collection, review, and administration experiences under CRDB governance. |
| Dataverse | Dataverse database, solution publisher, custom tables, relationships, choices, auditing, security roles, teams, and application users | Provides the operational MEL record store for programme configuration, beneficiaries, forms, submissions, indicators, workflow, evidence metadata, and audit. |
| Web API and portal security | Power Pages Web API site settings, table permissions, page permissions, and CSRF-enabled browser access | Allows the portal to read and write Dataverse records safely through Power Pages security instead of unmanaged credentials. |
| Workflow and automation | Power Automate/cloud-flow ownership, connection references, service identities/application users, and approved notification mailbox or communication path | Supports assignments, invitations, verification, approvals, reporting projections, notifications, and integration workflows without personal accounts. |
| Integration | Approved Power Platform connectors, Dataverse APIs, Azure API Management, Logic Apps, Functions, or other Azure integration services inside the CRDB Microsoft tenant | Connects the MEL platform to CRDB systems and external datasets through governed Microsoft integration paths. |
| Reporting and analytics | Power BI workspace, semantic model ownership, refresh credentials, Fabric workspace/capacity decision, OneLake/Lakehouse/Warehouse path where approved | Supports management reporting, indicator facts, cross-system analysis, and future stakeholder reporting beyond portal demonstration charts. |
| Evidence and storage | Dataverse file columns, governed SharePoint/OneDrive for Business location, or approved Azure storage inside the Microsoft tenant | Stores photos, files, signatures, generated reports, and evidence metadata with retention and audit controls. |
| Governance and ALM | Managed Environments, DLP/data policies, solution pipelines/deployment pipelines, environment variables, connection references, release owner, rollback process, and audit monitoring | Makes delivery repeatable, reviewable, supportable, and compliant with CRDB operating controls. |

## Why this matters

The platform handles programme monitoring, beneficiary information, financing context, field evidence, submissions, audit trails, and reporting outputs. These are institutional data assets, not just UI screens.

Clear CRDB Microsoft ecosystem ownership matters because it controls:

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

The platform should therefore be researched and documented as a **Microsoft-ecosystem enterprise MEL workload**:

```text
CRDB Microsoft ecosystem
  -> Enterprise MEL workload
    -> Programme / scheme / product configuration
      -> Operational data, field observations, indicator results, evidence, reports, and learning actions
```

The working assumption for enterprise planning is:

- Microsoft Entra ID for identity and SSO.
- Power Platform environments for lifecycle separation.
- Dataverse as the operational MEL system of record where it fits.
- Power Pages as the authenticated portal surface for the current prototype and pilot path; any future UI change must remain inside CRDB's approved Microsoft ecosystem.
- Power Automate / Dataverse automation for workflow and integration orchestration where suitable.
- Power BI and Microsoft Fabric for enterprise analytics, semantic models, reporting, and cross-system data integration.
- Power Platform solutions, managed environments, DLP/data policies, and ALM for governance.

The approved platform boundary is the CRDB Microsoft tenant and approved Microsoft services. Research, planning, and implementation should stay inside that boundary.

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

## Microsoft ecosystem enterprise infrastructure view

The long-term system should be documented primarily inside the CRDB Microsoft ecosystem. Research and brainstorming should therefore focus on how to compose Power Platform, Dataverse, Power Pages, Power Automate, Power BI, Fabric, Entra ID, Azure integration services, security, and ALM into one enterprise MEL workload.

Recommended Microsoft-first enterprise infrastructure capabilities:

| Capability | Microsoft ecosystem resource | Enterprise MEL use |
|---|---|---|
| Identity and SSO | Microsoft Entra ID, Entra groups, Conditional Access, MFA | Single sign-on, named users, group-based administration, private-site access, and role assignment governance. |
| Environment strategy | Power Platform development, test/UAT, and production environments with Dataverse | Separates build, review, and production operations while keeping components in the same governed ecosystem. |
| Portal/application UI | Power Pages, custom pages/components, possible Power Apps/model-driven admin surfaces | Authenticated user portal, MEL officer workspace, field data entry, admin configuration, access-management surfaces. |
| Operational database | Dataverse tables, relationships, choices, alternate keys, auditing, security roles | Programme configuration, results framework, forms, submissions, beneficiary registry, indicators, workflow state, and audit. |
| Form runtime | Power Pages-hosted web forms/XForms runtime, Dataverse-stored form definitions and versions | Configurable field data collection without hard-coding TACATDP-specific forms into the application. |
| Workflow and automation | Power Automate, Dataverse plug-ins where approved, business process flows where useful | Assignment, onboarding, review, verification, notification, projection refresh, approval, and learning-action workflows. |
| Integration | Dataverse APIs, Power Platform connectors, Azure API Management, Azure Logic Apps or Azure Functions where approved | Governed ingestion from core banking, CRM, insurance, climate/GIS systems, and other CRDB systems without making MEL the system of record for those domains. |
| Evidence and documents | Dataverse file columns, SharePoint/OneDrive for Business where governed, Azure storage only if CRDB approves | Photos, files, signed documents, report outputs, evidence hashes, retention, and auditability. |
| Analytics and warehouse | Power BI, Microsoft Fabric, OneLake, Link to Fabric, Fabric Lakehouse/Warehouse, Synapse Link for Dataverse if selected | Enterprise reporting, medallion architecture, semantic models, cross-system analytics, indicator facts, and management dashboards. |
| Spatial and climate analytics | Dataverse location data, Power BI maps/Azure Maps where approved, Fabric geospatial processing where suitable | Region/district/ward coverage, farm/intervention locations, climate exposure overlays, and geographic performance analysis. |
| Governance and security | Managed Environments, DLP/data policies, Dataverse security roles, Power Pages web roles/table permissions, auditing | Least privilege, connector governance, environment control, private/public site control, and data-protection enforcement. |
| ALM and operations | Power Platform solutions, solution pipelines/deployment pipelines, environment variables, connection references, Azure DevOps/Git where approved | Repeatable delivery, approval gates, rollback, release notes, source control, and operational support. |
| Observability and support | Power Platform admin center, Power Pages diagnostics, Dataverse auditing, Power BI/Fabric monitoring, Microsoft Purview/Sentinel if CRDB uses them | Usage, health, audit, security monitoring, data lineage, incident response, and compliance reporting. |

The enterprise architecture exercise should therefore produce a Microsoft-resource and permission map up front so CRDB can confirm ownership, access, integration paths, and support responsibilities before the platform moves beyond prototype delivery. A standalone administrator-facing version is available in `crdb-microsoft-environment-permission-map-20260813.md`.

## Microsoft resource and permission map for environment setup

This map is intended for CRDB Microsoft 365, Power Platform, Dataverse, Power Pages, Power BI/Fabric, and security administrators. Its purpose is to make the development and production environments ready for controlled sharing without depending on personal developer access.

Microsoft guidance treats a Power Platform environment as the container for business data, apps, flows, and target audiences. Microsoft ALM guidance also recommends separate development and production environments, with at least one test environment for validation before production deployment. For this MEL platform, CRDB should therefore prepare at minimum:

```text
CRDB Microsoft tenant
  -> SFU MEL Development environment
  -> SFU MEL Test/UAT environment
  -> SFU MEL Production environment
```

### Administrator setup map

| Setup area | Development environment readiness | Production environment readiness | Minimum administrator permission or owner | Sharing gate before users are invited |
|---|---|---|---|---|
| Tenant governance | Confirm tenant policy allows approved administrators to create and manage required Power Platform environments. | Confirm production environment creation, governance, audit, backup, DLP, and support ownership. | Power Platform Administrator or Dynamics 365 Administrator at tenant level. | Named CRDB tenant/platform owner is recorded; environment creation is not tied to a personal developer account. |
| Environment provisioning | Create a CRDB-owned development environment with Dataverse and an agreed region, URL, currency, language, refresh cadence, and security group. | Create a CRDB-owned production environment with Dataverse, approved region, production naming, security group, capacity allocation, and no sample data. | Power Platform Administrator/Dynamics 365 Administrator; environment creator must have required license/capacity. | Environment IDs, URLs, type, region, security group, and owner are recorded in the deployment runbook. |
| Test/UAT environment | Create a separate test/UAT environment for solution import testing, app validation, permissions testing, and stakeholder review. | Production receives only validated managed solution releases from UAT. | Power Platform Administrator plus release owner. | UAT is available and can import the same solution version intended for production. |
| Environment access group | Assign a Microsoft Entra security group for development makers/admins. | Assign production access through separate Microsoft Entra groups for platform admins, MEL users, reviewers, reporting viewers, and support. | Entra administrator and Power Platform administrator. | No broad tenant-wide access; environment access is group-based and documented. |
| Dataverse administration | Assign System Administrator to approved platform admins; assign System Customizer to approved makers where schema changes are allowed. | Assign System Administrator only to production platform owners/support; users receive custom least-privilege roles. | Dataverse System Administrator in each target environment. | Tenant-level admin alone is not treated as Dataverse data access; Dataverse roles are explicitly assigned and verified. |
| Dataverse solution identity | Create CRDB solution publisher, solution unique name, prefixes, environment variables, and connection references. | Import managed solution; configure production environment variables and production-owned connections. | Solution owner/System Administrator; release owner for managed imports. | Solution is importable without editing unmanaged production components. |
| Dataverse business roles | Create development roles for administrators, makers, testers, and automation. | Create production roles such as `SFU MEL Platform Administrator`, `SFU MEL Manager`, `SFU MEL Officer`, `SFU Data Collector`, `SFU Data Reviewer`, `SFU Reporting Viewer`, and `SFU Automation Service`. | Dataverse System Administrator/security role owner. | Role-to-person/group matrix is approved before sharing. |
| Application/service identities | Create non-production application user or flow owner for development automation where needed. | Create production application user/service identity with least-privilege Dataverse role and owned connections. | Entra app/application owner, Dataverse System Administrator, Power Platform admin. | No production process depends on a personal user profile, temporary PAC auth, or personal mailbox. |
| Power Pages site | Create or bind the development Power Pages site to the development Dataverse environment. | Create or bind the production Power Pages site to the production Dataverse environment. | Power Pages admin/Website Owner plus environment Dataverse role. | Site ID, environment URL, and public/private visibility setting are recorded before sharing links. |
| Power Pages visibility | Keep development/test private and grant named preview users through site visibility access. | Decide production visibility and identity-provider approach before go-live. | Power Pages site owner/admin. | Private-site access is granted before invitation redemption/testing; public visibility is not enabled without CRDB approval. |
| Power Pages authentication | Configure approved Microsoft identity provider path for testers. | Configure approved production authentication path and sign-in policies. | Power Pages admin, Entra identity owner. | Successful sign-in is verified separately from Dataverse/portal role access. |
| Power Pages authorization | Configure web roles, page permissions, and table permissions for development testers. | Configure production web roles, page permissions, and least-privilege table permissions for all user groups. | Power Pages admin and Dataverse System Administrator. | Browser `/_api` read/write smoke tests pass for each shared role; anonymous Dataverse table access is not enabled for MEL data. |
| Power Pages Web API | Enable required table and field Web API site settings in development. | Enable only approved production table/field Web API settings. | Power Pages admin/System Administrator. | `/_api` calls use Power Pages authentication, table permissions, and CSRF; no client secrets or bearer tokens are placed in browser code. |
| Field collection runtime | Deploy the prototype web forms/XForms runtime against development Dataverse tables and assignments. | Deploy only validated runtime assets through the approved release path. | Power Pages admin/release owner. | Form assignments, submission create, saved-record read, and review paths work for test users. |
| Workflow and automation | Create development Power Automate flows/cloud-flow connections for onboarding, assignment, validation, projection refresh, and notification tests. | Create production-owned flows/connections with service identity or approved owner. | Flow owner, Power Platform admin, Dataverse System Administrator. | Flow ownership, connection references, retry/error handling, and audit path are documented. |
| DLP/data policies | Confirm development connectors are allowed by CRDB policy and do not mix business data with unapproved connectors. | Apply production DLP/data policy for Dataverse, Power Pages, Power Automate, Power BI/Fabric, SharePoint/OneDrive, Azure services, and approved connectors. | Power Platform Administrator for tenant policies; Environment Admin/System Administrator for scoped policies. | Required connectors are in the correct data group and blocked connectors are known before makers build flows/apps. |
| Reporting workspace | Create development Power BI workspace or report authoring workspace for prototype analytics. | Create production Power BI workspace, dataset/semantic model ownership, viewer groups, refresh owner, and certification path where applicable. | Power BI/Fabric workspace admin and reporting owner. | Reports are shared through workspace/app permissions, not file copies or personal workspaces. |
| Fabric/warehouse path | Decide whether development analytics use Dataverse direct query/export, Link to Fabric, Synapse Link, Lakehouse, or Warehouse. | Confirm production Fabric capacity/workspace, OneLake/Lakehouse/Warehouse ownership, data refresh, lineage, and retention if enterprise analytics is required. | Fabric administrator, Power BI admin, data platform owner. | Data movement path is approved before production reporting or cross-system analytics is promised. |
| Evidence/document storage | Test Dataverse file columns and governed SharePoint/OneDrive storage for evidence metadata and generated reports. | Configure production-approved evidence storage, retention, permissions, and audit. | Dataverse/System Administrator, SharePoint admin or approved storage owner. | Storage path supports photos/files/signatures/report outputs without exposing sensitive field evidence. |
| Integration services | Document development connectors/APIs for core banking, CRM, insurance, climate/GIS, or other CRDB systems. | Use approved Azure API Management, Logic Apps, Functions, Dataverse APIs, or Power Platform connectors inside the CRDB Microsoft tenant. | Integration owner, Azure owner, Power Platform admin, source-system owner. | Integration ownership, credentials, data classification, and failure handling are approved before connection. |
| Monitoring and audit | Enable development diagnostics and Dataverse/Power Pages audit evidence needed for testing. | Enable production audit, support ownership, Power Platform admin center monitoring, Power Pages diagnostics, Dataverse audit, Power BI/Fabric monitoring, and incident process. | Platform operations, security, compliance, and support owners. | Administrators can identify who changed data/configuration and when, and can support access incidents. |
| Backup and recovery | Confirm development backup/restore expectations and disposable-data policy. | Confirm production backup, restore, rollback, release recovery, and incident escalation. | Power Platform admin, Dataverse admin, operations owner. | Production sharing is blocked until backup/recovery ownership is documented. |
| Release and sharing | Share development only with named builders/testers after role, visibility, and Web API checks pass. | Share production only after managed solution import, permissions verification, security review, support ownership, and release approval. | Release owner, platform owner, Power Pages owner, Dataverse owner. | Sharing checklist is signed off by CRDB IT/platform owner and SFU product owner. |

### Minimum setup sequence for administrators

1. Confirm CRDB Microsoft tenant owner, Power Platform administrator, Dataverse administrator, Power Pages administrator, Power BI/Fabric administrator, security/compliance owner, and SFU product owner.
2. Provision development, test/UAT, and production Power Platform environments with Dataverse.
3. Assign environment security groups and Dataverse administrator roles.
4. Create the CRDB MEL solution publisher, solution, environment variables, connection references, and release ownership model.
5. Configure development Power Pages site, site visibility, authentication, web roles, page permissions, table permissions, and Web API site settings.
6. Configure development Dataverse roles, application users/service identities, and workflow owners.
7. Validate development sharing with named testers: sign-in, private-site visibility, invitation/external identity, web role, table permission, `/_api` read/write, form assignment, submission create, saved-record read, and dashboard/report read.
8. Create or confirm UAT environment and import the same managed solution intended for production.
9. Configure production DLP/data policies, production-owned connections, service identities, audit, backup/recovery, monitoring, and support ownership.
10. Import the managed solution into production, configure production environment variables/connections, verify Power Pages security, verify Dataverse least-privilege roles, verify reporting workspace permissions, and only then share production links.

### Environment readiness checklist

| Check | Development | Production |
|---|---|---|
| Environment exists with Dataverse | Required | Required |
| Environment owner recorded | Required | Required |
| Security group assigned | Required | Required |
| Dataverse System Administrator assigned to platform owner | Required | Required |
| Custom MEL roles created | Recommended for pilot | Required |
| Power Pages site created in same environment | Required | Required |
| Site visibility decision recorded | Required | Required |
| Test users granted private-site access where applicable | Required | Required before private preview |
| Web roles/page permissions/table permissions configured | Required | Required |
| Power Pages Web API enabled only for required tables/fields | Required | Required |
| Browser `/_api` smoke test passed | Required | Required |
| Power Automate/cloud-flow owner and connections recorded | Required if flows are used | Required if flows are used |
| DLP/data policy reviewed | Required | Required |
| Managed solution import tested | Required in UAT | Required |
| Production-owned service identity/application user configured | Optional for prototype | Required for automation |
| Power BI/Fabric workspace and owner recorded | Required if reporting is shared | Required if reporting is shared |
| Evidence/document storage owner recorded | Required if files are captured | Required if files are captured |
| Audit/monitoring/support owner recorded | Recommended | Required |
| Backup/recovery/rollback path documented | Recommended | Required |

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

## External systems and data ownership inside a Microsoft integration approach

The MEL platform should not become CRDB's core banking system, CRM, HR system, insurance system, or climate-data platform. Those systems remain authoritative for their domains.

The MEL platform should consume selected data through governed Microsoft integration services:

```text
Core banking / loan systems
CRM / customer systems
Insurance / guarantee systems
HR / branch structures
GIS / climate data
Field data collection
        -> Microsoft-governed integration layer
          -> Dataverse MEL operational data platform
            -> Fabric / Power BI analytics layer
              -> Dashboards, reports, and learning actions
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

## Microsoft platform layers for prototype, pilot, and enterprise delivery

| Layer | CRDB resource | Why it is needed |
|---|---|---|
| Tenant governance | Microsoft 365 / Entra tenant, Power Platform admin center, tenant policies | Controls who can create, administer, expose, and govern platform resources. |
| Environment strategy | Development, test/UAT, and production Power Platform environments with Dataverse | Separates development changes from user testing and production operation. |
| Dataverse | Custom tables, relationships, choices, alternate keys, security roles, teams, application users | Provides the system of record for forms, submissions, beneficiaries, indicators, audit, and reporting projections. |
| Power Pages | CRDB-owned site records, page/web-file metadata, site visibility, authentication, web roles, page permissions, table permissions, Web API settings | Hosts the field and review portal while enforcing Power Pages security over Dataverse access. |
| Power Automate / workflow | Environment-owned cloud flows or approved server-side processing | Processes onboarding, notifications, projection refresh, approvals, and integrations where browser-only logic is insufficient. |
| Reporting | Power BI workspace, Dataverse connector access, Fabric workspace/capacity where approved, semantic model ownership, refresh credentials | Supports management reporting and future stakeholder reporting without relying only on portal charts. |
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

## Minimum CRDB Microsoft resource request by delivery stage

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
- Production DLP policy change.
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

### For scalable production platform in the CRDB Microsoft ecosystem

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
- Fabric workspace/capacity decision if enterprise analytics, warehouse/lakehouse, OneLake, or Link to Fabric is used.
- Data integration ownership for core banking, CRM, insurance, climate/GIS, and other source systems.
- Certified semantic models and report ownership for CRDB/SFU reporting.
- Data retention, export, privacy, and stakeholder-publication rules.

Microsoft ecosystem research still needs to confirm:

- Power Pages fit for the expected portal UX, access model, and performance.
- Dataverse fit for operational MEL records, field evidence metadata, workflow, audit, and scale.
- Fabric/Power BI fit for warehouse, lakehouse, semantic model, indicator facts, and cross-system reporting.
- Power Automate/Dataverse automation fit for verification, notification, projection refresh, and approval workflows.
- Which approved Azure services inside the CRDB Microsoft tenant are needed for API management, integration, secrets, storage, monitoring, or scheduled processing.

## Permission checklist before continuing scalable work

Before moving beyond prototype UI refinement, confirm the Microsoft ecosystem owners:

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
- [ ] Whether Microsoft Fabric/Power BI workspaces and capacities are available for enterprise MEL analytics.
- [ ] Whether Azure integration services are approved for connecting non-Dataverse CRDB systems.

## Recommended architecture position

Use the current TACATDP prototype to prove workflow and stakeholder value, but document the scalable product as CRDB-owned Microsoft ecosystem resources:

```text
CRDB Microsoft Entra tenant
  -> Power Platform environment strategy
    -> Dataverse enterprise MEL operational model
      -> Programme configuration and results framework
      -> Indicator registry and indicator engine
      -> Beneficiary/party and intervention registries
      -> Field data collection and verification workflow
      -> Audit, access, workflow, and evidence metadata
    -> Power Pages / Power Apps user experiences
    -> Power Automate / Dataverse automation
    -> Fabric / Power BI analytics, warehouse, semantic models, reports
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
- Create and manage Power Platform environments: <https://learn.microsoft.com/en-us/power-platform/admin/create-environment>
- Power Platform ALM environment strategy: <https://learn.microsoft.com/en-us/power-platform/alm/environment-strategy-alm>
- Power Platform governance considerations: <https://learn.microsoft.com/en-us/power-platform/admin/governance-considerations>
- Power Platform data policy strategy: <https://learn.microsoft.com/en-us/power-platform/guidance/adoption/dlp-strategy>
- Manage data policies: <https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss>
- Power Pages solutions: <https://learn.microsoft.com/en-us/power-pages/configure/power-pages-solutions>
- Power Platform ALM overview: <https://learn.microsoft.com/en-us/power-platform/alm/overview-alm>
- Organize Power Platform solutions: <https://learn.microsoft.com/en-us/power-platform/alm/organize-solutions>
- Power Platform Well-Architected: <https://learn.microsoft.com/ga-ie/power-platform/well-architected/>
- Dataverse and Microsoft Fabric medallion architecture: <https://learn.microsoft.com/en-us/power-platform/architecture/reference-architectures/enterprise-data-fabric-dataverse>
- Link Dataverse to Microsoft Fabric: <https://learn.microsoft.com/en-us/power-apps/maker/data-platform/fabric-link-to-data-platform>
- Azure Synapse Link for Dataverse: <https://learn.microsoft.com/en-us/power-apps/maker/data-platform/azure-synapse-link-synapse>
- Microsoft Fabric storage options: <https://learn.microsoft.com/en-us/fabric/fundamentals/store-data>
- Microsoft Fabric lakehouse and warehouse decision guide: <https://learn.microsoft.com/en-us/fabric/fundamentals/decision-guide-lakehouse-warehouse>
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
