# AccessAuditLogs Schema Package Readiness - 2026-07-21

Status: review-ready package/export preparation. No export or environment write performed.

## Purpose

Prepare an audit-schema-only managed solution update for `AccessAuditLogs` using the existing TACATDP solution lineage. This artifact defines what must be included, what must be excluded, and how an operator should export/package after an environment is explicitly selected.

## Package Intent

- Solution lineage: existing TACATDP managed solution, not an ad hoc solution.
- Package type: managed solution update.
- Suggested version: next patch/minor version after the currently imported target version.
- Scope: additive `AccessAuditLogs` schema only.
- Deployment behavior: schema import first; Web API site settings, table permissions, portal upload, and write activation remain separate phases.

## Include

- Table `AccessAuditLogs`.
- All 23 columns from `schemas/dataverse/access-audit-schema.json`.
- Choice metadata for `Action`, `ResultStatus`, and `ScopeType`.
- Lookups to Contacts, Projects, Forms, FormVersions, FormAssignments, and `RollbackOf`.
- Alternate keys:
  - `ak_access_audit_log` on `AuditKey`;
  - `ak_access_audit_request` on `RequestId`.
- Existing TACATDP publisher and solution unique name.

## Exclude

- Plug-in assemblies, plug-in types, plug-in steps, and images.
- Portal write activation.
- `ACCESS_WRITE_ACTIONS_ENABLED = true`.
- Broad production Web API `fields=*` settings for audit/access tables.
- Data Collector audit table read permission.
- Project Manager write permission until project-scoped relationships are proven.
- Portal upload unless explicitly approved as a separate phase.
- Seed data or access audit records.

## Operator Commands

Run these only after the operator has selected and authenticated to the correct source environment. These commands are examples for an approved export session; they are not executed by this readiness slice.

```bash
pac auth list
pac env who
pac solution list
```

Confirm the active solution unique name and target version, then export using the existing solution lineage:

```bash
pac solution export \
  --name tacatdp_prototype \
  --path ./dist/TACATDP_Impact_Tracking_Prototype_<version>_managed_audit_schema.zip \
  --managed true \
  --overwrite
```

Inspect the exported ZIP before sharing:

```bash
python3 scripts/validate-access-audit-package-readiness.py
python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/access-audit-schema.json
```

If a package file has been produced, inspect it manually or with a package-inspection script before import. Confirm no plug-in payload and no portal write activation are present.

## Pre-Export Gate

```bash
python3 scripts/validate-access-audit-package-readiness.py
python3 scripts/validate-access-audit-packaging.py
python3 scripts/validate-access-webapi-permission-plan.py
python3 scripts/validate-access-write-service-shell.py
python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/access-audit-schema.json
git diff --check
```

Expected dry-run result:

- `Writes performed: false`
- operation count `32`
- one table, 23 columns, 7 relationships, 2 alternate keys

## Import Sequence

1. Import the audit-schema-only managed solution update.
2. Publish customizations.
3. Confirm schema components exist.
4. Keep User & Access writes disabled.
5. Add Web API site settings only in the separate approved permission phase.
6. Add table permissions only in the separate approved permission phase.
7. Upload portal assets only in the separate approved portal phase.
8. Flip `ACCESS_WRITE_ACTIONS_ENABLED` only in the later single-action activation phase.

## Readiness Decision

This package is ready for an approved export only when all validators pass and the operator confirms the source environment is the intended Mshirika/CRDB-aligned development environment.
