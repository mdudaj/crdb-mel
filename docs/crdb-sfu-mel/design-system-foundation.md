# CRDB SFU MEL Design System Foundation

Date: 2026-08-02

## Purpose

Define the shell, design tokens, reusable components, and UX rules for the CRDB Sustainable Finance Unit Integrated Digital MEL Tool. This artifact guides the immediate TACATDP shell alignment and future MEL platform work.

The default product theme is a light banking operations interface. Dark dashboard references are used only for composition lessons: elevated grouped cards, dense data blocks, operational hierarchy, and a right-side actions/attention rail.

## Evidence And Design Inputs

- CRDB public website and sustainability positioning: CRDB presents itself as a bank with strong digital, ESG, and sustainable finance commitments.
- CRDB Sustainable Finance Unit context: TACATDP is the first programme/project inside a future Integrated Digital MEL platform.
- Material Design principles: clear navigation hierarchy, predictable layout, component states, data tables, tabs, dialogs, drawers, and responsive behavior.
- Existing TACATDP UX governance: shell-owned route identity, compact route content, admin actions at the bottom of side navigation, and project tabs inside the project workspace.
- MEL platform patterns from ActivityInfo, DevResults, DHIS2, and evaluation practice: data collection, indicator tracking, evidence, maps, dashboards, reporting, validation, permissions, and learning loops.
- Mockups: `docs/crdb-sfu-mel/mockups/light-direction/`.

## Product Position

The MEL Tool is a CRDB banking operations platform for monitoring, evaluation, reporting, learning, compliance, and evidence management across sustainable finance programmes.

The first supported project is TACATDP. TACATDP should appear as a project/programme context, not as the permanent product identity.

## Shell Layout

Use one governed shell for authenticated users:

1. **Left navigation rail**
   - Full-height deep navy rail.
   - Top: CRDB Bank logo/lockup and `MEL Tool` system name.
   - Middle: segmented navigation groups.
   - Bottom: organization/branch selector, e.g. `Sustainable Finance Unit` and `Head Office`, with dropdown affordance.
2. **Top app bar**
   - Sticky, light surface.
   - Left: one hamburger/collapse action.
   - Title/subtitle: current route only.
   - Right: programme selector, period selector, sync status, user menu.
   - Do not place page-local CRUD actions here unless they are route-level global actions.
3. **Main workspace**
   - Light background.
   - Uses a 12-column responsive layout.
   - Cards are grouped by workflow: attention, active work, metrics, lists, reporting, evidence, and learning.
4. **Right operational rail**
   - Desktop: persistent right column for Quick Actions, Attention, status checks, or future MEL Assistant.
   - Tablet/mobile: collapses below main content or into a drawer.
5. **Footer**
   - Bottom of shell workspace.
   - Stable organization/legal/environment text only.

## Navigation Groups

### Current Work

Visible in the immediate TACATDP release:

- Dashboard
- Projects
- Reporting

### MEL Platform

Future-capable modules, exposed only when implemented or deliberately shown as current-scope placeholders:

- Programmes
- Beneficiaries
- Field Data
- Indicators
- Evidence
- Learning

### Administration

Role-gated administrator routes:

- System Activity
- User & Access
- Configuration

## Design Tokens

### Color

- Page background: `#F4F8F2`
- Soft page background: `#EEF5EC`
- Surface: `#FFFFFF`
- Muted surface: `#F8FBF7`
- Border: `#D9E6D4`
- Strong border: `#C0D8B9`
- Text: `#102018`
- Muted text: `#5C6B60`
- Side nav navy: `#082B49`
- Side nav highlight: `#1E63B6`
- CRDB green/action: `#43B02A`
- Green text/success: `#236B22`
- Amber warning: `#F59E0B`
- Yellow active marker: `#F2C84B`
- Blue information: `#2F6FED`
- Teal evidence/geo: `#19A7A6`
- Red risk/failure: `#C62828`

### Typography

- Font stack: `Segoe UI`, `Roboto`, `Arial`, sans-serif.
- Route title: 24-28px, 700-800 weight.
- Section title: 20-24px, 700-800 weight.
- Metric value: 26-32px, 700-800 weight.
- Body text: 14-16px.
- Labels/eyebrows: 12-13px, uppercase only where useful.
- Do not scale font size by viewport width.

### Spacing

- Base spacing unit: 4px.
- Component internal padding: 16-24px.
- Card grid gap: 20-28px.
- Dense row gap: 8-12px.
- Shell top bar height: 80-88px.
- Side nav expanded width: 224-240px.

