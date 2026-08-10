# TACATDP Dashboard ECharts Prototype Slice

Date: 2026-08-10

## Scope

This slice revises the Power Pages Vue SPA so the default Dashboard route is a dedicated TACATDP visualization dashboard. The previous mixed dashboard pattern, where operational workbench content and beneficiary visualization shared the same surface, is removed.

The prototype dashboard uses demonstration data. It must not be presented as official CRDB Bank, Green Climate Fund, or TACATDP statistics.

## Route and navigation decision

- `Dashboard` is the high-fidelity TACATDP visualization route.
- `Workspace` holds the operational form/workbench components that were previously mixed into the dashboard.
- The left drawer keeps the administration section for product completeness.
- `Organizations` remains visible as a future-ready route for implementation partners, CRDB units/branches, cooperatives, AMCOS/SACCOS, and other institutions responsible for programme data. For the current TACATDP prototype, it is not a core workflow.

## Visualization decision

Use Apache ECharts through `vue-echarts` for all dashboard charts and the Tanzania regional map.

Reasons:

- ECharts supports line, bar, donut, and choropleth map visualizations from one library.
- The map can use local GeoJSON, avoiding external map tiles and permission issues in Power Pages.
- A local administrative-boundary map is more appropriate than the previous marker-only prototype for region-level TACATDP financing and MEL review.
- Removing Leaflet keeps the dependency graph aligned with the current implementation.

## Map data source

The prototype map uses a local Tanzania ADM1 GeoJSON asset:

- Source file: `powerpages/webforms-spa/src/assets/maps/tanzania-adm1.json`
- Boundary source: geoBoundaries Open Tanzania ADM1 dataset, boundary ID `TZA-ADM1-36957248`
- Administrative unit type: Regions
- Source attribution in geoBoundaries metadata: OpenStreetMap, Wambacher

## Dashboard information hierarchy

The dashboard follows the supplied TACATDP KPI mockup:

1. Programme-wide KPI cards: loans, borrowers, disbursement, repayment, training, and estimated climate impact.
2. Core analytics: loan portfolio type, cumulative disbursement trend, regional distribution map, technology financing, and loan performance.
3. MEL outcome cards: improved practices, yield, soil fertility reports, and tCO₂e avoided.
4. Operational monitoring: training summary and recent data submissions.
5. Programme goal: concise domain context for reviewers.

## Implemented files

- `powerpages/webforms-spa/src/components/dashboard/TacatdpDashboardPage.vue`
- `powerpages/webforms-spa/src/prototype/tacatdpDashboardData.ts`
- `powerpages/webforms-spa/src/assets/maps/tanzania-adm1.json`
- `powerpages/webforms-spa/src/views/AssignedFormsView.vue`
- `powerpages/webforms-spa/src/styles.css`
- `scripts/validate-beneficiary-kpi-map-slice.py`
- `scripts/validate-webforms-spa-foundation.py`
- `scripts/stage-powerpages-spa-build.py`

## Power Pages package

The staged package references build marker:

```text
tacatdp-dashboard-20260810-001
```

The current staged entry assets are:

```text
/assets/index-B4OQ5yHn.mjs
/assets/index-iJm6_0ke.css
```

## Verification

Run:

```bash
npm run build:mshirika-runtime
python3 scripts/stage-powerpages-spa-build.py
python3 scripts/validate-webforms-spa-foundation.py
python3 scripts/validate-beneficiary-kpi-map-slice.py
node --check powerpages/tacatdp-monitoring-tool/.powerpages-site/web-files/index-B4OQ5yHn.mjs
```

Known build warnings:

- `@getodk/web-forms` still emits direct `eval` warnings from the upstream ODK runtime bundle.
- Some built chunks exceed 500 KB.

## Mshirika deployment

Deployment approval was given on 2026-08-10.

Target:

- Environment: `PowerPagesDeveloper-070926-125720`
- Environment URL: `https://orga3cf4b37.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- PAC user: `john.mduda@mshirikacorp.onmicrosoft.com`

The upload used the PAC 2.9.3 fresh-package workaround:

1. Downloaded a fresh Enhanced-model package from Mshirika.
2. Overlaid the approved Home fragments and SPA web-files.
3. Uploaded the fresh-format package with `pac pages upload --modelVersion Enhanced --forceUploadAll`.

Result:

```text
Power Pages website upload succeeded in 247.89 secs.
```

Post-upload verification downloaded the site again and confirmed both Home fragments reference:

```text
/assets/index-B4OQ5yHn.mjs?v=tacatdp-dashboard-20260810-001
/assets/index-iJm6_0ke.css?v=tacatdp-dashboard-20260810-001
```

The downloaded `index-B4OQ5yHn.mjs` bundle passed `node --check`.

If the browser still shows stale content, purge Power Pages cache or restart the site, then reload with browser cache disabled.
