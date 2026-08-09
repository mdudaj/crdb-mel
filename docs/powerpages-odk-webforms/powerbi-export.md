# Power BI Export

## Purpose

Use `scripts/export-submissions-powerbi.py` as the interim reporting bridge for TACATDP Power BI work while the prototype remains in the current Dataverse development environment.

The script reads Dataverse `Submissions` and the latest matching `SubmissionVersions` record, then writes a CSV that Power BI Desktop can import. It does not write to Dataverse.

## Command

```bash
python3 scripts/export-submissions-powerbi.py \
  --env-file .env \
  --output artifacts/exports/tacatdp-submissions-powerbi.csv
```

To verify one saved record appears in the same submitted-record shape as the portal Saved tab:

```bash
python3 scripts/export-submissions-powerbi.py \
  --env-file .env \
  --check-instance "uuid:..."
```

## Output

The CSV includes stable reporting columns:

- Dataverse submission and submission-version ids.
- ODK `instance_id` and computed `display_name`.
- submitter email, submitted/updated timestamps, lifecycle status, and review state.
- form metadata preserved in `SubmissionVersions.SubmissionJson`.
- latest submission version number.
- flattened XML leaf fields prefixed with `xform_`.

Power BI can load the CSV directly with **Get data > Text/CSV**. For a production-grade setup, connect Power BI to Dataverse directly and reproduce this script's latest-version and XML-flattening logic as a governed Dataverse view, dataflow, or server-side projection table.

## Current Limitation

This export is a reporting bridge, not the final analytics model. Repeat groups and repeated element names are joined into one cell with ` | `. If Power BI needs one row per repeat item or controlled normalization, add a `SubmissionAnswers` or reporting projection slice before dashboard production.
