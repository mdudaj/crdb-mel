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

## Mshirika dashboard layout revision

On 2026-08-10, the revised shell/dashboard layout was deployed to Mshirika.

Revision scope:

- moved the dashboard title/subtitle out of the dashboard content and into the shell header;
- restored the CRDB logo to the sidenav brand area and moved the leaf symbol beside the TACATDP label;
- compacted the sidenav and enabled drawer scrolling so lower menu items are not clipped on shorter screens;
- kept first-row KPI labels, values, and change lines on single lines;
- rebuilt the final-row climate, training, submission, and program-goal cards to match the requested text/icon/illustration treatment;
- moved the “Last updated / Data synced / copyright” footer content to the persistent shell footer.

Result:

```text
Power Pages website upload succeeded in 212.88 secs.
```

Post-upload verification downloaded the site again and confirmed both Home fragments reference:

```text
/assets/index-D18L6wsc.mjs?v=tacatdp-dashboard-20260810-002
/assets/index-BFYDxzL8.css?v=tacatdp-dashboard-20260810-002
```

The downloaded `index-D18L6wsc.mjs` bundle passed `node --check`.

## Mshirika loan portfolio legend revision

On 2026-08-11, the Loan Portfolio by Type legend fix was deployed to Mshirika.

Revision scope:

- removed the ECharts legend from the Loan Portfolio by Type donut canvas;
- rendered the legend as HTML beside/bottom-right of the donut area;
- recentered the donut and centre value;
- kept the card action in the shared card footer.

Build and package marker:

```text
tacatdp-dashboard-20260811-002
```

Post-upload verification downloaded the site again and confirmed the deployed Home fragments reference:

```text
/assets/index-_YAHDKxX.mjs?v=tacatdp-dashboard-20260811-002
/assets/index-B7MyrjMt.css?v=tacatdp-dashboard-20260811-002
```

The downloaded `index-_YAHDKxX.mjs` bundle passed `node --check`.

Deployment note: with PAC 2.9.3, the successful upload used a clean fresh Enhanced-model package. The overlay replaced the fresh package's existing Home copy files in place and copied only the required Home-referenced web files. Do not copy the repository `web-pages/home` folder wholesale into a fresh package, because the fresh download may use `content-pages/Home.en-US...` while the repository mirror uses `content-pages/en-US/...`; mixing both creates duplicate or primary-key-missing webpage records.

## CRDB dashboard chart spacing revision

On 2026-08-11, the dashboard chart spacing revision was deployed directly to CRDB after device-code PAC authentication with the delegated Denis Muroba profile.

Revision scope:

- pushed the Loan Portfolio by Type doughnut left and its legend slightly right/down so the first legend marker no longer touches the doughnut;
- moved Loan Performance centre text into the native ECharts doughnut title, matching the Loan Portfolio by Type pattern;
- changed the Tanzania regional map visual legend to a more granular piecewise disbursed legend;
- shifted the map layout left/centre-left to reserve readable right-side legend space.

Target:

- Environment: `TACATDP-CRDB-Dev`
- Environment URL: `https://org5eb0379b.crm4.dynamics.com/`
- Website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- PAC user: `dmuroba@CRDBBANK.CO.TZ`
- Source branch/commit: `prototype-next-delivery` / `d3d4f21`

Build and package marker:

```text
tacatdp-dashboard-20260811-004
```

Deployment used a clean fresh Enhanced-model CRDB package, replaced the fresh package Home copy files in place, copied only the required Home-referenced web files, and uploaded with:

```text
pac pages upload --environment https://org5eb0379b.crm4.dynamics.com/ --path <fresh-package>/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
```

Result:

```text
Power Pages website upload succeeded in 236.56 secs.
```

Post-upload verification downloaded the CRDB site again and confirmed the deployed Home fragments reference:

```text
/assets/index-BKbav0i7.mjs?v=tacatdp-dashboard-20260811-004
/assets/index-onZrj1qI.css?v=tacatdp-dashboard-20260811-004
```

The downloaded `index-BKbav0i7.mjs` bundle passed `node --check`.
