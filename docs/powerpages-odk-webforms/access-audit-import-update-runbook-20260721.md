# Access Audit Import and Update Runbook - 2026-07-21

Status: review-ready. Do not execute without explicit environment-write approval.

## Goal

Import the `AccessAuditLogs` schema through the governed TACATDP solution path without enabling User & Access live writes prematurely.

## Phase 0: Confirm Target

1. Confirm target environment URL and tenant account.
2. Run `pac env who` and verify the environment is the intended Mshirika or CRDB environment.
3. Confirm the existing managed solution unique name and version.
4. Confirm the importer has table/column/relationship/key privileges. If plug-ins are excluded, `prvCreatePluginAssembly` is not required for this audit-only package.
5. Confirm no direct PAC or browser action is planned against the wrong environment.

## Phase 1: Schema Import

1. Run the local validators:

   ```bash
   python3 scripts/validate-access-audit-packaging.py
   python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/access-audit-schema.json
   ```

2. Build or export the managed solution update using existing TACATDP solution lineage.
3. Import the managed update.
4. Publish customizations.
5. Confirm `AccessAuditLogs`, choices, lookups, and alternate keys exist.

Do not configure portal write activation in this phase.

## Phase 2: Web API Site Settings

Only after schema import is verified, add or package the minimum Power Pages Web API settings for administrator roles:

Use `access-webapi-permission-package-plan-20260721.md` as the detailed field and role plan.

| Setting | Value |
| --- | --- |
| `Webapi/mp_accessauditlog/enabled` | `true` |
| `Webapi/mp_accessauditlog/fields` | exact approved field list, not broad `*` for production |
| `Webapi/mp_formassignment/enabled` | already existing or add only for approved assignment write phase |
| `Webapi/mp_formassignment/fields` | exact approved field list for assignment write phase |

Use the logical table name confirmed in the target environment. Do not assume plural Web API paths until verified from Dataverse metadata and Power Pages runtime.

## Phase 3: Table Permissions

Apply or package permissions separately from schema import:

| Table | Role | Minimum operations |
| --- | --- | --- |
| `AccessAuditLogs` | Platform Administrator | Read, Create; Update only if one-row result lifecycle is approved |
| `AccessAuditLogs` | Project Manager | Optional scoped Create/Read only if CRDB approves delegated administration |
| `AccessAuditLogs` | Data Collector | None by default |
| `FormAssignments` | Platform Administrator | Read, Create, Update for approved write phase |
| `FormAssignments` | Project Manager | Optional project-scoped Read/Create/Update |
| `Contacts` | Platform Administrator | Read relevant contacts; create/update only if onboarding automation is approved |

If Power Pages runtime returns table permission errors after scripted creation, open the Power Pages Security workspace, inspect the table permission, save it from the UI, restart the site, and retest. This follows the existing TACATDP permission troubleshooting evidence.

## Phase 4: Portal Upload

Portal upload is separate from schema and permissions.

1. Keep `ACCESS_WRITE_ACTIONS_ENABLED = false` for the first upload after schema import.
2. Upload only after build and validators pass.
3. Purge cache or restart the site.
4. Verify User & Access previews still render and final write buttons remain disabled.

## Phase 5: Post-Import Smoke Tests

Run smoke tests with three account types:

- Platform Administrator: can open User & Access and see preview payloads.
- Data Collector: cannot see User & Access and direct route shows permission denied.
- Reporting/Data user: existing project/data/reporting surfaces still work.

Check browser network activity:

- no `/_api/mp_accessaudit...` calls while writes are disabled;
- no `POST` or `PATCH` to `mp_formassignments` from User & Access while writes are disabled;
- existing read paths continue to work.

## Rollback

Do not delete the managed solution as routine rollback. If schema import fails, keep the previous solution version and export the import log. If permissions break runtime behavior, remove or disable only the newly added access-audit site settings/table permissions through an approved corrective update.
