# Indicator and evidence Dataverse implementation runbook

Status: approved planning artifact. This runbook is ready for administrator/developer review, but it does not execute Dataverse writes by itself.

Approved scope from 2026-08-20:

1. Indicator/evidence schema review approved.
2. Move to Dataverse implementation planning approved.
3. Prepare the Dataverse write runbook approved.

Environment-write boundary:

- Do not create tables until the target environment and user/service identity are confirmed immediately before execution.
- Do not expose new Power Pages Web API fields until a specific UI/API surface requires them.
- Do not add table permissions until access scope is agreed.
- Do not run a production import/deployment from this runbook.

## Evidence inspected

- `schemas/dataverse/indicator-evidence-schema.json`
- `schemas/dataverse/indicator-evidence-schema.md`
- `docs/powerpages-odk-webforms/prototype-model-design-20260820.md`
- `schemas/dataverse/import-order.md`
- `scripts/dataverse-schema-plan.py`
- `scripts/dataverse-schema-deploy.py`
- Microsoft Learn, Power Pages portals Web API overview: `/_api` uses EntitySetName in code, table logical name in site settings, explicit `Webapi/<table>/fields` is mandatory, wildcard `*` is deprecated, and calls require CSRF for writes.
- Microsoft Learn, Power Pages table permissions: Dataverse access from forms, lists, Liquid, and portals Web API follows table permissions associated with web roles.
- Microsoft Learn, Dataverse alternate keys: alternate keys support robust upsert/import, but key columns must fit supported types/size constraints and null values do not enforce uniqueness.
- Microsoft Learn, PAC solution import: `pac solution import --path ... --environment ... --publish-changes` imports a solution zip into a Dataverse environment.

## Tables to create after final execution approval

| Order | Table | Purpose |
|---:|---|---|
| 1 | `mp_IndicatorDefinition` | Indicator/KPI catalogue with code, unit, formula, frequency, method, disaggregation, and verification method. |
| 2 | `mp_DataSourceMapping` | Source-field and transform mapping for indicator inputs. |
| 3 | `mp_Observation` | Atomic measured/reported/imported/estimated/modelled source value. |
| 4 | `mp_IndicatorResult` | Dashboard/report-ready indicator fact with method, verification status, source summary, and calculated timestamp. |
| 5 | `mp_Evidence` | GPS/photo/document/submission/system evidence references linked to observations or results. |

This order lets definitions and mappings exist before observations/results, and creates evidence after the target relationships exist.

## Preflight checklist

Run these checks before any write:

```bash
git status -sb
node scripts/validate-indicator-evidence-schema.mjs
python3 scripts/dataverse-schema-plan.py \
  --schema-file schemas/dataverse/indicator-evidence-schema.json \
  --solution "$POWER_PLATFORM_SOLUTION_UNIQUE_NAME"
pac auth list
pac auth who
pac env who
```

Required result:

- Working tree contains only the intended implementation changes.
- Schema validator passes.
- Dry-run plan shows `writes_performed: false`.
- PAC profile points to the intended development environment.
- Target solution name and publisher prefix are confirmed.

## Dataverse schema execution plan

Preferred implementation path:

1. Generate or hand-author solution metadata for the five tables from `indicator-evidence-schema.json`.
2. Include the metadata in the CRDB MEL development solution.
3. Import the solution into the confirmed development environment.
4. Publish changes.
5. Verify metadata inventory.
6. Only then configure Power Pages Web API and table permissions needed by the prototype.

Execution command shape after package creation:

```bash
pac solution import \
  --path "<solution-zip>" \
  --environment "<development-environment-url-or-id>" \
  --publish-changes
```

Do not use `--skip-dependency-check` unless the exact dependency is understood and approved. Do not use `--force-overwrite` unless the target customization impact has been reviewed.

## Field and relationship checks

Before import, verify:

- All tables use the approved `mp` publisher prefix.
- Primary name columns exist and are text-compatible.
- Lookup targets already exist:
  - `mp_Project`
  - `mp_TrackedEntity`
  - `mp_Submission`
  - `mp_SubmissionReportRow`
- Choice values are stable enough for development review.
- Long text fields are used for JSON/source summaries where the value can exceed single-line text limits.
- Evidence file references are pointers only; no secret, bearer URL, or raw private file payload is stored in public-readable fields.

## Alternate-key implementation notes

The review schema proposes:

- `AK_IndicatorDefinition_Project_Code`
- `AK_DataSourceMapping_Key`
- `AK_Observation_Key`
- `AK_Evidence_Key`
- `AK_IndicatorResult_Key`

Microsoft Dataverse supports alternate keys for lookup, choice, text, number, decimal, and datetime columns, but null key values do not enforce uniqueness. Therefore:

