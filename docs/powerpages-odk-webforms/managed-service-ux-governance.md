# TACATDP Managed Service UX Governance

Date: 2026-07-21

## Purpose

TACATDP is no longer only a form deployment. It is a Microsoft-managed banking
operations system for project monitoring, data collection, access management,
reporting, and future multi-project administration. Every new UI slice must
therefore follow one governed UX system rather than page-local design decisions.

This document is the agent-facing UX contract for future TACATDP portal work.
Agents must inspect it before changing the Power Pages SPA, portal shell,
admin surfaces, or CRUD workflows.

## Research Inputs

- Microsoft Power Pages 2026 release wave 1 overview:
  `https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-pages/`
- Microsoft Power Platform release plans for Power Pages governance,
  authentication controls, Power BI embed token v2, security agent,
  server-side logic, and authorization unification:
  `https://releaseplans.microsoft.com/en-us/?app=Power+Pages`
- Material Design data-table guidance:
  `https://m2.material.io/design/components/data-tables.html`
- Material Design navigation drawer guidance:
  `https://m2.material.io/components/navigation-drawer`
- Material Design dialog guidance:
  `https://m2.material.io/develop/web/components/dialogs`
- Fluent 2 drawer guidance for confirmation/error handling in drawers:
  `https://fluent2.microsoft.design/components/web/react/core/drawer/usage`
- Baymard accidental tap/destructive action recovery research:
  `https://baymard.com/blog/handling-accidental-taps-on-touch-devices`
- Existing TACATDP UX artifacts:
  - `monitoring-tool-ux-design-system.md`
  - `access-management-ux-design-system.md`
  - `access-management-requirements.md`
  - `adr-0007-portal-user-access-management.md`
- Local shell precedents:
  - LIMS `docs/UX_DESIGN_SYSTEM.md` separates routine drawer items from a
    bottom `Configuration` section.
  - LIMS `templates/viewflow/includes/lims_site_menu.html` groups menu items
    into `primary` and `configuration`.
  - STEMGEN `static/dissertation/ui/authenticated.css` uses a collapsible
    sidebar where the lower nav section is pushed to the bottom with
    `margin-top: auto`.

## Product UX Position

TACATDP is the first supported programme/project for CRDB Sustainable Finance
Unit's Integrated Digital MEL platform. The current release remains scoped to
TACATDP field monitoring and impact tracking, but the platform foundation must
support future sustainable-finance MEL modules such as beneficiaries, financed
activities, climate rationale, indicators, ESS/risk, geo insights, and reporting
templates.

The product must feel like a quiet, high-trust Microsoft 365 banking operations
tool:

- task-first, not marketing-first;
- compact, readable, and operational;
- CRDB-branded through tokens and restraint, not decorative backgrounds;
- governed by roles, auditability, and confirmation for risky changes;
- optimized for bank workers who need clarity, speed, and confidence;
- compatible with future CRDB transfer and Power Pages governance features.

Do not design TACATDP like a research survey launcher, prototype demo,
marketing site, or consumer dashboard.

Do not mirror TACATDP workbook sheets directly as navigation. Treat source
spreadsheets and M&E plans as evidence for domain concepts, indicators,
reporting outputs, and validation rules; then translate them into coherent
banking workflows.

## Information Architecture

### Global Shell

Use a Microsoft/Material-style app shell:

- full-height left navigation drawer pinned from top to bottom;
- right workspace containing the sticky top app bar, page header/content, and
  footer;
- one top-left hamburger switcher in the sticky top bar, used to collapse the
  desktop rail or open the mobile drawer;
- CRDB identity and product identity must live inside this shell, not in a
  separate Power Pages website header;
- project-first main content;
- admin-only entries hidden by Power Pages role and reinforced by route checks.

For the Monitoring Tool SPA page, keep the Power Pages website header/footer
runtime enabled when required for portal JavaScript services such as
`shell.getTokenDeferred`, but visually suppress the default portal
header/footer on the SPA page. Do not allow the default portal chrome to appear
around the SPA, because it creates duplicate navigation and footer content. If
a future slice wants a different shell pattern, document the alternative as an
explicit UX decision before implementation.

Use a navigation drawer only when TACATDP has five or more durable top-level
destinations or two or more hierarchy levels that users switch between
frequently. Do not combine a primary drawer with another competing primary
navigation pattern.

### Shell Slot Contract

Every TACATDP authenticated portal screen must use these shell slots in this
order:

1. `managed-side-nav`
   - Full-height left rail or mobile drawer.
   - Contains brand lockup, operational navigation, and bottom administration
     navigation only.
   - Does not contain page actions, project tabs, page footers, form controls,
     profile actions, or row actions.
