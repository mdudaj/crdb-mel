# User and Access Management UX Design System

Date: 2026-07-21

Status: Feature-specific UX contract for User & Access. For cross-feature
managed-service UI rules, Material-style CRUD patterns, drawers,
confirmations, and agent delivery gates, also follow
`managed-service-ux-governance.md` and
`managed-service-ux-agent-checklist.md`.

## Goal

Define the UX direction for TACATDP **User & Access** management before implementing the portal shell. The design must suit a managed banking environment where users perform operational work, where authorization mistakes carry real risk, and where CRDB staff should not need developer scripts or raw Dataverse table edits for routine access administration.

## Evidence Reviewed

- Current TACATDP design system: `docs/design-system.md`
- Current Monitoring Tool UX system: `docs/powerpages-odk-webforms/monitoring-tool-ux-design-system.md`
- Current portal shell: `powerpages/webforms-spa/src/views/AssignedFormsView.vue`
- Current shell tokens/CSS: `powerpages/webforms-spa/src/styles.css`
- TACATDP access-management artifacts:
  - `access-management-research.md`
  - `access-management-requirements.md`
  - `adr-0007-portal-user-access-management.md`
- Microsoft Power Pages styling guidance:
  - https://learn.microsoft.com/en-us/power-pages/getting-started/style-site
- Microsoft Power Pages page editor guidance:
  - https://learn.microsoft.com/en-us/power-pages/getting-started/customize-pages
- Fluent 2 design principles:
  - https://fluent2.microsoft.design/design-principles
- Fluent 2 accessibility guidance:
  - https://fluent2.microsoft.design/accessibility
- Fluent 2 layout guidance:
  - https://fluent2.microsoft.design/layout
- Fluent 2 content design guidance:
  - https://fluent2.microsoft.design/content-design
- Nielsen Norman Group data-table task framing, via public summary: data tables must support finding records, comparing data, viewing/editing one row, and taking actions on records.

## Design Position

TACATDP should feel like a quiet Microsoft 365 banking operations tool:

- familiar Microsoft interaction patterns;
- compact, readable, task-first screens;
- explicit permission and status language;
- restrained CRDB branding through logo, tokens, accents, and state colors;
- no marketing-style hero layouts for operational surfaces;
- no decorative visual noise;
- no prototype diagnostics in the normal user flow.

The current shell already provides the base: CRDB logo, `Monitoring Tool` product name, tokenized colors, compact cards, Material-style tabs, icon actions with tooltips, and accessible focus states. The User & Access slice should extend these patterns rather than introduce a second visual system.

## User Tasks

### Platform Administrator

Primary tasks:

- see all TACATDP users;
- determine whether a user can sign in;
- determine what the user can access;
- assign project/form access;
- change role;
- suspend or reactivate access;
- inspect recent access changes.

UX needs:

- dense table/list for scanning users;
- clear role and access summary;
- side panel for detail/change workflow;
- confirmation before high-impact changes;
- audit trail.

### Project Manager

Primary tasks:

- manage access for assigned projects;
- add data collectors/reviewers/reporting users to project forms;
- identify users missing contact/sign-in setup;
- suspend project access.

UX needs:

- project-scoped user list;
- role-limited actions;
- clear "You can manage this project only" scope messaging;
- no platform-wide settings.

### Reviewer / Supervisor

Primary tasks:

- understand who can submit and review records for assigned projects;
- view access state when investigating workflow issues.

UX needs:

- mostly read-only access visibility;
- concise access status; 
- no edit controls unless explicitly permitted.

### Data Collector / Bank Officer

Primary tasks:

- confirm they are signed in;
- see assigned project/form;
- collect or edit records.

UX needs:

- no User & Access navigation;
- permission-denied page if deep-linked;
- simple explanation when no project/form is assigned.

### Reporting Officer / Auditor

Primary tasks:

- confirm reporting access;
- see project/form data access scope;
- know whether export/Power BI access is permitted.

UX needs:

- read-only visibility into assigned scope;
- no user-management controls.

## Information Architecture

Add **User & Access** under the authenticated project platform shell. For the current single-project prototype, show it as a top-level admin area only to Platform Administrator. As multi-project support arrives, keep the same feature but allow project-scoped entry points.

Recommended structure:

1. **Users**
   - All visible users in scope.
   - Search by name/email.
   - Filter by role, status, project, form, contact state.
   - Row actions: View, Assign, Suspend/Reactivate.

2. **Invitations / Contact Status**
   - Users without contacts.
   - Users with contacts but no assignment.
   - Email mismatch warnings.
   - Manual invitation guidance first; automation only after CRDB approval.

3. **Roles**
   - Read-only role definitions in first slice.
   - Role matrix reference.
   - Avoid free-form role creation in MVP.

4. **Access Changes**
   - Audit-oriented list of recent changes.
   - Who changed what, for whom, when, and previous/new value.

## Screen Model

### User & Access Landing

Use an operational command layout, not a hero page.

Top area:

- title: `User & Access`;
- subtitle: concise scope such as `Manage TACATDP project and form access`;
- right-side primary action: `Add user` or `Assign access`, depending on first implemented workflow;
- small status facts:
  - active users;
  - users missing assignment;
  - users requiring contact/sign-in;
  - suspended users.

Do not use oversized page headings, decorative illustrations, or explanatory cards that repeat what the controls already do.

### Users Table

The table is the core surface.

Columns:

- Name;
- Email;
- Contact state;
- Role;
- Projects;
- Forms;
- Access status;
- Last changed;
- Actions.

Rules:

- Search field stays visible in the toolbar.
- Filters are visible, not hidden behind an obscure icon.
- Pagination is required; do not use infinite scroll.
- Row actions are icon-only with `aria-label` and tooltip, matching the existing Data tab exception.
- Keep destructive/high-impact actions out of the row itself; open detail side panel first.
- On mobile, switch to compact user cards with the same fields and actions.

### User Detail Side Panel

Use a side panel or modal-style drawer for detail and changes. This keeps the user list stable while administrators inspect or update one user.

Sections:

- Identity:
  - name;
  - exact contact email;
  - contact id if shown only in support/debug area;
  - sign-in/contact state.
- Role:
  - current TACATDP role;
  - role description;
  - allowed capabilities summary.
- Access:
  - projects;
  - forms/form versions;
  - status.
- Change history:
  - recent access changes.

Actions:

- Save changes;
- Suspend access;
- Reactivate access;
- Cancel.

### Add / Assign Access Flow

Use a short wizard or step sequence:

1. Find or enter user email.
2. Confirm contact/sign-in state.
3. Select role.
4. Select project and form access.
5. Review and confirm.

Every step should show exactly what will happen. If the contact does not exist, explain that the user may need to sign in once or be invited through the approved CRDB/Power Pages process.

### Permission Denied

Non-admin users who deep-link into User & Access should see:

- `You do not have access to User & Access`;
- short explanation;
- link back to assigned project/work queue.

Do not expose role names, contact ids, table names, or technical permission details in this screen.

## Component Additions

Reuse existing shell tokens and add these component recipes:

| Component | Purpose |
| --- | --- |
| `AdminSectionHeader` | Compact title, scope text, and right-side command slot |
| `AccessMetricStrip` | Small operational facts without decorative dashboard clutter |
| `UserAccessTable` | Dense desktop/tablet user-management table |
| `UserAccessCard` | Mobile fallback for one user |
| `ContactStateBadge` | Contact exists, not found, email mismatch, suspended |
| `RoleBadge` | Platform Administrator, Project Manager, Reviewer, Data Collector, Reporting Officer, Auditor |
| `PermissionSummary` | Plain-language list of what the selected role can do |
| `AccessDrawer` | One-user detail/change side panel |
| `ConfirmAccessChangeDialog` | Confirmation for suspend, role change, broad project access |
| `AccessAuditList` | Recent access changes |

## Visual Rules

- Keep cards at `8px` radius or less, matching the current `--mt-radius-md`.
- Use the existing CRDB green as the primary action and focus color.
- Use muted backgrounds and borders for operational grouping.
- Use yellow/accent only for caution or secondary brand emphasis, not as a dominant page color.
- Use red only for errors, revoked access, failed invitation, or blocked permission states.
- Do not introduce purple/blue gradients, decorative blobs, large illustrations, or marketing hero panels.
- Do not nest cards inside cards.
- Keep page sections unframed where a toolbar/table relationship is enough.
- Prefer dense tables and drawers for admin work over large repeated cards on desktop.

## Interaction Rules

- Role changes and suspensions require confirmation.
- Assignment writes must be idempotent.
- Save states must be visible: saving, saved, failed.
- Failed writes must say what the admin can do next.
- Reversible actions should use `Suspend` rather than `Delete`.
- Avoid bulk actions in the first slice unless the audit and undo behavior is ready.
- Keep primary actions text+icon; use icon-only only for repeated row actions.

## Content Rules

- Use bank-worker terms:
  - `User & Access`;
  - `Project access`;
  - `Form access`;
  - `Suspend access`;
  - `Reactivate access`;
  - `Contact not found`;
  - `Email mismatch`.
- Avoid technical first-line labels such as `mp_formassignment`, `contactid`, `web role`, or `table permission`.
- Technical details may appear in a support/debug detail area for Platform Administrator.
- Use concise, specific labels. Do not use `Click here`, directional text, or vague commands.

## Accessibility Rules

- Every icon-only action must have an accessible name and tooltip.
- Focus order must follow toolbar, table/list, row action, drawer.
- Drawer open should move focus into the drawer and return focus to the triggering row action when closed.
- Status changes need visible text and `aria-live` where appropriate.
- Do not communicate contact/role status by color alone.
- Tables need semantic table markup or an accessible grid pattern.
- Mobile cards must preserve all critical labels; do not rely only on column position.

## Current UI Enhancements Required

Before the User & Access shell is built:

- Reuse existing `monitoring-shell`, `top-action-bar`, `status-banner`, `icon-action--compact`, and tooltip patterns.
- Add admin shell tokens only if the current token set cannot express a state.
- Add role/contact badges as reusable classes/components.
- Add table toolbar patterns that can later also improve Data/Export UX.
- Keep admin views within the same app shell as Summary/Data/Exports/Power BI.
- Do not add a separate branded admin microsite.

## Acceptance Criteria

- User & Access uses the existing Monitoring Tool shell and CRDB token system.
- The first screen is an operational admin surface, not a marketing/landing page.
- Platform Administrator can scan users in a dense table on desktop/tablet.
- Mobile users get readable user cards, not a horizontally broken table.
- Search, filters, pagination, empty, loading, error, and permission-denied states are specified before implementation.
- Role definitions are visible in plain language.
- Assignment/suspension changes happen through a detail drawer or confirmation flow, not accidental row clicks.
- Email/contact mismatch is visible and understandable to non-developer admins.
- The UI supports auditability: who, what, when, previous/new state.
- No portal UI exposes secrets, bearer tokens, app credentials, or raw tenant configuration.

## Implementation Note

Do not implement the shell until the design is reviewed against the current running portal after the CRDB cache purge/restart. The first code slice should be read-only User & Access with real contacts and assignments, because that can validate layout, role visibility, contact matching, and permission boundaries before writes are added.
