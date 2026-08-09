# Loading Performance Requirements - 2026-07-29

## Task Classification

This is a bounded performance and perceived-loading improvement for the
TACATDP Power Pages SPA. It changes when data and heavy UI dependencies are
loaded, but it does not change the Dataverse schema, security model, user roles,
or submission payload contract.

Primary risk is behavioral regression in startup, Data tab, Reporting tab, and
Collect runtime loading.

## Product Requirements

### Problem

Users experience slow first load and slow content availability in Mshirika, with
longer delays in CRDB. Current startup loads assigned forms, local drafts, all
submitted records, and one latest-version request per submission before the
workspace is fully ready.

### Goals

- Show the managed portal shell quickly after authenticated page load.
- Stop loading submission lists during initial workspace startup.
- Load Data, Reporting, User & Access, and Collect dependencies only when the
  user opens those areas.
- Provide visible, task-specific loading states instead of a blank or blocked
  app.
- Capture admin/debug timing evidence that can compare Mshirika and CRDB.

### Non-Goals

- No Dataverse schema migration in this slice.
- No Power Pages role or table permission changes.
- No dashboard feature expansion.
- No broad redesign of the shell/navigation.
- No CDN/platform-setting change without separate CRDB admin approval.

### Functional Requirements

| ID | Requirement |
| --- | --- |
| LP-RQ-01 | The app must render the shell before submission data is loaded. |
| LP-RQ-02 | Initial `loadWorkspace()` must load assigned forms and local drafts only. |
| LP-RQ-03 | Submission/reporting rows must load only when the user opens Data or Reporting, or explicitly refreshes. |
| LP-RQ-04 | Data and Reporting panels must show local loading, empty, error, and retry states. |
| LP-RQ-05 | The ODK runtime must load only when the user starts Collect or edit/review that needs the runtime. |
| LP-RQ-06 | Datepicker code/CSS must not be preloaded on the Home page unless the first route is Reporting/Data. |
| LP-RQ-07 | Admin/debug timing must record mount and major data-load durations without logging secrets or payload bodies. |
| LP-RQ-08 | Existing submission, edit, export, and access workflows must continue to work after lazy loading. |

### Look And Feel Requirements

- Use the existing managed shell: side nav, top sticky bar, content region, and
  bottom shell footer.
- Loading states must be quiet and operational, suitable for bank staff.
- Use skeleton blocks or concise status rows inside the affected panel.
- Avoid full-page spinners after the shell has rendered.
- Use labels such as:
  - `Loading assigned projects`
  - `Loading data page`
  - `Preparing form`
  - `Loading reporting view`

## User Stories

| ID | Story |
| --- | --- |
| LP-US-01 | As a bank officer, I want the portal shell to appear quickly so I know the system is responding. |
| LP-US-02 | As a data collector, I want project/form assignment loading to be separated from large submitted data loading so I can start Collect sooner. |
| LP-US-03 | As a reporting user, I want Reporting to load when opened, with clear progress and retry if it fails. |
| LP-US-04 | As a platform administrator, I want timing diagnostics so we can compare Mshirika and CRDB performance using evidence. |

## Acceptance Criteria

| ID | Acceptance Criterion |
| --- | --- |
| LP-AC-01 | Browser startup does not call `listSavedSubmissions()` from initial mount. |
| LP-AC-02 | The shell renders even while assignments or panel data are still loading. |
| LP-AC-03 | Opening a project Data tab triggers paginated data loading for that view only. |
| LP-AC-04 | Opening Reporting triggers reporting data loading for that view only. |
| LP-AC-05 | Collect triggers ODK runtime loading only when Collect starts. |
| LP-AC-06 | Datepicker bundle is not preloaded by the Home page for default Dashboard/Projects load. |
| LP-AC-07 | Admin/debug timing logs include app mount and major API durations. |
| LP-AC-08 | Existing validators pass after implementation. |
| LP-AC-09 | Mshirika smoke test records before/after timings. |
| LP-AC-10 | CRDB smoke test records before/after timings after deployment. |

## Requirements Traceability

| Requirement | Stories | Acceptance |
| --- | --- | --- |
| LP-RQ-01 | LP-US-01 | LP-AC-02 |
| LP-RQ-02 | LP-US-01, LP-US-02 | LP-AC-01 |
| LP-RQ-03 | LP-US-03 | LP-AC-03, LP-AC-04 |
| LP-RQ-04 | LP-US-01, LP-US-03 | LP-AC-02, LP-AC-03, LP-AC-04 |
| LP-RQ-05 | LP-US-02 | LP-AC-05 |
| LP-RQ-06 | LP-US-01 | LP-AC-06 |
| LP-RQ-07 | LP-US-04 | LP-AC-07, LP-AC-09, LP-AC-10 |
| LP-RQ-08 | all | LP-AC-08 |

## Artifact Readiness

- Investigation exists:
  `loading-performance-investigation-20260729.md`.
- Requirements exist in this file.
- ADR exists:
  `adr-0009-loading-performance-lazy-startup.md`.
- Architecture note exists:
  `loading-performance-architecture-20260729.md`.
- Delivery plan exists:
  `loading-performance-delivery-plan-20260729.md`.
- No environment write is required before implementation.
- Deployment to CRDB still requires explicit approval.

## Definition Of Done

- Requirements and ADR are committed before implementation.
- Startup no longer loads full submission data.
- Lazy loading is covered by focused validators or tests.
- Mshirika deployment is smoke-tested before CRDB update.
- CRDB update includes timing comparison evidence.
- No secrets, tokens, or user payload data appear in logs.

## Verification Summary

Planned verification:

```bash
npm --prefix powerpages/webforms-spa run build:mshirika-access
python3 scripts/validate-webforms-spa-foundation.py
python3 scripts/validate-access-mshirika-activation.py
python3 scripts/verify-powerpages-api-smoke-hosted.py --help
git diff --check
```

Browser verification:

- Record console timings on Mshirika.
- Record console timings on CRDB after deployment.
- Use browser Network tab to confirm no startup call to full submissions list.
- Confirm Data, Reporting, Access, and Collect still load when opened.
