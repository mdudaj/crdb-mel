# User & Access Permission Matrix - 2026-07-21

Status: proposed, review-ready.

## Purpose

Map TACATDP business roles to the Dataverse and Power Pages permissions needed for the User & Access workflow. This is a planning artifact only; it does not grant privileges in Dataverse or Power Pages.

## Role Scope

| Role | Scope source | Notes |
| --- | --- | --- |
| Platform Administrator | Power Pages web role plus TACATDP role record | Can manage all projects, forms, assignments, exports, and access records. |
| Project Manager | Project membership role | Can manage users only for assigned projects if CRDB approves delegated administration. |
| Supervisor / Reviewer | Project/form assignment | Can inspect submissions and review workflow where enabled; cannot manage access. |
| Data Collector / Bank Officer | Form assignment | Can collect assigned forms and view allowed own records. |
| Reporting Officer | Project assignment | Can view reporting/export surfaces for assigned projects. |
| Read-only Auditor | Project assignment | Can view assigned records and status/audit summaries where approved. |

## Portal Route Access

| Route / area | Platform Admin | Project Manager | Reviewer | Data Collector | Reporting Officer | Auditor |
| --- | --- | --- | --- | --- | --- | --- |
| Projects list | Yes | Yes | Yes | Yes | Yes | Yes |
| Project summary | Yes | Assigned | Assigned | Assigned | Assigned | Assigned |
| Collect | Yes | Optional | No | Assigned forms | No | No |
| Data tab | Yes | Assigned projects | Assigned projects | Own allowed records only | Assigned projects | Assigned projects |
| Exports | Yes | Assigned projects | Optional | No | Assigned projects | Optional |
| Power BI | Yes | Assigned projects | Optional | No | Assigned projects | Optional |
| User & Access | Yes | Assigned projects only if delegated | No | No | No | No |
| Settings / Configuration | Yes | No | No | No | No | No |

## Table Permission Requirements

| Table / logical area | Platform Admin | Project Manager | Non-admin users |
| --- | --- | --- | --- |
| Contacts | Read relevant contacts; create only if CRDB approves portal contact creation | Read relevant contacts | Read own contact only |
| Projects | Read all; update only through configuration flow | Read assigned | Read assigned |
| Forms | Read all; update only through configuration flow | Read assigned project forms | Read assigned forms |
| FormVersions | Read all | Read assigned project form versions | Read assigned form versions |
| FormAssignments | Read/create/update for all assignments | Read/create/update within assigned projects | Read own active assignments only |
| AccessAuditLogs | Read/create/update result fields for all access events | Create/read scoped events if delegated | No access by default |
| Submissions / reporting rows | Read by role and project scope | Read assigned projects | Limited by role and assignment |

## Web API Site Settings

Enable Power Pages Web API only for the minimum tables and fields required by an approved slice.

The detailed runtime package plan is `access-webapi-permission-package-plan-20260721.md`. First live write activation should be Platform Administrator only until project-scoped delegated administration has been proven.

| Table | Minimum operations | Activation timing |
| --- | --- | --- |
| Contacts | Read; create only if approved | User lookup/onboarding slice |
| FormAssignments | Read, create, update | Assignment write slice |
| ProjectMembership or equivalent | Read, create, update | Schema-hardening slice |
| AccessAuditLogs | Read, create, update result status/message if one-row audit lifecycle is approved | Before any mutation write is enabled |

## Dataverse Privilege Expectations

Solution import and schema deployment are administrator tasks and are separate from portal runtime permissions.

| Activity | Expected permission holder | Required capability |
| --- | --- | --- |
| Import solution with tables/columns | Power Platform admin or maker with sufficient Dataverse privileges | Create entity/table, create attributes, create relationships, create keys |
| Import solution containing plugin assemblies | Admin with plugin assembly privilege | `prvCreatePluginAssembly` and related plugin registration privileges |
| Configure Power Pages identity provider | CRDB tenant/site administrator | Microsoft Entra provider configuration |
| Configure web roles/table permissions | Power Pages administrator or solution deployment process | Web role, table permission, site setting management |
| Use portal User & Access UI | Platform Administrator; optionally Project Manager | Runtime table permissions through Power Pages `/_api` |

## Confirmation and Guardrail Rules

- Every critical CRUD action must use a confirmation step.
- Delete is avoided for access state; use suspend/inactive status unless CRDB explicitly approves hard delete for a narrow table.
- Every write action requires a business reason.
- Every write action must create or update an audit record.
- Ordinary data collectors must never receive audit table read permission by default.
- Do not grant audit read access to Data Collector / Bank Officer roles by default.
- Browser code must not include secrets, bearer tokens, app credentials, or privileged service-principal credentials.

## Approval Checklist

Before activation in CRDB or Mshirika:

- Confirm final role names with CRDB.
- Confirm whether Project Managers can manage users or whether only Platform Administrators can.
- Confirm whether audit rows use one-row lifecycle updates or physically append-only requested/result events.
- Confirm table permissions are included in the solution or applied manually by an approved administrator.
- Confirm smoke-test accounts for Platform Administrator, Project Manager, and Data Collector.
