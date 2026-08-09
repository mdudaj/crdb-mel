# Access Audit Dataverse Schema

Status: review-ready, no environment write.

This schema adds a dedicated audit table for the Monitoring Tool **User & Access** workflow. It does not enable portal writes by itself. It defines the audit contract that must exist before Add user, role change, suspend, reactivate, assignment removal, or rollback actions are enabled.

## Table

### AccessAuditLogs

Append-only audit record for every attempted or completed User & Access change.

Ownership: organization-owned.

Primary name column: `AuditKey`

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `AuditKey` | `Text` | Yes | Stable event key. Recommended format: `access:{utcTimestamp}:{actorEmail}:{action}:{affectedEmail}:{requestId}`. |
| `Action` | `Choice` | Yes | InviteUser/AssignProject/AssignForm/ChangeRole/SuspendAccess/ReactivateAccess/RemoveAssignment/RollbackAccessChange. |
| `ResultStatus` | `Choice` | Yes | Requested/Succeeded/Failed/Rejected/RolledBack. |
| `ActorEmail` | `Text` | Yes | Signed-in administrator email from the Power Pages session. |
| `ActorContact` | `Lookup:Contacts` | No | Power Pages contact for the administrator when available. |
| `ActorRolesJson` | `MultilineText` | No | Snapshot of detected Power Pages roles used for route/action authorization. |
| `AffectedEmail` | `Text` | Yes | Email of the user whose access is being changed. |
| `AffectedContact` | `Lookup:Contacts` | No | Power Pages contact for the affected user when available. |
| `TargetRole` | `Text` | No | Target business role label. |
| `ScopeType` | `Choice` | Yes | Platform/Project/Form/FormVersion/Assignment. |
| `Project` | `Lookup:Projects` | No | Project scope when the change is project-scoped. |
| `Form` | `Lookup:Forms` | No | Form scope when the change affects a form. |
| `FormVersion` | `Lookup:FormVersions` | No | Form version scope when assignment is version-specific. |
| `FormAssignment` | `Lookup:FormAssignments` | No | Assignment row touched by the access change when available. |
| `PreviousStateJson` | `MultilineText` | No | Before snapshot of relevant assignment/contact/role fields. Required by policy for mutation actions. |
| `NewStateJson` | `MultilineText` | No | After snapshot of relevant assignment/contact/role fields. Required by policy for mutation actions. |
| `Reason` | `MultilineText` | Yes | Business reason entered by the administrator before the change is submitted. |
| `SourceRoute` | `Text` | Yes | Portal route/action source, for example `UserAccess:AddUser` or `UserAccess:Suspend`. |
| `RequestId` | `Text` | Yes | Client-generated operation id used to correlate access mutation and audit records. |
| `CorrelationId` | `Text` | No | Optional server, flow, or Dataverse correlation id when available. |
| `RollbackOf` | `Lookup:AccessAuditLogs` | No | Original audit event being rolled back. |
| `OccurredAt` | `DateTime` | Yes | UTC timestamp when the administrator requested or completed the action. |
| `ResultMessage` | `MultilineText` | No | Short failure, rejection, or post-action note. Must not contain secrets or raw tokens. |

## Alternate Keys

| Table | Key | Columns | Purpose |
| --- | --- | --- | --- |
| `AccessAuditLogs` | `ak_access_audit_log` | `AuditKey` | Stable audit event key for idempotent audit persistence. |
| `AccessAuditLogs` | `ak_access_audit_request` | `RequestId` | Prevents duplicate audit rows for the same portal operation request. |

## Write-Path Policy

- Every access mutation must create an audit row.
- Actor email, affected email, action, scope, reason, source route, request id, result status, and timestamp are required.
- Mutation actions must capture before and after state snapshots.
- Rollback does not edit or delete the original audit row; rollback creates a new audit row referencing `RollbackOf`.
- Result messages must stay business-readable and must not include secrets, bearer tokens, anti-forgery tokens, or raw credential material.

## Import Position

Create this schema after the canonical Power Pages/ODK tables exist:

1. `Projects`
2. `Forms`
3. `FormVersions`
4. `FormAssignments`
5. `Contacts` / Power Pages contact table already exists in Dataverse
6. `AccessAuditLogs`
7. table permissions and Web API site settings after explicit approval

## Permissions Before Use

- Portal administrators need create/read permission for `AccessAuditLogs`.
- Ordinary data collectors should not read access audit rows by default.
- Access mutation code also needs only the narrow create/update privileges required for the specific target tables.
- Power BI/reporting access to audit rows should be granted separately from submission reporting.

## Verification Before Environment Write

- Run `python3 scripts/validate-access-audit-design.py`.
- Run `python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/access-audit-schema.json`.
- Confirm all planned operations are additive.
- Confirm CRDB approves portal audit-row create permission and the administrator web-role scope.
