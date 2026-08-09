# CRDB Reporting Web API Correction

Date: 2026-07-16

## Incident

After managed solution `0.2.2.0` and Package Deployer `1.0.2` were installed in
CRDB, the signed-in Data tab returned:

```text
404 9004010C: Resource not found for the segment mp_submissionreportrow.
```

The SPA used the correct plural entity set, `mp_submissionreportrows`, and the
Dataverse reporting table existed. Environment inspection showed that the target
site had none of the reporting Web API site settings or reporting table
permissions.

## Root Cause

The development site contained the required configuration, but its eight Web API
site settings and four table permissions were orphan Power Pages components that
were not owned by `tacatdp_prototype`. Adding the whole Power Pages site to the
solution did not adopt those existing child components. The `0.2.2.0` managed
export therefore omitted all 12 components, and the package validator did not
check for them.

## Correction

Each reporting component was explicitly added to the existing unmanaged solution:

- `mp_submissionreportrow`: enabled, fields, Authenticated Users permission.
- `mp_submissionrepeatrow`: enabled, fields, Authenticated Users permission.
- `mp_submissionanswer`: enabled, fields, Authenticated Users permission.
- `mp_exportsetting`: enabled, fields, Authenticated Users permission.

The corrected managed solution is `0.2.3.0`; Package Deployer is `1.0.3`. It
retains the no-plugin constraint and the Denis/Hailo seed assignments. The package
validator requires all 12 component IDs and verifies that every reporting table
permission references the Authenticated Users web role.

## Delivery And Verification

1. Inspect this note, `reporting-export-requirements.md`, the package validator,
   and `package-deployer-seed-delivery.md`.
2. Deploy Package Deployer `1.0.3` to CRDB with `pac package deploy`; do not use
   `pac data import`.
3. Confirm managed solution `tacatdp_prototype` is version `0.2.3.0`.
4. Restart the Power Pages site and purge its cache.
5. Sign in and request `/_api/mp_submissionreportrows?$top=1`. A `200` response
   proves the entity set is exposed; `403` indicates role/permission assignment
   still needs inspection; `404 9004010C` indicates the site settings did not
   reach the active site.
6. Open the Data tab and verify list, detail, pagination, filtering, and CSV
   download. This authenticated target-environment smoke test remains mandatory.

Rollback is operational: retain the previous package, do not uninstall the
managed solution or delete data, and correct/redeploy under the same solution
lineage if target verification fails.
