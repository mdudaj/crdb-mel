# Access Web API and Table Permission Package Plan - 2026-07-21

Status: review-ready planning artifact. No environment write.

## Purpose

Define the minimum Power Pages Web API site settings and table permissions needed before User & Access write actions can be activated. This plan follows the audit schema packaging work but does not enable portal writes.

## Governing Boundary

- `ACCESS_WRITE_ACTIONS_ENABLED` remains `false`.
- No `/_api/mp_accessaudit...` endpoint is wired in browser code.
- No Power Pages site setting or table permission is created by this artifact.
- Runtime permissions must be applied only after schema import, administrator role approval, and explicit environment-write approval.

## Web API Site Settings

Use exact logical table names confirmed in the target environment before packaging. The names below assume the publisher prefix remains `mp`.

| Site setting | Value | Activation phase | Notes |
| --- | --- | --- | --- |
| `Webapi/mp_accessauditlog/enabled` | `true` | Audit permission phase | Required before the portal can persist audit rows. |
| `Webapi/mp_accessauditlog/fields` | `mp_auditkey,mp_action,mp_resultstatus,mp_actoremail,mp_actorrolesjson,mp_affectedemail,mp_targetrole,mp_scopetype,mp_previousstatejson,mp_newstatejson,mp_reason,mp_sourceroute,mp_requestid,mp_occurredat,mp_resultmessage` | Audit permission phase | Start with non-lookup fields; add lookup fields only after binding names are confirmed. |
| `Webapi/mp_formassignment/enabled` | `true` | Assignment write phase | Already used for reads; create/update only after approval. |
| `Webapi/mp_formassignment/fields` | `mp_formassignmentid,mp_assignmentkey,mp_useremail,mp_formversion` | Assignment write phase | Minimum fields for idempotent assignment create and lookup binding. |
| `Webapi/contact/enabled` | `true` | Contact lookup phase | Read-only administrator lookup. |
| `Webapi/contact/fields` | `contactid,fullname,emailaddress1,statecode` | Contact lookup phase | Do not expose broad contact fields. |

Do not use `*` for production access-management tables unless CRDB explicitly approves a temporary troubleshooting window.

## Table Permissions

### Platform Administrator

| Table | Scope | Read | Create | Write | Append | Append To | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `mp_accessauditlog` | Global | Yes | Yes | Conditional | No | No | Write only if one-row Requested -> Succeeded/Failed lifecycle is approved. |
| `mp_formassignment` | Global | Yes | Yes | Yes | Yes | No | Needed for first live `AssignForm` candidate and suspend/reactivate status changes. |
| `mp_formversion` | Global | Yes | No | No | No | Yes | Required when creating assignment rows that bind to an existing form version. |
| `contact` | Global or Contact scope | Yes | No | No | No | No | Read relevant contacts only; create/update deferred. |

### Project Manager

Delegated Project Manager permissions are optional and require CRDB approval.

| Table | Scope | Minimum access |
| --- | --- | --- |
| `mp_accessauditlog` | Parent/relationship scoped where possible | Create and read only scoped access events. |
| `mp_formassignment` | Parent/relationship scoped where possible | Read/create/update only for assigned projects. |
| `mp_formversion` | Parent/relationship scoped where possible | Read assigned project form versions and Append To for assignment binding. |
| `contact` | Restricted read | Read enough to identify assigned project users. |

If project-scoped relationships are not sufficient in the current schema, do not grant Project Manager write permission yet. Keep the first live write limited to Platform Administrator.

### Data Collector / Bank Officer

| Table | Access |
| --- | --- |
| `mp_accessauditlog` | None by default. |
| `mp_formassignment` | Existing own/assigned read only. No create/update. |
| `contact` | Own contact only if needed by Power Pages. |

## Scope Decision

Use this order of preference:

1. Parent/relationship scoped permissions for delegated project administration.
2. Global permissions only for Platform Administrator.
3. No access for roles where a safe scope cannot be expressed.

For the first activation, use Platform Administrator only. Defer Project Manager write access until project membership relationships are deployed and tested.

## Activation Checklist

Before turning on any live write path:

1. `AccessAuditLogs` schema exists in the target environment.
2. The exact `mp_accessauditlog` logical name and Web API entity set behavior are verified.
3. Site settings are present for audit, assignment, and contact tables.
4. Table permissions are visible in Power Pages Security workspace and saved there if runtime does not recognize scripted relationships.
5. Administrator contact has the approved admin web role.
6. `ACCESS_WRITE_ACTIONS_ENABLED` remains `false` for the first verification upload.
7. Browser Network panel confirms no write calls occur from preview flows.
8. Only after smoke tests pass should a separate approved slice flip the write flag for one action.

## Smoke Tests

### Platform Administrator

- Can open User & Access.
- Can load users and contact states.
- Can generate Add user and Change role preview payloads.
- After permissions are applied but before write flag activation, no `POST` to `mp_accessauditlog` occurs.
- In a later approved write test, can create one audit row.

### Data Collector / Bank Officer

- Does not see User & Access navigation.
- Direct route shows permission denied.
- Cannot read `mp_accessauditlog` through browser `/_api`.
- Existing collect and assigned form behavior still works.

### Reporting Officer / Reviewer

- Existing Data, Exports, and Power BI guidance continue to load according to assigned project permissions.
- No access-management write controls are visible.

## Known Power Pages Runtime Rule

Direct Dataverse creation of table permission and relationship rows may not be enough for runtime authorization. If `/_api` returns `EntityPermissionReadIsMissing`, open the table permission in Power Pages Security workspace, confirm the web role, save it, restart the site, and retest.
