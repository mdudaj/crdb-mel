# Baseline Dataverse schema and import delivery plan — 2026-08-13

Status: planning only. This artifact does not authorize or perform Dataverse schema writes, permission changes, deployment, or baseline data import.

Source workbook:

`/home/jmduda/Downloads/TACATDP/TACATDP_Impact_Data_Tracking_for_Financed_Beneficiaries_-_all_versions_-_English_en_-_2026-08-13-06-12-18.xlsx`

Latest form definition:

`/home/jmduda/Downloads/TACATDP/TACATDP_Tool.xlsx`

Do not commit the workbook or generated raw-row extracts. It contains beneficiary names, phone numbers, customer identifiers, location data, and programme monitoring data.

## Artifact gate

- Work type: data/schema delivery planning for the TACATDP baseline import.
- Existing artifacts reused:
  - `ubongo/projects/crdb-mel/overview.md`
  - `skills/power-pages-odk-webforms/SKILL.md`
  - `docs/powerpages-odk-webforms/beneficiary-dataverse-schema-plan-20260811.md`
  - `schemas/dataverse/odk-central-inspired-mvp-schema.json`
  - `schemas/dataverse/beneficiary-entity-extension-schema.json`
  - `schemas/dataverse/reporting-projection-schema.json`
  - `schemas/dataverse/import-order.md`
  - `schemas/import-templates/*.csv`
  - `/home/jmduda/Downloads/TACATDP/TACATDP_Tool.xlsx`
- New artifact:
  - `docs/powerpages-odk-webforms/baseline-dataverse-import-delivery-plan-20260813.md`
- Implementation boundary:
  - Planning and evidence analysis only.
  - No PAC write, Dataverse schema write, table permission change, site setting change, deployment, or import.
- Required approval before execution:
  - Target environment confirmation.
  - Explicit Dataverse schema-write approval.
  - Explicit baseline-import approval.
  - Confirmation of whether phone/customer identifiers may be imported as plain text, masked values, or hash-only identifiers.

## Workbook evidence

The submitted-data workbook is an XLSX export with one root submission sheet and multiple repeat sheets.

| Sheet | Rows excluding header | Columns | Purpose |
|---|---:|---:|---|
| `TACATDP Impact Data Tracking...` | 965 | 1,307 | Root baseline submission/profile facts. |
| `loan_repeat` | 1,151 | 37 | One or more TACATDP loans per root submission. |
| `vc1_repeat` | 813 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc2_repeat` | 845 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc3_repeat` | 921 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc4_repeat` | 695 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc5_repeat` | 451 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc6_repeat` | 721 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc7_repeat` | 147 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc8_repeat` | 124 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc9_repeat` | 179 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc14_repeat` | 394 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc10_repeat` | 106 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc18_repeat` | 41 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc11_repeat` | 73 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc12_repeat` | 12 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc15_repeat` | 4 | 18 | Production-cost repeat rows for one value-chain stage. |
| `vc13_repeat` | 6 | 18 | Production-cost repeat rows for one value-chain stage. |

Important parsing findings:

- The workbook uses inline strings and sparse cells. Import code must parse cell references, not simple positional lists.
- The root sheet has repeated labels such as `Direct Male Beneficiaries` under different value-chain sections. Import code must preserve column address, generated field key, or source path to avoid overwriting duplicate labels.
- Repeat sheets link back to root rows by `_submission__uuid`, `_submission_meta/rootUuid`, and `_parent_index`.
- The root sheet includes direct fields useful for the prototype:
  - `Customer ID`
  - `Customer Name`
  - `Gender`
  - `Farmer/Beneficiary Age`
  - `age_group`
  - `Education Level`
  - `Zone`
  - `CRDB Branch`
  - `Region`
  - `District`
  - `Ward`
  - `Village`
  - `Farmer's Phone Number`
  - `Since joining TACATDP, how many loans have you received through TACATDP?`
  - `total_loan_amount`
  - `TACATDP ARA Technology Deployed...`
  - `Uses Irrigation?`
  - `Water Source`
  - `Energy Source Baseline`
  - `Energy Source After`
  - `Baseline Yield (kg)`
  - `Yield After Intervention (kg)`
  - `yield_change`
  - `Did individual or farmer group receive ARA training?`
  - `Type of Training Received`
  - `Number of MALE farmers trained`
  - `Number of FEMALE farmers trained`
  - `_uuid`
  - `_submission_time`

