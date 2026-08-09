# Operational UX Research and Plan - 2026-07-30

## Purpose

Define the next UX direction for Impact Monitoring while CRDB user access is
being prepared. The platform is now a managed Microsoft 365 banking operations
system, not only a TACATDP form launcher. The dashboard, navigation, project
workspace, reporting, and user-management surfaces must therefore be organized
around operational decisions.

## Evidence Reviewed

- User-provided dashboard critique from 2026-07-30.
- Current TACATDP source:
  - `powerpages/webforms-spa/src/views/AssignedFormsView.vue`
  - `docs/powerpages-odk-webforms/managed-service-ux-governance.md`
  - `docs/powerpages-odk-webforms/monitoring-tool-ux-design-system.md`
  - `docs/powerpages-odk-webforms/access-management-ux-design-system.md`
  - `docs/powerpages-odk-webforms/loading-performance-architecture-20260729.md`
  - `docs/powerpages-odk-webforms/reporting-export-role-scope-delivery-20260730.md`
- Material Design:
  - navigation guidance says navigation should be organized around content and
    tasks, and side navigation is appropriate for many top-level destinations
    or two or more hierarchy levels:
    https://m2.material.io/patterns/navigation.html
  - navigation drawers provide access to destinations and are recommended for
    five or more top-level destinations or deeper hierarchies:
    https://m2.material.io/components/navigation-drawer
  - data tables organize rows and columns for scanning, comparison, sorting,
    filtering, actions, and pagination:
    https://m2.material.io/design/components/data-tables.html
- Microsoft design guidance:
  - Fluent 2 emphasizes familiar, platform-natural experiences, focus, low
    clutter, and inclusive design:
    https://fluent2.microsoft.design/design-principles
  - Fluent content design recommends concise, decision-oriented language:
    https://fluent2.microsoft.design/content-design
  - Fluent layout guidance uses spacing and hierarchy to create relationships
    and guide decisions:
    https://fluent2.microsoft.design/layout
- Microsoft Power Pages:
  - Power Pages security uses authenticated users, web roles, table
    permissions, page permissions, and site visibility:
    https://learn.microsoft.com/en-us/power-pages/security/power-pages-security
  - Dataverse records exposed through Power Pages forms, lists, Liquid, and Web
    API are protected by table permissions associated with web roles:
    https://learn.microsoft.com/en-ca/power-pages/security/table-permissions
  - The portals Web API uses `/_api`, requires site settings, follows table
    permissions, and requires CSRF tokens for writes:
    https://learn.microsoft.com/ga-ie/power-pages/configure/web-api-overview
- ODK references:
  - ODK Central organizes projects, forms, submissions, users, and role-based
    permissions:
    https://docs.getodk.org/central-intro/
  - ODK Central project roles distinguish Administrators, Project Managers,
    Viewers, and Data Collectors:
    https://docs.getodk.org/central-users/
  - ODK Collect exposes draft, finalized, ready-to-send, sent, and edit flows:
    https://docs.getodk.org/collect-forms/
  - ODK Central review states include Received, Edited, Has Issues, Approved,
    and Rejected:
    https://docs.getodk.org/central-submissions/
- Accessibility:
  - WCAG 2.2 target-size minimum is 24 by 24 CSS pixels except documented
    exceptions:
    https://www.w3.org/TR/wcag/
  - WAI-ARIA APG provides accessible patterns for dynamic widgets including
    tabs, dialogs, tables, grids, and focus management:
    https://www.w3.org/WAI/ARIA/apg/

## Current UX Diagnosis

The current shell is clean and already follows the managed-service direction:
left navigation, top app bar, admin-only User & Access, project workspaces,
Material-style tabs, role-aware reporting export, and improved loading
performance.

The main gap is that the landing dashboard still reads as a status summary. It
shows technically true facts, but it does not yet answer the operational
questions a bank worker has when starting work:

1. What do I need to do now?
2. Which project or form needs attention?
3. What records are drafts, queued, submitted, returned, or approved?
4. Is the system synchronized and healthy enough for field work?
5. What can I see or export based on my role?

The next UX direction should therefore shift from entity counts to an
operational command center.

## Product Position

Use **Impact Monitoring** as the platform product name. TACATDP appears as a
project name only when the user is working inside that project or reviewing
that project's reporting and access scope.

The platform should feel like:

