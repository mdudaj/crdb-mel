# CRDB development environment sharing map

Date: 2026-08-13

## Purpose

This document lists the minimum CRDB Microsoft resources and permissions required to create a development environment where the delivery team can build the Sustainable Finance MEL Platform and the Sustainable Finance Unit can review it continuously.

This is a development-environment request only. It does not request production go-live, production data access, or production deployment.

## Immediate outcome needed

CRDB should provide one governed development environment that allows:

- the delivery team to import/build the Power Platform solution;
- the Power Pages prototype to run against Dataverse in the same environment;
- SFU reviewers to sign in and review the portal without repeated access blockers;
- development changes to be validated before later UAT or production handover;
- access, table permissions, form assignments, submissions, dashboards, and reports to be tested with named users.

## Development environment baseline

| Required item | Recommended value for development review |
|---|---|
| Environment type | Power Platform development or sandbox environment with Dataverse |
| Environment owner | Named CRDB Power Platform/platform owner |
| Security boundary | Microsoft Entra security group for approved makers, testers, SFU reviewers, and admins |
| Application host | CRDB-owned Power Pages site in the same Dataverse environment |
| Operational data store | Dataverse |
| Development sharing model | Named users/groups only; private site access if the site is private |
| Deployment model | Solution-based development with documented environment variables and connection references |
| Review users | Named SFU reviewers with site visibility, Power Pages identity, web role, and Dataverse/table-permission path |

## Key capability, resource, use, and permission map

