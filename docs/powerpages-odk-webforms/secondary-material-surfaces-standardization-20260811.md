# Secondary Material Surfaces Standardization — August 11, 2026

## Scope

This slice standardizes secondary surfaces that remain inside Project detail and Access workflow pages after route-level lists, tables, cards, and drawers were aligned.

Targeted surfaces:

- Project record detail panel and normalized answer rows.
- Project export creation panel and saved export rows.
- Project Power BI connection, connection steps, and reporting-table rows.
- Access configuration authorization rows and readiness rows.
- Add-user workflow review, result, manual invitation, and technical detail lists.

## Requirements

- Preserve current routes, data loading, access write gates, and user actions.
- Reuse the existing shared Material hooks instead of adding page-local one-off anatomy.
- Keep dense field/value content in `material-detail-list` and `material-detail-row` structures.
- Keep homogeneous actionable rows keyboard reachable with `material-row`.
- Keep workflow actions aligned through `material-drawer-actions`.
- Do not apply metric-card accent rails to these surfaces.

## Material 3 UI check

- Component pattern: secondary cards, sectioned detail lists, and homogeneous list rows.
- Existing tokens/components reused: `--mt-*` spacing, radius, surface, border, text, and shared row/detail classes.
- Material guidance checked: lists should keep primary/supporting content in stable row anatomy and actions/status on predictable trailing areas; detail panels should keep clear title, content, and actions.
- Responsive behavior: existing mobile grid collapse rules remain in place because page-local classes are preserved.
- Accessibility: semantic headings and description lists remain; export/table/readiness rows added to the shared focusable row contract where actionable or scannable.
- Validator/test: `validate-secondary-material-surfaces.mjs`, `validate-project-detail-material-surface.mjs`, and `validate-material-ui-abstractions.mjs`.

## Non-goals

- No Dataverse schema, Power Pages permission, authentication, or data write behavior changed.
- No new dependency was added.
- No deployment was performed as part of this slice.

## Verification

Run from `powerpages/webforms-spa`:

```bash
npm run test:material
npm run typecheck
npm run build:mshirika-runtime
npm run test:powerpages-assets
```

Known non-blocking build output may still include the ODK direct `eval` warning, large chunk warnings, and duplicate Power Pages partial URL warnings for ODK locale chunks.
