# Access Audit Solution Packaging Checklist - 2026-07-21

Status: review-ready packaging preparation. No environment write.

## Purpose

Prepare the `AccessAuditLogs` schema for governed solution packaging before any User & Access write action is enabled. This checklist separates schema packaging from Power Pages Web API settings, table permissions, portal upload, and smoke testing.

## Inputs

- `schemas/dataverse/access-audit-schema.json`
- `schemas/dataverse/access-audit-schema.md`
- `docs/powerpages-odk-webforms/access-write-path-contract-20260721.md`
- `docs/powerpages-odk-webforms/access-permission-matrix-20260721.md`
- `docs/powerpages-odk-webforms/access-write-service-shell-20260721.md`
- `docs/powerpages-odk-webforms/access-write-preview-ui-20260721.md`

## Solution Components To Package

| Component | Required | Notes |
| --- | --- | --- |
| Table `AccessAuditLogs` | Yes | Organization-owned table for centralized audit administration. |
| Primary name column `AuditKey` | Yes | Stable audit event key. |
| Choice column `Action` | Yes | InviteUser, AssignProject, AssignForm, ChangeRole, SuspendAccess, ReactivateAccess, RemoveAssignment, RollbackAccessChange. |
| Choice column `ResultStatus` | Yes | Requested, Succeeded, Failed, Rejected, RolledBack. |
| Choice column `ScopeType` | Yes | Platform, Project, Form, FormVersion, Assignment. |
| Required text/date columns | Yes | ActorEmail, AffectedEmail, Reason, SourceRoute, RequestId, OccurredAt. |
| Optional JSON/message columns | Yes | ActorRolesJson, PreviousStateJson, NewStateJson, ResultMessage, CorrelationId. |
| Lookups | Yes | Contacts, Projects, Forms, FormVersions, FormAssignments, and self-reference RollbackOf. |
| Alternate key `ak_access_audit_log` | Yes | Uses `AuditKey`. |
| Alternate key `ak_access_audit_request` | Yes | Uses `RequestId`. |
| Power Pages Web API site settings | Not in schema package | Package/apply only after table approval. |
| Power Pages table permissions | Not in schema package | Package/apply only after role model approval. |
| Portal write activation | No | `ACCESS_WRITE_ACTIONS_ENABLED` must remain false. |

## Pre-Packaging Checks

```bash
python3 scripts/validate-access-audit-package-readiness.py
python3 scripts/validate-access-audit-design.py
python3 scripts/validate-access-write-path-contract.py
python3 scripts/validate-access-write-service-shell.py
python3 scripts/validate-access-audit-packaging.py
python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/access-audit-schema.json
```

Expected schema plan:

- `Writes performed: false`
- one table;
- twenty-three columns;
- seven relationships;
- two alternate keys;
- additive operation count `32`.

## Packaging Rules

- Keep the existing solution lineage. Do not create an ad hoc solution for the audit table.
- Use the approved publisher prefix and solution unique name.
- Add only additive components for this slice.
- Do not include plug-in assemblies in this package unless CRDB has granted and approved plug-in privileges.
- Do not enable portal writes in the same package as first audit schema import.
- Do not grant audit read access to ordinary data collectors by default.
- Use `access-audit-schema-package-readiness-20260721.md` and `access-audit-schema-package-manifest-20260721.md` before an approved export.

## Review Questions

- Has CRDB approved one-row audit lifecycle updates, or do they require physically append-only requested/result events?
- Will Project Managers receive delegated audit create/read permission, or only Platform Administrators?
- Are Power Pages table permissions packaged in the managed solution or applied manually through the Security workspace after import?
- Which administrator accounts will run smoke tests in Mshirika and CRDB?