- For `AK_IndicatorDefinition_Project_Code`, do not leave `mp_project` null for project-specific indicators.
- If reusable enterprise indicators need null project scope, add a non-null text scope column such as `mp_scopecode` before implementation.
- Avoid key values containing characters that Microsoft documents as problematic for upsert URLs: `<`, `>`, `*`, `%`, `&`, `:`, `/`, `\\`, `#`.

## Power Pages Web API plan

Do not enable browser access for every field by default.

If a future UI reads indicator results, configure only the required logical table settings:

```text
Webapi/mp_indicatorresult/enabled=true
Webapi/mp_indicatorresult/fields=mp_resultkey,mp_project,mp_indicatordefinition,mp_reportingperiod,mp_geography,mp_value,mp_unit,mp_method,mp_verificationstatus,mp_disaggregationjson,mp_sourcesummaryjson,mp_calculatedat,mp_status
```

If a future UI reads definitions:

```text
Webapi/mp_indicatordefinition/enabled=true
Webapi/mp_indicatordefinition/fields=mp_name,mp_code,mp_project,mp_description,mp_indicatortype,mp_resultlevel,mp_unit,mp_formula,mp_reportingfrequency,mp_disaggregationjson,mp_verificationmethod,mp_responsibleunit,mp_reportingframework,mp_status
```

Do not expose `mp_Evidence` to broad browser reads until evidence storage, privacy classification, and reviewer roles are agreed.

Reminder from Microsoft docs and project experience:

- Site settings use table logical names.
- Browser `/_api` URLs use EntitySetName and are case-sensitive.
- `Webapi/<table>/fields` must list explicit fields.
- Table permissions must be associated with the relevant web role.
- Mutating browser calls require CSRF handling.

## Table permission plan

Minimum development review permissions after schema import:

| Table | Portal role | Access type | Privileges | Reason |
|---|---|---|---|---|
| `mp_IndicatorDefinition` | Authenticated Users or MEL Officer role | Global or scoped | Read only | Let dashboard/help surfaces show definitions. |
| `mp_IndicatorResult` | Authenticated Users or MEL Officer role | Global or scoped | Read only | Let dashboard consume governed result facts. |
| `mp_DataSourceMapping` | MEL Admin only | Scoped/admin | Read only from portal; write only in maker/admin path | Mapping is configuration, not ordinary portal data entry. |
| `mp_Observation` | MEL Admin / Data Quality role | Scoped/admin | Read only from portal initially | Observation values may expose respondent or evidence lineage. |
| `mp_Evidence` | Evidence Reviewer role only | Scoped/admin | Read only initially | Evidence can include GPS/photo/document references. |

Avoid portal writes to these tables for the first implementation. Scheduled calculation should run through approved Power Automate ownership or an approved application user/service principal.

## Seed data plan

Create a small development seed after schema exists:

| Indicator code | Name | Method | Status |
|---|---|---|---|
| `TAC-BEN-001` | Beneficiary profiles imported | Imported | Active |
| `TAC-FIN-001` | Reported baseline amount | Reported | Active |
| `TAC-REG-001` | Regions covered | Imported | Active |
| `TAC-TEC-001` | Technologies financed | Imported | Active |
| `TAC-TRN-001` | Farmers trained | Reported | Active |

Do not seed official repayment or tCO₂e indicators as verified results until finance and climate methodologies are approved.

## Post-import verification

After schema import:

1. Confirm all five tables exist in the target solution.
2. Confirm display names, primary names, ownership, and required columns.
3. Confirm lookup relationships to existing runtime tables.
4. Confirm alternate-key system jobs complete successfully.
5. Confirm no table was created with TACATDP-only names.
6. Confirm no Power Pages Web API setting uses wildcard `*`.
7. Confirm no evidence fields are public-readable.
8. Run a browser read smoke test only for tables intentionally exposed to Power Pages.

## Rollback / containment

If the schema import fails:

- Do not retry with `--force-overwrite` immediately.
- Capture the import log and failed component name.
- Check missing dependency tables and alternate-key constraints.
- If a partial unmanaged import created tables in development, delete only the failed development components after approval and after confirming no data has been entered.

If Power Pages reads fail after permission setup:

- Confirm EntitySetName for the browser route.
- Confirm table logical name for site settings.
- Confirm `Webapi/<table>/fields` includes every `$select`, `$filter`, and lookup shadow field used.
- Confirm table permission and web role association through Power Pages Security workspace.
- Clear/restart portal cache before retesting.

## Definition of done for this runbook

- The approved schema has an execution order.
- Preflight commands are listed.
- Microsoft-specific Power Pages and Dataverse constraints are documented.
- Table-permission scope is intentionally conservative.
- Evidence fields are protected by default.
- Verification and rollback checks are defined before any environment write.
