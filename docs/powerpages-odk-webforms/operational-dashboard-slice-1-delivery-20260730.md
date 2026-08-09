# Operational Dashboard Slice 1 Delivery - 2026-07-30

## Task Classification

Frontend UX implementation. Low-risk code change limited to the Power Pages SPA
landing dashboard and reusable dashboard styling. No Dataverse schema, table
permission, site setting, authentication, deployment, or data migration change.

## Requirements Note

Deliver the first operational dashboard slice from
`operational-ux-research-and-plan-20260730.md` using existing data only.

The authenticated landing view must:

- prioritize attention and current work before generic counters;
- show one primary collection action for the active assignment;
- expose local drafts, assigned forms, active projects, and submitted-count
  state without loading heavy reporting datasets at startup;
- show connectivity as a small sync/status strip, not as a major dashboard
  card;
- keep project/form selection contextual to the project workspace;
- preserve the existing role/data-scope rule: collectors do not get all-record
  export/read behavior through dashboard shortcuts.

Non-goals:

- no new Dataverse schema;
- no fake completion percentages;
- no global form selector;
- no new top-level route;
- no CRDB deployment in this slice.

## UX Description

The Dashboard becomes a compact operational command center:

1. route header with refresh action;
2. `Attention required` panel;
3. active assignment card with `Collect` as the only primary action;
4. small workload metric strip;
5. two-column lower layout containing assigned projects and recent activity;
6. sync/status information shown as operational context.

The dashboard should feel like a Microsoft 365 banking operations surface:
quiet, compact, decision-oriented, and role-aware.

## User Story

As a signed-in CRDB staff member, I want the landing page to show what needs my
attention and the next action I can take, so that I can continue collection or
review work without interpreting technical counters.

Acceptance:

- I can see whether there are attention items.
- I can start collection from the active assignment.
- I can see local draft count and assignment count.
- I can open the project workspace.
- I receive a clear empty state when no projects are assigned.

## Accessibility Checklist

- Icon buttons keep text labels or accessible names.
- Status and error banners remain visible and use `aria-live` where applicable.
- Dashboard cards use semantic headings and lists where practical.
- Touch/click actions remain at least 24 by 24 CSS pixels.
- Skeleton loading panels use `aria-live` and do not trap focus.
- Color is not the only state indicator; labels accompany state chips.

## Acceptance Criteria

- Dashboard no longer starts with four generic status cards.
- `Online` is shown in a compact status strip with last refresh context.
- `Attention required` appears before work cards.
- Active assignment has one primary `Collect` action.
- Assigned projects remain visible and open the existing project workspace.
- Recent activity uses existing `submissions` data when available and otherwise
  shows a concise empty state.
- No `mp_submissionreportrow` or full submission load is added to startup.
- `npm run build` passes.
- `python3 scripts/validate-webforms-spa-foundation.py` passes.

## Artifact Readiness

Ready to implement.

Evidence:

- `operational-ux-research-and-plan-20260730.md`
- `managed-service-ux-governance.md`
- `monitoring-tool-ux-design-system.md`
- `loading-performance-architecture-20260729.md`
- `AssignedFormsView.vue`
- `styles.css`

## Trace

Protocol trace: `20260730-084739-797d17`.

Implementation surfaces:

- `powerpages/webforms-spa/src/views/AssignedFormsView.vue`
- `powerpages/webforms-spa/src/styles.css`

## Screenshot or Render Evidence

Local Vite render evidence:

- Desktop screenshot:
  `/tmp/tacatdp-operational-dashboard-20260730.png`
- Mobile screenshot:
  `/tmp/tacatdp-operational-dashboard-mobile-20260730.png`

Observed result:

- dashboard hierarchy is clear;
- attention panel appears before active work and metrics;
- active assignment actions fit on desktop and stack on mobile;
- footer remains below the shell content;
- no text or action overlap was visible in the checked viewports.

Hosted screenshot evidence is deferred until the next Mshirika/CRDB upload.

## Verification Summary

Commands:

```bash
npm run build
python3 scripts/validate-webforms-spa-foundation.py
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-BAoMJLdj.mjs
git diff --check
npx playwright screenshot --wait-for-timeout=2500 http://127.0.0.1:5174/ /tmp/tacatdp-operational-dashboard-20260730.png
npx playwright screenshot --viewport-size=390,844 --wait-for-timeout=2500 http://127.0.0.1:5174/ /tmp/tacatdp-operational-dashboard-mobile-20260730.png
```

Results:

- `npm run build` passed.
- `validate-webforms-spa-foundation.py` passed.
- Packaged entry `node --check` passed.
- `git diff --check` passed.
- Desktop and mobile screenshots were captured from the local Vite server.

Known warnings:

- Vite still reports direct `eval` and large chunks from upstream
  `@getodk/web-forms`. This is a known production-hardening risk and was not
  introduced by the dashboard slice.