### Radius And Elevation

- Small radius: 4px.
- Standard radius: 8px.
- Large workflow cards: 10px maximum unless a component requires otherwise.
- Use restrained elevation for surfaces; avoid floating decorative cards nested inside other cards.

## Reusable Components

### App Shell

Slots:

- `SideNav`
- `TopAppBar`
- `WorkspaceBody`
- `RightOperationalRail`
- `ShellFooter`

### SideNav

Anatomy:

- brand lockup
- grouped nav sections
- active marker
- bottom org/branch selector

Rules:

- Admin routes stay in the bottom group.
- Current project tabs never appear in global navigation.
- Collapsed rail must provide tooltips.

### TopAppBar

Anatomy:

- collapse/menu button
- route title/subtitle
- programme selector
- period selector
- sync status
- user menu

Rules:

- One menu switcher only.
- No duplicate page banners repeating the same route title.

### Operational Card

Anatomy:

- optional icon/status chip
- label
- value/title
- helper text
- optional action

Rules:

- Sibling cards share height, padding, icon treatment, and action alignment.
- Metrics must state scope and freshness when values combine local/server/derived data.

### Right Operational Rail

Sections:

- Quick Actions
- Attention
- Reporting status or MEL Assistant placeholder

Rules:

- Quick actions must be real commands or clearly labelled roadmap items.
- AI/MEL Assistant remains future capability until backed by approved architecture.

### Data Table / Line List

Use for submitted records, beneficiaries, evidence, indicators, and audit rows.

Rules:

- Paginated by default.
- Show data scope: my records, project records, programme records, or portfolio records.
- Include loading, empty, error, partial-load, and permission-denied states.

### Tabs

Use Material-style bottom active indicator.

Rules:

- Tabs belong inside object workspaces such as Project, Programme, or User details.
- Do not duplicate tabs in side navigation.

### Forms And Wizards

Rules:

- One field per row by default.
- Visible labels above fields.
- Helper/error text below fields.
- Confirmation step for sensitive CRUD, assignment, invitation, export, and configuration actions.

## State And Feedback Rules

Every user action must produce visible feedback:

- loading
- success
- validation failure
- permission failure
- queued/pending server processing
- retry/recover action when available

Do not redirect silently after a create/update/delete operation.

## MEL-Specific Product Rules

- Field data is not the whole MEL system; it feeds evidence, indicators, dashboards, reports, and learning.
- Indicators must link to definitions, targets, disaggregation, data source, and verification status.
- Evidence must support GPS/photo/document/timestamp/submitter metadata and audit trail.
- Dashboards should expose attention, progress, data quality, compliance risk, and reporting status before decorative charts.

Do not use implementation delivery wording such as `readiness` in normal user-facing UI labels. Use status, checks, setup, health, configuration, or next action instead. Keep readiness gates in documentation, validators, handoffs, or explicit administrator diagnostics only.
- Learning must support lessons learned, case studies, adaptive management actions, and feedback loops.
- Reports must distinguish operational dashboards from formal donor/government/GCF reporting outputs.

## Responsive Behavior

Desktop:

- Expanded left nav.
- Main workspace plus right operational rail.
- 12-column card grid.

Tablet:

- Collapsible nav.
- Right rail moves below main cards or becomes a drawer.
- Two-column card grid.

Mobile:

- Drawer navigation.
- One-column content.
- Right rail becomes stacked panels below primary work.
- Touch targets at least 44px.

## Accessibility Rules

- All controls need visible labels or accessible labels.
- Focus state must be visible.
- Color cannot be the only status indicator.
- Cards and lists must preserve semantic order.
- Destructive or sensitive actions require confirmation.
- Tooltips supplement but do not replace accessible names.

## Immediate TACATDP Implementation Reference

Use `mel-light-01-tacatdp-command-centre` as the immediate shell reference.

Expose only the scoped working routes unless future modules are deliberately shown as roadmap:

- Dashboard
- Projects
- Reporting
- User & Access
- System Activity

Keep future MEL modules out of the default route set until the client approves scope expansion, or show them as explicit roadmap previews for administrators only.

## Future Platform Reference

Use `mel-light-02-sfu-portfolio-overview` as the future SFU portfolio shell direction.

Future routes should be introduced only when they have data contracts, permissions, empty/loading/error states, and acceptance criteria.
