# Data Tab Action and Calendar Polish

Date: 2026-07-15
Status: implemented, locally verified, and deployed to the development Power Pages site

## Requirements Note

The Data tab is an operational review surface for bank staff. Its current View and Edit buttons occupy too much horizontal space and wrap on narrow layouts. Its separate native From and To date inputs do not read as one reporting period and the browser-controlled calendar presentation is visually weak.

This slice changes presentation and interaction only. Reporting filters, FetchXML behavior, row detail, edit behavior, permissions, page size, and data scope remain unchanged.

## Product Requirements

- Keep all actions for a reporting row on one horizontal line.
- Use icon-only row actions: Eye for View and Pencil for Edit.
- Every icon action must have an accessible name and a tooltip on pointer hover and keyboard focus.
- Tooltips must not be the only source of meaning; `aria-label` remains authoritative for assistive technology.
- Replace separate From and To native controls with one project-styled Updated date range picker.
- The picker must show selected start and end dates as a single range, permit calendar selection, and retain typed date entry.
- Selecting or clearing a range must continue to update `reportDateFrom` and `reportDateTo` in `YYYY-MM-DD` form for the existing API.
- An incomplete range must not apply a half-filter accidentally.
- Clear filters becomes an icon-only action with an accessible tooltip and remains aligned with the filter row.
- Do not change the Exports or Power BI workflows in this slice.

## UX Description

### Row Actions

- The Actions column contains a compact action group with two 38 by 38 pixel icon buttons.
- Buttons remain side by side at desktop, tablet, and phone widths.
- Hover or focus reveals a short tooltip above the button: `View record` or `Edit record`.
- Disabled state remains visually distinct and does not reflow the table.

### Updated Date

- The filter is labeled `Updated date` and displays a Calendar icon plus either `Select date range` or the formatted selected period.
- Activating it opens a compact calendar popover below the field on desktop and a width-constrained overlay on smaller screens.
- The calendar clearly distinguishes today, range start, range end, and days between them.
- Month navigation uses familiar arrow icons with accessible labels.
- The user can type dates as well as choose them from the calendar.
- The picker closes after a complete range is applied; clearing it restores all dates.
- The CRDB primary green marks endpoints; a lighter neutral/brand tint marks the interval.

## Accessibility Checklist

- [x] Icon buttons have `type="button"`, unique `aria-label`, and decorative icons use `aria-hidden="true"`.
- [x] Tooltips appear on both hover and `:focus-visible` and do not capture pointer events.
- [x] Action buttons meet a minimum 38 by 38 pixel target and retain a visible focus ring.
- [x] Action group does not wrap at phone width.
- [x] Date range input has a persistent visible label.
- [x] Calendar supports keyboard navigation, Escape close, and typed date entry through the maintained Vue Datepicker component.
- [x] Selected dates and today are not identified by color alone.
- [x] Range changes do not submit a form and incomplete ranges are not applied.
- [x] Popover text and controls use the CRDB theme and were checked at desktop and phone widths.

## Acceptance Criteria

1. View and Edit render as icons only and remain on one row at 360 px and desktop widths.
2. Hovering or focusing either icon shows the correct tooltip; screen readers receive the same command through `aria-label`.
3. The Data filter bar contains one Updated date range picker instead of separate From and To controls.
4. A selected date range produces the same `dateFrom` and `dateTo` API values as before.
5. Clearing the date picker removes both date values.
6. Search, submitter, review-state, pagination, View, and Edit behavior are unchanged.
7. SPA typecheck/build and foundation validation pass.
8. Desktop and mobile screenshots show no overlap, clipping, unexpected wrapping, or blank calendar.

## Artifact Readiness

- Existing product/design-system source: `monitoring-tool-ux-design-system.md`.
- Existing reporting contract: `reporting-export-requirements.md`.
- Implementation surfaces: `AssignedFormsView.vue`, `styles.css`, `validate-webforms-spa-foundation.py`.
- Architecture decision: not applicable; this is a bounded component and presentation revision with no persistence or service boundary change.
- Schema/example: not applicable; API date strings remain unchanged.
- Dependency: approved and installed `@vuepic/vue-datepicker@14.0.0`.
- Deployment approval: granted on 2026-07-15. Development Power Pages upload and managed solution export are complete; CRDB import remains pending because no CRDB PAC authentication profile is configured on this workstation.

## Evidence

- Material Design date pickers recommend a desktop dropdown calendar, clear current/selected/range states, and typed input as an accessible alternative: https://m2.material.io/components/date-pickers
- USWDS date-range guidance recommends preserving manual date entry and testing the customized component for accessibility: https://designsystem.digital.gov/components/date-range-picker/
- Vue Datepicker supports range mode and multiple calendar/input configurations: https://vue3datepicker.com/props/modes/

## Verification Instructions

1. Run `npm run build` in `powerpages/webforms-spa`.
2. Run `python3 scripts/validate-webforms-spa-foundation.py`.
3. Start local preview and capture Data tab screenshots at 1440 by 1000 and 390 by 844.
4. Verify tooltips with pointer and keyboard focus.
5. Select, type, and clear a date range and inspect the resulting reporting request.

## Verification Evidence

- `npm run build`: passed.
- `python3 scripts/validate-webforms-spa-foundation.py`: passed.
- Headless Chrome at 1440 by 1000 and 390 by 844:
  - View/Edit action group computed as `display: flex`, `flex-wrap: nowrap`.
  - Both actions computed at 38 px width and contained no visible text node.
  - Tooltip reached opacity 1 after pointer hover.
  - Calendar rendered at 386 px desktop and 304 px mobile.
  - Calendar inherited CRDB primary `#236b22`.
  - Last 7 days produced `09 Jul 2026 - 15 Jul 2026`; clear restored an empty range.
- Screenshots: `/tmp/tacatdp-data-desktop.png`, `/tmp/tacatdp-calendar-desktop.png`, `/tmp/tacatdp-tooltip-desktop.png`, `/tmp/tacatdp-data-mobile.png`, and `/tmp/tacatdp-calendar-mobile.png`.

## Deployment Evidence

- Development website: `TACATDP Monitoring Tool` (`fccc0cc6-7f5e-4885-aeb8-2272e68130a3`).
- Release marker: `data-calendar-polish-20260715-001`.
- Enhanced-model `pac pages upload --forceUploadAll`: completed successfully.
- Direct Dataverse file-column downloads for the main, ODK, CSS, and runtime assets matched the local build by SHA-256 and byte count.
- Hosted Dataverse configuration verification passed for all 12 entity sets, 24 Web API settings, 12 table permissions, role links, the portal contact, assignment seed, and file-backed XForm.
- The source solution was updated from `0.1.0.0` to `0.2.0.0`.
- The active main module and stylesheet were added to `tacatdp_prototype` as existing `powerpagecomponent` records before export.
- Managed package: `/home/jmduda/Downloads/TACATDP_Impact_Tracking_Prototype_0_2_0_0_managed.zip`.
- Package SHA-256: `501f8401cdf2c128b125a169b099f0e4c600d92791586f67959a60db07f324ca`.
- ZIP inspection confirmed `tacatdp_prototype`, version `0.2.0.0`, managed state, and the complete main, CSS, ODK, and runtime file payloads.
- A clean rebuild rerun after deployment could not start because the workspace sandbox approval reviewer timed out twice. The deployed files came from the previously successful production build, and their live hashes match that build exactly.
