# Dashboard Submitted Records Entrypoint Delivery - 2026-07-30

## Task Classification

- Project: TACATDP Power Pages monitoring tool.
- Change type: frontend UX refinement with state-semantics governance.
- Risk: low; no schema, permission, deployment, authentication, or data-write change.
- Trace: `20260730-112430-a10b28`.

## Requirements Note

The dashboard must communicate how a user accesses submitted records without pretending that record data has already been loaded. The submitted-records surface should be user-oriented, for example `Open Data to view submitted records`, and should show the user's data visibility scope.

The dashboard must avoid implementation-language copy such as `Loaded on demand`. It must also avoid a submitted-record count at startup unless the data table has actually queried the records in that session.

## Product Requirements

- Replace the fourth workload metric with a data-access scope indicator.
- Make the submitted-records dashboard panel an entry point to the project Data tab.
- Show the relevant visibility scope: `My records` for collector scope and `All project records` for administrator/all-record scope.
- Keep `Collect` as the filled primary action in the active-assignment card, and keep `Open` as the primary action inside each assigned-project card.
- Preserve lazy loading of submitted records so dashboard startup does not query large record tables.

## UX Description

The dashboard uses a predictable operational hierarchy: status, attention, active assignment, workload metrics, work queue, and data access. The submitted-records panel is not an empty table preview. It is a compact action card with:

- eyebrow: `Data access`;
- title: `Submitted records`;
- secondary action: `Open Data`;
- summary: `View submitted records, review status, and recent changes.`;
- scope line: `Scope: My records` or `Scope: All project records`;
- optional recent rows only when records are already available in the session.

Metric cards share anatomy: body on the left and a bounded icon well on the right. Icons are decorative and hidden from assistive technology.

## Accessibility Checklist

- The submitted-records entry has a visible heading and button label.
- The Open Data button has an explicit `aria-label`.
- Metric icons are decorative with `aria-hidden="true"`.
- The scope text is visible text, not tooltip-only information.
- The dashboard still supports keyboard activation through native buttons.
- Empty state language describes the next action and does not imply data loss.

## Acceptance Criteria

- Dashboard metric strip contains `Data access`, not `Submitted records` as a startup metric.
- The dashboard includes `Open Data to view submitted records`.
- The submitted-records panel shows `Scope:` with the current reporting visibility scope.
- `Loaded on demand`, `No recent activity loaded`, and `id: 'submitted-records'` are absent from the dashboard source.
- Assigned-project `Open` remains primary within the project card; submitted-records `Open Data` remains secondary because it opens a data surface rather than starting work.
- `npm run build`, `scripts/validate-webforms-spa-foundation.py`, `node --check`, and `git diff --check` pass.
- Desktop and mobile screenshots show no overlap or clipped action text.

## Artifact Readiness

- Reused artifacts: `managed-service-ux-governance.md`, `monitoring-tool-ux-design-system.md`, `operational-dashboard-state-semantics-delivery-20260730.md`.
- Updated executable guard: `scripts/validate-webforms-spa-foundation.py`.
- New artifact: this delivery note.
- Not applicable: ADR, schema artifact, permission plan, deployment runbook. This slice changes copy/component layout only.

## Implementation Instructions

Inspect:

- `powerpages/webforms-spa/src/views/AssignedFormsView.vue` for dashboard metrics and submitted-records panel.
- `powerpages/webforms-spa/src/styles.css` for metric and data-entry panel anatomy.
- `scripts/validate-webforms-spa-foundation.py` for regression assertions.

Implement:

- Replace the submitted-records metric with data-access scope state derived from the existing reporting-access scope helper.
- Make the submitted-records panel a Data-tab entry point with visible scope and user-facing wording.
- Add metric icon anatomy using existing Lucide icons.
- Keep record querying in the Data tab, not workspace startup.

Verify:

- `npm run build`
- `python3 scripts/validate-webforms-spa-foundation.py`
- `node --check <built-index-file>`
- `git diff --check`
- Playwright screenshot at desktop and mobile widths.

## Verification Summary

- `npm run build` passed on 2026-07-30. Vite/Rolldown still reports the known upstream `@getodk/web-forms` direct-`eval` and chunk-size warnings.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check powerpages/tacatdp-monitoring-tool/.powerpages-site/web-files/index-CSHg0cjz.mjs` passed.
- `git diff --check` passed.
- Desktop screenshot: `/tmp/tacatdp-dashboard-submitted-entry-final-desktop-20260730.png`.
- Mobile screenshot: `/tmp/tacatdp-dashboard-submitted-entry-final-mobile-20260730.png`.
- Packaged Home page references use cache key `dashboard-submitted-entry-20260730-001` and built assets `index-CSHg0cjz.mjs` / `index-C8Ti5iJo.css`.