## Latest XLSForm evidence

The latest form used to collect the data is `TACATDP_Tool.xlsx`. It must be the field-definition authority for import mapping; the submitted-data export is the row source.

| XLSForm sheet | Rows excluding header | Columns | Purpose |
|---|---:|---:|---|
| `survey` | 609 | 17 | Field definitions, groups, repeats, constraints, calculations, relevance, labels, and hints. |
| `choices` | 1,306 | 10 | Controlled options and cascading choice metadata. |
| `settings` | 1 | 4 | Form identity and version. |

Settings:

| Setting | Value |
|---|---|
| `id_string` | `tacatdp_impact_evaluation` |
| `version` | `2608130924` |
| `default_language` | `Swahili (sw)` |
| `background-geolocation` | `TRUE` |

Survey type counts:

| Type | Count |
|---|---:|
| `integer` | 121 |
| `calculate` | 101 |
| `note` | 93 |
| `select_one` | 71 |
| `decimal` | 58 |
| `begin_group` | 33 |
| `end_group` | 33 |
| `select_multiple` | 27 |
| `text` | 20 |
| `begin_repeat` | 19 |
| `end_repeat` | 19 |
| `datetime` | 2 |
| `select_one_from_file` | 2 |
| `date` | 2 |
| `geopoint` | 1 |

Form repeat groups:

| Repeat name | Label / purpose | Repeat count / relevance |
|---|---|---|
| `loan_repeat` | Loan Details | `${loan_count}` |
| `vc1_repeat` | Stage 1: Farm Preparation beneficiaries | `selected(${vc_stages1},'1')` |
| `vc2_repeat` | Stage 2: Farm Operations beneficiaries | `selected(${vc_stages1},'2')` |
| `vc3_repeat` | Stage 3: Input Supply beneficiaries | `selected(${vc_stages1},'3')` |
| `vc4_repeat` | Stage 4: Weeding / Field Management beneficiaries | `selected(${vc_stages1},'4')` |
| `vc5_repeat` | Stage 5: Pre-harvest / Pest Control beneficiaries | `selected(${vc_stages1},'5')` |
| `vc6_repeat` | Stage 6: Harvesting beneficiaries | `selected(${vc_stages1},'6')` |
| `vc7_repeat` | Stage 7: Post-harvest Handling beneficiaries | `selected(${vc_stages1},'7')` |
| `vc8_repeat` | Stage 8: Storage / Warehousing beneficiaries | `selected(${vc_stages1},'8')` |
| `vc9_repeat` | Stage 9: Crop Transport beneficiaries | `selected(${vc_stages1},'9')` |
| `vc10_repeat` | Stage 10: Value Addition / Processing beneficiaries | `selected(${vc_stages1},'10')` |
| `vc11_repeat` | Stage 11: Aquaculture Production beneficiaries | `selected(${vc_stages1},'11')` |
| `vc12_repeat` | Stage 12: Fisheries Landing beneficiaries | `selected(${vc_stages1},'12')` |
| `vc13_repeat` | Stage 13: Aquaponics Systems beneficiaries | `selected(${vc_stages1},'13')` |
| `vc14_repeat` | Stage 14: Marketing / Trading beneficiaries | `selected(${vc_stages1},'14')` |
| `vc15_repeat` | Stage 15: Consumption / User beneficiaries | `selected(${vc_stages1},'15')` |
| `vc16_repeat` | Stage 16: Trainers & Trainees beneficiaries | `selected(${vc_stages1},'16')` |
| `vc17_repeat` | Stage 17: Farmer group collective engagement in ARA/CSA capacity building and adoption | `selected(${vc_stages1},'17')` |
| `vc18_repeat` | Stage 18: Other value-chain activity beneficiaries | `selected(${vc_stages1},'18')` |

