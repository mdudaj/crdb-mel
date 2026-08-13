# CRDB Microsoft resources and permissions — scalable MEL platform

Date: 2026-08-13

## Purpose

This artifact explains which CRDB Microsoft resources and permissions are required to move from the current TACATDP prototype to a scalable Sustainable Finance MEL Platform.

The current prototype proves the product direction. A scalable platform needs a governed Microsoft resource model so CRDB can own, secure, operate, audit, and extend the system without depending on one developer profile, one temporary environment, or ad hoc permission fixes.

## Why this matters

The platform handles programme monitoring, beneficiary information, financing context, field evidence, submissions, audit trails, and reporting outputs. These are institutional data assets, not just UI screens.

Clear CRDB Microsoft resource ownership matters because it controls:

1. **Data protection** — Dataverse records, field evidence, user identities, and reporting outputs must be protected by least-privilege roles.
2. **Operational continuity** — the platform must not depend on one individual's laptop, PAC profile, tenant account, or developer environment.
3. **Environment correctness** — Power Pages, Dataverse schema, Power Automate flows, and Power BI reports must live in the intended CRDB environment, not a mismatched tenant or preview environment.
4. **Access troubleshooting** — Power Pages private-site access, invitation redemption, external identity binding, web roles, table permissions, and Dataverse roles are separate gates.
5. **ALM and auditability** — solutions, environment variables, managed deployments, and release records are needed so CRDB can review, approve, import, roll back, and support changes.
6. **Future scalability** — multi-programme MEL needs stable environments, groups, service identities, DLP/data policies, reporting workspaces, and clear ownership before more modules are added.

## Current prototype state

The active implementation path is:

- Power Pages hosted Vue SPA.
- ODK Web Forms / XForms runtime for field collection.
- Dataverse tables for forms, assignments, submissions, submission versions, attachments, reporting projections, onboarding, and access audit.
- Power Pages `/_api` for browser-to-Dataverse access.
- ECharts dashboard with demonstration TACATDP data for visualisation.
- Mshirika as the current preview environment for latest UI review.
- CRDB as the intended client environment, with access and deployment verification handled separately.

The current prototype can continue as a proof-of-concept, but scalable delivery needs CRDB-owned environments, roles, identities, policies, and ALM.

## Microsoft platform layers

| Layer | CRDB resource | Why it is needed |
|---|---|---|
| Tenant governance | Microsoft 365 / Entra tenant, Power Platform admin center, tenant policies | Controls who can create, administer, expose, and govern platform resources. |
| Environment strategy | Development, test/UAT, and production Power Platform environments with Dataverse | Separates development changes from user testing and production operation. |
| Dataverse | Custom tables, relationships, choices, alternate keys, security roles, teams, application users | Provides the system of record for forms, submissions, beneficiaries, indicators, audit, and reporting projections. |
| Power Pages | CRDB-owned site records, page/web-file metadata, site visibility, authentication, web roles, page permissions, table permissions, Web API settings | Hosts the field and review portal while enforcing Power Pages security over Dataverse access. |
| Power Automate / workflow | Environment-owned cloud flows or approved server-side processing | Processes onboarding, notifications, projection refresh, approvals, and integrations where browser-only logic is insufficient. |
| Reporting | Power BI workspace, Dataverse connector access, report ownership, refresh credentials, future Fabric/Synapse boundary if approved | Supports management reporting and future stakeholder reporting without relying only on portal charts. |
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

## Minimum CRDB resource request

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

### For scalable production platform

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

Use the current TACATDP prototype to prove workflow and stakeholder value, but document the scalable product as CRDB-owned Microsoft resources:

```text
CRDB Microsoft Entra tenant
  -> Power Platform environment strategy
    -> Dataverse solution and security roles
    -> Power Pages site and portal security
    -> Power Automate/server-side processing
    -> Power BI reporting workspace
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
