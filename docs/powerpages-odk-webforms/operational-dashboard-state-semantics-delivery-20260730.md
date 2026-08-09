# Operational Dashboard State Semantics - 2026-07-30

## Task Classification

Frontend UX refinement. Low-risk changes to dashboard copy, status provenance,
clear-state density, and action hierarchy. No schema, permission, authentication,
API, synchronization engine, or deployment change.

Protocol trace: `20260730-100430-1dfd07`.

## Product Requirements

The dashboard must describe only state that the current implementation can
prove. It must distinguish device-local state from server-refreshed assignment
state and must not imply that submitted records or Dataverse health were
refreshed at startup.

For signed-in Impact Monitoring users:

- browser connectivity is labelled `Device connected` or `Device offline`;
- refresh time is explicitly scoped to assignments;
- drafts are labelled as records on the current device;
- assigned form count is not described as urgent work without evidence;
- submitted-record guidance directs the user to the project Data tab;
- a clear attention state is compact and states the scope of checks;
- `Collect` remains the only primary action in the active assignment;
- dashboard navigation and refresh actions use the secondary action treatment.

## System Design Thinking

### Boundary

In scope: the authenticated dashboard's state labels, attention clear state,
metric wording, and action hierarchy. Out of scope: new server health probes,
submission counts at startup, sync queues, conflict handling, capability APIs,
or dashboard projections.

### Actors and Jobs

- Collector or bank officer: identify available work and start collection
  without mistaking device connectivity for successful synchronization.
- Manager or administrator: understand assignment and data visibility without
  incurring a reporting query during startup.
- Support staff: diagnose whether displayed state came from the device or the
  latest assignment refresh.

### Structure

- Browser -> dashboard: `navigator.onLine` connectivity signal.
- IndexedDB -> dashboard: restorable drafts on this browser/device.
- Power Pages Web API -> dashboard: signed-in user's assigned forms.
- Project Data tab -> user: submitted records loaded on demand under existing
  table-permission and reporting-scope rules.

### Dynamics and Delays

Power Pages assignment reads can take several seconds. Submission/reporting
queries are intentionally lazy to protect startup time. Generic `Online`,
`refreshed`, and `Clear` labels can therefore overstate freshness or health.

### Leverage Points

Precise provenance labels improve trust without adding requests. Correcting the
shared secondary-action selector restores the intended visual hierarchy across
existing icon actions. Both changes are reversible and require no data changes.

### Design Rules

- State labels must name their source or scope when sources have different
  freshness guarantees.
- Browser connectivity must not be labelled as server synchronization.
- Device-local drafts must say `on this device`.
- Lazy data guidance must describe the user action, not the implementation.
- A positive attention state must not claim whole-platform health.
- One task surface has one visually dominant primary action.

### Delivery Slices

This slice changes the existing dashboard only and adds validator assertions.
Future slices may define an operational-check rule model, capability contract,
sync state machine, and dashboard projection after separate approval.

### Backfire Risks

- Adding server checks now could reintroduce startup latency; no calls are added.
- Removing reporting scope from the status strip could hide authorization
  context; Data and Export surfaces retain their explicit scope disclosure.
- Global secondary-button correction affects shared icon actions; visual checks
  must cover dashboard and mobile layouts.

### Synthesis

Make the existing lightweight dashboard more truthful before expanding its
monitoring architecture. Preserve lazy reporting and Power Pages security
boundaries while improving user decisions through precise state language.

## UX Description

The status strip becomes a compact provenance line: device connection,
assignment refresh time, and draft count on this device. The empty attention
surface collapses to a short positive row; actual attention items keep the full
panel. The active assignment retains a green `Collect` action while `View
project`, refresh, project navigation, and Data navigation use a neutral
secondary treatment.

## Accessibility Checklist

- Connectivity keeps visible text in addition to the colored state dot.
- Refresh retains an accessible name describing assignments and drafts.
- The clear attention row uses an icon plus text, not color alone.
- Primary and secondary actions retain visible labels and focus rings.
- No focus order, route authorization, or ODK runtime semantics change.

## Acceptance Criteria

- Dashboard does not display generic `Online` as a synchronization guarantee.
- Assignment refresh time is explicit.
- Draft count says it applies to this device.
- Metric label is `Assigned forms`, not `Forms requiring action`.
- Submitted-record guidance says to open Data and does not say `Loaded on demand`.
- Clear attention state is compact and bounded to known dashboard checks.
- `Collect` is visually primary; secondary icon actions render with a neutral
  surface treatment.
- Workspace startup still does not call `listSavedSubmissions`.
- SPA build, foundation validator, syntax check, and desktop/mobile render checks
  pass.

## Artifact Readiness

Ready. Reuses:

- `operational-ux-research-and-plan-20260730.md`
- `operational-dashboard-slice-1-delivery-20260730.md`
- `managed-service-ux-governance.md`
- `loading-performance-architecture-20260729.md`
- `monitoring-tool-ux-design-system.md`

An ADR is not required because this slice does not change architecture or data
contracts.

Implementation surfaces:

- `powerpages/webforms-spa/src/views/AssignedFormsView.vue`
- `powerpages/webforms-spa/src/styles.css`
- `scripts/validate-webforms-spa-foundation.py`
- built Power Pages web files and Home asset references

## Screenshot Or Render Evidence

Local Vite render evidence:

- Desktop: `/tmp/tacatdp-dashboard-state-semantics-desktop-20260730.png`
- Mobile: `/tmp/tacatdp-dashboard-state-semantics-mobile-20260730.png`

Observed:

- clear attention state is compact and visibly bounded;
- status provenance remains readable on desktop and wraps cleanly on mobile;
- `Collect` is the only filled action in the active assignment;
- secondary actions use the neutral surface treatment;
- action labels and project/version text fit without overlap;
- the shell footer remains outside the scrollable workspace content.

## Verification Summary

Commands:

```bash
npm run build
python3 scripts/validate-webforms-spa-foundation.py
node --check powerpages/tacatdp-monitoring-tool/.powerpages-site/web-files/index-C_Cvh4Er.mjs
git diff --check
npx playwright screenshot --wait-for-timeout=2500 http://127.0.0.1:5174/ /tmp/tacatdp-dashboard-state-semantics-desktop-20260730.png
npx playwright screenshot --viewport-size=390,844 --wait-for-timeout=2500 http://127.0.0.1:5174/ /tmp/tacatdp-dashboard-state-semantics-mobile-20260730.png
```

Results:

- production build passed;
- foundation validator passed with new semantic-copy and secondary-action
  assertions;
- packaged module syntax check passed;
- diff whitespace check passed;
- desktop and mobile render inspection passed.

Built assets:

- `index-C_Cvh4Er.mjs`
- `index-B9OjN5jt.css`
- cache key `dashboard-state-semantics-20260730-001`

Known upstream warnings remain for direct `eval` and large chunks in
`@getodk/web-forms`. No Power Pages upload or environment change was performed.
