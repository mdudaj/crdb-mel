# Managed Shell Side Navigation Delivery

Date: 2026-07-21

## Scope

Deliver the first TACATDP managed-service portal shell with a collapsible left
navigation drawer. The shell supports predictable movement between operational
work and administration. The 2026-07-21 route/content revision promotes the
authenticated landing surface from a prototype project hero to a concise
operational dashboard, and makes Reporting a real route.

## Requirements

- Keep Dashboard as the first authenticated screen.
- Keep Projects as a dedicated operational route.
- Make Reporting a dedicated cross-project route, not a shortcut into a
  project Data tab.
- Add a desktop left navigation drawer with a collapsible rail mode.
- Keep the side navigation pinned to the full left edge from top to bottom.
- Push the app top bar, current page header, page content, and future footer
  into the right workspace.
- Place one three-bars menu switcher at the left of the top bar, not inside the
  side navigation rail.
- Keep the Power Pages website header/footer runtime enabled for portal Web API
  token support, but visually suppress the default portal chrome so the app
  shell is the only visible header/footer.
- Place routine operational destinations at the top of the drawer.
- Place administration/configuration destinations in a bottom drawer group.
- Keep User & Access role-gated and available only to administrators.
- Keep project tabs inside the project workspace; do not duplicate Summary,
  Data, Exports, or Power BI as global navigation items.
- Use icon plus label controls in expanded navigation and icon-only controls
  with tooltips in collapsed mode.
- On mobile, use a modal drawer opened from a compact top bar.

## UX Description

The authenticated portal now uses a managed app shell:

- left navigation contains Projects and Reporting in the operational section;
- bottom navigation contains an Administration label, User & Access, and a
  disabled Configuration placeholder;
- side navigation owns the full-height left edge;
- right workspace contains a sticky top bar, page body, and footer;
- one hamburger switcher sits at the far left of the top bar;
- footer lives in the dedicated `managed-app-footer` slot at the bottom of the
  right workspace, outside page content;
- active states follow the current view;
- collapsed desktop mode preserves icons and hover/focus tooltips;
- mobile mode opens the same navigation order as a slide-in drawer.

The dashboard is now the default work surface. Opening a project continues to
show the project title, far-right Collect action, and Material-style project
tabs. Reporting opens as its own route with cross-project health, exports, and
Power BI readiness actions.

## Accessibility Checklist

- Icon navigation buttons have `aria-label` values.
- Collapsed rail items expose readable hover/focus tooltips.
- Mobile drawer open and close buttons have labels.
- Mobile drawer scrim is available as a button to close the drawer.
- Admin-only User & Access remains guarded by the existing admin-role check.
- State is shown through active styling and visible labels, not color alone.

## Implementation Instructions

Inspect these files when revising this slice:

- `powerpages/webforms-spa/src/views/AssignedFormsView.vue`
- `powerpages/webforms-spa/src/styles.css`
- `docs/powerpages-odk-webforms/managed-service-ux-governance.md`
- `docs/powerpages-odk-webforms/managed-service-ux-agent-checklist.md`
- `docs/powerpages-odk-webforms/monitoring-tool-ux-design-system.md`

Package steps:

1. Run `npm run build` from `powerpages/webforms-spa`.
2. Copy the generated `dist/assets/index-*.mjs` and `dist/assets/index-*.css`
   entry assets into both Power Pages web-files packages.
3. Add matching `*.webfile.yml` metadata for new hashed entry assets.
4. Update both Home page copies to reference the new entry assets with a fresh
   cache-busting query string.
5. Run `python3 scripts/validate-webforms-spa-foundation.py`.
6. Upload the enhanced Power Pages package with PAC.
7. Download the site after upload and verify Home references and web files.
8. Purge Power Pages cache and visually check desktop and phone widths.

## Verification

- `npm run build` passed. Vite still reports known upstream ODK dependency
  warnings about `eval` and large chunks.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `pac env who` confirmed `PowerPagesDeveloper-070926-125720`.
- `pac pages list` confirmed site `TACATDP Monitoring Tool` with website ID
  `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`.
- `pac pages upload --modelVersion 2 --forceUploadAll` completed with
  `Power Pages website upload succeeded`.
- A post-upload `pac pages download --modelVersion Enhanced` confirmed the
  hosted package contains the new Home references and matching web files.
- Package Home references were updated to
  `index-DwNb1_Hr.mjs?v=managed-shell-20260721-001` and
  `index-B5sk633-.css?v=managed-shell-20260721-001`.
- Shell layout revision package references were updated to
  `index-BNlcpJnd.mjs?v=shell-topbar-20260721-001` and
  `index-B-T0FMDy.css?v=shell-topbar-20260721-001`.
- The shell layout revision was uploaded to Mshirika and a post-upload
  enhanced-model download confirmed those Home references and web files exist
  in the hosted site package.
- `node --check` passed on the downloaded hosted `index-BNlcpJnd.mjs` entry.
- The integrated shell revision was uploaded to Mshirika. A post-upload
  enhanced-model download confirmed:
  - Home includes `tacatdp-portal-chrome-reset` to hide the default portal
    header/footer visually.
  - Home references `index-BbQqhSlU.mjs?v=shell-integrated-20260721-001` and
    `index-CqjOYCq5.css?v=shell-integrated-20260721-001`.
  - The `Monitoring Tool SPA` page template keeps
    `adx_usewebsiteheaderandfooter: true` so Power Pages runtime services
    remain available.
  - `node --check` passed on the downloaded hosted `index-BbQqhSlU.mjs` entry.
- The shell slot correction was uploaded to Mshirika. A post-upload
  enhanced-model download confirmed Home references
  `index-DzV91Y7G.mjs?v=shell-slots-20260721-001` and
  `index-CqjOYCq5.css?v=shell-slots-20260721-001`.
- The footer was moved out of the Projects page hero and into the dedicated
  `managed-app-footer` slot after `managed-workspace-body`.
- `validate-webforms-spa-foundation.py` now checks the managed shell slots and
  fails when the shell footer is missing or the hamburger switcher rule is not
  followed.
- The route/content model revision was uploaded to Mshirika. A post-upload
  enhanced-model download confirmed:
  - Home includes `tacatdp-portal-chrome-reset` to keep default portal chrome
    visually suppressed while retaining Power Pages runtime services.
  - Home references `index-BqvSAFo3.mjs?v=route-model-20260721-001` and
    `index-BVFW9552.css?v=route-model-20260721-001`.
  - The hosted web-files package contains `index-BqvSAFo3.mjs` and
    `index-BVFW9552.css`.
  - `node --check` passed on the downloaded hosted `index-BqvSAFo3.mjs` entry.
- `validate-webforms-spa-foundation.py` now checks that the AppView union
  includes `dashboard` and `reporting`, the default view is `dashboard`, and
  global Reporting calls `openReporting()` instead of jumping into a project
  Data tab.

## Remaining Evidence

Hosted screenshot evidence must be captured after portal restart and cache
purge. Required visual checks are:

- desktop expanded drawer;
- desktop collapsed drawer tooltip behavior;
- mobile drawer open and close behavior;
- project workspace still shows the Collect action and project tabs correctly.
