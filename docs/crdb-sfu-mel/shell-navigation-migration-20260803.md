# CRDB SFU MEL Shell Navigation Migration

Date: 2026-08-03
Trace: `20260802-213608-3f954a`

## Task Classification

Frontend UX change. The runtime shell navigation is migrated from the earlier TACATDP monitoring-tool route list to the CRDB Sustainable Finance Unit MEL information architecture.

## Requirements

1. The shell must present the product as `MEL Tool`, while TACATDP remains a project inside the workspace and the department name remains in the bottom organization selector.
2. The side navigation must use durable MEL groups instead of one flat monitoring-tool route list.
3. Routes that are functional today must remain clickable: Dashboard, Projects, Data Collection, Reporting, User & Access, and System Activity.
4. Future MEL modules may be visible only as uniform navigation entries that open a scoped out-of-current-delivery page; they must not look disabled or broken.
5. Administration entries must remain in the bottom section of the side navigation and must remain role-gated where implemented.
6. The top bar remains the single route identity surface; page content must not reintroduce a competing large header.

## UX Description

The authenticated shell uses a full-height navy left navigation drawer with CRDB logo and `MEL Tool`. Navigation is grouped as:

- Field Operations: Dashboard, Projects, Data Collection.
- Results & Reporting: Reporting, Power BI.
- MEL Platform: Programmes, Beneficiaries, Field Data, Indicators, Evidence, Learning.
- Administration: System Activity, User & Access, Settings.

The bottom organization selector remains `Sustainable Finance Unit / Head Office`. Future platform entries use the same visual treatment as implemented entries and route to an explicit current-scope message.

## Acceptance Criteria

1. Desktop side navigation shows the CRDB logo and `MEL Tool`.
2. Side navigation groups are `Field Operations`, `Results & Reporting`, `MEL Platform`, and `Administration`.
3. Dashboard, Projects, Data Collection, Reporting, System Activity, and User & Access keep their existing route behavior.
4. Future platform entries use the same visual treatment as other nav entries and open a current-scope route.
5. Collapsed side navigation hides text but keeps icon tooltips.
6. Non-admin users do not see User & Access or System Activity.

## Accessibility Checklist

- Navigation groups use separate `nav` landmarks with descriptive `aria-label` values.
- Buttons retain `aria-label` values.
- Disabled roadmap entries use native disabled button behavior.
- Collapsed navigation keeps tooltip text for icon-only recognition.
- The single hamburger switcher remains in the sticky top bar.

## Implementation Instructions

Inspect:

- `docs/crdb-sfu-mel/design-system-foundation.md`
- `docs/powerpages-odk-webforms/managed-service-ux-governance.md`
- `powerpages/webforms-spa/src/views/AssignedFormsView.vue`
- `powerpages/webforms-spa/src/styles.css`

Implement by changing only the shell navigation structure and shared navigation CSS. Do not add full route pages for future MEL modules in this slice.

Verify:

```bash
npm run build:mshirika-runtime
python3 scripts/prepare-powerpages-spa-fragment.py --marker mel-shell-20260803-002
pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
```

After upload, purge Power Pages cache and restart the site. In the browser, confirm the Home page uses the newest bundle marker and the side navigation displays the grouped MEL shell.

## Verification Summary

- `npm run build:mshirika-runtime` passed on 2026-08-03.
- `node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-C1XMyZpl.mjs` passed.
- `python3 scripts/validate-webforms-spa-foundation.py` passed after updating the executable shell contract from `Impact Monitoring` to `MEL Tool`.
- Mshirika upload succeeded with `pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll`.
- Post-upload download confirmed both Home fragments reference `index-C1XMyZpl.mjs?v=mel-shell-20260803-004` and `index-CokLer1h.css?v=mel-shell-20260803-004`.
- Post-upload downloaded bundle contains `Field Operations`, `Results & Reporting`, `MEL Platform`, and `Data Collection`.

Known non-blocking warnings:

- Vite still reports upstream `@getodk/web-forms` direct `eval` usage and large chunk warnings.
- PAC upload still reports stale `powerpagecomponent` records that do not exist; upload completes successfully and Home/bundle verification passed.
