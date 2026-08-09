# Startup Skeleton Background Hydration Delivery - 2026-07-30

## Task Classification

Frontend UX and perceived-performance improvement for the Power Pages shell startup. This change does not alter Dataverse schema, table permissions, authentication, submission writes, reporting projection, or user-management writes.

## Requirement

The portal shell and route headers must render immediately while Dataverse workspace assignment data loads in the background. Slow `listAssignedForms` calls should not show a full blocking loading panel on Dashboard or Projects.

## UX Description

- The managed shell, top bar, side navigation, and route header render first.
- Dashboard metrics show compact skeleton values while assignments are loading.
- Dashboard and Projects show project-card skeleton previews while the assignment query is in flight.
- Empty states appear only after hydration finishes and no assignments are returned.
- Error states remain visible and actionable after failed hydration.
- Skeleton animation respects `prefers-reduced-motion`.

## Implementation

- Added `workspaceHydrating` as a route-body loading signal separate from `loading`.
- `loadWorkspace` now sets and clears `workspaceHydrating` around the assignment/draft hydration call.
- Replaced Dashboard and Projects blocking loading panels with skeleton metric/project content.
- Kept `measureAsync('view:loadWorkspace')` and `api:listAssignedForms` instrumentation.
- Added validator checks that prevent reintroducing blocking startup panels.
- Packaged bundle `index-bZwSdwHP.mjs?v=startup-skeleton-20260730-001` with the matching CSS and hashed build assets.

## Acceptance Criteria

- App shell appears immediately after the SPA mounts.
- Dashboard route does not replace content with a full loading panel while assignments load.
- Projects route does not replace content with a full loading panel while assignments load.
- Skeleton cards show while the first assignment load is in flight.
- Empty-state messaging waits until `workspaceHydrating` is false.
- Existing performance timing logs remain available.

## Accessibility Checklist

- Skeleton cards use visible layout placeholders and avoid interactive controls.
- Loading preview regions use `aria-live` or `aria-busy` where useful.
- Motion is disabled when `prefers-reduced-motion: reduce` is active.
- Error messages remain text-based and visible.

## Verification Summary

Commands run:

```bash
npm --prefix powerpages/webforms-spa run build:mshirika-runtime
python3 scripts/validate-webforms-spa-foundation.py
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-bZwSdwHP.mjs
git diff --check
pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
```

Result:

- Build passed.
- Foundation validator passed.
- Packaged entry syntax check passed.
- Whitespace check passed.
- Mshirika Power Pages upload succeeded in 83.57 seconds.
- PAC emitted the known `powerpagecomponent ... Does Not Exist` warnings but returned success.

## Review Instructions

1. Purge Power Pages cache and restart the Mshirika site.
2. Open the portal in a fresh tab.
3. Confirm shell and route header appear quickly.
4. Confirm Dashboard/Projects show skeleton content while assignment data loads.
5. Confirm project cards replace skeletons after hydration.
6. Confirm console still reports `view:loadWorkspace` and `api:listAssignedForms` timings.

## Residual Risk

This improves perceived startup but does not reduce the Dataverse assignment query latency itself. If CRDB still sees long assignment timings, the next options remain a server-side/user-access projection table or a smaller startup API surface.
