# Collect Persistent Runner Delivery - 2026-07-30

## Task Classification

Frontend UX and runtime lifecycle improvement for the Power Pages Collect route. The change does not alter Dataverse schema, permissions, authentication, submission payloads, reporting projection, or access-management writes.

## Requirement

After a user has opened a Collect form once in the current SPA session, internal navigation should not destroy the ODK runtime component. Moving to Project, Reporting, Dashboard, or User & Access and then returning to Collect for the same form should feel immediate.

## UX Description

- First Collect open still shows normal staged loading while the form definition and ODK runtime are prepared.
- Internal navigation hides the Collect runner instead of unmounting it.
- Returning to Collect for the same active form shows the already mounted runner.
- Hidden runner content is marked with `aria-hidden` and `inert` while inactive so it is not reachable by assistive technology or keyboard focus.
- Full browser refresh, different form version, or edit mode still uses the governed hydration path.

## Implementation

- Replaced the final `activeView` runner branch with a persistent `.persistent-runner-view` section.
- Used `v-show="activeView === 'runner'"` instead of `v-if`/`v-else` so the ODK component remains mounted.
- Added hidden-state guards: `aria-hidden` and `inert` when the runner is not active.
- Added validator rules to require the persistent runner view and accessibility guards.
- Packaged bundle `index-DIkDBSuY.mjs?v=persistent-runner-20260730-001`.

## Acceptance Criteria

- First Collect open continues to work with loading messages.
- Switching to another internal menu and returning to the same Collect form does not remount the runner subtree.
- Hidden Collect content is not keyboard-focusable while inactive.
- Full page reload remains safe and follows the existing XForm cache/hydration flow.
- Validator prevents reverting to a destroy-on-navigation runner branch.

## Accessibility Checklist

- The hidden runner uses `aria-hidden` while inactive.
- The hidden runner uses `inert` while inactive.
- No new pointer-only controls were introduced.
- Existing loading and error text remains visible.
- Existing ODK runtime label is preserved.

## Verification Summary

Commands run:

```bash
npm --prefix powerpages/webforms-spa run build:mshirika-runtime
python3 scripts/validate-webforms-spa-foundation.py
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-DIkDBSuY.mjs
git diff --check
pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
```

Result:

- Build passed.
- Foundation validator passed.
- Packaged bundle syntax check passed.
- Whitespace check passed.
- Mshirika Power Pages upload succeeded in 96.96 seconds.
- PAC emitted the known `powerpagecomponent ... Does Not Exist` warnings but returned success.

## Review Instructions

1. Purge Power Pages cache and restart the Mshirika site.
2. Open the project and click Collect.
3. Wait for the form to render.
4. Navigate to another internal menu item.
5. Return to the project and click Collect again.
6. Expected result: the same Collect form appears immediately in the same SPA session.

## Residual Risk

This keeps one active Collect runner mounted. If future multi-form switching keeps multiple forms warm, we should add an explicit runner cache eviction policy. Current behavior is scoped to the selected form workflow.