Large controlled lists in the form:

| Choice list | Rows |
|---|---:|
| `branch` | 240 |
| `district` | 195 |
| `crop_adaptation` | 124 |
| `crop_name` | 123 |
| `intervention` | 36 |
| `cost_item` | 33 |
| `region` | 31 |
| `unit_measure` | 31 |
| `adaptation_result` | 28 |
| `RA` | 28 |
| `technology` | 21 |
| `climate_risk` | 21 |
| `adaptation` | 21 |
| `additional` | 21 |
| `SDGs` | 21 |
| `collateral` | 21 |

Import planning consequences:

- `TACATDP_Tool.xlsx` defines the stable field names such as `Customer_Name`, `Gender`, `age`, `region`, `district`, `ward`, `village`, `Farmer_Phone`, `loan_repeat`, `loan_amount`, `loan_year`, `technology`, `Uses_Irrigation`, `ara_training`, and value-chain beneficiary fields.
- The export uses labels as column headers, so the importer must map export labels back to XLSForm `survey.name` keys before writing normalized payloads.
- The form has 19 repeat groups, but the current submitted-data export contains `loan_repeat` and only some `vc*_repeat` sheets. The importer must tolerate repeat groups with no exported rows.
- `select_one_from_file` fields `ward` and `village` require external CSV choice files in the collection runtime. For the first import, store raw ward/village values and labels as snapshots unless the approved Dataverse village reference table is already deployed and verified.
- The `choices` sheet should seed governed vocabulary/reference data where practical, but high-cardinality or cascading choices should not be flattened into hard-coded Dataverse choices.

## Recommended minimal schema boundary

Use a two-layer import model:

1. Canonical source-of-truth rows preserve the submitted workbook evidence.
2. Beneficiary projection rows support the prototype UI, dashboard, and later reporting.

Do not create a TACATDP-only beneficiary identity table. Continue with the existing decision to model beneficiaries as tracked entities.

### Current runtime inventory

The Power Pages form runtime already uses the canonical ODK-style submission tables. Do not recreate them for the baseline import.

Repo/runtime evidence:

| Existing capability | Evidence |
|---|---|
| Runtime writes submission headers | `powerpages/webforms-spa/src/powerpages-api/client.ts` calls `createRecord('/_api/mp_submissions', ...)`. |
| Runtime writes immutable/current submission versions | `client.ts` calls `createRecord('/_api/mp_submissionversions', ...)`. |
| Runtime stores XML and JSON payloads | `mp_xformsubmissionxml` and `mp_submissionjson` are written by `createSubmissionVersion`. |
| Runtime links version rows to submission rows | `createSubmissionVersion` writes `mp_Submission@odata.bind`. |
| Runtime supports multiple versions per instance | `nextSubmissionVersionNumber()` queries `mp_submissionversions` by `mp_instanceid`. |
| Runtime reads latest saved version | `getLatestSubmissionVersionByInstanceId()` queries `mp_submissionversions` ordered by `mp_versionnumber`. |
| Power Pages Web API/table-permission plan includes these tables | `scripts/powerpages-configure-webapi.py` includes `mp_submission`, `mp_submissionversion`, and `mp_submissionattachment`. |

Inventory conclusion:

- `mp_Project`, `mp_Form`, `mp_FormVersion`, `mp_FormAssignment`, `mp_Submission`, `mp_SubmissionVersion`, and `mp_SubmissionAttachment` are part of the existing runtime architecture.
- The baseline import should seed or update records in those existing tables, not introduce replacement tables.
- Before execution, run a read-only CRDB environment inventory to confirm the deployed state and current row counts.