2. `managed-app-content`
   - Right workspace pushed by the side nav.
   - Owns the top bar, page body, and shell footer.
3. `managed-top-bar`
   - Sticky top bar at the top of the right workspace.
   - Far-left item is the single hamburger shell switcher.
   - Center/primary title area shows product context and current page title.
   - Future global user/profile actions may be added at the far right only when
     implemented as a governed user menu.
   - Does not contain project form selectors, project tabs, CRUD row actions,
     or page-specific bulk actions.
4. `managed-workspace-body`
   - Contains the active route/page content.
   - Page-specific headers such as project title, Collect action, filters,
     Material tabs, tables, cards, drawers, and forms live here.
   - Project tabs remain inside the project page content, below the project
     command surface.
5. `managed-app-footer`
   - Single shell footer at the bottom of the right workspace.
   - Contains stable organization/legal/environment text only.
   - Does not live inside a page hero, project command card, data table,
     tab panel, drawer, or form runtime.

Do not add page-local header/footer components that compete with these slots.
If a new surface needs a different arrangement, create a documented shell
variant before implementation.

Recommended future top-level destinations:

- Dashboard
- Programmes
- Projects
- Beneficiaries
- Field Monitoring
- Indicators
- Climate Risk
- Geo Insights
- Reporting
- Audit / Activity
- Help / Support
- Configuration
- User & Access

For the current stage, use **Dashboard** as the default authenticated landing
surface. The Dashboard summarizes assigned projects, forms, submitted records,
draft/sync state, and recent activity. Keep **Projects** as a project list or
workspace entry route. Show **User & Access** only to platform administrators.
Follow `operational-ux-research-and-plan-20260730.md` when changing the
Dashboard or route organization. The Dashboard is an operational command center,
not a status landing page: attention, current work, workload/sync state,
progress/trend, and recent activity must take priority over generic entity
counts. Role-specific dashboard sections must reflect real authorization scope,
not navigation-only hiding.

### Side Navigation Placement

Follow the LIMS/STEMGEN shell precedent: routine operational destinations live
at the top of the side navigation, while administrative destinations live in a
separate bottom group.

Top group:

- Dashboard
- Projects
- Reporting, once it becomes a cross-project destination
- Audit / Activity, if it is used for operational review rather than platform
  administration
- Help / Support, if present

Bottom group:

- User & Access
- Configuration
- Project settings
- Form/XLSForm management
- Environment / integration settings
- Security / governance tools

Rules:

- Bottom items are shown only when the signed-in user's role permits them.
- Label the bottom group `Administration` or `Configuration`; use one label,
  not both, unless the groups become meaningfully distinct.
- Use a visual divider before the bottom group.
- Keep the bottom group pinned near the bottom of the drawer on desktop.
- In collapsed desktop rail mode, bottom items remain at the bottom and expose
  tooltips.
- On mobile modal drawer, preserve the same order: operational items first,
  administrative items after a divider.
- The side-nav collapse/open switcher belongs in the right workspace top bar,
  not inside the navigation rail.
- Use the three-bars menu icon for the shell switcher. Do not add a second
  close/collapse icon unless an explicitly documented shell variant requires it.
- Do not place `User & Access`, `Configuration`, or security-sensitive settings
  beside routine project work items in the top group.
- Profile, sign out, and password/account self-service belong in the user menu,
  not the side navigation.
- Project tabs remain inside the project workspace; do not duplicate Summary,
  Data, Exports, or Power BI in the side navigation.

### Project Workspace

After opening a project, the page structure is fixed:

1. Compact project command surface:
   - project title;
   - key status line;
   - far-right `Collect` action with notepad icon.
2. Material-style tabs with bottom active indicator:
   - Summary
   - Data
   - Exports
   - Power BI
   - Settings, only when project administration is implemented.
3. Tab content as dense operational surfaces, not repeated explanatory cards.

The form selector belongs inside the project context, never in the global top
shell. For single-form TACATDP, keep the form implicit; for multi-form support,
place form scope controls inside project tabs.

### Route Content Area

Use `managed-portal-route-content-model.md` as the route/content-area contract.
Every route inside `managed-workspace-body` must use compact operational route
anatomy:

1. route header;
2. optional status strip;
3. primary route content;
4. contextual drawer/dialog;
5. route-level empty/loading/error states.

Authenticated routes must not use oversized marketing or prototype heroes. The
global `Reporting` destination must become a real reporting route, not a
shortcut that silently opens a selected project's Data tab.

## Material Component Rules

### Tabs