- a Microsoft 365 operations tool;
- a banking-grade managed service;
- role-governed and auditable;
- compact, predictable, and calm;
- optimized for daily work by CRDB staff.

It should not feel like:

- a research prototype;
- a Kobo/ODK clone;
- a marketing landing page;
- a diagnostic console;
- a form-only launcher.

## Core Design Decision

Use a two-level operational model:

1. **Global operational dashboard**
   - Answers "what should I do now?"
   - Role-specific.
   - Shows attention, active assignments, workload, synchronization, recent
     activity, and role-specific shortcuts.
2. **Project workspace**
   - Answers "what is happening in this project?"
   - Uses the existing project command surface and Material tabs:
     Summary, Data, Exports, Power BI, and future Settings.
   - Keeps collection contextual to a project/form, with the `Collect` action
     on the project command surface.

Do not introduce a global form selector. If a global `Collect data` destination
is added later, it must land on a task queue and still require a project/form
context before opening the ODK runtime.

## Information Architecture

### Current Stage

Keep the existing shell but revise route purpose:

| Route | Purpose |
| --- | --- |
| Dashboard | Role-specific operational command center |
| Projects | Browse and open project workspaces |
| Reporting | Cross-project reporting entry point, role-scoped |
| User & Access | Admin-only user, invitation, role, assignment, and delivery settings |

### Planned Platform Stage

When multi-project and monitoring features mature, evolve toward:

| Top side nav | Purpose |
| --- | --- |
| Home | Operational dashboard and attention queue |
| Projects | Project workspaces, forms, targets, team/site context |
| Data collection | Drafts, queued records, returned records, assigned collection work |
| Monitoring | Progress, data quality, field activity, exceptions |
| Reports | Standard reports, exports, Power BI, scheduled reporting |

Bottom administration group:

| Bottom side nav | Purpose |
| --- | --- |
| User & Access | Users, roles, invitations, project/form assignment |
| Configuration | Mailbox, notification, integration, environment, Power BI settings |
| Audit | Security and operational audit, if separated from Monitoring |

Only add top-level destinations when they are real routes with useful content.
Do not add empty navigation promises.

## Role-Specific Dashboard Model

### Data Collector / Bank Officer

Primary question: What data should I collect or correct now?

Show:

- active assignment card with one primary `Continue collection` or `Collect`
  action;
- drafts and queued records;
- returned records requiring correction;
- submitted today;
- synchronization state;
- recent own submissions.

Hide:

- user-management controls;
- all-record exports;
- project configuration;
- platform health unless it affects collection.

### Supervisor / Reviewer

Primary question: What records or people need review?

Show:

- attention required: returned, has issues, failed projection, missing
  attachments, short-duration anomalies when available;
- review queue;
- submissions by collector/site/form;
- data-quality indicators;
- recent review activity.

### Project Manager

Primary question: Is this project on track and what needs intervention?

Show:

- project progress against target when configured;
- forms active/inactive/version changed;
- team activity and assignment coverage;
- data-quality alerts;
- export/reporting freshness;
- scoped User & Access entry when permitted.

### Programme Manager

Primary question: Are programmes and reporting obligations on track?

Show:

- cross-project progress;
- trends by period/geography/form;
- upcoming deadlines;
- Power BI/reporting readiness;
- high-level data-quality exceptions.

### Platform Administrator

Primary question: Is the platform healthy and governed?

Show:

- failed onboarding requests;
- mailbox/manual-code delivery configuration;
- role and permission setup state;
- form version state;
- projection/queue failures;
- audit and environment warnings.

## Dashboard Layout Contract

Use this order on desktop and tablet:

1. **Attention required**
   - First visible panel after the route header.
   - Shows exceptions and next actions.
   - If clear, show a compact positive empty state: `No issues require your
     attention`.
2. **Active assignment / current work**
   - One project/form card focused on the primary user task.
   - One clear primary action.
   - Secondary actions move to a compact menu or adjacent secondary buttons.
3. **Operational metric strip**
   - Small, actionable metrics only.
   - Recommended first-slice metrics:
     - Active projects
     - Forms requiring action
     - Local drafts
     - Submitted today
     - Pending sync
     - Returned / has issues
4. **Progress or trend**
   - Show target progress only if denominator/target exists.
   - If no target exists, show activity trend or submitted-today summary
     instead of a fake percentage.
