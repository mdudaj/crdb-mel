# Indicator and evidence schema

Status: review-only schema artifact. This document does not authorize Dataverse table creation, table-permission changes, Power Pages site-setting changes, imports, or deployment.

## Purpose

This schema moves the next MEL design step out of dashboard code and into a reviewable Dataverse model. It defines the minimum objects needed for governed indicator definitions, source-field mapping, observations, evidence, and calculated indicator results.

TACATDP remains the first configured project. The schema must still support broader CRDB Sustainable Finance MEL use cases without adding TACATDP-only indicator or beneficiary tables.

## Evidence inspected

- `docs/powerpages-odk-webforms/prototype-model-design-20260820.md`
- `schemas/dataverse/beneficiary-entity-extension-schema.json`
- `schemas/dataverse/reporting-projection-schema.md`
- `schemas/dataverse/odk-central-inspired-mvp-schema.md`
- `powerpages/webforms-spa/src/components/dashboard/tacatdpBaselineProjection.ts`
- `docs/powerpages-odk-webforms/automatic-projection-refresh-research.md`
- `skills/power-pages-odk-webforms/SKILL.md`

## Model boundary

Canonical submissions and imported report rows remain the evidence source. The indicator model is an additive projection layer:

```text
Form / import / integration source
  -> mp_Submission / mp_SubmissionVersion
  -> mp_SubmissionReportRow
  -> mp_Observation
  -> mp_IndicatorResult
  -> dashboard, reports, Power BI
```

Dashboard components can continue to calculate prototype values temporarily, but the durable target is that dashboards read `mp_IndicatorResult` rows with method, verification status, source summary, and calculation timestamp.

## Proposed tables

| Table | Purpose | Key fields |
|---|---|---|
| `mp_IndicatorDefinition` | Defines each KPI/indicator as metadata. | `mp_code`, `mp_name`, `mp_indicatortype`, `mp_unit`, `mp_formula`, `mp_reportingfrequency`, `mp_disaggregationjson`, `mp_verificationmethod`, `mp_status`. |
| `mp_DataSourceMapping` | Maps source fields or integrations to indicator inputs. | `mp_mappingkey`, `mp_indicatordefinition`, `mp_sourcetype`, `mp_sourcetable`, `mp_sourcecolumn`, `mp_sourcepath`, `mp_transformrule`, `mp_required`, `mp_active`. |
| `mp_Observation` | Stores one atomic reported/measured/imported/estimated/modelled input value. | `mp_observationkey`, `mp_project`, `mp_trackedentity`, `mp_submission`, `mp_submissionreportrow`, `mp_datasourcemapping`, `mp_valuedecimal`, `mp_valuetext`, `mp_method`, `mp_qualitystatus`. |
| `mp_Evidence` | Links supporting payloads, GPS/photo/document references, timestamps, hashes, and verification state. | `mp_evidencekey`, `mp_project`, `mp_observation`, `mp_indicatorresult`, `mp_submission`, `mp_evidencetype`, `mp_uriorfilereference`, `mp_hash`, `mp_verificationstatus`. |
| `mp_IndicatorResult` | Stores dashboard/report/Power BI-ready indicator facts. | `mp_resultkey`, `mp_project`, `mp_indicatordefinition`, `mp_reportingperiod`, `mp_geography`, `mp_trackedentity`, `mp_value`, `mp_method`, `mp_verificationstatus`, `mp_sourcesummaryjson`, `mp_calculatedat`. |

## Design rules

- Do not compute official indicators directly in dashboard components.
- Do not treat `mp_IndicatorResult` as source truth; results are derived facts with lineage.
- Do not combine measured, imported, estimated, modelled, or verified values without exposing method and verification status.
- Do not store secrets, bearer URLs, or raw sensitive identifiers in `mp_uriorfilereference`, `mp_sourcesummaryjson`, or public logs.
- Keep project scope explicit through `mp_project`; future enterprise indicators may be reusable, but project-specific results and observations must be scoped.
- Keep TACATDP technology, geography, crop, borrower, sex, youth, and partner dimensions as disaggregation metadata or governed references, not hard-coded dashboard branches.

## Initial implementation order after approval

1. Create `mp_IndicatorDefinition`.
2. Create `mp_DataSourceMapping`.
3. Create `mp_Observation`.
4. Create `mp_IndicatorResult`.
5. Create `mp_Evidence`.
6. Add alternate keys after columns exist.
7. Add table permissions and Power Pages Web API fields only for the surfaces that need browser reads.
8. Move calculation from browser projection to approved Power Automate or service-owned Dataverse automation.

This order keeps the definition and mapping catalogue available before generated observations/results are created.

## Prototype mapping candidates

| Current dashboard area | Future indicator model treatment |
|---|---|
| Beneficiary/profile count | `mp_IndicatorDefinition` for active/imported beneficiary count; `mp_IndicatorResult` aggregate by project, region, and period. |
| Reported amount | Financial indicator with mapping to baseline loan amount/report-row fields; method should remain `Imported` or `Reported` until finance source is approved. |
| Regional map | Indicator results grouped by geography, backed by observations derived from report rows and source region fields. |
| Technologies financed | Output indicator grouped by technology category; mapping should point to classified baseline technology fields. |
| Farmers/youth trained | Output indicators with source mappings to training fields; true training-session indicators remain unavailable until session records exist. |
| Climate outcomes | Estimated/modelled indicators only after SFU approves formulas, assumptions, and verification method. |
| Repayment and loan performance | Keep unavailable/demo until approved finance/core-banking integration supplies servicing status. |

## Permission considerations

For future browser reads, Power Pages Web API field settings must include every selected/filter/bound field. For future browser writes, table permissions must include create/write/append privileges on the source table and append-to privileges on referenced lookup tables. Evidence references should be read-restricted because they may point to field photos, GPS, signatures, or sensitive supporting documents.

For scheduled calculations, prefer an approved application user/service principal or Power Automate owner instead of privileged browser-side logic.

## Verification

Run:

```bash
node scripts/validate-indicator-evidence-schema.mjs
node scripts/validate-prototype-model-design.mjs
```

Expected result:

- The schema is marked review-only and environment-write false.
- The five required indicator/evidence tables exist.
- Required fields, relationships, and alternate keys exist.
- The model-design document links to this schema artifact.