- Use Material-style tabs for peer sections in one context.
- Active state uses a bottom indicator.
- Do not use pill buttons for Summary/Data/Exports/Power BI.
- Tabs must preserve keyboard focus, `aria-selected`, and readable labels.
- Tabs change views; they must not submit data or trigger writes.

### Data Tables

Use tables for desktop/tablet CRUD lists with three or more related fields per
record. Tables must support:

- finding records through search and visible filters;
- comparing records through stable columns;
- opening one record for view/edit in a drawer;
- taking row-level actions through a compact action group;
- pagination, not infinite scroll.

Required table anatomy:

- toolbar above table;
- visible search field at the end of the toolbar;
- visible filters before search;
- semantic table headers;
- sortable columns only where sorting is implemented;
- one-line icon-only row actions with tooltip and `aria-label`;
- pagination below table;
- empty, loading, error, and no-results states.

Do not put destructive or high-impact actions directly in row buttons. Row
actions may open detail, edit, or a contextual menu; high-impact changes must
continue in a drawer and confirmation dialog.

On mobile, replace dense tables with compact record cards that preserve the
same critical fields and action names.

### Drawers / Side Sheets

Use a right-side drawer for inspecting or editing one record while preserving
the user's table/list context. Drawers are preferred for:

- user detail;
- role/access assignment;
- submission detail;
- export setting detail;
- Power BI connection guidance;
- project/form configuration detail.

Drawer rules:

- right side on desktop/tablet;
- full-screen sheet on phone widths;
- header contains title, entity identity, and close action;
- body is sectioned into readable groups;
- footer contains sticky actions when editing;
- show inline errors near the failed section and a summary message for
  multiple errors;
- move focus into the drawer on open and return focus to the triggering row
  action on close;
- do not launch frequent confirmation dialogs from overlay drawers unless the
  action is high impact.

Drawers do not replace confirmation. They collect and review changes; dialogs
confirm high-impact commits.

### Dialogs and Confirmations

Use confirmation dialogs for actions that are high severity, hard to reverse,
security-sensitive, or likely to affect another user.

Required confirmations:

- suspend/reactivate user access;
- change platform or project role;
- grant access to all project forms;
- revoke project/form access;
- publish a new form version;
- replace an active XLSForm;
- delete or retire export settings;
- reconnect or change Power BI integration;
- submit a record when validation result is uncertain;
- discard unsaved edits.

Confirmation dialog rules:

- title names the consequence, for example `Suspend access for John Mduda?`;
- body states exactly what will change and what will not change;
- include affected project/form/user names;
- destructive confirmation action is a specific verb: `Suspend access`,
  `Revoke access`, `Retire export`;
- dismissive action is `Cancel`;
- confirmation action is disabled until mandatory review fields are satisfied;
- for severe irreversible actions, require typed confirmation using a stable
  identifier such as user email, project name, or form name;
- do not use vague buttons such as `OK`, `Done`, or `Close` for commits.

For reversible, frequent, low-risk actions, prefer undo/snackbar or soft state
over repeated modal confirmations. For high-severity banking/access changes,
prefer explicit confirmation even when an audit trail exists.

### Forms and CRUD Flows

CRUD screens must use a two-phase pattern:

1. Edit in a drawer or focused form surface.
2. Review/confirm before committing high-impact changes.

Every write workflow must show:

- loaded entity identity;
- changed fields;
- before/after values for role, status, project, form, or export scope;
- validation errors before submit;
- saving state;
- success state;
- failure state with next action;
- audit expectation: who, what, when, previous/new value.

Avoid ambiguous `Apply` buttons. Use clear verbs:

- `Save changes`
- `Assign access`
- `Suspend access`
- `Reactivate access`
- `Publish version`
- `Create export`
- `Update connection`

## Role-Based UX

### Platform Administrator

Can see global User & Access, project configuration, reporting setup, and audit
views. Use dense tables, drawers, confirmation dialogs, and audit history.

### Project Manager

Can manage users and forms only within assigned projects. Show scope boundaries
in plain language. Hide platform-wide controls.

### Reviewer / Supervisor

Can inspect records and review states. Editing or access writes are hidden
unless explicitly granted.

### Data Collector / Bank Officer

Lands on assigned projects/forms. No User & Access navigation. Permission
denied pages should use plain language and route back to assigned work.

### Reporting Officer / Auditor

Can inspect data/export/Power BI access according to project scope. Avoid
collection/admin controls unless explicitly assigned.

## User & Access UX Rules

User & Access is a critical security workflow, so apply the strictest UX rules:

- admin-only navigation and route access;
- searchable, filterable user table;
- detail/change drawer for one user;
- no accidental row-level suspend/revoke;
- confirmations for role/scope/status changes;
- visible contact state and email mismatch warnings;
- role definitions in plain language;
- audit history visible from detail;
- no raw `contactid`, table names, or web-role relationship labels in first-line
  UX;
