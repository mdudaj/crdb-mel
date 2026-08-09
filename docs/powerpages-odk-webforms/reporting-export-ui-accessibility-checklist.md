# Reporting Export UI Accessibility Checklist

Date: 2026-07-14

## Checked

- Project and section navigation uses real buttons with visible text labels.
- Section controls use `role="tab"` and `aria-selected` for Summary, Data, Exports, and Power BI.
- The project dashboard has an accessible label based on the selected project name.
- The Collect action has matching visible and accessible text and uses a notepad icon.
- Search inputs have explicit accessible names and hidden labels.
- The submitted-data table uses semantic `table`, `thead`, `tbody`, and `th scope="col"`.
- The table is wrapped in a focusable horizontal-scroll region for narrow screens.
- Loading and submission status areas use `aria-live`.
- Icon usage remains icon plus text; no icon-only primary navigation was introduced.
- Mobile CSS collapses form header, toolbars, guidance cards, and table controls to one column.

## Remaining Manual Checks

- Browser check in the hosted Power Pages session after upload.
- Keyboard tab-order check through project cards, Collect, section tabs, search, table, and Edit.
- Screen-reader announcement check for tab state after section changes.
