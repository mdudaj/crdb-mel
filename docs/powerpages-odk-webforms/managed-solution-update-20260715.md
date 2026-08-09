# TACATDP Managed Solution Update 0.2.2.0

Date: 2026-07-15
Status: exported; CRDB import pending target authentication or administrator action

## Scope

This update carries the current TACATDP portal and Dataverse solution lineage into CRDB as an update to the previously imported managed solution. It includes the reporting portal slices already delivered in development, the Data-tab action and calendar polish, and the Owner visibility revision under release marker `data-owner-detail-20260715-001`.

Version `0.2.2.0` intentionally excludes the deferred C# automatic-projection plug-in assembly because the CRDB import account does not yet have `prvCreatePluginAssembly`. It includes no plug-in assembly, type, execution step, or image. Automatic projection refresh will be delivered later after permission and execution-role approval.

The update preserves the existing solution unique name `tacatdp_prototype` and publisher lineage. It must be imported as an update, not as a new ad hoc solution.

## Package

- File: `/home/jmduda/Downloads/TACATDP_Impact_Tracking_Prototype_0_2_2_0_managed_no_plugin.zip`
- Unique name: `tacatdp_prototype`
- Version: `0.2.2.0`
- Managed: yes
- SHA-256: `14259c8bea1cdc4ad69ffadc2c7607275adb208d79f119f3a1bae6ffa311a052`

ZIP inspection confirms that the active main module, stylesheet, ODK bundle, and Vue runtime are present as Power Pages component file payloads. The development solution inventory contains the active site and all referenced portal bundle components. The ZIP contains no `PluginAssemblies/` payload and no root component type 90, 91, 92, or 93.

## Import Instructions

1. In the CRDB Power Platform environment, open **Solutions** and select **Import solution**.
2. Choose the managed ZIP listed above.
3. Confirm that Power Platform identifies the existing `TACATDP Impact Tracking Prototype` solution and presents an **Update** action from the earlier version to `0.2.2.0`.
4. Use the standard update option. Do not select stage-for-upgrade unless CRDB administrators intentionally require a separate upgrade process.
5. Keep environment-specific connection references and environment variables unchanged unless the import wizard explicitly reports a missing binding.
6. Complete the import, publish all customizations, then clear or restart the Power Pages site cache before verification.

An administrator can perform these steps, or the `denis muroba` account can be granted sufficient solution import/customization privileges and a CRDB PAC profile can be configured for an assisted import. The current machine has only the development PAC profile, so no direct CRDB import was attempted.

## Post-Import Verification

1. Confirm solution `tacatdp_prototype` reports version `0.2.2.0` and managed state.
2. Open the CRDB Power Pages site in Preview and authenticate as a normal bank user.
3. Open a project, select **Data**, and confirm rows load without a 400 or 500 response.
4. Confirm the Data list has no Owner column; select View and confirm the detail panel shows `Owner: <email>`.
5. Confirm View and Edit are icon-only, remain on one row, and show tooltips on hover and keyboard focus.
6. Open the Updated date picker, select and clear a range, and confirm filtering and pagination remain functional.
7. Confirm Exports and Power BI tabs remain active and retain the existing reporting behavior.
8. Submit or edit a test record and verify the canonical submission data remains intact. Automatic projection execution is still deferred as documented; use the trusted projection builder where required.

## Rollback

Do not delete the managed solution as a routine rollback because that can remove solution-owned components and data. If import fails, retain the existing CRDB version and export the import log. If post-import verification fails, restore the previously approved portal asset references through the same solution lineage or import a vendor-approved corrective version with a higher version number.
