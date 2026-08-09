# User & Access Write-Path Contract - 2026-07-21

Status: proposed, implementation blocked until CRDB/DAMAX approve the audit schema, table permissions, and portal write activation.

## Purpose

Define the governed write path for User & Access actions before any portal create/update/delete calls are enabled. This contract turns the current preview UI into a banking-appropriate workflow with confirmation, reason capture, idempotency, audit evidence, and rollback rules.

## Governing Artifacts

- `docs/powerpages-odk-webforms/access-management-requirements.md`
- `docs/powerpages-odk-webforms/access-management-acceptance-criteria.md`
- `docs/powerpages-odk-webforms/adr-0007-portal-user-access-management.md`
- `schemas/dataverse/access-audit-schema.json`
- `schemas/dataverse/access-audit-schema.md`
- `docs/powerpages-odk-webforms/managed-service-ux-governance.md`
- `docs/powerpages-odk-webforms/managed-service-ux-agent-checklist.md`

## Write Actions

| Action | Scope | Target row | Required actor role | Confirmation | Required reason |
| --- | --- | --- | --- | --- | --- |
| Add user / prepare user | Platform or Project | Contact reference and assignment preparation | Platform Administrator or assigned Project Manager | Yes | Yes |
| Assign project | Project | Project membership or assignment bridge | Platform Administrator or assigned Project Manager | Yes | Yes |
| Assign form | Form/FormVersion | `mp_formassignment` initially; membership-linked assignment later | Platform Administrator or assigned Project Manager | Yes | Yes |
| Change role | Project or Platform | Project membership role or platform role mapping | Platform Administrator; Project Manager only within assigned project if approved | Yes | Yes |
| Suspend access | Assignment or Project | Assignment/membership status | Platform Administrator or assigned Project Manager | Yes | Yes |
| Reactivate access | Assignment or Project | Assignment/membership status | Platform Administrator or assigned Project Manager | Yes | Yes |
| Remove assignment | Assignment | Assignment/membership status, preferably inactive rather than delete | Platform Administrator or assigned Project Manager | Yes | Yes |
| Rollback access change | Same as original event | New compensating mutation and audit row | Platform Administrator | Yes | Yes |

## Required User Flow

1. Administrator opens **User & Access** and selects a user, project, form, or assignment.
2. UI shows the current state in a detail drawer or dedicated task panel.
3. Administrator chooses a single action.
4. UI opens a confirmation step showing:
   - affected user email;
   - target project/form/role/status;
   - current state;
   - proposed new state;
   - required business reason;
   - warning that the change will be audited.
5. Client generates a stable `RequestId` before any write.
6. Client creates an `AccessAuditLogs` row with `ResultStatus=Requested`.
7. Client performs the target mutation through Power Pages `/_api`.
8. Client records the result:
   - preferred first implementation: update the same audit row from `Requested` to `Succeeded` or `Failed`;
   - stricter future implementation: create a second result event if CRDB requires physically append-only audit rows.
9. UI refreshes the affected lists and shows saved, failed, or permission-denied state.

## Idempotency Rules

- Each user action must have one client-generated `RequestId`.
- `RequestId` must be unique per attempted mutation and covered by `ak_access_audit_request`.
- Retrying a failed network request must first check whether the same `RequestId` already exists.
- Assignment create must search by affected user email, project, form, form version, and active status before creating a new row.
- If an equivalent active assignment already exists, the action must become a no-op success with an audit result message explaining that access already existed.

## State Snapshot Rules

Before mutation, capture the smallest useful JSON snapshot:

- assignment id, project id, form id, form version id;
- affected email and contact id when available;
- old role/status/start/end dates;
- old assignment source and lifecycle fields where present.

After mutation, capture the same fields with the new values. Do not include anti-forgery tokens, cookies, bearer tokens, app credentials, or raw request headers.

## Failure Handling

| Failure | Expected UI behavior | Audit behavior |
| --- | --- | --- |
| User lacks admin route role | Hide route and show permission-denied if accessed directly | No mutation attempt |
| Table permission missing | Show permission-denied with support code | Audit may fail too; record browser support code locally only |
| Audit create fails | Stop before target mutation | No target mutation |
| Target mutation fails | Show failed state and preserve current list | Mark audit row failed or append failed result event |
| Duplicate assignment detected | Show access already exists | Mark audit as succeeded no-op |
| Contact not found | Show pending-login/contact-missing state | Audit requested or rejected, depending on action |
| Cache/session delay | Show saved with refresh guidance | Mark audit succeeded |

## Rollback Rules

- Rollback never edits or deletes the original audit event.
- Rollback creates a new `RollbackAccessChange` audit row that references the original event through `RollbackOf`.
- Rollback must capture before and after snapshots of the compensating change.
- Rollback is limited to reversible access mutations; it must not delete submissions, submission versions, attachments, or reporting projection rows.

## Activation Gates

Writes remain disabled until all gates pass:

- CRDB Microsoft identity sign-in is confirmed for the target site.
- Administrator web role strategy is approved.
- `AccessAuditLogs` schema is deployed through the governed solution process.
- Power Pages table permissions are packaged or applied for:
  - read/create audit rows for administrator roles;
  - read/create/update assignment or membership rows for administrator roles;
  - no audit read permission for ordinary data collectors by default.
- Portal Web API site settings exist for each enabled table and field set.
- Smoke tests pass for Platform Administrator, Project Manager, and Data Collector accounts.

## Verification Commands

Run before implementation:

```bash
python3 scripts/validate-access-audit-design.py
python3 scripts/validate-access-write-path-contract.py
python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/access-audit-schema.json
python3 scripts/validate-webforms-spa-foundation.py
```

Run after implementation, before deployment:

```bash
npm --prefix powerpages/webforms-spa run build
python3 scripts/validate-webforms-spa-foundation.py
python3 scripts/validate-access-write-path-contract.py
git diff --check
```

## Delivery Decision

The next implementation slice may add client-side service methods and disabled feature flags, but must not enable live write actions until the activation gates above are satisfied.
