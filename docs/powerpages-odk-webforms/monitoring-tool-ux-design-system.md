# Monitoring Tool UX Design System

Date: 2026-07-11

Status: Feature-specific UX contract. For cross-feature managed-service UI
rules, Material-style CRUD patterns, drawers, confirmations, and future
multi-project governance, also follow
`managed-service-ux-governance.md` and
`managed-service-ux-agent-checklist.md`.

## Product Name

Use **Monitoring Tool** in the user-facing shell. Avoid "Collector" because the product scope includes assigned forms, drafts, submissions, history, review status, and eventually monitoring operations.

## Design Goal

Deliver a CRDB-branded, mobile-first field monitoring experience that feels like a focused operational tool, not a prototype diagnostics page. The ODK Web Forms runtime remains the form engine; the host shell owns authentication state, navigation, project/form selection, loading, status, history, and submission feedback.

## Evidence Used

- Microsoft Power Pages authentication and `/_api` behavior govern login, contact/session state, table permissions, and CSRF-protected Dataverse access.
- ODK Collect organizes field work around projects/forms, drafts, ready-to-send/submitted states, form navigation, validation, and editing rules.
- ODK Web Forms should own the actual XForm rendering and validation surface.
- LIMS and STEMGEN show the reusable project pattern: semantic tokens, shared component recipes, explicit shell boundaries, task-focused pages, labeled back actions, and feature CSS only for narrow exceptions.
- TACATDP brand assets are available at `assets/images/CRDB_Bank_PLC.png` and `assets/images/CRDB_Bank_PLC.svg`.

## UX Principles

- Use Power Pages / Microsoft Entra authentication. Do not build custom login.
- If the user is unauthenticated, route to the Power Pages sign-in flow and return to the requested page after login.
- Keep one primary task per page state: choose work, fill form, review history, or inspect a submission.
- Show the signed-in user in the shell, but do not make the identity line the page headline.
- Use CRDB identity through tokens, logo placement, and restrained accent colors, not decorative backgrounds.
- Keep ODK runtime styling isolated. Do not target generic `button`, `input`, `label`, `select`, or `textarea` inside the ODK host.
- Move developer diagnostics behind a collapsible debug panel or development flag before sharing.
- Preserve clear status states: loading, empty, ready, saving draft, submitting, submitted, failed, offline/pending.

## Screen Model

### Unauthenticated

- Present a compact CRDB-branded sign-in panel only if automatic redirect is not possible.
- Primary action: "Sign in with Microsoft".
- Login must use the configured Power Pages / Microsoft Entra provider.

### Home / Work Queue

Show the user what they can do now:

- CRDB logo and product name: **Monitoring Tool**.
- Signed-in user name/email in the top shell area.
- Project list or current project summary.
- Assigned forms count.
- Local drafts count.
- Recent submitted count.
- Offline/sync status once offline sync is introduced.

For the current single-project MVP, use the same project-first pattern that will scale later: Home shows project cards only. Opening a project shows the project CRUD workspace.

### Project Detail

- Top action bar with icon+text Back, project name, device connectivity, and a
  refresh action whose label or accessible name states what data it refreshes.
- Sections:
- Project command card with only the project title and a far-right **Collect** action.
- Material-style tabs below the project command card: Summary, Data, Exports, and Power BI.
- The **Collect** action uses a notepad icon, sits at the far right like the project Open action, and opens the data collection form.
- Do not put a form selector in the top shell. For the current single-form prototype, keep the form implicit in the project dashboard; future multi-form support can add form scope inside the project without changing global navigation.
- Use Material-style tabs with a bottom active indicator, not pill buttons, for the project dashboard sections.
- Saved records are shared across authenticated users for this proof. Do not filter saved submitted records by the current user's email unless a future role/permission requirement explicitly changes the scope.
- Place search at the end of the Data toolbar. Search must filter as the user types across loaded submitted records.
- Show the Data tab as a dense operational table with pagination. Rows must expose record identity, owner when known, version, review state, updated time, and a compact icon-only action group. Row actions remain on one line and expose their names through accessible hover/focus tooltips and `aria-label`.
- Present reporting dates as one Updated date range control with a calendar popover and typed-input fallback, not as visually unrelated From and To fields.
- The dashboard should feel like a bank operations tool, not a research/survey launcher or diagnostics page.
- Cards and action areas use a restrained CRDB left accent strip. State text must be visible; do not communicate state by color alone.
- State text must name its provenance when sources have different freshness:
  use `Device connected`, `Assignments refreshed`, and `Drafts on this device`
  rather than implying server synchronization or whole-platform health.
- Use **Collect** for new submissions. Avoid "Start" in the project/data list shell.
- Use **Edit** for submitted saved records. Edit must load the latest submitted instance into ODK Web Forms edit mode and save a new submission version for the same ODK instance id.
- Draft cards must represent restorable ODK instance state. Do not display runtime-load markers as drafts because opening them creates an empty form and teaches the wrong workflow.

### Data, Exports, and Power BI

- The Data area is project-scoped for the current prototype and is used for inspecting submitted records, not for selecting which form to collect.
- Exports are project/form dataset configurations. Root CSV exports are acceptable for the first slice, but XLSX is required when repeat groups need to be included.
- Power BI guidance should point users toward governed Dataverse reporting projection tables. Do not present developer-generated CSV files as the primary Power BI integration path.
- Keep Summary, Data, Exports, and Power BI as peer Material tabs so bank staff can scan operational functions quickly.

### Form Loading

Use a reusable centered loading panel:

- CRDB logo.
- "Loading form".
- Form name and version when known.
- Loading dots or progress indicator.
- Optional secondary line: "Preparing the secure form session".

This same loading panel should be reused for page-level loading, assignment loading, form version loading, and submit transitions.

### Form Runner

- Top action bar with Back to project, form name, version, save/draft status, and submit state.
- ODK Web Forms gets the full main form area below the action bar.
- Host shell must provide spacing before and after the ODK runtime.
- Submit shows a blocking CRDB-branded progress panel with the CRDB logo, "Submitting record", "Saving to Dataverse", and animated dots. Do not leave users wondering whether a submit click was accepted.
- Successful submit returns to the project data-card list on the Saved tab and displays the submit result as a status banner. Failed submit stays on the form runner and keeps the error visible there.
- Attachment binary warnings should be visible but not framed as a total failure when submission and metadata persistence succeeded.

### History

- Show only the signed-in user's submissions unless an admin role is explicitly added later.
- List form name, version, submission time, lifecycle, review state, attachment count, and sync/file warning state.
- Submission detail can show canonical instance id and payload metadata for support, but not as the default first thing a field user sees.

## Component Inventory

- `AppShell`: CRDB brand header, user area, page container, status slot.
- `TopActionBar`: labeled Back, page title/subtitle, right-side actions.
- `LoadingPanel`: centered CRDB logo, loading message, animated dots/progress.
- `ProjectCard`: project name, active forms, drafts, recent submissions.
- `DataCard`: saved submission or local draft identity, status, updated time, Open action, and CRDB left accent.
- `MaterialTabs`: Summary, Data, Exports, and Power BI tabs with a bottom active indicator.
- `PaginationBar`: Previous/Next controls for 10 records per page.
- `StatusBanner`: success/warning/error/offline states with `aria-live`.
- `DebugPanel`: collapsible diagnostics gated away from normal user flow.
- `OdkRuntimeBoundary`: the only host that contains ODK Web Forms; CSS must remain scoped.

## Token Direction

Create TACATDP tokens under the SPA CSS before further UI work:

- Typography: system UI/Segoe UI for shell; preserve ODK runtime typography inside the ODK boundary.
- Spacing: 4, 8, 12, 16, 20, 24, 32.
- Radius: 4 for compact controls, 8 for cards/panels.
- CRDB brand: derive primary/accent values from `CRDB_Bank_PLC.svg` and verify contrast.
- Neutrals: white surfaces over a muted off-white/green-tinted page background.
- Focus: visible focus rings on buttons, cards, form-list rows, and top-bar actions.

## Implementation Instructions

Before improving the UI:

1. Inspect this document, `requirements.md`, `delivery-plan.md`, `slice-checklist.md`, `powerpages/webforms-spa/src/views/AssignedFormsView.vue`, and `powerpages/webforms-spa/src/styles.css`.
2. Inspect CRDB assets in `assets/images/`.
3. Compare reusable patterns from LIMS `docs/UX_DESIGN_SYSTEM.md` and STEMGEN UI tokens/components before inventing a new component rule.
4. Before UI work, write down the expected behavior, data visibility scope, loaded-record limit/pagination, search fields, empty/error states, and what each primary action does. If any of these are unclear, stop and clarify before implementing.
5. Create or update shared shell components/tokens first; avoid page-local styling.
6. Keep ODK Web Forms in `OdkRuntimeBoundary` and verify host CSS does not style ODK controls except for explicitly documented host boundary spacing/footer adjustments.
7. Keep icon+text action controls for primary navigation and commands. Data-table row actions are the compact exception: use icon-only buttons with `aria-label` and hover/focus tooltips, and keep sibling row actions on one line.
8. Use the maintained `@lucide/vue` package for shell icons. Back uses `ArrowLeft`; project Open uses `FolderOpen`; Collect uses `NotepadText`; Edit uses `Pencil`; Refresh uses `RefreshCw`; Data uses `Database` or table-oriented icons where needed; Search uses `Search`. Do not use text glyphs such as `<`, `>`, `R`, `S`, `D`, or `+` as icons.
9. Build and visually check both mobile and desktop widths before upload.

## Acceptance Criteria

- User-facing text says **Monitoring Tool**.
- Unauthenticated users are sent to Microsoft/Power Pages login.
- Authenticated users land on a work queue, not a prototype diagnostic page.
- Authenticated users first see project cards.
- Project detail shows a project command card with the project title and a far-right Collect action.
- Project detail shows Material-style tabs with bottom active state: Summary, Data, Exports, and Power BI.
- The Data tab shows a paginated submitted-record table with search at the end of the toolbar, a unified Updated date range picker, and one-line icon-only View/Edit actions with accessible tooltips.
- Saved records include all submitted records readable by the authenticated user, not only records owned by that user's email.
- Drafts tab does not show stale runtime-load markers as editable drafts.
- Loading uses the CRDB branded `LoadingPanel`.
- Submit uses the CRDB branded blocking progress panel and returns to the Saved data-card list after success.
- The form runner has a top action bar and a full-width ODK runtime area.
- Prototype diagnostics are hidden behind a debug panel.
- Mobile view is readable without forcing a tablet layout.
- Shell CSS is tokenized and does not broadly restyle ODK controls.

## References

- ODK Collect form management and drafts: https://docs.getodk.org/collect-forms/
- ODK Collect form navigation: https://docs.getodk.org/collect-filling-forms/
- ODK form logic: https://docs.getodk.org/form-logic/
- ODK Web Forms: https://docs.getodk.org/web-forms-intro/
- Power Pages Web API: https://learn.microsoft.com/en-us/power-pages/configure/web-api-overview
