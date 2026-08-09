# Projection Plug-in Package Exclusion

Date: 2026-07-15
Status: approved temporary CRDB packaging boundary

## Decision

CRDB import users do not currently have `prvCreatePluginAssembly`, and approval may take time. Export the next TACATDP managed solution without the deferred C# automatic-projection plug-in so the portal, reporting schema, exports, and Power BI work can proceed.

This is a solution-membership change only. Keep the signed assembly and plug-in type registered in the development environment for later activation work. Do not create a step or image, delete the assembly/type, change permissions, or alter projection tables/data.

## Verified Starting State

- Source solution: `tacatdp_prototype` version `0.2.1.0`.
- Plug-in assembly: `6cfe4209-c97f-f111-ab0e-7ced8d41fa2d`.
- Plug-in type: `6ffe4209-c97f-f111-ab0e-7ced8d41fa2d`.
- Assembly solution component: `6dfe4209-c97f-f111-ab0e-7ced8d41fa2d`, component type 91.
- Registered execution steps: none.
- Registered images: none.
- The `0.2.1.0` managed ZIP contains one plug-in DLL under `PluginAssemblies/` and one root component of type 91.

## Acceptance Criteria

1. The development assembly and type still exist after packaging changes.
2. The assembly is no longer a member of `tacatdp_prototype`.
3. The new managed ZIP has no `PluginAssemblies/` payload.
4. The new `solution.xml` has no root component type 90, 91, 92, or 93.
5. Portal Power Pages components, reporting tables, export configuration, and solution lineage remain present.
6. The new version is higher than `0.2.1.0` and imports as an Update.

## Operating Boundary

Automatic projection refresh remains unavailable in CRDB. Run the trusted projection builder when reporting rows must be refreshed until CRDB approves plug-in assembly creation and the execution-user/role/step/image delivery is separately approved. Restore automation only through a later, higher managed solution version.

## Implementation Instructions

Use the Dataverse `RemoveSolutionComponent` action for component type 91 and the verified assembly ID because PAC CLI 2.8.1 has no remove-solution-component command. Verify removal by solution inventory and separately verify the assembly/type remain registered. Increment the solution version, export managed, inspect the ZIP, and compare the non-plug-in root component inventory with the prior package. Do not delete any Dataverse component or data.

## Verification Summary

- `RemoveSolutionComponent` returned HTTP 200 for assembly component ID `6cfe4209-c97f-f111-ab0e-7ced8d41fa2d`.
- Source solution inventory contains no component type 90, 91, 92, or 93.
- Development assembly and plug-in type remain registered; steps and images remain absent.
- Managed solution version: `0.2.2.0`.
- Package: `/home/jmduda/Downloads/TACATDP_Impact_Tracking_Prototype_0_2_2_0_managed_no_plugin.zip`.
- Package SHA-256: `14259c8bea1cdc4ad69ffadc2c7607275adb208d79f119f3a1bae6ffa311a052`.
- ZIP inspection found no plug-in or SDK message path and no plug-in root component.
- The critical main, CSS, and ODK Power Pages assets remain present; the embedded main module matches the verified production build.
