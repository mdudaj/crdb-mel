# Managed Portal Route and Content Model

Date: 2026-07-21

## Purpose

Define what the TACATDP Monitoring Tool should show after sign-in and how the
right content area should be organized as the portal grows from a prototype
into a managed banking operations system.

This artifact governs future route, navigation, and content-area changes in
the Power Pages SPA.

## Evidence

- TACATDP current shell implementation:
  - `powerpages/webforms-spa/src/views/AssignedFormsView.vue`
  - `powerpages/webforms-spa/src/styles.css`
- TACATDP shell governance:
  - `managed-service-ux-governance.md`
  - `managed-service-ux-agent-checklist.md`
- Local precedents:
  - LIMS keeps a pinned drawer and top app bar while the task surface scrolls.
  - LIMS separates routine work from bottom configuration/admin navigation.
  - STEMGEN uses a side nav, top bar, app content area, and persisted collapsed
    rail state.
- Microsoft Power Pages web-template guidance: when `Use Website Header and
  Footer` is enabled, the page template renders between global header/footer;
  when disabled, the template must render the complete response.
- Material layout guidance: desktop app structure uses app bar, side
  navigation, and content canvas; app-bar nav icon opens navigation or moves up
  hierarchy; drawer destinations should be organized by importance and grouped
  when related.

## Current Problem

The shell slots are now correct, but the route content still behaves like a
prototype:

- after login, the first content area is a large projects hero rather than a
  concise operational dashboard;
- global navigation and project context are partially mixed;
- Reporting currently jumps into the selected project's Data tab instead of
  being a real reporting route;
- User & Access is a route-like surface but still shares implementation with
  one large component;
- project pages carry too much page-specific structure without a reusable route
  contract;
- there is no documented rule for what belongs in the right content area when a
  user first signs in.

## Route Model

Use explicit route states even while the first implementation remains a
single-page Vue component. Future work should migrate these states to real route
objects or a small local router.

### `/` or `/dashboard`

Default authenticated landing route.

Purpose:

- tell the signed-in bank worker what needs attention now;
- provide entry into assigned projects;
- summarize recent collection/reporting activity;
- show access limitations clearly.

Content anatomy:

1. `route-header`
   - title: `Dashboard`;
   - subtitle: role-aware summary such as assigned projects/forms;
   - right actions: Refresh only.
2. `status-strip`
   - Projects in scope;
   - Assigned forms;
   - Submitted records;
   - Drafts or sync state when offline work is implemented.
3. `work-queue`
   - assigned projects as dense rows/cards;
   - each project has Open as the primary action;
   - no form selector at global level.
4. `recent-activity`
   - recent submissions or access warnings;
   - capped preview with link to the relevant route.
5. `empty/permission states`
   - no projects assigned;
   - signed in but contact/role not configured;
   - portal runtime/API unavailable.

Do not use a marketing-style hero on the authenticated dashboard.

### `/projects`

Project list route.

Purpose:

- browse project workspaces;
- filter/search projects once multi-project support is implemented.

Content anatomy:

1. route header: `Projects`;
2. toolbar: search/filter/sort when multiple projects exist;
3. project table or compact project cards;
4. empty and no-results states.

For the current single-project MVP, `/dashboard` may contain the project list
directly and `/projects` can be the same view.

### `/projects/:projectId`

Project workspace route.

Purpose:

- manage work inside one project context.

Content anatomy:

1. project command surface;
   - project title;
   - concise state line;
   - far-right `Collect` action with notepad icon.
2. Material tabs:
   - Summary;
   - Data;
   - Exports;
   - Power BI;
   - Settings only when project administration is implemented.
3. tab content.

Rules:

- form selector belongs here, inside project context, when multi-form support
  exists;
- Summary is informational and operational;
- Data is for submitted rows and review/detail drawers;
- Exports is for named export definitions and generated files;
- Power BI is for governed connection guidance and projection health;
- project Settings is not a global side-nav item unless it becomes a separate
  administration route.

### `/projects/:projectId/collect`

Form-runner route.

Purpose:

- collect or edit one submission with ODK Web Forms.

Content anatomy:

1. runner top action surface inside the workspace body;
   - back to project;
   - form name/version;
   - save/submit/runtime status.
2. ODK runtime boundary.
3. submit progress overlay when saving.

Rules:

- runner is not a side-nav destination;
- ODK controls remain inside `odk-runtime-host`;
- global shell remains visible unless a documented full-screen runner variant
  is introduced.

### `/reporting`

Cross-project reporting route.

Purpose:

- show reporting health and projection status across projects/forms;
- route bank workers to project data, exports, and Power BI readiness.

Content anatomy:

1. route header: `Reporting`;
2. reporting status strip:
   - projection freshness;
   - failed projections;
   - export definitions;
   - Power BI readiness.