| App capability | Microsoft ecosystem resource | Enterprise MEL use | Permissions to enable for development sharing |
|---|---|---|---|
| Development workspace | Power Platform development or sandbox environment with Dataverse | Gives the delivery team a CRDB-owned place to build, import, test, and share the MEL prototype without relying on personal/developer trial environments. | Power Platform Administrator or Dynamics 365 Administrator creates environment; assign environment security group; assign Dataverse System Administrator to named platform owner; assign Environment Maker/System Customizer to approved makers if schema and solution changes are allowed. |
| Environment access control | Microsoft Entra security group linked to the environment | Controls who can enter the development environment and access its apps, flows, Dataverse resources, and maker tools. | Entra admin creates/maintains group; Power Platform admin assigns group to environment; add delivery users, SFU reviewers, and admin/support users explicitly. |
| Solution delivery | Power Platform solution, publisher, environment variables, connection references | Allows repeatable delivery of Dataverse tables, Power Pages components, flows, and configuration between development, UAT, and later production. | Dataverse System Administrator or System Customizer for solution build; release owner can import/export solutions; connection owners can authorize required development connections. |
| Portal hosting | Power Pages site in the same development environment | Hosts the SFU MEL portal for dashboard review, field-form review, data submission, saved records, beneficiary review, and access testing. | Power Pages site owner/admin; environment Dataverse role sufficient to manage site; ability to configure site visibility, authentication, web roles, page permissions, table permissions, and Web API site settings. |
| Continuous SFU review access | Power Pages site visibility and Microsoft sign-in | Allows SFU reviewers to open the development portal repeatedly without the “successful sign-in but no access” blocker. | If private, grant site visibility access to named SFU Microsoft users; configure approved Microsoft identity provider path; create/link Power Pages Contact/external identity through invitation or approved identity flow; do not rely only on successful Microsoft sign-in. |
| Portal role-based access | Power Pages web roles, page permissions, and table permissions | Controls what SFU reviewers, MEL officers, data collectors, reviewers, and administrators can see or do in the portal. | Create development web roles such as `SFU MEL Reviewer`, `SFU MEL Officer`, `SFU Data Collector`, and `SFU Platform Admin`; assign contacts/users to roles; configure page permissions; configure table permissions with least privilege for each portal function. |
| Dataverse operational model | Dataverse tables, relationships, choices, alternate keys, audit settings | Stores programme configuration, forms, assignments, submissions, submission versions, beneficiaries, indicators, dashboard projections, and access audit records. | Dataverse System Administrator/System Customizer for schema work; custom least-privilege roles for SFU reviewers and testers; enable auditing for relevant tables if review/audit evidence is required. |
| Browser-to-Dataverse access | Power Pages Web API `/_api` site settings | Allows the hosted portal to read and write Dataverse data using Power Pages authentication, web roles, table permissions, and CSRF protection. | Power Pages admin/System Administrator enables Web API table and field site settings only for required development tables/fields; configure table permissions first; verify authenticated `/_api` read/write with named users. |
| Field data collection | Power Pages-hosted web forms/XForms runtime and Dataverse form/submission tables | Allows reviewers to test baseline data collection, assignment-based form access, draft/submit behavior, saved records, and submission review paths. | Portal reviewer/collector web role; read access to project/form/form-version/assignment records; create access for submissions/submission versions where applicable; append/append-to permissions for lookup associations; no anonymous submission access. |
| Beneficiary and monitored entity review | Dataverse beneficiary/party/intervention tables and portal routes | Allows SFU to review beneficiary identity, programme participation, intervention context, and monitoring records as the model matures. | Development Dataverse roles for read/review; Power Pages table permissions for portal read paths; write/edit only for approved development admin roles; keep schema writes limited to approved makers. |
| Dashboard and KPI review | Power Pages portal dashboard, Dataverse reporting projection tables, ECharts prototype visuals | Allows SFU to continuously review operational KPIs, TACATDP prototype visuals, regional map, submissions, and MEL readiness. | Power Pages read permissions to reporting/projection tables; Dataverse read roles for reviewers; explicit label that prototype figures are demonstration data unless sourced from approved records. |
| Reporting proof | Power BI workspace or development reporting workspace, Dataverse connector, optional Fabric path | Allows SFU and BI/reporting owners to review whether portal dashboards and future reports align with CRDB reporting expectations. | Power BI workspace Admin/Member for report authors; Viewer for SFU consumers; Dataverse read access for reporting identity; refresh credential owned by CRDB, not a personal developer profile. |
| Workflow automation | Power Automate flows, Dataverse triggers/actions, connection references | Supports invitations, assignments, notifications, review state changes, projection refresh, and access audit flows during development. | Flow owner or service account approved by CRDB; environment permissions to create/edit flows; Dataverse role with least privilege for tables/actions used by the flow; connection references documented. |
| Notification and invitation testing | Power Automate, Dataverse invitation records, approved mailbox/connector where used | Allows SFU reviewers and test users to receive access/invitation notifications without ad hoc personal sender dependencies. | Approved development mailbox or connector owner; flow connection owner; Power Pages invitation/contact permissions if invitations are used; record invitation state and external identity after redemption. |
| Evidence and attachments | Dataverse file columns, notes, SharePoint/OneDrive for Business, or approved Azure storage inside CRDB tenant | Allows development testing of photos, files, signed forms, generated reports, and evidence metadata. | Dataverse file/table permissions for metadata; storage owner permissions if SharePoint/OneDrive/Azure storage is used; restrict evidence access to named reviewer/admin roles; do not expose sensitive evidence anonymously. |
| Integration proof | Dataverse APIs, approved Power Platform connectors, Azure API Management/Logic Apps/Functions inside CRDB Microsoft tenant if needed | Allows development validation of future integration paths to CRDB systems or external datasets without placing credentials in the portal. | Integration owner approval; connector allowed by DLP policy; service identity or named connection owner; no secrets in browser code or committed source. |
| DLP and connector governance | Power Platform data policies | Ensures development apps and flows use approved connectors and do not mix business data with unapproved services. | Power Platform Administrator reviews/sets DLP policy; required connectors placed in appropriate data group; blocked connectors documented before flow/app build. |
| Development diagnostics | Power Platform admin center, Power Pages diagnostics, Dataverse audit, browser/runtime smoke checks | Helps diagnose access blockers, missing table permissions, stale site cache, failed submissions, and API errors during continuous SFU review. | Platform admin/support owner can inspect environment health, Power Pages site state, Dataverse audit, and relevant flow runs; browser smoke checks are run after every permission or site-setting change. |
| Backup and recovery expectation | Power Platform environment backup/restore and solution export | Allows the team to recover from development mistakes and preserve reviewable releases. | Power Platform admin owns backup/restore policy; release owner exports solution versions; development data retention expectations are documented. |
| Sharing gate | Named CRDB/SFU user list, Entra group, Power Pages site visibility, web roles, Dataverse roles, and smoke-test evidence | Defines when the development environment is ready for SFU review. | Share only after named users can sign in, pass private-site visibility if applicable, hold correct web roles/table permissions, and complete dashboard/read, form assignment/read, submission/create, saved-record/read checks. |

