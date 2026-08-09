# Collect Runtime Cache Delivery - 2026-07-29

## Task Classification

Frontend performance and UX hardening for the Power Pages Collect runtime. The change affects the authenticated portal shell and data collection route only; Dataverse schema, table permissions, submission writes, and access management behavior are unchanged.

## Requirement

When a bank worker opens Collect for an assigned form, the portal must avoid unnecessary startup work and provide clear staged loading feedback. The first Collect open may still download the XForm XML from Dataverse file storage. Repeat opens of the same form version should reuse a local browser cache where available, then mount the ODK runtime without re-downloading the XForm attachment.

## User Story

As an authenticated assigned user, I want the Collect action to show clear progress and open the form predictably, so that slow Dataverse or Power Pages calls do not look like a broken page.

## UX Description

- Collect first shows `Loading form definition...` for a new submission or `Loading form definition for edit...` for edits.
- After the XForm XML is available, the runner changes to `Preparing form runtime...` before mounting the ODK component.
- If hydration fails, the user remains on the runner and sees an explicit error instead of a silent spinner.
- The ODK runtime host is mounted only when the selected assignment has hydrated XForm XML.

## Architecture Decision

Use a dedicated IndexedDB cache for XForm XML instead of `sessionStorage`, `localStorage`, or the existing draft database.

Rationale:

- TACATDP XForms can be large enough to exceed normal Web Storage quota.
- The existing draft IndexedDB database should not be migrated during a performance slice because it stores user draft work.
- A separate cache database is disposable and can fail without affecting form submission or draft recovery.
- Cache keys include form version id, version label, and a hash of the current XForm marker/XML so updated form versions do not reuse stale XML.
- The cache keeps the latest five XForms to bound local storage growth.

## Implementation

- Added `powerpages/webforms-spa/src/offline/xform-cache.ts` with a dedicated `tacatdp-xform-cache` IndexedDB database and `xforms` store.
- Updated `hydrateAssignmentRuntime` to measure and use:
  - `api:getCachedXForm`
  - `api:getXFormAttachment`
  - `api:downloadXFormXml`
  - `api:setCachedXForm`
  - `api:hydrateAssignmentRuntime`
- Kept assignment startup metadata-only; XForm XML is still loaded only when Collect/Edit is opened.
- Updated package entry to `index-CR_9dv7u.mjs?v=collect-cache-20260729-002`.

## Acceptance Criteria

- Workspace startup does not call `listSavedSubmissions`.
- Assignment list loads through the linked metadata query with fallback.
- Collect/Edit hydrates XForm XML on demand only.
- First Collect open logs granular timings for cache lookup, attachment lookup, download, cache write, and hydration.
- Repeat Collect open for the same form version should show `api:getCachedXForm` and avoid `api:downloadXFormXml` when IndexedDB is available.
- If IndexedDB is unavailable or full, Collect still loads by downloading the XForm from Dataverse.
- Loading text changes through the staged messages above.

## Accessibility Checklist

- Loading and error feedback remain visible text, not color-only state.
- The ODK runtime section keeps an explicit `aria-label`.
- The runner does not mount a blank runtime host before XForm XML is ready.
- Error handling leaves the user on the current route with actionable text.
- No new pointer-only interaction was introduced in this slice.

## Verification Summary

Commands run:

```bash
npm --prefix powerpages/webforms-spa run build:mshirika-runtime
python3 scripts/validate-webforms-spa-foundation.py
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-CR_9dv7u.mjs
git diff --check
pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
```

Result:

- Build passed.
- Foundation validator passed.
- Packaged entry syntax check passed.
- Whitespace check passed.
- Mshirika Power Pages upload succeeded in 73.13 seconds.
- PAC reported the recurring `powerpagecomponent ... Does Not Exist` warnings during upload, but returned success.

## Review Instructions

1. Purge Power Pages cache and restart the Mshirika site.
2. Open the portal and enable console timings if needed:

```javascript
localStorage.TACATDP_DEBUG_PERF = "true"
```

3. Open a project, click Collect, and wait for the form to render.
4. Close/back out and open Collect again for the same form version.
5. Compare console timings. The repeat open should avoid `api:downloadXFormXml` if the XForm was cached successfully.

## Risks And Follow-Up

- First load can still be slow because Dataverse file download and ODK mount remain necessary.
- Repeat-load improvement depends on browser IndexedDB availability and storage quota.
- ODK package chunks remain large and are documented as a future optimization candidate.
- If CRDB production still shows high first-load times, the next realistic options are server-side XForm flattening/projection and hosting static versioned XForm assets behind approved Power Platform controls.
