# System Activity Material Surface Refinement — August 11, 2026

## Scope

This slice refines the System Activity route after the Projects, Users, Project detail, and Reporting Material passes. The intent is to make operational health, events, onboarding diagnostics, submissions, and integrations follow the same Material-style surface and row contract while preserving authorization and diagnostics behavior.

## Delivered behavior

- System Activity keeps the administrator authorization gate.
- System Activity keeps its metric summary cards and section tabs.
- Health, Events, Onboarding, Submissions, and Integrations panels now use a shared `system-activity-surface` class.
- Activity rows now use a stable `system-activity-row--material` class with keyboard focus and hover feedback.
- Activity rows keep:
  - text-labelled status chips,
  - event identity,
  - supporting detail and target,
  - explicit next-action content.
- Activation diagnostics remains a semantic desktop table and now includes:
  - accessible caption,
  - scoped column headers,
  - keyboard-reachable rows,
  - numeric alignment for active assignment count,
  - text-labelled status chips for contact, email, invitation, redemption, identity, web role, assignment, and next action.

## Non-goals

- No authorization, role detection, invitation, identity-binding, assignment, Dataverse, or Power Pages Web API logic changed.
- No activity event generation changed.
- No new UI dependency was added.
- No deployment was performed as part of this slice.

## Verification

Run from `powerpages/webforms-spa`:

```bash
npm run test:material
npm run typecheck
npm run build:mshirika-runtime
npm run test:powerpages-assets
```

The focused validator is:

```bash
node ../../scripts/validate-system-activity-material-surface.mjs
```