### Existing canonical tables to use

Use the existing ODK Central-inspired runtime tables. The imported KoboToolbox baseline should be represented as if it had been submitted through the current runtime, preserving source metadata. The canonical form identity should use:

- `XmlFormId`: `tacatdp_impact_evaluation`
- `Version`: `2608130924`
- `Name`: TACATDP baseline/impact tracking form

| Existing table | Baseline import use |
|---|---|
| `mp_Project` | Confirm or seed TACATDP project container. |
| `mp_Form` | Confirm or seed form identity for `tacatdp_impact_evaluation`. |
| `mp_FormVersion` | Import/seed latest XLSForm version `2608130924` from `TACATDP_Tool.xlsx`. |
| `mp_Submission` | Import one row per KoboToolbox root workbook submission using `_uuid` as `mp_instanceid`. |
| `mp_SubmissionVersion` | Import immutable payload version containing normalized JSON for the root row plus linked repeat metadata. |
| `mp_SubmissionAttachment` | Defer unless source media files are available and approved. |

The first import does not require `mp_SubmissionAttachment` unless media files are available and approved.

### Required beneficiary/entity bridge tables

Create or confirm the minimal subset needed to link collected baseline submissions to durable beneficiary profiles. These tables are the target schema slice.

| Table | Minimal use in this slice |
|---|---|
| `mp_TrackedEntity` | One beneficiary identity per imported customer/submission candidate. |
| `mp_EntityIdentifier` | Store approved external identifiers such as customer ID, import UUID, and optionally masked phone. |
| `mp_BeneficiaryProfile` | Current profile for list/detail views: name, category, region, district, ward/village snapshots, demographic summary, verification status. |
| `mp_BeneficiarySubmissionLink` | Lineage from each projection row back to the canonical submission. |
| `mp_BeneficiaryIdentityMatch` | Optional review queue for likely duplicates; do not auto-merge. |

Defer `mp_BeneficiaryProgrammeParticipation`, `mp_BeneficiaryFinanceLink`, `mp_BeneficiaryTechnologyAdoption`, `mp_BeneficiaryTrainingParticipation`, `mp_BeneficiaryOutcomeSnapshot`, `mp_BeneficiaryGroupMembership`, `mp_BeneficiaryLocationHistory`, full production-cost normalization, and geography reference binding unless they are required for the next prototype screen.

The immediate beneficiary target is intentionally narrow:

```text
KoboToolbox baseline export
  ↓
existing mp_Submission / mp_SubmissionVersion
  ↓
mp_BeneficiarySubmissionLink
  ↓
mp_TrackedEntity + mp_EntityIdentifier + mp_BeneficiaryProfile
```

The collection tool and future follow-up forms should only need the beneficiary/entity ID plus normal submission metadata. The full answer payload remains in `mp_SubmissionVersion`; current beneficiary profile fields live in `mp_BeneficiaryProfile`.

## Schema adjustments required before import

The current `beneficiary-entity-extension-schema.json` is close, but the baseline import needs a small review before environment write:

1. Add or confirm profile fields for:
   - gender;
   - age years;
   - age group;
   - education level;
   - zone;
   - branch;
   - ward snapshot;
   - village snapshot;
   - data-verification/import status.
2. Add or confirm finance fields for:
   - loan year;
   - total number of TACATDP loans;
   - value-chain stages financed;
   - primary value-chain stage.
3. Add or confirm outcome fields can store:
   - indicator code;
   - value;
   - unit;
   - reporting period;
   - measurement method;
   - verification status;
   - source field key.
4. Confirm whether `Farmer's Phone Number` and `Customer ID` may be stored:
   - as plain text;
   - masked;
   - hash-only;
   - or excluded from the first import.

## Import mapping

### Root submission sheet