3. reporting table:
   - Project;
   - Form;
   - Records;
   - Last updated;
   - Projection status;
   - Actions.
4. detail drawer for projection/export status.

Rules:

- global Reporting should not silently open a project's Data tab;
- project Data remains available inside `/projects/:projectId`;
- cross-project reporting can deep-link into project Data, Exports, or Power BI.

### `/access`

User & Access administration route.

Purpose:

- review users, roles, contacts, and assignments;
- later invite/suspend/assign users with confirmation and audit.

Content anatomy:

1. route header: `User & Access`;
2. access status strip;
3. user table with filters/search;
4. right drawer for user detail;
5. role reference/permission guidance.

Rules:

- visible only to administrators;
- write actions remain disabled until audit/permission model is packaged;
- high-impact writes require confirmation.

### `/configuration`

Future bottom-admin route.

Purpose:

- environment, project schema, XLSForm management, Power BI settings, and
  integration configuration.

Do not implement as a generic dumping ground. Add sub-routes only when there is
real functionality.

## Side Navigation Model

### 2026-08-13 navigation revision

The prototype has moved beyond a TACATDP-only field launcher. It is now being
positioned as a Sustainable Finance MEL platform where TACATDP remains the
first finance-project proof of concept.

Agreed navigation language:

- Rename `Projects / Loans` to `Finance Projects`.
- Add a future operational-work route label as `Operational Initiatives`, not
  `Operations`.

Reason:

- `Finance Projects` should stay tied to financed programmes, loans,
  guarantees, insurance-linked finance, facilities, beneficiaries, and financed
  technologies.
- `Operational Initiatives` covers broader non-finance MEL work without naming
  specific internal examples in the navigation.
- Operational initiatives should be modelled later through the configurable
  architecture, not as hard-coded TACATDP or finance-project routes.

Current implementation guidance:

- Update only the visible menu label from `Projects / Loans` to
  `Finance Projects` in the next UX slice.
- Do not implement a full `Operational Initiatives` module yet.
- If a placeholder is added, keep it non-promissory and visibly marked as
  planned/future.
- After beneficiary entity implementation, baseline import, and minimal KPI
  projection visualisation, revisit configurable architecture so finance
  projects and operational initiatives are both configured programme/activity
  types under the same MEL platform model.

Top operational group:

- Dashboard
- Projects
- Reporting

Bottom administration group:

- User & Access
- Configuration

Optional future items:

- Audit / Activity, if used for operational review;
- Help / Support, if supported by real content.

Do not put project tabs, forms, row actions, or one-off actions in the side
navigation.

## Right Content Area Rules

Every route inside `managed-workspace-body` must use this page anatomy:

1. `route-header`
   - route title;
   - short route-specific subtitle;
   - right-aligned route actions.
2. `route-status-strip`, only when useful;
3. primary route content;
4. contextual detail drawer or dialog;
5. route-level empty/loading/error states.

Action placement:

- global shell action: top bar only;
- route-wide action: route header right side;
- object action: object command surface;
- table row action: row action group;
- destructive/high-impact action: drawer/dialog confirmation.

Do not use oversized hero sections for authenticated work routes. Use compact
route headers and dense operational surfaces.

## Delivery Plan

Slice 1: route model refactor without changing backend behavior.

- Rename current `projects` view to `dashboard` or introduce a `dashboard`
  active view.
- Add `Dashboard` side-nav item and make it the authenticated landing view.
- Keep `Projects` as a route/list view, even if it currently mirrors the
  dashboard project list.
- Change global `Reporting` to a real reporting landing view with projection
  and export status summaries, not a direct jump to project Data tab.
- Keep project Summary/Data/Exports/Power BI tabs inside project workspace.
- Keep User & Access in bottom admin navigation.

Slice 2: content-area componentization.

- Extract shell-level components:
  - `ManagedShell`;
  - `ManagedSideNav`;
  - `ManagedTopBar`;
  - `ManagedFooter`.
- Extract route-level components:
  - `RouteHeader`;
  - `StatusStrip`;
  - `WorkspacePanel`;
  - `DataTableToolbar`;
  - `DetailDrawer`.
- Keep ODK runtime isolated.

Slice 3: route persistence.

- Introduce URL hash or history-state routing so refresh/back/forward preserve
  dashboard, project, tab, and selected record.

## Acceptance Criteria

- After login, the user sees a compact Dashboard, not a prototype hero.
- Side nav top group contains Dashboard, Projects, and Reporting.
- Side nav bottom group contains User & Access and Configuration.
- Global Reporting opens a reporting route, not a project tab side effect.
- Project tabs remain inside a project route.
- The right content area follows route-header, status-strip, primary-content,
  drawer/dialog, and state patterns.
- The shell footer remains outside route content.
- Validator or tests protect shell slot order and route anatomy where feasible.
