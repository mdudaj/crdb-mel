# Reporting Projection Builder Delivery: 2026-07-14

## Scope

Delivered a trusted deploy-script path that reads canonical `Submissions` and latest `SubmissionVersions`, parses submitted XForm XML, and builds derived reporting projection payloads for:

- `SubmissionReportRows`
- `SubmissionRepeatRows`
- `SubmissionAnswers`

The builder is dry-run by default and performs no environment writes unless `--execute` is passed after reporting tables and alternate keys exist.

## Files

- `scripts/build-reporting-projections.py`
- `scripts/validate-reporting-projection-builder.py`
- `scripts/dataverse-schema-deploy.py`
- `schemas/dataverse/reporting-projection-schema.json`
- `schemas/dataverse/reporting-projection-schema.md`

## Behavior

- Reads submitted canonical rows from `mp_submissions`.
- Reads the latest payload version from `mp_submissionversions`.
- Preserves canonical XML as the source of truth; reporting rows are derived only.
- Builds stable keys:
  - root report row: `mp_reportkey`
  - repeat row: `mp_repeatrowkey`
  - long answer row: `mp_answerkey`
- Detects repeated sibling groups as repeat rows.
- Writes root answers into `mp_rootanswersjson`.
- Writes one long-format answer row for root and repeat answers.
- Uses Dataverse alternate-key upsert paths only when `--execute` is explicitly supplied.

## Verification

- `python3 scripts/validate-reporting-projection-builder.py` passed.
- `python3 scripts/dataverse-schema-plan.py --schema-file schemas/dataverse/reporting-projection-schema.json` passed with 75 no-write operations.
- `python3 scripts/dataverse-schema-deploy.py --schema-file schemas/dataverse/reporting-projection-schema.json --no-publish` passed in dry-run mode and reported 4 tables, 58 columns, 13 relationships, and 4 alternate keys.
- `python3 scripts/build-reporting-projections.py --top 10` passed in dry-run mode against the dev Dataverse environment:
  - canonical submissions read: 5
  - report rows: 5
  - repeat rows: 0
  - answer rows: 145
  - failed projections: 0
  - writes performed: false

## Executed After Approval

After explicit approval, the reporting schema and projections were written to the dev/upstream Dataverse environment:

1. `python3 scripts/dataverse-schema-deploy.py --schema-file schemas/dataverse/reporting-projection-schema.json --execute`
   - Created 4 reporting tables.
   - Created 58 columns.
   - Created 13 relationships.
   - Created 4 alternate keys.
   - Published customizations.
2. `python3 scripts/build-reporting-projections.py --top 500 --execute`
   - Read 5 canonical submitted records.
   - Wrote 5 report rows.
   - Wrote 145 answer rows.
   - Wrote 0 repeat rows because current smoke submissions do not contain repeat groups.
   - Failed projections: 0.
3. Temporary `probe:*` rows created during alternate-key troubleshooting were deleted after explicit approval.

Final verified reporting counts:

- `mp_submissionreportrows`: 5
- `mp_submissionrepeatrows`: 0
- `mp_submissionanswers`: 145
- `mp_exportsettings`: 0
- `probe_report_rows`: 0

## Risks

- The current live TACATDP smoke submissions did not contain repeat groups, so repeat-row behavior is validated by fixture only until a hosted repeat submission exists.
- Projection tables need Power Pages table permissions before the portal can read them through `/_api`.
- Power BI should connect to reporting tables, not canonical XML payload tables, unless an admin explicitly approves broader access.