| Source field | Target |
|---|---|
| `_uuid` | `mp_Submission.mp_instanceid`; `mp_EntityIdentifier` type `source_uuid`. |
| `_submission_time` | `mp_Submission.mp_submittedat`; `mp_SubmissionVersion.mp_createdon/import timestamp` equivalent. |
| full root row JSON | `mp_SubmissionVersion.mp_submissionjson`, normalized with XLSForm `survey.name` keys where possible and retaining source labels/column addresses for traceability. |
| `Customer ID` | `mp_EntityIdentifier` type `customer_id`, subject to privacy decision. |
| `Customer Name` | `mp_TrackedEntity.mp_displayname`; `mp_BeneficiaryProfile.mp_name`. |
| `Gender`, `Farmer/Beneficiary Age`, `age_group`, `Education Level` | `mp_BeneficiaryProfile` demographic fields after schema confirmation. |
| `Zone`, `CRDB Branch`, `Region`, `District`, `Ward`, `Village` | `mp_BeneficiaryProfile` location/branch snapshots. |
| `Farmer's Phone Number` | `mp_EntityIdentifier` type `phone`, masked/hash-only unless plain text is explicitly approved. |
| `Since joining TACATDP... loans`, `total_loan_amount` | Keep in `mp_SubmissionVersion.mp_submissionjson` for the first slice; normalize to `mp_BeneficiaryFinanceLink` later only when the UI/dashboard needs finance facts outside the raw payload. |
| `TACATDP ARA Technology Deployed...` | Keep in `mp_SubmissionVersion.mp_submissionjson` for the first slice; normalize to `mp_BeneficiaryTechnologyAdoption` later only when technology facts are needed outside the raw payload. |
| `Did individual or farmer group receive ARA training?`, `Type of Training Received`, training counts | Keep in `mp_SubmissionVersion.mp_submissionjson` for the first slice; normalize to `mp_BeneficiaryTrainingParticipation` later only when training facts are needed outside the raw payload. |
| yield/water/energy fields | Keep in `mp_SubmissionVersion.mp_submissionjson` for the first slice; normalize to `mp_BeneficiaryOutcomeSnapshot` later only when KPI/outcome facts are needed outside the raw payload. |

### `loan_repeat`

| Source field | Target |
|---|---|
| `_submission__uuid` / `_submission_meta/rootUuid` | Join to `mp_Submission`. |
| `What was the amount (TZS) of this loan?` | `mp_BeneficiaryFinanceLink.mp_disbursedamount`. |
| `In what year was this loan received?` | Proposed finance field `mp_loanyear`. |
| `Which agricultural value chain stages were financed by this loan?` | Proposed finance field `mp_valuechainstages`. |
| `What was the primary agricultural value chain stage financed by this loan?` | Proposed finance field `mp_primaryvaluechainstage`. |

### `vc*_repeat`

Defer full import in the first slice unless the current prototype needs production-cost detail. If included later:

| Source field | Target |
|---|---|
| `_submission__uuid` / `_submission_meta/rootUuid` | Join to `mp_Submission`. |
| `Production cost item` | Production-cost line item label. |
| `Unit of measure` | Unit label. |
| `Quantity` | Quantity decimal. |
| `Unit cost (TZS)` | Unit cost currency/decimal. |
| `vc*_subtotal` | Subtotal currency/decimal. |

## Proposed delivery sequence

### Step 1 — Local import planner

Create a no-write workbook planner script:

```bash
python3 scripts/plan-baseline-workbook-import.py \
  --xlsform "/home/jmduda/Downloads/TACATDP/TACATDP_Tool.xlsx" \
  --workbook "/home/jmduda/Downloads/TACATDP/TACATDP_Impact_Data_Tracking_for_Financed_Beneficiaries_-_all_versions_-_English_en_-_2026-08-13-06-12-18.xlsx" \
  --summary-json /tmp/tacatdp-baseline-import-summary.json
```

The script must:

