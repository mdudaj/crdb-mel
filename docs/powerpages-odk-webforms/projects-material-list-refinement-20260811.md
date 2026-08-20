# Projects Material List Refinement — August 11, 2026

## Scope

This slice refines the Projects route after the Users list and Project detail surface passes. The intent is to make the project entry list follow the same Material-style list/card contract while preserving the existing project assignment and navigation behavior.

## Delivered behavior

- The Projects route now groups its header, loading skeletons, project cards, and empty state inside one `project-list-surface`.
- The list has a visible heading, support text, and assigned-project count chip.
- Each project card now has stable anatomy:
  - header with project identity and text-labelled assignment status,
  - content with description and compact facts,
  - footer with the Open project action aligned consistently.
- Project cards remain elevated and keep the existing left accent shade for the project list, as requested.
- Project cards are keyboard reachable and have hover/focus feedback.
- Loading and empty states remain scoped to the Projects surface.

## Non-goals

- No project assignment, Dataverse query, draft, submission, export, or navigation logic changed.
- No dashboard project list behavior changed beyond shared CSS inheritance.
- No new UI dependency was added.
- No deployment was performed as part of this slice.

## Verification

Run from `powerpages/webforms-spa`:

```bash
npm run test:material
npm run typecheck
npm run build:mshirika-runtime
npm run test:powerpages-assets
```

The focused validator is:

```bash
node ../../scripts/validate-projects-material-list.mjs
```
