# Beneficiary bridge schema deployment preflight — 2026-08-13

Status: preflight only. This artifact does not authorize or perform Dataverse schema writes, table permission changes, Power Pages changes, or baseline data import.

## Artifact gate

- Work type: additive Dataverse schema deployment preflight for the TACATDP baseline beneficiary bridge.
- Required artifacts:
  - schema contract;
  - migration plan;
  - approval record;
  - requirements traceability;
  - verification summary;
  - handoff.
- Existing artifacts reused:
  - `schemas/dataverse/platform-tables.json`
  - `schemas/dataverse/platform-columns.csv`
  - `schemas/dataverse/platform-relationships.csv`
  - `schemas/dataverse/platform-alternate-keys.csv`
  - `schemas/dataverse/beneficiary-entity-extension-schema.json`
  - `docs/powerpages-odk-webforms/baseline-dataverse-import-delivery-plan-20260813.md`
- New implementation artifact:
  - `scripts/plan-beneficiary-bridge-schema-deployment.py`
- Runtime dry-run output:
  - `/tmp/tacatdp-beneficiary-bridge-schema-deployment-plan.json`
- Implementation boundary:
  - local schema planning and CRDB read-only inventory only;
  - no Dataverse write;
  - no baseline import;
  - no portal permission or Web API setting change.

## Current CRDB inventory evidence

Target checked with read-only aggregate FetchXML:

| Item | Value |
|---|---|
| Environment name | `TACATDP-CRDB-Dev` |
| Environment ID | `42a3b1e6-8eea-e74a-ae11-3edc41e62d57` |
| PAC identity | `dmuroba@CRDBBANK.CO.TZ` |

Existing runtime prerequisites:

| Table | Current CRDB state |
|---|---|
| `mp_project` | Exists; count 1. |
| `mp_form` | Exists; count 1. |
| `mp_formversion` | Exists; count 1. |
| `mp_formassignment` | Exists; count 10. |
| `mp_formattachment` | Exists; count 1. |
| `mp_submission` | Exists; count 2. |
| `mp_submissionversion` | Exists; count 2. |
| `mp_submissionattachment` | Exists; count 0. |

Missing bridge tables:

| Table | Current CRDB state |
|---|---|
| `mp_trackedentity` | Not found in CRDB metadata. |
| `mp_entityidentifier` | Not found in CRDB metadata. |
| `mp_beneficiaryprofile` | Not found in CRDB metadata. |
| `mp_beneficiarysubmissionlink` | Not found in CRDB metadata. |

## Schema contract

The minimal bridge schema must link imported baseline submissions to durable beneficiary identities while leaving the full workbook payload in the canonical submission-version table.

Proposed minimal slice:

| Table | Source artifact | Purpose |
|---|---|---|
| `mp_TrackedEntity` | `schemas/dataverse/platform-tables.json` | Central monitored entity identity for beneficiaries and future non-beneficiary monitored subjects. |
| `mp_EntityIdentifier` | `schemas/dataverse/platform-tables.json` | Approved identifiers for tracked entities, including source UUID and approved customer/phone identifier treatment. |
| `mp_BeneficiaryProfile` | `schemas/dataverse/beneficiary-entity-extension-schema.json` | Current beneficiary profile projection for list/detail UI and review. |
| `mp_BeneficiarySubmissionLink` | `schemas/dataverse/beneficiary-entity-extension-schema.json` | Lineage link from beneficiary identity/profile back to canonical submission records. |

Excluded from this minimal slice:

| Table | Reason deferred |
|---|---|
| `mp_BeneficiaryIdentityMatch` | Useful for duplicate review, but not required before the first idempotent import dry-run. |
| `mp_BeneficiaryProgrammeParticipation` | Can be derived later when programme participation UI/reporting is Dataverse-backed. |
| `mp_BeneficiaryFinanceLink` | Defer until finance detail is queried outside `mp_SubmissionVersion` JSON. |
| `mp_BeneficiaryTechnologyAdoption` | Defer until technology adoption is queried outside `mp_SubmissionVersion` JSON. |
| `mp_BeneficiaryTrainingParticipation` | Defer until training is queried outside `mp_SubmissionVersion` JSON. |
| `mp_BeneficiaryOutcomeSnapshot` | Defer until KPI/outcome projections are required for the dashboard. |
| `mp_BeneficiaryGroupMembership` | Defer until group/member review is implemented. |
| `mp_BeneficiaryLocationHistory` | Defer until location correction/history is implemented. |

Required relationships in this slice:

| Relationship | Purpose |
|---|---|
| `mp_Project -> mp_TrackedEntity.mp_project` | Project boundary for reusable monitored entities. |
| `mp_TrackedEntity -> mp_EntityIdentifier.mp_trackedentity` | Identifier rows belong to a tracked entity. |
| `mp_TrackedEntity -> mp_BeneficiaryProfile.mp_trackedentity` | One current profile per beneficiary identity. |
| `mp_Project -> mp_BeneficiaryProfile.mp_project` | Profile is project-scoped. |
| `mp_TrackedEntity -> mp_BeneficiarySubmissionLink.mp_trackedentity` | Submission lineage belongs to a beneficiary identity. |
| `mp_Submission -> mp_BeneficiarySubmissionLink.mp_submission` | Link preserves canonical submission source lineage. |

Required alternate keys in this slice:

| Key | Columns | Purpose |
|---|---|---|
| `AK_TrackedEntity_Project_Type_Key` | `mp_project`, `mp_entitytype`, `mp_entitykey` | Idempotent beneficiary identity creation. |
| `AK_EntityIdentifier_Entity_Type_Value` | `mp_trackedentity`, `mp_identifiertype`, `mp_identifiervalue` | Idempotent identifier creation. |
| `AK_BeneficiaryProfile_TrackedEntity` | `mp_trackedentity` | One current beneficiary profile per tracked entity. |
| `AK_BeneficiarySubmissionLink_Key` | `mp_linkkey` | Idempotent source-lineage links. |

The local planner currently reports 36 planned operations:

| Operation type | Count |
|---|---:|
| Create table | 4 |
| Create column | 20 |
| Create lookup relationship | 4 |
| Create relationship record | 4 |
| Create alternate key | 4 |

Before live deployment, the execution script must confirm all four alternate keys above are included or explicitly report why any key is not applicable to the target deployment API.

## Migration plan

Execution is not approved yet. When approved, use this order:

1. Confirm target environment:
   - `TACATDP-CRDB-Dev`
   - environment ID `42a3b1e6-8eea-e74a-ae11-3edc41e62d57`
   - authenticated profile expected to be `dmuroba@CRDBBANK.CO.TZ` or an approved service principal/application user.
2. Rerun read-only inventory for:
   - `mp_project`
   - `mp_submission`
   - `mp_trackedentity`
   - `mp_entityidentifier`
   - `mp_beneficiaryprofile`
   - `mp_beneficiarysubmissionlink`
3. Stop if any target bridge table already exists with conflicting metadata.
4. Create `mp_TrackedEntity`.
5. Create `mp_EntityIdentifier`.
6. Create `mp_BeneficiaryProfile`.
7. Create `mp_BeneficiarySubmissionLink`.
8. Create required relationships and lookup columns.
9. Create required alternate keys.
10. Publish metadata.
11. Rerun inventory and dry-run import plan.
12. Do not import baseline rows until the dry-run import summary is accepted.

Rollback/repair boundary:

- This slice must be additive only.
- Do not delete or rename existing runtime tables.
- If a partially created table exists, stop and document exact metadata state before attempting repair.
- Do not remove tables in CRDB development without explicit destructive-action approval.

## Approval record

Current approval state:

| Action | Approval state |
|---|---|
| Read-only CRDB inventory | Approved and completed. |
| Local schema dry-run planning | Approved and completed. |
| Dataverse schema write | Not approved. |
| Table permission change | Not approved. |
| Power Pages Web API setting change | Not approved. |
| Baseline data import | Not approved. |

Required approval before next execution step:

> Approve additive Dataverse schema deployment to `TACATDP-CRDB-Dev` for only `mp_TrackedEntity`, `mp_EntityIdentifier`, `mp_BeneficiaryProfile`, and `mp_BeneficiarySubmissionLink`, including required relationships and alternate keys.

## Requirements traceability

| Requirement | Evidence | Delivery surface | Verification |
|---|---|---|---|
| Reuse existing form runtime storage. | CRDB inventory shows `mp_submission` and `mp_submissionversion` exist. | No new submission replacement tables planned. | Read-only aggregate inventory. |
| Model beneficiaries as durable entities, not only form rows. | `beneficiary-detail-model-slice-20260811.md`; `beneficiary-entity-extension-schema.json`. | `mp_TrackedEntity`, `mp_BeneficiaryProfile`. | `scripts/validate-beneficiary-entity-schema.mjs`. |
| Preserve source submission lineage. | Baseline import plan and ODK-style runtime contract. | `mp_BeneficiarySubmissionLink`. | Local bridge import dry-run plan. |
| Keep import idempotent. | Baseline workbook has 965 root rows and future reruns are expected. | Alternate keys for tracked entity, identifiers, profile, and submission link. | Schema deployment planner output and pre-execution review. |
| Avoid premature full enterprise schema deployment. | User requested minimal beneficiary entity and baseline import path first. | Only four tables selected; optional/deferred tables excluded. | `/tmp/tacatdp-beneficiary-bridge-schema-deployment-plan.json`. |
| Avoid PII exposure during planning. | Workbook contains beneficiary names, phone numbers, IDs, and location data. | Planner uses schema artifacts and sanitized counts only. | No raw workbook rows or PII committed. |

## Verification commands

```bash
python3 scripts/plan-beneficiary-bridge-schema-deployment.py \
  --repo-root /home/jmduda/KodeX/crdb-mel \
  --output-json /tmp/tacatdp-beneficiary-bridge-schema-deployment-plan.json

python3 scripts/plan-beneficiary-bridge-import.py \
  --baseline-summary /tmp/tacatdp-baseline-import-summary.json \
  --repo-root /home/jmduda/KodeX/crdb-mel \
  --output-json /tmp/tacatdp-beneficiary-bridge-import-plan.json

PYTHONPYCACHEPREFIX=/tmp/tacatdp-pycache python3 -m py_compile \
  scripts/plan-beneficiary-bridge-schema-deployment.py \
  scripts/plan-beneficiary-bridge-import.py

node scripts/validate-beneficiary-entity-schema.mjs

git diff --check
```

## Next action

After review, either:

1. approve additive schema deployment to CRDB development for the four-table bridge slice; or
2. revise the schema contract before any environment write.

## Deployment attempt

The first approved deployment attempt is recorded in `docs/powerpages-odk-webforms/beneficiary-bridge-schema-deployment-attempt-20260813.md`.

The attempt was blocked before any Dataverse write because the CRDB Azure CLI profile was not logged in and the device-code login did not complete. PAC remained authenticated for read-only inventory, but the metadata writer requires a Dataverse Web API access token.
