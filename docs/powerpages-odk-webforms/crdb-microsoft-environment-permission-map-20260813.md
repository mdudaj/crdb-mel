# CRDB Microsoft environment resource and permission map

Date: 2026-08-13

## Purpose

This document guides CRDB Microsoft 365, Power Platform, Dataverse, Power Pages, Power BI/Fabric, security, and Sustainable Finance Unit administrators to prepare the Microsoft tenant resources and permissions required to share the Sustainable Finance MEL Platform safely.

The platform must leverage CRDB's approved Microsoft tenant infrastructure. The goal is not to select another technology stack. The goal is to make the CRDB Microsoft environments ready for development review, UAT, pilot handover, and production sharing.

## Audience

- CRDB Microsoft tenant administrators
- Power Platform administrators
- Dataverse administrators
- Power Pages administrators
- Power BI/Fabric administrators
- Security, compliance, and DLP policy owners
- Integration/API administrators
- Sustainable Finance Unit product owners
- Release and support owners

## Required environment model

Microsoft guidance treats a Power Platform environment as the container for business data, apps, flows, and target audiences. Microsoft ALM guidance recommends separate development and production environments, with at least one test environment for validation before production deployment.

For this MEL platform, CRDB should prepare at minimum:

```text
CRDB Microsoft tenant
  -> SFU MEL Development environment
  -> SFU MEL Test/UAT environment
  -> SFU MEL Production environment
```

## Administrator setup map

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

## Minimum setup sequence for administrators

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

## Environment readiness checklist

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

## Sharing decision gates

Development sharing is ready only when:

- the development environment exists with Dataverse;
- the Power Pages site is in the same environment;
- named testers have site visibility access if the site is private;
- Dataverse roles, web roles, page permissions, table permissions, and Web API settings are configured;
- browser `/_api` read/write smoke tests pass for the expected tester roles;
- form assignment, submission create, saved-record read, and dashboard/report read paths pass.

Production sharing is ready only when:

- the production environment exists with Dataverse and is owned by CRDB;
- release is through managed solution import or another CRDB-approved ALM path;
- production service identities, owned connections, DLP/data policy, audit, monitoring, backup, and support ownership are documented;
- Power Pages authentication, site visibility, web roles, page permissions, table permissions, and Web API settings are verified;
- Power BI/Fabric workspace permissions and refresh ownership are verified if reporting is shared;
- CRDB IT/platform owner and Sustainable Finance Unit product owner approve sharing.

## Non-goals

This document does not approve or perform:

- Dataverse schema writes;
- Power Pages permission changes;
- site visibility changes;
- production deployment;
- DLP policy changes;
- service-principal creation;
- Power BI/Fabric workspace creation.

Those actions require explicit CRDB/user approval and target confirmation.

## Official Microsoft references checked

- Create and manage Power Platform environments: <https://learn.microsoft.com/en-us/power-platform/admin/create-environment>
- Power Platform ALM environment strategy: <https://learn.microsoft.com/en-us/power-platform/alm/environment-strategy-alm>
- Dataverse role-based security roles: <https://learn.microsoft.com/en-us/power-platform/admin/database-security>
- Power Pages security overview: <https://learn.microsoft.com/en-us/power-pages/security/power-pages-security>
- Manage Power Platform data policies: <https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss>
