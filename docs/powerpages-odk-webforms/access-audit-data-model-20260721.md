# Access Audit Data Model Delivery - 2026-07-21

## Purpose

Define the audit data model required before enabling User & Access write actions in the portal.

## Delivered Artifacts

- `schemas/dataverse/access-audit-schema.json`
- `schemas/dataverse/access-audit-schema.md`
- `scripts/validate-access-audit-design.py`
- Updated `docs/powerpages-odk-webforms/access-management-requirements.md`
- Updated `docs/powerpages-odk-webforms/adr-0007-portal-user-access-management.md`
- Updated `schemas/dataverse/import-order.md`

## Scope

The proposed `AccessAuditLogs` table records append-only access events for:

- invite user;
- assign project;
- assign form;
- change role;
- suspend access;
- reactivate access;
- remove assignment;
- rollback access change.

Each access mutation must capture actor, affected user, action, scope, business reason, source route, request id, timestamp, result status, and before/after state snapshots.

## Non-Goals

- No Dataverse schema deployment.
- No Power Pages table-permission or site-setting changes.
- No portal write code.
- No change to the currently deployed read-only User & Access UI.

## Traceability

| Requirement | Artifact |
| --- | --- |
| Audit every access mutation | `access-audit-schema.json`, `access-management-requirements.md` |
| Require administrator reason | `Reason` column, write-path policy |
| Capture before/after state | `PreviousStateJson`, `NewStateJson`, write-path policy |
| Support rollback without deleting history | `RollbackOf`, `RollbackAccessChange`, ADR update |
| Keep design review-only | `environment_write=false`, `portal_write_enabled=false`, validator |

## Verification

- `python3 scripts/validate-access-audit-design.py` passed.
- `python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/access-audit-schema.json` passed and reported `Writes performed: false`.
- Dry-run plan reported 32 additive operations: one table, columns/lookups, seven relationships, and two alternate keys.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `git diff --check` passed.
