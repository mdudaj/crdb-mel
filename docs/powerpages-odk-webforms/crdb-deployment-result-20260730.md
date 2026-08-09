# CRDB Deployment Result - 2026-07-30

## Classification

High-risk CRDB Dataverse and Power Pages deployment.

## Target

- Environment: `TACATDP-CRDB-Dev`
- Dataverse URL: `https://org5eb0379b.crm4.dynamics.com/`
- Power Pages URL: `https://tacatdp.powerappsportals.com/`
- Deployment identity: `dmuroba@CRDBBANK.CO.TZ`

## Result

Deployment completed from this workstation using PAC device-code authentication.

Completed steps:

- Imported the existing no-plugin managed solution baseline and published customizations.
- Exported the current Mshirika managed solution with the latest onboarding, notification settings, and access-management schema.
- Verified the current Mshirika managed export contains `mp_notificationdeliverysetting`, `mp_onboardingrequest`, `mp_formassignment`, workflow components, and no plug-in assembly entries.
- Imported the current Mshirika managed solution into CRDB asynchronously.
- Published CRDB customizations after import.
- Uploaded the latest Power Pages site source to CRDB with `--forceUploadAll`.
- Confirmed CRDB solution list contains `tacatdp_prototype` version `0.2.3.0`.
- Confirmed CRDB Power Pages list contains `TACATDP Monitoring Tool`.
- Confirmed `mp_notificationdeliverysetting` and `mp_onboardingrequest` are queryable in CRDB by FetchXML. Both returned no rows, which confirms table availability but no seeded data.

## Commands Run

```bash
pac auth create --name tacatdp-crdb-denis-20260730 --environment https://org5eb0379b.crm4.dynamics.com/ --deviceCode
pac solution import --path artifacts/deployments/crdb-20260730/TACATDP_Impact_Tracking_Prototype_0_2_3_0_managed_no_plugin.zip --environment https://org5eb0379b.crm4.dynamics.com/ --publish-changes
pac solution import --path artifacts/deployments/crdb-20260730/TACATDP_Impact_Tracking_Prototype_current_mshirika_managed.zip --environment https://org5eb0379b.crm4.dynamics.com/ --publish-changes --async --max-async-wait-time 60
pac pages upload --environment https://org5eb0379b.crm4.dynamics.com/ --path artifacts/deployments/crdb-20260730/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
pac solution list --environment https://org5eb0379b.crm4.dynamics.com/
pac pages list --environment https://org5eb0379b.crm4.dynamics.com/
pac org fetch --environment https://org5eb0379b.crm4.dynamics.com/ --xml "<fetch count='1'><entity name='mp_notificationdeliverysetting'><attribute name='mp_notificationdeliverysettingid'/></entity></fetch>"
pac org fetch --environment https://org5eb0379b.crm4.dynamics.com/ --xml "<fetch count='1'><entity name='mp_onboardingrequest'><attribute name='mp_onboardingrequestid'/></entity></fetch>"
```

## Import Notes

`pac package deploy` was not used because this Linux PAC build reports that Dataverse Package Deployer requires .NET Framework. The managed solution import fallback was used instead.

The first current-solution import attempt had a transport connection reset. Dataverse then reported a concurrent import lock, confirming the first import had started server-side. After waiting, the async import retry completed successfully.

## Remaining Manual Steps

- Purge Power Pages cache and restart the CRDB site.
- Open `https://tacatdp.powerappsportals.com/` in an authenticated CRDB browser session.
- Confirm Home loads the `notification-settings-20260730-001` bundle.
- Confirm Denis and Hailo expose the `Platform Administrator` web role in `window.__TACATDP_POWERPAGES__.roles`.
- Confirm `User & Access` is visible.
- Open `User & Access > Configuration` and save the default manual-code notification delivery setting if no row exists yet.
- Confirm project/form visibility.
- Run create/invite/assign smoke with manual-code fallback.
- Run collect submit/edit and Data tab smoke.

## Known Boundary

The notification delivery settings table exists but has no seeded row. The SPA falls back to manual-code defaults when the row is missing. The first administrator save from the Configuration tab should create the singleton `onboarding-delivery` row if Power Pages table permissions are correct.
