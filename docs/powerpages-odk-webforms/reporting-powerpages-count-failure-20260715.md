# Power Pages Reporting Count Failure: 2026-07-15

## Classification

- Work type: hosted Power Pages Web API incident and bounded bug fix.
- Risk: user-facing reporting outage; no schema, authentication, or permission
  change is required.
- Affected surface: project `Data` tab request for
  `mp_submissionreportrows`.

## Reported Behavior

The hosted Data tab returned HTTP `500` with Power Pages error `9004010A`.
Microsoft documents this response as the generic wrapper for an unhandled
Power Pages Web API exception.

## Evidence Inspected

- Deployed SPA request builder in
  `powerpages/webforms-spa/src/powerpages-api/client.ts`.
- Live Dataverse metadata, 24 Web API site settings, 12 table permissions,
  enhanced permission-role links, and the authenticated portal contact.
- Live reporting permission scope and parent relationship.
- Direct Dataverse FetchXML paging and count response.
- Authenticated Power Pages browser request matrix.
- Microsoft Power Pages read operations, Web API error handling, server-side
  caching, and Dataverse FetchXML count/paging documentation.

Authoritative references:

- https://learn.microsoft.com/en-us/power-pages/configure/read-operations
- https://learn.microsoft.com/en-us/power-pages/configure/web-api-http-requests-handle-errors
- https://learn.microsoft.com/en-us/power-pages/admin/clear-server-side-cache
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/fetchxml/count-rows
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/fetchxml/page-results

## Root Cause

The request specified total count twice:

1. FetchXML root attribute `returntotalrecordcount="true"`.
2. OData query option `&$count=true` on the same FetchXML request.

Microsoft documents these as equivalent alternatives. Direct Dataverse accepts
the redundant combination, but the hosted Power Pages `/_api` proxy throws an
unhandled exception and returns `9004010A` when both are present.

The authenticated browser matrix isolated the behavior:

| Request variant | Status |
| --- | ---: |
| OData select/filter/order/top/count | 200 |
| FetchXML `top` | 200 |
| FetchXML `count` and `page` | 200 |
| FetchXML lookup filter | 200 |
| FetchXML `returntotalrecordcount` plus OData `$count` | 500 |

The exact deployed request was then replayed with only `&$count=true` removed:

```json
{"status":200,"rows":5,"count":5}
```

This proves that table permissions, lookup filtering, selected fields, ordering,
and FetchXML page attributes are not the cause of this incident.

## Resolution Requirement

- Keep FetchXML `count`, `page`, and `returntotalrecordcount="true"`.
- Remove the redundant OData `&$count=true` option.
- Continue reading the total from response property `@odata.count`.
- Do not reintroduce Dataverse-unsupported `$skip`.
- Add a validator regression rule that rejects a reporting request combining
  FetchXML `returntotalrecordcount` with OData `$count`.

## Implementation Instructions

Inspect:

- `powerpages/webforms-spa/src/powerpages-api/client.ts`
- `scripts/validate-webforms-spa-foundation.py`
- this incident artifact
- the Microsoft references above

Steps:

1. Remove `&$count=true` from `listSubmissionReportRows` only.
2. Preserve `returntotalrecordcount="true"` in `buildReportingFetchXml`.
3. Extend the SPA validator with positive and negative count-mechanism checks.
4. Run the validator, TypeScript typecheck, production build, and diff check.
5. Upload only after explicit Power Pages upload approval.
6. Clear Power Pages configuration/cache, then verify the hosted Data tab.

## Acceptance And Rollback

Acceptance requires the hosted Data tab to return the five current rows for the
selected form without a `500`, while preserving the displayed total and paging
controls. Network evidence must show FetchXML `returntotalrecordcount="true"`
and no appended `$count=true`.

Rollback is the prior SPA web-file asset and Home-page module reference. Do not
roll back to the earlier `$skip` implementation because Dataverse rejects it.

## Implementation Status

- Reporting request corrected to use only FetchXML
  `returntotalrecordcount="true"`.
- Validator now requires the FetchXML count attribute and rejects an appended
  OData `$count` within `listSubmissionReportRows`.
- TypeScript typecheck, SPA foundation validator, production build, and diff
  check passed.
- Packaged build marker: `reporting-count-fix-20260715-002`.
- Main web-file record and path remain `index-CN7Dkkk-.mjs`; its content is the
  verified `index-CjnfNLz_.mjs` production build.
- Approved enhanced-model upload succeeded in 119.79 seconds.
- Both hosted Home rows contain marker `reporting-count-fix-20260715-002`.
- The hosted main web-file SHA-256 is
  `6241acecfc7b4701158a51509b7acb2cc091ec8938ccbbed58fa64df047a8f45`,
  matching both local deployment packages and the verified production build.
- Hosted bundle inspection confirms FetchXML total count is present and the
  duplicate OData count is absent.
- The hosted Power Pages/Dataverse verifier passed for all entity sets, site
  settings, permissions, role links, portal contact state, and seed XForm data.
- Final authenticated Data-tab verification remains pending after a Power Pages
  server-side cache refresh.

## Safety Review

- No secrets were printed or persisted.
- The diagnostic `Webapi/error/innererror` site setting was explicitly approved,
  enabled temporarily, found ineffective for this unhandled exception, and
  deleted after the retry.
- No table permission, authentication, schema, or business-data mutation was
  made during diagnosis.
- Power Pages upload remains an explicit approval gate.