- technical IDs only in a support/debug section.

## Reporting / Exports / Power BI UX Rules

The Power BI tab must present governed connection guidance, not manual files as
the primary integration.

- Use Dataverse reporting projection tables as the preferred source.
- Show data freshness and projection status.
- Export settings are project/form scoped.
- Root CSV can exist for first slice; repeat groups require XLSX or separate
  related datasets.
- Changing export schema or Power BI connection is high impact and needs
  review/confirm.
- Use Power BI embed/support features only when configured by administrators and
  compatible with CRDB governance.

## State Provenance And Freshness

- A status label must describe what was actually checked or refreshed.
- Browser connectivity is `Device connected` or `Device offline`; it is not a
  server-health or synchronization guarantee.
- Device-local records must say `on this device`.
- Assignment, submission, projection, and reporting refresh times are separate
  facts and must not share a generic `Last refreshed` label.
- Positive attention states must be bounded to the checks that ran; do not use
  `Clear` as a whole-platform health claim.
- Lazy data surfaces must describe the user's next action, such as `Open Data
  to view submitted records`, without exposing implementation wording.
- Dashboard submitted-record surfaces must not show a record count unless the
  records were actually queried for that session. Before query, present the
  surface as a `Data access` entry point with the user's visibility scope, for
  example `Scope: My records` or `Scope: All project records`.

## Microsoft Power Pages 2026 Implications

Power Pages 2026 direction reinforces TACATDP's managed-service UX:

- governance and security should be first-class user/admin experiences;
- security scan, security agents, and admin security controls should inform
  support/admin views, not be hidden from operational owners;
- non-production visibility governance means site visibility must be treated as
  a deployment concern;
- external authentication-provider controls strengthen the decision to rely on
  CRDB Microsoft identity rather than custom login;
- Power BI embed token v2 and future authorization unification may simplify
  reporting and role mapping, but current UI must still work with web roles,
  contacts, table permissions, and Dataverse roles.

Agents must check current Microsoft release status before implementing features
that depend on newly released Power Pages capabilities.

## Visual System Rules

- Use CRDB logo and green/yellow tokens with restraint.
- Avoid purple/blue gradients, decorative blobs, large hero images, and
  marketing layouts.
- Use `8px` or smaller card radius unless the existing token says otherwise.
- Use compact spacing suitable for operational scanning.
- Do not nest cards inside cards.
- Prefer tables, drawers, tabs, and status strips over oversized dashboards.
- State must be communicated with text and icons, not color alone.
- Use `@lucide/vue` icons for shell controls.
- Primary actions are text+icon.
- Repeated table row actions may be icon-only only when they have tooltip and
  accessible label.

## Accessibility Rules

- Every interactive control must have a visible or accessible name.
- Icon-only controls require tooltip and `aria-label`.
- Dialogs and drawers trap/manage focus appropriately.
- Close returns focus to the launching control.
- Status changes use visible text and `aria-live` where appropriate.
- Tables use semantic table markup or an accessible grid pattern.
- Mobile card fallback preserves labels that table columns normally provide.
- Keyboard users must be able to open drawer, change fields, cancel, confirm,
  and return to the list.

## Agent Delivery Rules

Before implementing a TACATDP frontend slice, agents must document:

1. user role and task;
2. entity scope: global, project, form, submission, export, or user;
3. data visibility: all records, project-scoped, form-scoped, or current user;
4. write impact: none, low, medium, high, irreversible;
5. required component pattern: table, drawer, dialog, tabs, full-screen form;
6. loading, empty, error, success, and permission-denied states;
7. confirmation and audit requirements;
8. mobile fallback;
9. verification commands and browser checks.

Agents must not implement page-local UX that violates this document without
first updating this governance artifact and explaining the reason.

## Implementation Checks

Minimum checks for future UI slices:

- `npm run build`
- `python3 scripts/validate-webforms-spa-foundation.py`
- affected component/DOM contract tests where available;
- desktop and phone visual inspection;
- hosted Power Pages smoke check after upload;
- cache-busting or cache purge/restart after deployed CSS/JS changes.

## Open Decisions

- Whether to adopt a permanent left navigation drawer once multi-project,
  reporting, configuration, audit, and access management are all active.
- Whether to introduce a dedicated `Settings` project tab or reserve settings
  for platform administrators only.
- Whether future Power Pages authorization unification should move TACATDP role
  UX from web-role/contact language to Dataverse security-role/system-user
  language after CRDB validates the Microsoft feature in their tenant.
