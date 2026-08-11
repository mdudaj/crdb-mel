# Dataverse Import Order: Multi-Project Monitoring Platform

Generated review artifact for TACATDP. This document does not authorize or perform environment writes.

## Scope

- Source model: `docs/multi-project-monitoring/data-model.md`
- Field source: `docs/xlsform-field-inventory.csv` and `schemas/xlsform-to-list-mapping.csv`
- Vocabulary source: `schemas/reference-data/*.csv`
- High-volume village source: `schemas/reference-data/TACATDP_RefVillages.csv`
- Renderer contract: `schemas/dataverse/form-renderer-contract.json`
- Platform publisher prefix placeholder: `mp`
- TACATDP project code: `tacatdp`

## Recommended create/import sequence

1. Create the Power Platform solution and publisher after approval; replace the placeholder `mp` prefix only if the approved publisher prefix differs.
2. Create project/governance tables from `platform-tables.json` and `platform-columns.csv`.
3. Create instrument metadata tables and relationships: `mp_Instrument`, `mp_InstrumentVersion`, `mp_EventDefinition`, `mp_InstrumentEventBinding`, `mp_GroupDefinition`, `mp_FieldDefinition`, `mp_FieldRule`.
4. Create controlled vocabulary tables and relationships: `mp_VocabularyScheme`, `mp_VocabularyTerm`, `mp_VocabularyTermLabel`, `mp_VocabularyTermRelation`, `mp_ProjectVocabularyBinding`, `mp_FieldVocabularyBinding`, `mp_ExternalAuthorityIdentifier`.
5. Review renderer metadata extensions in `form-renderer-contract.json`, especially `RenderMode`, `NavigationMode`, `ControlKind`, `LookupProviderType`, and rule-expression scope, before adding them to Dataverse.
6. Create high-volume reference data table `mp_VillageReference` with indexed `RegionCode`, `DistrictCode`, and `WardCode` columns for delegated cascading lookup filters.
7. Create runtime tables and relationships: `mp_TrackedEntity`, `mp_EntityIdentifier`, `mp_Encounter`, `mp_Submission`, `mp_GroupInstance`, `mp_AnswerValue`, `mp_MultiSelectAnswer`, `mp_Attachment`, `mp_SubmissionReview`, `mp_AuditEvent`.
8. Create beneficiary extension tables from `beneficiary-entity-extension-schema.json` only after reviewing `docs/powerpages-odk-webforms/beneficiary-dataverse-schema-plan-20260811.md`. These tables extend `mp_TrackedEntity`; they do not replace it with a TACATDP-only beneficiary identity table.
9. Create projection/export tables: `mp_ExportProfile`, `mp_ExportColumn`.
10. For the ODK Central-inspired Power Pages prototype path, create canonical tables from `odk-central-inspired-mvp-schema.json`: `Projects`, `Forms`, `FormVersions`, `FormAssignments`, `FormAttachments`, `Submissions`, `SubmissionVersions`, and `SubmissionAttachments`.
11. Create reporting projection tables from `reporting-projection-schema.json`: `SubmissionReportRows`, `SubmissionRepeatRows`, `SubmissionAnswers`, and `ExportSettings`. Run `python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/reporting-projection-schema.json` first and confirm it is additive.
12. Create access-audit tables from `access-audit-schema.json` before enabling any User & Access write actions. Run `python3 scripts/validate-access-audit-design.py` and `python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/access-audit-schema.json` first.
13. Create onboarding request queue table from `onboarding-request-schema.json` before enabling the Add User create/invite/assign submit path. Run `python3 scripts/validate-access-onboarding-queue-schema.py` and `python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/onboarding-request-schema.json` first.
14. Before packaging access audit, review `docs/powerpages-odk-webforms/access-audit-solution-packaging-20260721.md` and `docs/powerpages-odk-webforms/access-audit-import-update-runbook-20260721.md`; run `python3 scripts/validate-access-audit-packaging.py`.
15. Add alternate keys from `platform-alternate-keys.csv`, `beneficiary-entity-extension-schema.json`, `reporting-projection-schema.json`, `access-audit-schema.json`, and `onboarding-request-schema.json` after referenced columns exist.
16. Import seed records in this order: `mp_Project`, `mp_Instrument`, `mp_InstrumentVersion`, `mp_EventDefinition`, `mp_GroupDefinition`, `mp_VocabularyScheme`, non-village `mp_VocabularyTerm`, `mp_VocabularyTermLabel`, `mp_VillageReference`, `mp_FieldDefinition`, `mp_FieldRule`, vocabulary/reference bindings, and project bindings.
17. Import TACATDP metadata from `tacatdp-field-definitions.csv`, `tacatdp-vocabulary-terms.csv`, and `tacatdp-village-reference.csv` only after the generated rows are reviewed.
18. Bind the Canvas app and Power Pages portal only after the reviewed dev Dataverse schema exists and table permissions are approved.

## Reference-data decision

Villages are intentionally not stored as generic `mp_VocabularyTerm` rows in this revision. The source contains 66297 villages, so a dedicated `mp_VillageReference` table is more efficient for Canvas cascading lookups because the app can delegate filters directly against indexed `RegionCode`, `DistrictCode`, and `WardCode` columns. Smaller choice lists remain governed vocabulary terms.

## Review checks before environment writes

- Confirm publisher prefix and solution name.
- Confirm whether the 72 fields without a `source_screen` match should stay grouped by old save-target projection or be assigned to explicit metadata groups. These are not missing XLSForm fields; they are fields whose labels did not map cleanly to the current Canvas screen YAML, mostly production-cost line-item fields.
- Confirm `mp_VillageReference` naming and key columns before creating tables.
- Confirm field-level requiredness remains app-visible-only; `required_in_dataverse` is intentionally `no` for imported TACATDP fields.
- Confirm `mp_AnswerValue` includes optional `mp_vocabularyterm` and `mp_villagereference` lookups before table creation, while retaining raw/code/label snapshots for export stability.
- Confirm alternate keys do not exceed Dataverse key constraints in the target environment.

## Generated artifact inventory

- `platform-tables.json`: 30 platform/reference tables.
- `platform-columns.csv`: 186 platform/reference/renderer columns.
- `platform-relationships.csv`: 48 relationships.
- `platform-alternate-keys.csv`: 22 alternate keys.
- `form-renderer-contract.json`: renderer surfaces, metadata extensions, supported rule subset, control mapping, and pilot flows.
- `odk-central-inspired-mvp-schema.json`: canonical Power Pages/ODK-style runtime tables.
- `beneficiary-entity-extension-schema.json`: additive beneficiary profile, participation, finance, technology, training, outcome, and submission-lineage extension tables around `mp_TrackedEntity`.
- `reporting-projection-schema.json`: additive reporting, export, and Power BI projection tables.
- `access-audit-schema.json`: additive User & Access audit log table required before portal access writes.
- `onboarding-request-schema.json`: additive User & Access queue table required before create/invite/assign onboarding submit is enabled.
- `access-audit-solution-packaging-20260721.md`: solution-packaging checklist for the access audit table, choices, lookups, alternate keys, site settings, and table permissions.
- `access-audit-import-update-runbook-20260721.md`: import/update runbook separating schema import, Web API settings, table permissions, portal upload, and smoke tests.
- `tacatdp-field-definitions.csv`: 292 TACATDP field definitions.
- `tacatdp-vocabulary-terms.csv`: 5190 TACATDP non-village vocabulary terms.
- `tacatdp-village-reference.csv`: 66297 TACATDP village reference rows.
