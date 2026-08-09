# AssignForm First Live Write Activation Design - 2026-07-21

Status: proposed design only. No implementation or environment write.

## Purpose

Define the first User & Access live write path: `AssignForm` only. This is the smallest useful mutation because it creates a form assignment without changing roles, deleting data, suspending access, or modifying submissions.

## Activation Boundary

- First live action: `AssignForm`.
- Allowed actor for first activation: Platform Administrator only.
- Project Manager write access remains deferred.
- ChangeRole, SuspendAccess, ReactivateAccess, RemoveAssignment, InviteUser, AssignProject, and RollbackAccessChange remain disabled.
- Access writes remain disabled by default unless an explicitly named test build sets `VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED=true`.
- The first activated build is limited to Mshirika development testing and must not be reused for CRDB without separate approval.

## Required Pre-Conditions

1. `AccessAuditLogs` schema has been imported through the governed solution path.
2. `ak_access_audit_request` exists on `RequestId`.
3. Platform Administrator has Power Pages table permission to create/read `mp_accessauditlog`.
4. Platform Administrator has read/create permission for `mp_formassignment`.
5. Platform Administrator has read and `Append To` permission on `mp_formversion`.
6. Site settings are enabled for the approved audit and assignment field lists.
7. Browser smoke confirms Data Collector cannot read `mp_accessauditlog`.
8. User & Access preview UI shows the exact audit and mutation payload before activation.

## Sequence

1. Administrator opens Add user access.
2. Administrator enters affected email, selects role, project, and one or more form versions.
3. Administrator enters a business reason before activation. Placeholder reasons are not accepted for live writes.
4. Client normalizes affected email to lowercase.
5. Client generates one `RequestId` per selected form version.
6. For each selected form version, client checks for an equivalent assignment:
   - same normalized `mp_useremail`;
   - same `_mp_formversion_value`;
   - active assignment status/lifecycle where the column exists.
7. If equivalent assignment exists:
   - do not create a duplicate assignment;
   - create or update audit result as succeeded no-op;
   - UI shows `Access already existed`.
8. If no equivalent assignment exists:
   - create `AccessAuditLogs` row with `Action=AssignForm` and `ResultStatus=Requested`;
   - create `mp_formassignment`;
   - record audit result as `Succeeded` or append a result event if strict append-only is selected;
   - refresh users and assignments.
9. If audit create fails, stop before assignment create.
10. If assignment create fails after audit create, record audit result `Failed` where permitted and show a recoverable failure state.

## Idempotency

- `RequestId` is unique per form-version assignment attempt.
- Retry must search for an existing audit row by `RequestId` before creating another audit row.
- Assignment create must search by normalized email and form version before creating a row.
- Duplicate assignment detection is a successful no-op, not a fatal error.
- The UI must explain no new access row was created because the user already had the selected form.

## Mutation Payload

Initial `mp_formassignment` create payload:

```json
{
  "mp_useremail": "affected.user@example.com",
  "mp_assignmentkey": "affected.user@example.com:<formVersionId>",
  "mp_FormVersion@odata.bind": "/mp_formversions(<formVersionId>)"
}
```

The exact lookup bind name must be confirmed from the target environment metadata before activation.

## Rollback

For a wrongly assigned form, do not delete submissions or related history.

First rollback option:

- mark the assignment inactive/suspended if a lifecycle/status column exists and has been approved;
- create a `RollbackAccessChange` audit row referencing the original AssignForm audit event.

If no status/lifecycle column exists yet:

- do not hard-delete as routine rollback;
- use an approved corrective package to add status/lifecycle support before enabling rollback.

## UI States

| State | Behavior |
| --- | --- |
| Preview | Shows request id, audit payload, future assignment payload, and disabled reason. |
| Ready | Shows enabled Apply/Create only after all activation gates pass. |
| Saving audit | Shows non-dismissive progress and prevents duplicate clicks. |
| Audit failed | Stops before assignment create; shows support-safe error. |
| Checking duplicate | Shows progress while searching existing assignments. |
| Already assigned | Shows saved/no-op state; refreshes user row. |
| Creating assignment | Shows non-dismissive progress and prevents duplicate clicks. |
| Assignment succeeded | Shows saved state and refreshes users/assignments. |
| Assignment failed | Shows failed state; audit result records failure where permitted. |
| Permission denied | Shows admin-facing support code without exposing tokens or headers. |

## Verification Before Implementation

```bash
python3 scripts/validate-access-assignform-activation-design.py
python3 scripts/validate-access-write-path-contract.py
python3 scripts/validate-access-webapi-permission-plan.py
python3 scripts/validate-access-write-service-shell.py
python3 scripts/validate-access-write-preview-ui.py
```

## Implementation Gate

The implementation slice may add code paths for `AssignForm`, but activation must remain off until explicit approval is given after schema and permission smoke tests pass.
