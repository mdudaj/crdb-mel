# Beneficiary KPI and Mapping Prototype Slice

Date: 2026-08-09

## Scope

This slice adds a lightweight beneficiary insight layer to the existing Power Pages Vue SPA. It does not create or deploy new Dataverse tables.

The prototype currently collects baseline records from beneficiaries. For the dashboard, beneficiary insights are derived from projected submission report rows so the portal can demonstrate operational KPIs before Power BI access is available.

## Prototype beneficiary model

For the prototype, a beneficiary is represented as a reporting-view projection with:

- beneficiary identifier;
- beneficiary or respondent name;
- beneficiary type;
- gender or sex where captured;
- district;
- ward;
- submitted date;
- optional latitude and longitude.

The implementation reads flexible baseline field names from `mp_rootanswersjson`, including `beneficiary_*`, `customer_*`, `respondent_*`, `district`, `ward`, `gender`, `sex`, `latitude`, and `longitude`.

## Visualisation library decision

Use:

- Apache ECharts through `vue-echarts` for KPI charts.
- Leaflet through `@vue-leaflet/vue-leaflet` for prototype maps.

Reasons:

- ECharts supports polished dashboard charts with good performance and responsive rendering.
- Leaflet is sufficient for a prototype map and works well with OpenStreetMap tiles.
- MapLibre GL JS remains the future-product option if the platform later needs vector tiles, WebGL rendering, or heavier geospatial layers.

## Dashboard behaviour

The dashboard now shows:

- total beneficiaries derived from reporting rows;
- districts covered;
- beneficiary type breakdown chart;
- district distribution chart;
- map markers when valid coordinates exist;
- a district coverage table when coordinates are not yet available.

Charts and maps are lazy-loaded after the dashboard shell renders. This preserves startup performance and avoids loading visualisation libraries before the user reaches the insight panels.

## Future Dataverse step

If the prototype is accepted, create a governed beneficiary master table and link baseline submissions to beneficiary records. The future schema should avoid TACATDP-only naming and support multiple Sustainable Finance Unit programmes/projects.

Candidate future tables:

- `mp_beneficiary`
- `mp_programme`
- `mp_project`
- `mp_beneficiaryprojectmembership`
- `mp_submission`
- `mp_submissionreportrow`

The prototype dashboard should then read beneficiary facts from the governed beneficiary/projection tables instead of deriving them only from `mp_rootanswersjson`.

## Verification

Run:

```bash
npm run build:mshirika-runtime
python3 scripts/validate-webforms-spa-foundation.py
python3 scripts/validate-beneficiary-kpi-map-slice.py
```

No deployment is included in this slice.
