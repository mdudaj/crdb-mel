# Baseline bridge payload dry-run — 2026-08-14

Status: payload dry-run completed. No Dataverse data writes were performed.

## Scope

This slice added a dry-run import tool that builds the intended Dataverse payload
plan for the latest TACATDP Kobo baseline workbook.

The tool validates:

- source row count;
- required source headers;
- identifier row counts;
- duplicate review groups;
- timestamp parsing;
- target table payload shapes;
- absence of raw sensitive values in the dry-run output.

## Command

```bash
python3 scripts/import-baseline-bridge.py \
  --xlsform /home/jmduda/Downloads/TACATDP/TACATDP_Tool.xlsx \
  --workbook /home/jmduda/Downloads/TACATDP/TACATDP_Impact_Data_Tracking_for_Financed_Beneficiaries_-_all_versions_-_English_en_-_2026-08-13-06-12-18.xlsx \
  --repo-root /home/jmduda/KodeX/crdb-mel \
  --output-json /tmp/tacatdp-baseline-bridge-payload-dry-run-20260814.json
```

## Runtime output

| Output | Purpose |
|---|---|
| `/tmp/tacatdp-baseline-bridge-payload-dry-run-20260814.json` | Sanitized payload dry-run report. |

The output includes aggregate counts, fingerprints, and payload shapes only. It
does not include raw beneficiary names, Customer IDs, phone numbers, or raw row
payloads.

## Dry-run result

| Target | Planned rows |
|---|---:|
| `mp_Submission` | 965 |
| `mp_SubmissionVersion` | 965 |
| `mp_TrackedEntity` | 965 provisional candidates |
| `mp_EntityIdentifier` | 2,886 |
| `mp_BeneficiaryProfile` | 965 |
| `mp_BeneficiarySubmissionLink` | 965 |

Identifier rows:

| Identifier type | Planned rows |
|---|---:|
| Source UUID | 965 |
| Customer ID | 956 |
| Farmer Phone Number | 965 |

Validation findings:

| Check | Result |
|---|---:|
| Missing required source headers | 0 |
| Missing Customer ID rows | 9 |
| Duplicate source UUID groups | 0 |
| Duplicate review groups | 10 |
| Duplicate review row memberships | 26 |
| Started timestamps parseable | 965 |
| Submitted timestamps parseable | 965 |
| Raw sensitive values checked in dry-run output | 2,777 |
| Raw sensitive value leaks | 0 |

## Duplicate treatment

Each Kobo root row remains a distinct `mp_Submission` and
`mp_SubmissionVersion`.

Each row also creates a provisional `mp_TrackedEntity` candidate. Customer ID and
phone repeats are queued for duplicate review and must not auto-merge tracked
entities during import.

This means the provisional tracked-entity count is 965, while the final resolved
beneficiary count may be lower after review.

## Schema follow-up resolved

`mp_EntityIdentifier.mp_identifiertype` must include a dedicated `Customer ID`
choice before live import. The importer expects Customer ID identifiers to use
that type rather than the generic `Other` value.

## Safety controls

- Dry-run mode is the default.
- Execute mode is blocked in this slice.
- Raw Customer ID and phone values are approved for Dataverse storage in the CRDB-controlled environment, but not for logs, markdown reports, commits, or handoff artifacts.
- The generated report contains fingerprints only for duplicate review evidence.

## Next slice

Enable the importer execution path and run the live Mshirika import after the
updated schema package is imported and verified.
