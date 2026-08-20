# Prototype model design — beneficiary, submission, and indicator projection

Status: review-ready model design. This artifact does not authorize Dataverse schema writes, table-permission changes, Power Pages site-setting changes, baseline import, or deployment.

## Purpose

This document consolidates the current prototype model after baseline import and dashboard KPI projection work.

The design goal is to keep the TACATDP prototype moving without hard-coding TACATDP as the future platform schema.

The core rule is:

> Canonical form submissions remain the evidence source. Beneficiary and dashboard records are projections derived from that evidence.

## Evidence inspected

- `schemas/dataverse/odk-central-inspired-mvp-schema.md`
- `schemas/dataverse/reporting-projection-schema.md`
- `schemas/dataverse/beneficiary-entity-extension-schema.json`
- `docs/powerpages-odk-webforms/beneficiary-dataverse-schema-plan-20260811.md`
- `docs/powerpages-odk-webforms/beneficiary-bridge-schema-deployment-preflight-20260813.md`
- `docs/powerpages-odk-webforms/baseline-bridge-import-dry-run-20260814.md`
- `docs/powerpages-odk-webforms/prototype-acceptance-scope-20260812.md`
- `powerpages/webforms-spa/src/components/dashboard/tacatdpBaselineProjection.ts`
- `powerpages/webforms-spa/src/powerpages-api/client.ts`

## Current model layers

| Layer | Current purpose | Tables / source | Prototype use |
|---|---|---|---|
| Project and form configuration | Defines TACATDP project, form identity, published XForm, assignment, and runtime form access. | `mp_Project`, `mp_Form`, `mp_FormVersion`, `mp_FormAssignment`, `mp_FormAttachment` | Project detail, form loading, collect action, baseline import context. |
| Canonical submission evidence | Stores submitted instance identity and versioned payload. This is the source of truth. | `mp_Submission`, `mp_SubmissionVersion`, `mp_SubmissionAttachment` | Saved records, edit/version flow, lineage for imports and reports. |
| Reporting projection | Stores current row-level report facts derived from canonical submission payloads. | `mp_SubmissionReportRow`, `mp_SubmissionRepeatRow`, `mp_SubmissionAnswer` | Dashboard live KPI projection, reporting table, export path, future Power BI. |
| Beneficiary bridge | Models imported beneficiaries as monitored entities linked back to source submissions. | `mp_TrackedEntity`, `mp_EntityIdentifier`, `mp_BeneficiaryProfile`, `mp_BeneficiarySubmissionLink` | Beneficiary registry, beneficiary detail, duplicate-aware baseline import. |
| Dashboard projection | Calculates prototype KPIs in the browser from report rows until a server-side indicator engine exists. | `mp_rootanswersjson` on report rows plus dashboard aggregate JSON | KPI cards, map, technology chart, loan stage chart, training card. |

## Minimal prototype model

For the current prototype, the minimum durable model is:

```text
mp_Project
  ├─ mp_Form
  │   └─ mp_FormVersion
  │       ├─ mp_FormAssignment
  │       └─ mp_Submission
  │           ├─ mp_SubmissionVersion
  │           └─ mp_SubmissionReportRow
  │               ├─ mp_SubmissionRepeatRow
  │               └─ mp_SubmissionAnswer
  └─ mp_TrackedEntity
      ├─ mp_EntityIdentifier
      ├─ mp_BeneficiaryProfile
      └─ mp_BeneficiarySubmissionLink ── mp_Submission
```

### What each model object owns

| Object | Owns | Does not own |
|---|---|---|
| `mp_SubmissionVersion` | Canonical XForm submission XML/JSON payload version. | Beneficiary master identity, dashboard result truth, duplicate decisions. |
| `mp_SubmissionReportRow` | Current root-level projection for browsing, dashboard, and export. | Raw source truth or identity merge decisions. |
| `mp_TrackedEntity` | Durable monitored entity identity for a farmer, group, AMCOS, SACCOS, organisation, or future non-beneficiary subject. | One-off form payload facts. |
| `mp_EntityIdentifier` | Approved identifiers such as source UUID, customer ID, and phone identifier values where approved. | Raw logs, terminal output, or public display of sensitive identifiers. |
| `mp_BeneficiaryProfile` | Current beneficiary profile projection for list/detail UX. | Historical payload evidence or all longitudinal facts. |
| `mp_BeneficiarySubmissionLink` | Lineage between a beneficiary identity and the source submission that created or updated it. | The source payload itself. |

## Baseline import treatment

The baseline import should remain append/replace capable:

| Mode | Expected behavior |
|---|---|
| Append | Add new canonical submissions and beneficiary candidates without deleting existing approved records. Existing keys are matched where possible. |
| Replace | Replace the current imported baseline projection set for the selected project/form version while preserving canonical lineage and avoiding silent identity merges. |

Current duplicate rule:

- Create one provisional `mp_TrackedEntity` candidate per baseline root row.
- Store approved identifiers in `mp_EntityIdentifier`.
- Do not auto-merge duplicate customer ID or phone candidates.
- Use `mp_BeneficiaryIdentityMatch` later for review workflow when merge/adjudication is implemented.

This matches the dry-run finding that the baseline has 965 root rows, 956 customer-ID rows, and duplicate customer/phone candidates that require review rather than automatic merging.

## Dashboard projection boundary

Dashboard cards must use one of three data classifications:

| Classification | Meaning | UI treatment |
|---|---|---|
| Baseline-supported projection | Calculated from imported baseline report rows. | Show live value with neutral copy such as `Baseline`, `Baseline estimate`, or `Projection`. |
| Demonstration data | Prototype-only value not supported by current imported fields. | Keep labelled as demo/prototype, or remove from the live card. |
| Not available | Required source data does not exist yet. | Show `Pending`, `Needs verification`, or `Not imported`; do not show fake zeroes or trend arrows. |

### Baseline-supported now

| Dashboard area | Current data source | Status |
|---|---|---|
| Beneficiary/profile count | imported beneficiary/report rows | Supported. |
| Submission/report-row count | `mp_SubmissionReportRow` reads | Supported. |
| Reported amount | baseline loan amount fields and `loan_repeat` aggregate | Supported as reported baseline amount. |
| Reported loan count | baseline loan count and aggregate repeat rows | Supported as reported baseline count. |
| Regional map | region plus reported amount/loan/profile/training summaries | Supported. |
| Technologies financed | classified TACATDP technology answers | Supported as categorized projection. |
| Loan financing by stage | value-chain stage answers and loan aggregate stages | Supported as stage selections, not loan-product classification. |
| Farmers trained | `total_trained` and related training counts | Supported. |
| Youth trained | `total_youth_trained` and youth training count fields | Supported as baseline estimate. |
| Recent submissions | report-row update/projected/submitted timestamps | Supported. |

### Not supported from baseline alone

| Dashboard area | Reason |
|---|---|
| Repayment rate | No repayment performance or NPL status fields in baseline import. Requires core banking / loan-servicing source. |
| Performing / at-risk / non-performing loan split | No reliable loan performance status fields in baseline import. Requires approved finance integration. |
| Official tCO₂e avoided | Baseline has climate-related fields, but official calculation requires approved methodology, validation rules, and verification status. |
| True training sessions | Baseline has trained people and training types, not actual session event records. |
| Official monthly disbursement trend | Loan-year/repeat data can support a rough cumulative trend, but official trend requires reliable disbursement dates/source. |

## Next scalable model

The next scalable product model should introduce explicit indicator facts instead of continuing to compute everything in dashboard components.

```text
mp_IndicatorDefinition
  ├─ code
  ├─ name
  ├─ unit
  ├─ formula
  ├─ reporting frequency
  ├─ source field mapping
  ├─ disaggregation rules
  └─ verification method

mp_IndicatorResult
  ├─ project
  ├─ indicator
  ├─ reporting period
  ├─ geography
  ├─ tracked entity or aggregate scope
  ├─ value
  ├─ method: measured / estimated / modelled
  ├─ verification status
  ├─ source submission/report row
  └─ calculated at
```

For prototype delivery, this can remain documented until the team approves the next Dataverse schema slice. The dashboard should continue using `tacatdpBaselineProjection.ts` as a transparent temporary indicator engine.

## Recommended next implementation sequence

1. Finalize the beneficiary bridge model as the current prototype identity model:
   - `mp_TrackedEntity`
   - `mp_EntityIdentifier`
   - `mp_BeneficiaryProfile`
   - `mp_BeneficiarySubmissionLink`
2. Add a duplicate-review surface before any merge behavior:
   - start with read-only duplicate candidates;
   - no auto-merge from customer ID or phone alone.
3. Move dashboard calculations from page component logic into a reusable projection service module:
   - keep the browser implementation for now;
   - make formulas testable with fixture report rows.
4. Define the first `mp_IndicatorDefinition` / `mp_IndicatorResult` schema review artifact:
   - include source field mapping;
   - include method and verification status;
   - do not write tables until approved.
5. Connect finance performance only after CRDB approves the finance/core-banking integration boundary:
   - repayment rate;
   - at-risk loans;
   - non-performing loans;
   - official disbursement dates.

## Acceptance criteria for this model

- The model keeps TACATDP as a project configuration, not the platform schema.
- Canonical submission payloads remain the source of truth.
- Beneficiary identity is represented through `mp_TrackedEntity`, not a TACATDP-only beneficiary table.
- Every beneficiary profile row can be traced to at least one source submission through `mp_BeneficiarySubmissionLink`.
- Dashboard calculations identify whether each metric is baseline-supported, demonstration-only, or unavailable.
- Unsupported KPIs are not shown as official live values.
- Sensitive identifiers are not printed in logs, committed docs, or handoff artifacts.
- Future indicator results include method and verification status before they are treated as official.

## Open decisions

| Decision | Current recommendation |
|---|---|
| Should we create `mp_IndicatorDefinition` and `mp_IndicatorResult` now? | Not yet. Document and review first; current dashboard projection is enough for prototype review. |
| Should duplicate customer IDs be merged automatically? | No. Queue for review; do not auto-merge. |
| Should beneficiary profile become the source of truth? | No. It is a current-state projection derived from submissions and identifiers. |
| Should repayment KPIs be kept in the dashboard? | Keep as clearly demo/pending until approved finance source exists. |
| Should Power BI read canonical submission XML? | No. Power BI should read reporting/indicator projection tables, not canonical payload tables by default. |

## Verification

Run:

```bash
node scripts/validate-prototype-model-design.mjs
node scripts/validate-beneficiary-entity-schema.mjs
npm run test:powerpages-assets
```

Expected result:

- Model-design validator passes.
- Beneficiary schema validator confirms tracked-entity extension rules.
- Power Pages asset/package tests remain green.
