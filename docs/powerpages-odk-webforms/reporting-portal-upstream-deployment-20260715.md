# Reporting Portal Upstream Deployment: 2026-07-15

## Target

- Environment: `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- Current deployed build marker: `reporting-count-fix-20260715-002`
- Superseded reporting build marker: `reporting-fetchxml-exportname-20260715-001`
- Initial reporting build marker: `reporting-data-export-powerbi-20260715-001` (superseded)

## Deployed Scope

- Project workspace with Material-style Summary, Data, Exports, and Power BI tabs.
- Paginated/filtered reporting Data table with normalized answer detail and Edit handoff.
- Named root-record CSV export settings and bounded browser download workflow.
- Power BI Dataverse connection guidance, reporting table names, relationship guidance, and permission boundary.
- Existing collection, edit, attachment-metadata, XForm, and project-workspace behavior retained.

Automatic projection execution is not part of this upload. The signed assembly
and plug-in type exist in Dataverse, but execution-user/role provisioning and the
step/post image were explicitly deferred. Run the trusted projection builder
after canonical submit/edit activity until activation is approved.

## Assets

- Main module: `/assets/index-CN7Dkkk-.mjs`
- Main stylesheet: `/assets/index-CY0LEOWx.css`
- ODK module preload: `/assets/index-Cg9qvMI9-CahRJN6e.mjs`
- Vue runtime preload: `/assets/runtime-core.esm-bundler-DauTPZIg.mjs`

Existing Dataverse web-file record IDs were reused. No duplicate website or
web-file records were intentionally created.

## Verification

- `npm run build`: passed; only the documented ODK direct-eval and large-chunk warnings remain.
- Reporting projection builder and Python/C# parity validators: passed.
- SPA foundation validator: passed.
- Main, ODK, and Vue runtime module syntax checks: passed.
- PAC target verification matched the recorded environment and website ID.
- Enhanced-model `pac pages upload --forceUploadAll`: succeeded in 95.10 seconds.
- Hosted verifier passed for 12 entity sets, 24 Web API settings, 12 table permissions, assignments, and file-backed XForm state.
- Dataverse verification found the new marker/main module on both Home rows and all four critical web-file records by their reused IDs.
- A post-deployment `9004010B` error exposed unsupported `$skip` paging. The
  corrected build uses FetchXML `count`/`page`, and a live two-page Dataverse
  test returned distinct rows with total count 5.
- The subsequent hosted `9004010A` error was isolated to redundant total-count
  mechanisms on one FetchXML request. The prepared corrective build retains
  FetchXML `returntotalrecordcount` and removes OData `$count`; an authenticated
  replay of the exact request returned HTTP 200, five rows, and count five.
- Export names are now generated as `<Form_Name>_YYYYMMDD_HHMMSS`; the local
  rendered check confirmed a read-only form-derived value and CSV filename.

PAC reported known stale `powerpagecomponent` update warnings for missing record
IDs during upload. The command completed successfully and post-upload hosted
state verification passed.

The `reporting-count-fix-20260715-002` upload also reported the known stale
component warnings, then completed successfully in 119.79 seconds. Post-upload
verification found the marker on both Home rows and downloaded the enhanced
main web-file with the same SHA-256 as the local production build. The complete
hosted configuration verifier passed.

## Remaining Runtime Checks

- Refresh Power Pages server-side cache or use Preview before visual testing.
- In an authenticated session, open Data and confirm projected rows load.
- Open a record and confirm normalized answers load.
- Save and download a named CSV export with current filters.
- Confirm the Power BI tab copies the development environment URL.
- Verify Power BI Desktop separately with a non-admin organizational user and an approved Dataverse reporting role.

## Rollback

Re-upload the previously verified `project-tabs-20260714-001` enhanced-model
package if the reporting shell causes a hosted regression. This portal rollback
does not remove canonical/reporting tables, projection rows, or the inactive
plug-in assembly/type.
