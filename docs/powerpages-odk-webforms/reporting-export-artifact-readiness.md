# Reporting, Export, and Power BI Artifact Readiness

## Ready

- Requirements captured in `reporting-export-requirements.md`.
- Architecture decision captured in `adr-0003-reporting-export-powerbi.md`.
- Delivery steps captured in `reporting-export-delivery-plan.md`.
- Acceptance criteria captured in `reporting-export-acceptance-criteria.md`.
- User stories captured in `reporting-export-user-stories.md`.
- Traceability captured in `reporting-export-traceability.md`.
- Research summary captured in `reporting-export-research.md`.
- Additive reporting schema captured in `schemas/dataverse/reporting-projection-schema.json`.
- Human review notes captured in `schemas/dataverse/reporting-projection-schema.md`.
- Dry-run support for reporting alternate keys added to `scripts/dataverse-schema-plan.py`.
- Projection builder captured in `scripts/build-reporting-projections.py`.
- No-network projection fixture validation captured in `scripts/validate-reporting-projection-builder.py`.
- Delivery summary captured in `reporting-projection-builder-delivery-20260714.md`.
- Reporting schema deployed after approval and projection rebuild completed with 5 report rows and 145 answer rows.
- Power Pages Web API settings and authenticated-user table permissions configured for all reporting and export settings tables.
- Browser-generated root CSV selected for the first bounded export slice because it reads governed projection rows and needs no new managed component or package.

## Ready Implementation Boundary

- Wire the Data tab to reporting projections through Power Pages `/_api`.
- Add named current-filter CSV exports and persist settings through `mp_exportsettings`.
- Add concrete Power BI Dataverse connector guidance without embedding reports or credentials.

## Deferred Decisions

- Select the XLSX generation mechanism after hosted repeat data exists.
- Confirm CRDB environment policy for Power BI Import versus DirectQuery before prescribing a single mode.
- Select server-side automation for automatic projection refresh after submit/edit.

## Approval Gates

- Explicit approval is required before live Dataverse schema writes.
- Explicit approval is required before Power Pages table permission changes.
- Explicit approval is required before Power Pages upload.
- Explicit approval is required before adding Power Automate/custom API/plugin components.