- use only Python standard library unless package installation is approved;
- parse XLSX via zipped XML or use an approved dependency later;
- parse the XLSForm `survey`, `choices`, and `settings` sheets;
- map export label columns to XLSForm field names;
- report unmapped export columns and XLSForm fields missing from the export;
- preserve duplicate headers by assigning stable source field keys;
- generate a sanitized summary with counts, sheet names, mapped-field coverage, duplicate-candidate counts, and validation issues;
- avoid writing PII to repo artifacts.

### Step 2 — Schema preflight

Run the local beneficiary bridge planner:

```bash
python3 scripts/plan-beneficiary-bridge-import.py \
  --baseline-summary /tmp/tacatdp-baseline-import-summary.json \
  --repo-root . \
  --output-json /tmp/tacatdp-beneficiary-bridge-import-plan.json
```

Then run dry-run schema plans and split results into existing runtime tables versus beneficiary/entity bridge tables:

```bash
python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/odk-central-inspired-mvp-schema.json
python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/beneficiary-entity-extension-schema.json
python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/reporting-projection-schema.json
```

Before any live write, verify target:

```bash
source scripts/use-powerplatform-env.sh crdb
pac auth who
pac pages list --environment "$POWER_PLATFORM_ENVIRONMENT_URL"
pac solution list --environment "$POWER_PLATFORM_ENVIRONMENT_URL"
```

### Step 3 — Schema deployment, after approval

Deploy only missing additive beneficiary/entity bridge schema. Do not delete or rename existing Dataverse objects.

Recommended order:

1. Confirm existing runtime tables and current row counts.
2. Seed latest `mp_FormVersion` from `TACATDP_Tool.xlsx` if not already present.
3. Create or confirm `mp_TrackedEntity` and `mp_EntityIdentifier`.
4. Create or confirm `mp_BeneficiaryProfile`.
5. Create or confirm `mp_BeneficiarySubmissionLink`.
6. Add only the alternate keys required for idempotent import.
7. Publish metadata.
8. Defer reporting projection tables unless the dashboard/reporting route will query them immediately.

### Step 4 — Dry-run import

Create a no-write importer mode:

```bash
python3 scripts/import-tacatdp-baseline-workbook.py \
  --xlsform "/home/jmduda/Downloads/TACATDP/TACATDP_Tool.xlsx" \
  --workbook "/home/jmduda/Downloads/TACATDP/TACATDP_Impact_Data_Tracking_for_Financed_Beneficiaries_-_all_versions_-_English_en_-_2026-08-13-06-12-18.xlsx" \
  --env crdb \
  --dry-run \
  --summary-json /tmp/tacatdp-baseline-import-dry-run.json
```

Dry run must report:

- root rows read;
- repeat rows read;
- rows skipped;
- rows that would create or match existing `mp_Submission`;
- rows that would create `mp_SubmissionVersion`;
- rows that would create or match `mp_TrackedEntity`;
- rows that would create `mp_BeneficiaryProfile`;
- rows that would create `mp_BeneficiarySubmissionLink`;
- duplicate identity candidates;
- missing required source fields;
- invalid numeric/date fields;
- privacy-sensitive fields detected.

### Step 5 — Import execution, after approval

Run execution only after the dry-run summary is accepted:

```bash
python3 scripts/import-tacatdp-baseline-workbook.py \
  --xlsform "/home/jmduda/Downloads/TACATDP/TACATDP_Tool.xlsx" \
  --workbook "/home/jmduda/Downloads/TACATDP/TACATDP_Impact_Data_Tracking_for_Financed_Beneficiaries_-_all_versions_-_English_en_-_2026-08-13-06-12-18.xlsx" \
  --env crdb \
  --execute \
  --batch-size 50
```

Import must be idempotent:

