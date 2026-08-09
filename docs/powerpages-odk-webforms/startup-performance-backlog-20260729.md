# Startup Performance Backlog

Date: 2026-07-29

## Current Evidence

Mshirika signed-in timings:

| Slice | Bundle | `api:listAssignedForms` |
| --- | --- | ---: |
| Original startup | pre-performance | 10642 ms |
| Metadata-only startup | `index-DJMa_UT7.mjs` | 4954 ms |
| Linked assignment metadata query | `index-BbJfdreX.mjs` | 3993 ms |

`app-mounted` is about 12-14 ms, so Vue startup is not the bottleneck. Remaining delay is likely the first authenticated Power Pages `/_api` Dataverse request plus portal/server-side cache behavior.

## Option 1 - Pause Performance Work for Now

Status: accepted for the current milestone.

Keep the current linked-query implementation and move to the Collect runtime blocker. Startup is not perfect, but it is materially better and no longer blocks project visibility through submission or XForm hydration waterfalls.

Use this option while Collect remains the largest functional gap.

## Option 2 - Improve Perceived Loading UX

Status: deferred, revisit after Collect runtime path is decided.

Scope:

- Render stable shell and project loading skeletons while assignment API loads.
- Show panel-local loading states instead of whole-workspace blank waits.
- Keep Data, Reporting, User & Access, and Collect route loading states separate.
- Add clear empty/error states for assignment fetch failures.

Value:

- Improves user trust during the remaining 3-4 second first API call.
- Does not reduce actual Dataverse latency.

Trigger to revisit:

- Users still report the portal feels stuck even after the linked-query deployment.
- CRDB environment first-call latency is significantly worse than Mshirika.

## Option 3 - Precomputed User Workspace Snapshot

Status: deferred; architectural feature, not a quick UI fix.

Scope:

- Add a small Dataverse table or server-generated record containing the signed-in user's current workspace/project/form assignment metadata.
- Update the snapshot when assignments, forms, form versions, or role changes occur.
- Read one small record on startup instead of joining assignment/form metadata live.

Value:

- Could make startup a single tiny read.
- Reduces dependence on linked FetchXML and per-request portal overhead.

Risks:

- Requires schema, processor/flow/plugin, invalidation rules, auditability, and permissions.
- Snapshot staleness must be governed because access changes in a banking environment must take effect predictably.

Trigger to revisit:

- Linked-query startup remains above an acceptable threshold in CRDB after cache warm-up.
- Multi-project support increases assignment metadata size.
- CRDB requires stricter audit/read models for workspace access.

## Current Next Action

Move to Collect runtime packaging. Do not spend more implementation time on startup performance until Collect has a deployable runtime path.
