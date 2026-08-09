# Reporting And Export Role Scope Delivery - 2026-07-30

## Task Classification

Authorization-sensitive frontend/API query hardening for TACATDP reporting and CSV exports in Power Pages. This change does not modify Dataverse schema, table permissions, authentication providers, or submission writes.

## Requirement

Platform administrators must be able to view and download all projected reporting records. Collectors must only see and download records where `mp_useremail` matches their signed-in Power Pages account email.

## Research Note

Microsoft Power Pages documentation states that the portals Web API follows table permissions assigned through web roles, and Dataverse access from Power Pages should be protected with table permissions. This slice keeps that platform control, but also adds an application-level query guard so report and export fetches cannot accidentally request all rows for collector sessions.

References:

- https://learn.microsoft.com/en-us/power-pages/configure/read-operations
- https://learn.microsoft.com/en-us/power-pages/security/power-pages-security
- https://learn.microsoft.com/en-us/power-pages/security/table-permissions

## UX Description

- Data tab displays the active reporting scope.
- Admin sessions show `All submitted records`.
- Collector sessions show `My submitted records` and the signed-in email.
- Submitter filter is disabled for collector sessions because the server query is already restricted to the signed-in user.
- Exports tab repeats the effective scope before download.
- Export success messages include the applied scope.

## Implementation

- Added `ReportingAccessScope` type.
- Added `PowerPagesApiClient.getReportingAccessScope()`.
- `listSubmissionReportRows` now injects role scope into FetchXML:
  - admin: no owner filter unless UI submitter filter is provided
  - collector: `mp_useremail eq <signed-in email>`
- `listAllSubmissionReportRows` inherits the same enforced scope for CSV downloads.
- `listExportSettings` is scoped so admins see all saved export definitions and collectors see only definitions they created.
- Data/Exports UI now discloses the effective scope.
- Validator now checks that report/export scope enforcement and UI disclosure remain present.

## Acceptance Criteria

- Platform Administrator can view all rows matching current filters.
- Platform Administrator can download all rows matching current filters.
- Collector can view only rows where `mp_useremail` equals their signed-in email.
- Collector CSV downloads are restricted to their submitted rows even when rerunning saved filters.
- Collector cannot use submitter filter to browse other users.
- Saved export definitions are scoped by creator for collectors.

## Accessibility Checklist

- Scope is visible text, not color-only state.
- Disabled submitter field uses native disabled behavior.
- Export result/error messages remain in live status banners.
- No new pointer-only interaction was introduced.

## Verification Summary

Commands run:

```bash
npm --prefix powerpages/webforms-spa run build:mshirika-runtime
python3 scripts/validate-webforms-spa-foundation.py
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-DK_-49-L.mjs
git diff --check
pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
```

Result:

- Build passed.
- Foundation validator passed.
- Packaged bundle syntax check passed.
- Whitespace check passed.
- Mshirika upload succeeded in 95.84 seconds.
- PAC emitted the known `powerpagecomponent ... Does Not Exist` warnings but returned success.

## Review Instructions

1. Purge Power Pages cache and restart Mshirika.
2. Test as Platform Administrator: Data tab should show all submitted records and Exports should download all matching rows.
3. Test as collector: Data tab should show `My submitted records`, submitter filter should be disabled, and downloaded CSV should include only that collector's rows.
4. Confirm console request FetchXML includes `mp_useremail` condition for collector sessions and not for admin sessions unless admin applies submitter filter.

## Residual Risk

This app-level guard complements but does not replace Power Pages table permissions. CRDB must still configure table permissions/web roles correctly during production deployment.