5. **Recent activity**
   - Compact table/list.
   - Uses role scope:
     - collectors see their own submitted/editable/returned records;
     - administrators and project managers see project-scoped/all permitted
       records.
6. **System/sync status**
   - Small status strip or side panel, not oversized dashboard cards.
   - Distinguish browser connectivity, server availability, auth session, local
     drafts, queued records, failed sync, and last successful refresh.

On mobile:

- Stack sections in the same priority order.
- Replace dense tables with record cards.
- Keep primary action visible near the active assignment.
- Keep icon targets at least 24 by 24 CSS pixels and preferably 40-44 pixels
  for touch comfort.

## Route and Component Organization

Use reusable components rather than page-local dashboard blocks:

| Component | Responsibility |
| --- | --- |
| `OperationalAttentionPanel` | Role-scoped exceptions and next actions |
| `ActiveAssignmentPanel` | Current project/form work and primary collect action |
| `OperationalMetricStrip` | Compact workload/status metrics |
| `SyncStatusStrip` | Connectivity, server, auth, sync queue, last refresh |
| `CollectionProgressPanel` | Target-aware progress or trend fallback |
| `RecordStatusSummary` | Draft, queued, submitted, returned, approved counts |
| `RecentActivityList` | Role-scoped recent submission/activity rows |
| `DataQualityPanel` | Review issues and quality signals when available |
| `AdminHealthPanel` | Onboarding, mailbox, permissions, projections, audit |

The dashboard should compose these components. Project tabs and User & Access
must reuse the same status, empty, table, drawer, confirmation, and snackbar
patterns.

## Operational State Model

Expose record state as a lifecycle, not a single ambiguous status:

```text
Local draft
  -> ready to submit
  -> queued for synchronization
  -> synchronizing
  -> submitted
  -> under review
      -> approved
      -> returned for correction
      -> rejected
```

Current Dataverse mapping:

| UX state | Current source |
| --- | --- |
| Local draft | IndexedDB local draft records |
| Submitted | `mp_submission` / `mp_submissionreportrow` lifecycle |
| Edited | submission version count and ODK-style review state |
| Received / Has issues / Approved / Rejected | `mp_reviewstate` |
| Projection ready/failed | `mp_projectionstatus` and `mp_projectionerror` |
| Pending sync / failed sync | future explicit local sync queue |

Do not display `Online` as a major metric. Show it as one part of sync status.

## Visual Rules

- Reduce repeated CRDB green borders.
- Use CRDB green mainly for brand and positive/primary actions.
- Use amber for pending/attention states.
- Use red for blocking errors and destructive actions.
- Use blue/teal sparingly for informational states.
- Use neutral surfaces for routine panels.
- Keep text sentence case and concise.
- Do not use oversized dashboard headings inside the app shell.
- Use tables for dense records on desktop and cards on mobile.
- Use drawers for inspect/edit flows.
- Use dialogs only for high-impact confirmation.
- Every write shows loading, success, and failure feedback.
- Every async status message uses visible text and an accessible live region
  where practical.

## Requirements

### R1. Role-specific landing

The authenticated landing page must render a dashboard view based on the
user's role/capabilities.

Acceptance:

- Data Collector sees own assignments, drafts, returned records, and own recent
  submissions.
- Platform Administrator sees operational plus platform-health items.
- Admin-only navigation remains hidden from non-admin roles and reinforced by
  route checks.

### R2. Attention before metrics

The dashboard must surface exceptions before normal project lists.

Acceptance:

- At least one `Attention required` panel appears before generic metrics.
- Clear state displays a compact "no issues" state.
- Items include action labels or route targets.

### R3. One primary action

Each work card must have one primary action.

Acceptance:

- Active assignment cards use `Collect`, `Continue collection`, or `Review`
  based on role and state.
- Secondary actions do not compete visually with the primary action.

### R4. Target-aware progress

Progress percentage must only be displayed when a denominator exists.

Acceptance:

- If no target is configured, the panel shows recent activity/trend instead.
- The UI does not invent completion percentages.

### R5. Explicit state and feedback

The platform must expose draft, sync, submitted, review, projection, and error
states in plain language.

Acceptance:

- Record lists show lifecycle and review state separately.
- Submission, onboarding, export, and assignment writes show success or failure
  messages and do not silently redirect.

### R6. Role-scoped data visibility