- Use `_uuid` as the source submission key.
- Use alternate keys for canonical submission and projection rows.
- Do not overwrite manually reviewed beneficiary data without an explicit `--update-reviewed` flag.
- Store import batch ID and source workbook hash in created records where supported.
- Log failed rows to `/tmp` or another non-repo runtime path unless a sanitized failure summary is explicitly requested.

### Step 6 — Post-import verification

Verify counts by Dataverse query:

- `mp_Submission`: expected up to 965 root submissions.
- `mp_SubmissionVersion`: expected up to 965 current source payload rows.
- `mp_TrackedEntity`: expected up to 965 candidate beneficiary identities, less if approved matching merges records.
- `mp_BeneficiaryProfile`: expected up to 965 profiles.
- `mp_BeneficiarySubmissionLink`: expected up to 965 source-lineage links.

Deferred normalized fact counts:

- `mp_BeneficiaryFinanceLink`: later, when finance detail is needed outside raw submission payloads.
- `mp_BeneficiaryTechnologyAdoption`: later, when technology adoption is needed outside raw submission payloads.
- `mp_BeneficiaryTrainingParticipation`: later, when training is needed outside raw submission payloads.
- `mp_BeneficiaryOutcomeSnapshot`: later, when KPI/outcome facts are needed outside raw submission payloads.

Verify portal/dashboard impact:

- Beneficiaries route can load Dataverse-backed records.
- Beneficiary detail route shows imported profile, finance, technology, training, and outcome facts.
- Dashboard prototype can switch from static demo data to imported baseline aggregates only after labels clearly state baseline/demo status.

## Acceptance criteria

The delivery is acceptable when:

- Schema writes are additive and scoped to the CRDB development environment.
- Raw workbook rows are preserved in canonical submission-version payloads.
- Beneficiary projections remain linked to source submissions.
- Duplicate beneficiary candidates are flagged, not silently merged.
- Privacy-sensitive fields are either excluded, masked, hashed, or explicitly approved for storage.
- Dry-run and execution summaries reconcile with workbook sheet counts.
- Import is idempotent and safe to rerun.
- No raw workbook, PII extract, token, `.env`, or secret is committed.

## Open decisions before execution

1. Confirm target environment: CRDB development first, not Mshirika.
2. Confirm whether this import should populate only CRDB or both CRDB and Mshirika for preview.
3. Confirm whether `Customer ID` may be stored as plain text.
4. Confirm whether `Farmer's Phone Number` may be stored as plain text, masked, hash-only, or excluded.
5. Confirm whether `loan_repeat` should stay only inside `mp_SubmissionVersion` JSON for the first slice.
6. Confirm whether production-cost repeat sheets should stay only inside `mp_SubmissionVersion` JSON for the first slice.
7. Confirm whether the portal should query `mp_BeneficiaryProfile` immediately after import or after a separate frontend binding slice.
8. Confirm whether `TACATDP_Tool.xlsx` version `2608130924` should be seeded as the canonical `FormVersion` for this import.

## Immediate next task

Implement the local no-write workbook planner and schema/import dry-run scripts first. Do not run live Dataverse writes until the dry-run output and privacy decisions are approved.

## Delivery evidence — beneficiary bridge preflight

Date: 2026-08-13.

Scope completed:

- Added a no-write baseline workbook planner.
- Added a no-write beneficiary bridge import planner.
- Ran local schema dry-runs for the runtime schema and beneficiary extension schema.
- Ran read-only aggregate CRDB environment inventory using `pac org fetch`.

No Dataverse schema writes, table permission changes, deployment actions, or data imports were performed.

### Local dry-run outputs

Generated runtime files:

| Runtime output | Purpose |
|---|---|
| `/tmp/tacatdp-baseline-import-summary.json` | Sanitized baseline workbook/XLSForm summary. |
| `/tmp/tacatdp-beneficiary-bridge-import-plan.json` | Sanitized beneficiary bridge import plan. |
| `/tmp/tacatdp-runtime-schema-plan.json` | Runtime schema dry-run plan. |
| `/tmp/tacatdp-beneficiary-schema-plan.json` | Beneficiary extension schema dry-run plan. |

