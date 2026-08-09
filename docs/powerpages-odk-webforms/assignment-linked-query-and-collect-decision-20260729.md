# Assignment Linked Query and Collect Runtime Decision

Date: 2026-07-29

## Task Classification

Frontend performance slice plus architecture decision note for the blocked Collect runtime. No schema, permission, authentication, or Dataverse data changes are included.

## Requirements Note

- Startup assignment loading should use one bounded metadata request where possible.
- Startup must not load `mp_xformxml`.
- If the linked query fails in a Power Pages environment, the portal should fall back to the previous metadata hydration path rather than blocking project access.
- Collect remains blocked until the ODK runtime assets can be packaged under Power Pages constraints or hosted through an approved Microsoft-managed static asset path.

## UX Description

The user-visible shell is unchanged. Project cards should appear faster because the portal now requests assignment, form-version metadata, and form metadata together. If the linked metadata query is rejected by Power Pages table permissions, users should still see the project through the slower fallback path.

Collect behavior is not presented as fixed in this slice. The runner still uses the existing loading/error states, but the ODK runtime build is not deployed.

## Accessibility Checklist

- No new controls or navigation patterns were added.
- Existing loading/error announcements remain unchanged.
- The assignment query change does not alter focus order, labels, or keyboard operation.
- Collect runtime accessibility review is deferred until a deployable runtime package exists.

## Acceptance Criteria

- `listAssignedForms()` first attempts a FetchXML query linking `mp_formassignment`, `mp_formversion`, and `mp_form`.
- The linked query returns assignment key, user email, form-version ID, form version label, form ID, form name, and XML form ID.
- Startup assignment summaries still do not include XForm XML.
- The old metadata hydration path remains as fallback.
- The validator enforces the linked-query path and no-startup-XForm rule.
- Mshirika upload package references `index-BbJfdreX.mjs` with marker `assignment-linked-query-20260729-001`.

## Change Summary

- Added `FormAssignmentMetadataRow` with FetchXML alias fields.
- Added `buildAssignedFormsFetchXml()`.
- Added `toLinkedSummary()` and alias string extraction.
- Updated `listAssignedForms()` to use the linked metadata query first, falling back to the metadata hydration path on failure.
- Strengthened `validate-webforms-spa-foundation.py` to require the linked assignment metadata path and Collect/Edit runtime hydration guard.
- Packaged `index-BbJfdreX.mjs`.

## Collect Runtime Decision

Decision: do not deploy Collect through the current Power Pages web-file upload package yet.

Rationale:

- `build:mshirika-runtime` succeeds locally, but emits ODK runtime chunks over the Power Pages web-file/content limit observed earlier:
  - `dist-pLvMFTNt.mjs`: about 1.8 MB
  - `index-Cg9qvMI9-CaiUDr-N.mjs`: about 2.24 MB
- The access/startup build remains uploadable and should continue to carry project, data, reporting, export, and user-management UX while the runtime path is resolved.

Approved next decision options:

1. Rework bundling/chunking so every ODK runtime web file is below the Power Pages limit.
2. Host ODK runtime assets on an approved Microsoft-managed static hosting endpoint and keep Power Pages as authenticated shell/orchestrator.
3. Defer Collect in Power Pages and provide a controlled interim data-entry path only if CRDB accepts the functional tradeoff.

Recommended next action: research and prototype option 1 first. If ODK’s published runtime cannot be split below the limit without modifying vendor output, escalate to option 2 for CRDB-approved Microsoft static hosting.

## Verification Summary

Commands run:

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

## Mshirika Upload

Uploaded to Mshirika with:

```bash
pac pages upload \
  --environment "https://orga3cf4b37.crm4.dynamics.com/" \
  --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool \
  --modelVersion Enhanced \
  --forceUploadAll
```

Result:

- Upload succeeded in 66.05 seconds.
- PAC printed the same non-terminal `powerpagecomponent ... Does Not Exist` warnings, then completed with `Power Pages website upload succeeded`.

## Render Evidence

Local production build generated `index-BbJfdreX.mjs`. Hosted visual/timing evidence must be captured after Mshirika upload, cache purge/restart, and signed-in reload.

## Artifact Readiness

Uploaded to Mshirika for timing review. Not ready for CRDB production update until Mshirika confirms whether the linked query works without falling back.