Dashboard and export counts must respect the same data visibility contract as
the Data and Export tabs.

Acceptance:

- Administrators/project managers can see/download all records permitted by
  table permissions and TACATDP role scope.
- Data collectors can see/download only records they submitted unless later
  requirements explicitly change that.

### R7. Performance-aware composition

Dashboard improvements must not reintroduce slow startup.

Acceptance:

- Startup fetches assignments and local draft state only.
- Reporting rows and detailed submission payloads load lazily or with small
  bounded counts.
- Existing performance markers remain available for browser testing.

## ADR-0010: Role-Based Operational Dashboard

Status: Proposed

Decision:

Impact Monitoring will use a role-based operational dashboard as the
authenticated landing surface. The dashboard will prioritize attention,
current work, workload/sync state, progress/trend, and recent activity instead
of generic entity counts.

Context:

The app has evolved into a managed banking platform with CRDB Microsoft
identity, Power Pages web roles/table permissions, project/form assignments,
submission/reporting projections, and governed User & Access workflows. A
status landing page is insufficient for daily operations.

Consequences:

- The dashboard becomes a workflow surface, not a reporting shortcut.
- Role and data-scope contracts must be reusable across dashboard, Data,
  Exports, Power BI, and User & Access.
- Collection remains project/form contextual to preserve the current model.
- Additional metrics may require schema/data work later, especially collection
  targets, sync queue, sites/geographies, and data-quality flags.
- Startup performance must remain protected by lazy-loading heavy data.

## Delivery Plan

### Slice 1: Dashboard IA and reusable components

Scope:

- Replace generic dashboard counters with attention, active assignment,
  workload metrics, sync strip, and recent activity shell.
- Use only existing data: assigned forms, local drafts, role flags, bounded
  reporting-row counts where available.
- No new Dataverse schema.

Verification:

- `npm run build`
- `python3 scripts/validate-webforms-spa-foundation.py`
- desktop and phone visual inspection;
- browser timing: dashboard shell should render before reporting rows or ODK
  runtime load.

### Slice 2: Record lifecycle labels and dashboard status contract

Scope:

- Normalize display labels for lifecycle, review, projection, draft, and local
  sync states.
- Reuse labels in Dashboard, Data tab, Exports, and submission detail.

Verification:

- unit/DOM checks for visible state chips;
- browser check with collector and admin roles.

### Slice 3: Role-specific dashboard variants

Scope:

- Add dashboard sections by capability:
  - collector view;
  - project manager/supervisor view;
  - platform admin health view.
- Keep hidden routes backed by real role checks.

Verification:

- browser smoke as collector and platform admin;
- confirm Data/Export scope remains unchanged.

### Slice 4: Targets and progress

Scope:

- Add a governed target data contract for project/form/period/site targets.
- Show progress only when target rows exist.

Verification:

- Dataverse schema/package review before write;
- progress falls back cleanly when no target exists.

### Slice 5: Data quality and monitoring route

Scope:

- Add data-quality signals and Monitoring route after the state model and
  projection builder can support them.
- Possible first signals: review state, failed projection, missing attachment
  metadata, duplicate instance id, stale draft/pending sync.

Verification:

- quality rules documented;
- no hidden all-record access for collectors.

## Definition of Ready for Implementation

Before coding Slice 1, inspect:

- this artifact;
- `managed-service-ux-governance.md`;
- `monitoring-tool-ux-design-system.md`;
- `loading-performance-architecture-20260729.md`;
- `AssignedFormsView.vue`;
- `styles.css`;
- current reporting role-scope delivery note.

Implementation must state:

- role being served;
- data visibility scope;
- loading, empty, error, success states;
- whether each metric is exact, bounded, or pending future schema;
- performance risk and lazy-loading decision.

## Recommended Next Slice

Deliver **Slice 1: Dashboard IA and reusable components** first.

Reason:

- It improves the first screen without waiting for CRDB mailbox, user testing,
  project targets, or new schema.
- It aligns the platform with bank-worker daily workflow.
- It protects current performance improvements by keeping heavy data lazy.
- It creates reusable components for later Monitoring, Reports, and User &
  Access polishing.

Non-goals for Slice 1:

- no fake completion percentages;
- no new global form selector;
- no new top-level routes unless content is real;
- no schema changes;
- no all-record exposure for collectors.

