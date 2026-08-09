# Reporting Export UI Verification Summary

Date: 2026-07-14

## Scope

Implemented the project dashboard workspace for the Monitoring Tool:

- project screen still comes first;
- opening a project now shows a project command card with the project title and a far-right Collect action;
- the Collect action uses a notepad icon and opens the data collection form;
- Summary, Data, Exports, and Power BI are Material-style peer tabs with a bottom active indicator;
- Data is the paginated submitted-record table surface;
- Exports and Power BI show product-path guidance until reporting projection backend work is implemented.

## Commands Run

```bash
npm run typecheck
npm run build
python3 scripts/validate-webforms-spa-foundation.py
```

## Local Render Smoke

Local Vite server:

```bash
npm run dev -- --host 127.0.0.1 --port 5173
```

Playwright verified that the project opens, Collect is visible, one Material tab is active, and Summary, Data, Exports, and Power BI sections are reachable. Screenshots were captured to:

- `/tmp/tacatdp-project-material-data-desktop.png`
- `/tmp/tacatdp-project-material-exports-mobile.png`

## Remaining Verification

- Hosted Power Pages upload has not been performed in this slice.
- Signed-in browser verification on the Power Pages site is still required after an approved upload.
- Reporting projection tables, named exports, and Power BI connection are planned but not implemented in this UI-only slice.