Dry-run findings:

| Finding | Result |
|---|---:|
| Root baseline rows planned | 965 |
| `loan_repeat` rows observed | 1,151 |
| Identity-match candidate rows flagged for review | 22 |
| Local runtime tables tied to schema artifact | Yes |
| Local beneficiary bridge tables tied to schema artifact | Yes |
| Raw PII included in dry-run output | No |
| Raw workbook rows included in dry-run output | No |
| Dataverse writes performed | No |

### CRDB read-only inventory

Target checked:

| Item | Value |
|---|---|
| Environment name | `TACATDP-CRDB-Dev` |
| Environment ID | `42a3b1e6-8eea-e74a-ae11-3edc41e62d57` |
| PAC identity | `dmuroba@CRDBBANK.CO.TZ` |

Runtime table counts:

| Dataverse table | Current CRDB count | Inventory result |
|---|---:|---|
| `mp_project` | 1 | Exists |
| `mp_form` | 1 | Exists |
| `mp_formversion` | 1 | Exists |
| `mp_formassignment` | 10 | Exists |
| `mp_formattachment` | 1 | Exists |
| `mp_submission` | 2 | Exists |
| `mp_submissionversion` | 2 | Exists |
| `mp_submissionattachment` | 0 | Exists |

Beneficiary bridge table inventory:

| Dataverse table | Current CRDB state |
|---|---|
| `mp_trackedentity` | Not found in CRDB metadata. |
| `mp_beneficiaryprofile` | Not found in CRDB metadata. |
| `mp_beneficiarysubmissionlink` | Not found in CRDB metadata. |

Inventory conclusion:

- The CRDB environment already has the form runtime tables used by the current Power Pages runtime.
- The baseline import should reuse the existing runtime tables, not recreate them.
- The minimal beneficiary bridge schema is not yet deployed to CRDB.
- The next approved schema slice should be additive: deploy only the missing bridge tables and required keys/relationships, then rerun dry-run import before execution.
- The detailed additive schema preflight is recorded in `docs/powerpages-odk-webforms/beneficiary-bridge-schema-deployment-preflight-20260813.md`.

### Verification commands run

```bash
python3 scripts/plan-baseline-workbook-import.py \
  --xlsform "/home/jmduda/Downloads/TACATDP/TACATDP_Tool.xlsx" \
  --workbook "/home/jmduda/Downloads/TACATDP/TACATDP_Impact_Data_Tracking_for_Financed_Beneficiaries_-_all_versions_-_English_en_-_2026-08-13-06-12-18.xlsx" \
  --summary-json /tmp/tacatdp-baseline-import-summary.json

python3 scripts/plan-beneficiary-bridge-import.py \
  --baseline-summary /tmp/tacatdp-baseline-import-summary.json \
  --repo-root /home/jmduda/KodeX/crdb-mel \
  --output-json /tmp/tacatdp-beneficiary-bridge-import-plan.json

python3 scripts/dataverse-schema-plan.py \
  --schema-file schemas/dataverse/odk-central-inspired-mvp-schema.json \
  --json > /tmp/tacatdp-runtime-schema-plan.json

python3 scripts/dataverse-schema-plan.py \
  --schema-file schemas/dataverse/beneficiary-entity-extension-schema.json \
  --json > /tmp/tacatdp-beneficiary-schema-plan.json

PYTHONPYCACHEPREFIX=/tmp/tacatdp-pycache python3 -m py_compile \
  scripts/plan-baseline-workbook-import.py \
  scripts/plan-beneficiary-bridge-import.py

node scripts/validate-beneficiary-entity-schema.mjs

git diff --check
```

CRDB inventory was executed with aggregate FetchXML only. The query output was redirected to `/tmp` files and summarized without retrieving or printing beneficiary rows.
