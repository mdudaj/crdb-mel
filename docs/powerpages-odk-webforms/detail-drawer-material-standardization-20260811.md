# Detail Drawer Material Standardization — August 11, 2026

## Scope

This slice standardizes record-detail drawer anatomy for the Sustainable Finance MEL Platform prototype after list, table, row, and card-footer abstractions were aligned.

The first implementation targets the two visible detail overlays currently used during prototype review:

- Beneficiary detail drawer.
- Users route access-detail drawer.

## Requirements

- Preserve current behavior, routes, data, and write gates.
- Keep modal semantics: `role="dialog"`, `aria-modal="true"`, labelled drawer titles, visible close actions, and scrim close targets.
- Use shared Material-style abstraction hooks for detail surfaces instead of page-local-only drawer anatomy.
- Keep detail rows scannable: field label first, value second, with overflow-safe text wrapping.
- Keep assigned-form and selected-user activity rows keyboard reachable.
- Do not apply metric-card accent rails to detail surfaces.

## Material 3 UI check

- Component pattern: drawer/detail surface with sectioned detail lists and compact row items.
- Existing tokens/components reused: `--mt-*` spacing, radius, surface, border, text, focus, and row tokens from `styles.css`.
- Material guidance checked: list content should keep primary content on the left and supplemental metadata/actions consistently positioned; dialogs and modal overlays should communicate purpose through a clear title, content, and actions.
- Responsive behavior: existing mobile drawer rules are preserved.
- Accessibility: existing dialog labelling is preserved; assignment/activity rows receive keyboard focus.
- Validator/test: `validate-beneficiary-detail-refinement.mjs`, `validate-users-detail-material-surface.mjs`, and `validate-material-ui-abstractions.mjs`.

## Delivered behavior

- Added shared CSS hooks:
  - `material-detail-surface`
  - `material-detail-header`
  - `material-detail-section`
  - `material-detail-list`
  - `material-detail-row`
  - `material-drawer-actions`
- Beneficiary drawer now uses shared detail surface, header, section, list, and row hooks.
- Users drawer now uses shared detail surface, header, list, section, row, and drawer-action hooks.
- Users assigned-form rows and selected-user activity rows now use shared `material-row` and are keyboard reachable.

## Non-goals

- No Dataverse schema, Power Pages permission, access workflow, routing, or data-loading behavior changed.
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

Build output may still show the known ODK direct `eval` warning and large chunk warnings.