## Minimum permissions to request now

### For CRDB administrators

- Power Platform Administrator or Dynamics 365 Administrator to create/manage the development environment.
- Ability to create a Dataverse-backed development/sandbox environment.
- Ability to assign a Microsoft Entra security group to the environment.
- Ability to assign Dataverse System Administrator to the named CRDB platform owner.
- Ability to create/manage the Power Pages site in the same environment.
- Ability to configure Power Pages site visibility, authentication, web roles, page permissions, table permissions, and Web API site settings.
- Ability to review or set development DLP/data policies for required connectors.

### For delivery team makers

- Environment Maker where app/flow creation is expected.
- System Customizer or approved maker role where solution/schema work is expected.
- Power Pages maker/admin access for the development site, if the team is expected to update the portal source.
- Permission to import/export unmanaged development solution artifacts.
- Access to development connection references required for Dataverse, Power Pages, Power Automate, and reporting proof.

### For SFU reviewers

- Microsoft Entra account or approved identity path.
- Environment access through the agreed security group where required.
- Power Pages private-site visibility access if the site is private.
- Power Pages Contact/external identity after invitation or approved sign-in flow.
- Power Pages web role for reviewer access.
- Dataverse/table-permission path that allows portal reads for dashboards, assignments, saved records, and reporting views.
- No maker/admin permissions unless a reviewer is explicitly acting as a platform admin.

## Development sharing readiness checklist

| Check | Required before sharing with SFU? |
|---|---|
| Development environment exists in CRDB Microsoft tenant | Yes |
| Environment has Dataverse | Yes |
| Environment owner and support contact are named | Yes |
| Security group controls environment access | Yes |
| Delivery team maker/admin permissions are assigned | Yes |
| Power Pages site exists in the same environment | Yes |
| Site visibility decision is recorded | Yes |
| Named SFU reviewers have private-site visibility access if needed | Yes |
| Authentication path is configured and tested | Yes |
| Power Pages contacts/external identities are created/verified for reviewers | Yes |
| Web roles are assigned to reviewer contacts/users | Yes |
| Page permissions are configured | Yes |
| Table permissions are configured for required tables | Yes |
| Power Pages Web API site settings are enabled only for required tables/fields | Yes |
| Browser `/_api` read test passes for reviewer role | Yes |
| Browser submission/create test passes for collector/tester role where applicable | Yes |
| Saved-record read test passes | Yes |
| Dashboard/report read path works | Yes |
| DLP/data policy allows required development connectors | Yes |
| Flow owners/connections are documented if flows are used | Yes |
| No client secrets or bearer tokens are stored in portal code | Yes |
| Development support/escalation owner is named | Yes |

## What CRDB can share back to the delivery team

To unblock delivery and continuous SFU review, CRDB can provide:

1. Development environment display name and environment URL.
2. Power Pages site name, website ID, and public/private visibility state.
3. Names/emails of platform owners, site admins, Dataverse admins, and SFU reviewers.
4. Confirmation of which account/group should be used for maker access.
5. Confirmation of whether the site will remain private during review.
6. Confirmation that required SFU reviewers have site visibility access if private.
7. Confirmation of allowed connectors under the development DLP policy.
8. Confirmation of whether Power BI/Fabric proof is required in this development phase.

Do not share secrets, passwords, API keys, connection strings, or private key material in this document or chat.

## Non-goals

This document does not request:

- production environment access;
- production deployment;
- production data migration;
- production DLP policy change;
- broad tenant administrator access for all makers;
- anonymous Dataverse table access;
- bypassing Power Pages table permissions;
- storing client secrets in browser code.

## Official Microsoft references checked

- Create and manage Power Platform environments: <https://learn.microsoft.com/en-us/power-platform/admin/create-environment>
- Dataverse role-based security roles: <https://learn.microsoft.com/en-us/power-platform/admin/database-security>
- Power Pages security overview: <https://learn.microsoft.com/en-us/power-pages/security/power-pages-security>
- Power Pages table permissions: <https://learn.microsoft.com/en-us/power-pages/security/assign-table-permissions>
- Manage Power Platform data policies: <https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss>
