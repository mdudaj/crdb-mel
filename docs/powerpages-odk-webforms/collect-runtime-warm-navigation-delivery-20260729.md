# Collect Runtime Warm Navigation Delivery - 2026-07-29

## Task Classification

Frontend UX and performance lifecycle fix for the Power Pages Collect route. This does not change Dataverse schema, table permissions, authentication, submission payloads, or access management writes.

## Requirement

After the first Collect load succeeds, internal portal navigation must not make reopening the same form feel like a cold start. The portal should preserve the hydrated assignment and XForm reference while the user moves between Dashboard, Project, Reporting, and User & Access screens in the same SPA session.

## UX Description

- First Collect open can still show staged loading while the XForm and ODK runtime are prepared.
- Reopening the same form after internal menu navigation should immediately render the already hydrated runtime path without resetting to `Loading form definition...`.
- Switching to a different form, opening an edit session, refreshing the workspace, or loading after a full browser refresh still follows the governed hydration path.
- If hydration fails, the user remains on Collect and receives visible error feedback.

## Implementation

- Added `warmedAssignments`, keyed by form version id, in `AssignedFormsView.vue`.
- Added `getWarmAssignment` and `rememberWarmAssignment` helpers.
- Updated project and reporting navigation to reuse a warmed assignment instead of replacing it with lightweight startup metadata.
- Updated `openRunner` to skip reset and hydration when the same form version already has hydrated XForm XML in the current SPA session.
- Added validator coverage so future changes do not remove the warm navigation lifecycle rule.
- Packaged bundle `index-Djs7oyiu.mjs?v=collect-warm-20260729-001`.

## Acceptance Criteria

- First Collect open still works with IndexedDB XForm cache and staged loading messages.
- Second Collect open for the same form is immediate after returning from Project/Data/Reporting/User & Access navigation in the same SPA session.
- The form is not mounted before XForm XML exists.
- Errors are visible and do not redirect the user silently.
- Full page reload remains safe: the app can hydrate from IndexedDB or Dataverse as before.

## Accessibility Checklist

- No new icon-only or pointer-only control was introduced.
- Loading and error feedback remain visible text.
- Existing runtime `aria-label` is preserved.
- No focus trap or modal behavior changed.

## Verification Summary

Commands run:

```bash
npm --prefix powerpages/webforms-spa run build:mshirika-runtime
python3 scripts/validate-webforms-spa-foundation.py
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-Djs7oyiu.mjs
git diff --check
pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
```

Result:

- Build passed.
- Foundation validator passed.
- Packaged bundle syntax check passed.
- Whitespace check passed.
- Mshirika upload succeeded in 79.23 seconds.
- PAC emitted the known `powerpagecomponent ... Does Not Exist` warnings but returned success.

## Review Instructions

1. Purge portal cache and restart the Mshirika site.
2. Open the portal and open the TACATDP project.
3. Click Collect and wait for first render.
4. Return to the project, switch to another menu item, then return to the same project and click Collect again.
5. Expected result: the same form opens immediately in the same SPA session. A full browser refresh can still pay first-load cost.

## Residual Risk

This preserves the hydrated XForm and avoids our own reset path. The ODK component may still pay some browser rendering cost if Vue remounts it after route/template changes. If that remains visible, the next step is a stronger architectural change: keep the runner subtree mounted with `v-show` or move Collect into a persistent route outlet.
