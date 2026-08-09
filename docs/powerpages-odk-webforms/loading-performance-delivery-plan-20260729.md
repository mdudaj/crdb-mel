# Loading Performance Delivery Plan - 2026-07-29

## Scope

Deliver the first loading-performance improvement slice:

1. Add timing instrumentation.
2. Remove submitted-record loading from initial mount.
3. Lazy-load Data, Reporting, Access, datepicker, and ODK runtime.
4. Improve panel-local loading states.

## Implementation Steps

### Step 1 - Timing Helpers

- Add a small performance helper under `powerpages/webforms-spa/src/`.
- Wrap major API calls in named timing measurements.
- Print a concise timing table to console for admin/debug builds.
- Ensure no payload bodies, tokens, or submission data are logged.

### Step 2 - Light Startup

- Refactor `loadWorkspace()` in `AssignedFormsView.vue`.
- Initial mount should call:
  - `api.listAssignedForms()`
  - `refreshLocalDrafts()`
- Remove initial call to `api.listSavedSubmissions()`.
- Keep route restoration working after mount.

### Step 3 - Data Tab Lazy Load

- Add explicit Data tab load state.
- Load paginated `mp_submissionreportrow` data when Data tab opens.
- Do not fetch answers/version details until View is clicked.

### Step 4 - Reporting Lazy Load

- Load reporting rows only when Reporting opens.
- Keep debounced filters.
- Show panel-level skeleton/loading/error state.

### Step 5 - Heavy Dependency Lazy Loading

- Move datepicker component import behind Reporting/Data filter rendering.
- Remove Home page datepicker `modulepreload`.
- Ensure `@getodk/web-forms` is imported only when Collect/Edit runtime opens.

### Step 6 - Validation

Run:

```bash
npm --prefix powerpages/webforms-spa run build:mshirika-access
python3 scripts/validate-webforms-spa-foundation.py
python3 scripts/validate-access-mshirika-activation.py
git diff --check
```

Add or update focused validators for:

- No `listSavedSubmissions()` in initial `loadWorkspace()`.
- Home page does not preload datepicker by default.
- Timing helper avoids payload/body logging.

### Step 7 - Mshirika Smoke Test

- Upload to Mshirika.
- Purge/restart only once after upload.
- Record console timings:
  - app mounted
  - assignments loaded
  - initial shell usable
  - Data first load
  - Reporting first load

### Step 8 - CRDB Smoke Test

After approval:

- Upload to CRDB.
- Purge/restart only once.
- Record same timings.
- Compare with Mshirika.

## Acceptance Gate

Proceed to cosmetic polishing only after:

- Initial workspace no longer loads submissions.
- Dashboard/Projects render without waiting for Data/Reporting.
- Data and Reporting still work when opened.
- Timing evidence is captured for Mshirika and CRDB.

## Rollback

If lazy loading breaks a critical workflow:

1. Re-upload the previously committed Power Pages package.
2. Restore previous Home page asset references.
3. Document failing route and console timing/error.

No Dataverse schema rollback should be required for this slice.
