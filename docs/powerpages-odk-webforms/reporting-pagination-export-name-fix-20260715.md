# Reporting Pagination and Export Name Fix: 2026-07-15

## Reported Behavior

- Data returned `400` / `9004010B`: `$skip` is not supported.
- Export name needed to be the selected form name, with spaces replaced by
  underscores, combined with a timestamp.

## Root Cause

The reporting client used OData `$top` plus `$skip` for direct page navigation.
Dataverse does not support `$skip`. Power Pages supports FetchXML read queries,
and Dataverse FetchXML supports `count` and `page` for bounded direct paging.

References:

- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query/page-results
- https://learn.microsoft.com/en-us/power-pages/configure/read-operations
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/fetchxml/page-results

## Delivered Behavior

- Data queries use an encoded FetchXML document with `count`, `page`, total
  record count, selected attributes, filters, and deterministic ordering by
  updated timestamp plus primary key.
- No reporting request sends `$skip`.
- Search, date, submitter, review-state, and form-version filters are emitted as
  escaped FetchXML conditions.
- Entering Exports generates a read-only name in the format
  `<Form_Name>_YYYYMMDD_HHMMSS`.
- Spaces become underscores, unsafe filename characters are replaced, and the
  same generated name is stored in the export setting and used for the CSV file.

## Verification

- TypeScript typecheck: passed.
- Production build: passed; documented ODK dependency warnings remain.
- SPA foundation validator and `git diff --check`: passed.
- Live Dataverse FetchXML test: page 1 returned 2 rows, page 2 returned 2
  different rows, total count was 5, and overlap was false.
- Headless Chromium rendered a read-only value matching
  `TACATDP_Impact_Evaluation_YYYYMMDD_HHMMSS` with no page errors; screenshot:
  `/tmp/tacatdp-reporting-export-name-20260715.png`.
- Enhanced-model upload succeeded in 91.47 seconds.
- Hosted verifier passed for entity sets, 24 Web API settings, 12 table
  permissions, assignments, and the file-backed XForm.
- Both hosted Home rows contain marker
  `reporting-fetchxml-exportname-20260715-001` and main module
  `index-CN7Dkkk-.mjs`.
- Main module reused web-file ID `da7f7a37-0b8c-4e92-ae25-d9018ffb47b0`.

## Remaining Browser Check

The initial hosted browser check exposed a second issue: combining FetchXML
`returntotalrecordcount="true"` with the equivalent OData `$count=true` caused
Power Pages to return `500` / `9004010A`. An authenticated request matrix proved
that OData, FetchXML paging, and the form-version lookup filter each pass; only
the duplicate count combination fails. The exact request returned five rows and
count five after removing only `$count=true`.

The corrected package marker is `reporting-count-fix-20260715-002`. After its
approved upload, refresh the Power Pages cache, open Data, navigate available
pages, and confirm Exports retains the selected-form timestamp name. No
permission or schema change is required.
