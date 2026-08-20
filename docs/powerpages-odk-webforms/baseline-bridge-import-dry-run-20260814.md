# Baseline bridge import dry-run — 2026-08-14

Status: dry-run completed. No Dataverse data writes were performed.

## Purpose

Plan the import of the latest Kobo baseline export into the minimal beneficiary
bridge schema deployed to Mshirika.

This step validates import scope, row counts, duplicate candidates, privacy
decisions, and target tables before inserting any baseline records.

## Inputs

| Input | File |
|---|---|
| Latest XLSForm | `/home/jmduda/Downloads/TACATDP/TACATDP_Tool.xlsx` |
| Latest Kobo export | `/home/jmduda/Downloads/TACATDP/TACATDP_Impact_Data_Tracking_for_Financed_Beneficiaries_-_all_versions_-_English_en_-_2026-08-13-06-12-18.xlsx` |

XLSForm identity:

| Item | Value |
|---|---|
| Form ID | `tacatdp_impact_evaluation` |
| Version | `2608130924` |

## Runtime outputs

| Output | Purpose |
|---|---|
| `/tmp/tacatdp-baseline-import-summary-20260814.json` | Sanitized workbook/XLSForm summary. |
| `/tmp/tacatdp-beneficiary-bridge-import-plan-20260814.json` | Sanitized beneficiary bridge import plan. |

The runtime outputs intentionally exclude raw beneficiary names, phone numbers,
customer IDs, and row payloads.

## Dry-run findings

| Finding | Result |
|---|---:|
| Root baseline rows | 965 |
| `loan_repeat` rows | 1,151 |
| Kobo `_uuid` rows | 965 |
| Duplicate `_uuid` values | 0 |
| Customer ID rows present | 956 |
| Customer ID duplicate values | 8 |
| Customer ID rows in duplicate groups | 22 |
| Phone rows present | 965 |
| Phone duplicate values | 2 |
| Phone rows in duplicate groups | 4 |

## Planned idempotent actions

| Target | Planned action | Expected rows |
|---|---|---:|
| `mp_Project` | Confirm or seed TACATDP project. | 1 |
| `mp_Form` | Confirm or seed form record. | 1 |
| `mp_FormVersion` | Confirm or seed XLSForm version `2608130924`. | 1 |
| `mp_Submission` | Create or match by Kobo instance/source ID. | 965 |
| `mp_SubmissionVersion` | Store normalized baseline payload. | 965 |
| `mp_TrackedEntity` | Create one provisional beneficiary identity candidate per root row before duplicate adjudication. Final resolved beneficiary count may be lower after review. | up to 965 |
| `mp_EntityIdentifier` | Create approved source UUID, Customer ID, and Farmer Phone Number identifier rows. Raw values must not be printed in logs/reports. | at least 2,886 |
| `mp_BeneficiaryProfile` | Create/update current beneficiary profile projection for provisional/resolved beneficiary identities. | up to 965 |
| `mp_BeneficiarySubmissionLink` | Create lineage link from beneficiary candidate to submission. | 965 |
| `mp_BeneficiaryIdentityMatch` | Optional review records for duplicate identity candidates. | 22 |

## Mshirika schema readiness

The previous schema deployment verified the four bridge tables in Mshirika:

| Table | Verification |
|---|---|
| `mp_trackedentity` | Exists; FetchXML count returned `0`. |
| `mp_entityidentifier` | Exists; FetchXML count returned `0`. |
| `mp_beneficiaryprofile` | Exists; FetchXML count returned `0`. |
| `mp_beneficiarysubmissionlink` | Exists; FetchXML count returned `0`. |

Count `0` is expected because schema was deployed before baseline data import.

## Identity governance before live import

Customer ID and Farmer Phone Number are approved identifiers for this
CRDB-controlled MEL environment. The platform is hosted in the CRDB/Microsoft
environment for that reason.

The live import must still preserve these controls:

1. Customer ID and Farmer Phone Number may be stored as identifiers in Dataverse.
2. Raw Customer ID and Farmer Phone Number values must not be printed in terminal logs, JSON summaries, markdown reports, commits, or handoff artifacts.
3. Duplicate customer/phone candidates remain review-only and are not auto-merged.
4. One provisional tracked-entity candidate per Kobo root row is acceptable before duplicate adjudication.
5. The baseline import remains schema/data-only and does not change Power Pages table permissions.

## Commands run

```bash
python3 scripts/plan-baseline-workbook-import.py \
  --xlsform /home/jmduda/Downloads/TACATDP/TACATDP_Tool.xlsx \
  --workbook /home/jmduda/Downloads/TACATDP/TACATDP_Impact_Data_Tracking_for_Financed_Beneficiaries_-_all_versions_-_English_en_-_2026-08-13-06-12-18.xlsx \
  --summary-json /tmp/tacatdp-baseline-import-summary-20260814.json

python3 scripts/plan-beneficiary-bridge-import.py \
  --baseline-summary /tmp/tacatdp-baseline-import-summary-20260814.json \
  --repo-root /home/jmduda/KodeX/crdb-mel \
  --output-json /tmp/tacatdp-beneficiary-bridge-import-plan-20260814.json
```

## Next implementation slice

Build the live baseline import command in no-automerge mode:

- upsert `mp_Submission` and `mp_SubmissionVersion`;
- create one `mp_TrackedEntity` candidate per root row;
- create source UUID, Customer ID, and Farmer Phone Number `mp_EntityIdentifier` rows;
- create `mp_BeneficiaryProfile` projection rows;
- create `mp_BeneficiarySubmissionLink` lineage rows;
- queue duplicate customer/phone candidates for review without auto-merging them.
