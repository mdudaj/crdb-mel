# Data Tab Owner Visibility Revision

Date: 2026-07-15
Status: implemented, deployed to development, and exported in managed solution `0.2.1.0`

## Requirement

The Data tab is an operational record list for bank staff. Remove the Owner column from the paginated table to reduce horizontal density. Preserve owner metadata and display it explicitly after the user selects the View action for a record.

## Scope

- Remove the Owner table header and row cell from the Data list.
- Keep Record, Version, Updated, Review, Projection, and Actions columns unchanged.
- Show `Owner: <email>` in the existing record detail panel; use `Unknown owner` when no value is available.
- Keep submitter filtering, CSV export owner data, Dataverse queries, permissions, and persistence unchanged.
- Rebuild and deploy through the existing Power Pages site and `tacatdp_prototype` managed solution lineage.

## Acceptance Criteria

1. The Data table does not render an Owner header or owner cell.
2. Selecting View opens the existing detail panel and shows an explicitly labeled Owner value.
3. Pagination, filters, View, Edit, exports, and Power BI behavior remain unchanged.
4. The SPA validator prevents Owner from returning to the Data list while requiring it in detail.
5. The production build and focused validator pass before deployment.

## Implementation Instructions

Inspect `AssignedFormsView.vue`, `validate-webforms-spa-foundation.py`, the current enhanced-model Power Pages package, and the active solution component inventory. Change only the list/detail markup and validator. Build the SPA, reuse existing Power Pages component IDs when updating hashed assets, upload to the explicit development website ID, verify live file-column hashes, increment the managed solution version, and inspect the exported ZIP before CRDB handoff.

No ADR or schema artifact is required because this revision changes only where already-loaded metadata is displayed.

## Verification Summary

- SPA foundation validator: passed, including the Owner list/detail regression rule.
- TypeScript check and production Vite build: passed; only the existing ODK direct-eval and large-chunk warnings remain.
- Deployment package module syntax and source/build byte comparison: passed.
- Development Power Pages upload completed in 96.69 seconds.
- Live main file-column SHA-256 matched the production build; Home release marker was present on both Home rows.
- Main bundle remained a member of `tacatdp_prototype` after its hash/name update.
- Managed solution `0.2.1.0` exported successfully.
- Package: `/home/jmduda/Downloads/TACATDP_Impact_Tracking_Prototype_0_2_1_0_managed.zip`.
- Package SHA-256: `a8702d1dcd32b2f38c423f3295044914d8e1f2dc1b93e0c917b5eb2f2e5a24ff`.
- ZIP inspection confirmed managed state, version `0.2.1.0`, and an embedded main module identical to the verified build.
