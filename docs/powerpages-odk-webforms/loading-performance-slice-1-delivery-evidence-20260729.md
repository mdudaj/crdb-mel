# Loading Performance Slice 1 Delivery Evidence

Date: 2026-07-29

## User Story

As an authenticated bank user, I want the Impact Monitoring portal to show my available workspace quickly before heavy reporting data is loaded, so that I can start navigation or collection without waiting for all submission records.

## UX Description

The first screen remains the managed portal shell and project workspace. Startup now prioritizes the authenticated assignment query and local draft refresh. The Data tab, date filters, and reporting records remain available, but their heavier data and datepicker runtime are loaded when that area is used.

Loading feedback remains in the existing shell states. No new informational clutter was added to the banking workspace. Optional timing logs are hidden by default and can be enabled only for troubleshooting with `localStorage.TACATDP_DEBUG_PERF = "true"`.

## Accessibility Checklist

- Existing keyboard-accessible route buttons, tabs, and data actions are unchanged.
- The date range control remains a Vue component mounted through the existing filter layout.
- No new visible text, animation, or auto-focus behavior was added during startup.
- Error handling and authenticated redirect behavior remain unchanged.

## Acceptance Criteria

- Initial workspace load must not call `api.listSavedSubmissions()`.
- Assigned project/form visibility must still load through `api.listAssignedForms()`.
- Saved/report data must still load through the existing reporting data path when the Data tab or filters are used.
- Datepicker JavaScript must not be part of the initial SPA import graph or home page modulepreload list.
- Browser timing logs must be available for startup and API calls without exposing secrets.
- Mshirika access build and TACATDP validators must pass.

## Render Evidence

Local production build completed successfully with the Mshirika access build target. Generated entry HTML uses the optimized entry bundle `index-D8Tmzwaz.mjs`, preloads only the icon chunk, and no longer modulepreloads the datepicker JavaScript chunk.

Hosted screenshot evidence was not taken in this slice because deployment/restart was intentionally deferred until review.

## Verification Summary

Commands run from `/home/jmduda/KodeX.2026/tacatdp`:

```bash
npm --prefix powerpages/webforms-spa run build:mshirika-access
python3 scripts/validate-webforms-spa-foundation.py
python3 scripts/validate-access-mshirika-activation.py
git diff --check
```

Results:

- `build:mshirika-access`: passed.
- `validate-webforms-spa-foundation.py`: passed.
- `validate-access-mshirika-activation.py`: passed.
- `git diff --check`: passed.

## Artifact Readiness

Ready for Mshirika upload review. CRDB deployment should follow only after the CRDB role/mailbox environment setup is confirmed and the optimized package is uploaded, cache purged, and the first authenticated render is timed.

## Requirements Note

This implements delivery plan slice 1 only: startup measurement, lazy submission loading, and datepicker JavaScript preload removal. Asset/platform cleanup remains a later slice and should include removal of stale web files only after confirming current hosted references and cache behavior.
