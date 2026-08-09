# AccessAuditLogs Package Manifest - 2026-07-21

Status: intended package manifest, not an exported solution inventory.

## Required Solution Contents

| Type | Component | Required |
| --- | --- | --- |
| Table | `AccessAuditLogs` | Yes |
| Column | `AuditKey` | Yes |
| Column | `Action` | Yes |
| Column | `ResultStatus` | Yes |
| Column | `ActorEmail` | Yes |
| Column | `ActorContact` | Yes |
| Column | `ActorRolesJson` | Yes |
| Column | `AffectedEmail` | Yes |
| Column | `AffectedContact` | Yes |
| Column | `TargetRole` | Yes |
| Column | `ScopeType` | Yes |
| Column | `Project` | Yes |
| Column | `Form` | Yes |
| Column | `FormVersion` | Yes |
| Column | `FormAssignment` | Yes |
| Column | `PreviousStateJson` | Yes |
| Column | `NewStateJson` | Yes |
| Column | `Reason` | Yes |
| Column | `SourceRoute` | Yes |
| Column | `RequestId` | Yes |
| Column | `CorrelationId` | Yes |
| Column | `RollbackOf` | Yes |
| Column | `OccurredAt` | Yes |
| Column | `ResultMessage` | Yes |
| Alternate key | `ak_access_audit_log` | Yes |
| Alternate key | `ak_access_audit_request` | Yes |

## Required Exclusions

| Type | Exclusion |
| --- | --- |
| Plug-in | No `PluginAssemblies/` payload. |
| Plug-in | No plug-in type, step, or image root components. |
| Portal | No portal upload bundled with audit schema-only package unless separately approved. |
| Web API | No broad audit/access `fields=*` production site settings. |
| Runtime | No `ACCESS_WRITE_ACTIONS_ENABLED = true`. |
| Permissions | No Data Collector audit read permission. |
| Data | No access audit seed rows. |

## Manual ZIP Review Checklist

- Confirm package unique name is the existing TACATDP solution unique name.
- Confirm package version is higher than the target imported version.
- Confirm `AccessAuditLogs` metadata exists.
- Confirm choices and alternate keys exist.
- Confirm plug-in payloads are absent.
- Confirm no portal JavaScript bundle flips write activation.
- Confirm import notes reference `access-audit-import-update-runbook-20260721.md`.
