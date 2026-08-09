# CRDB Deployment Result - 2026-07-28

## Classification

High-risk deployment to CRDB Dataverse and Power Pages environment.

## Target

- Environment: `TACATDP-CRDB-Dev`
- Dataverse URL: `https://org5eb0379b.crm4.dynamics.com/`
- PAC user: `dmuroba@CRDBBANK.CO.TZ`
- Power Pages site: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`

## Deployment Commands

The preferred Package Deployer command was attempted:

```bash
pac package deploy \
  --package artifacts/deployments/crdb-20260728/Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip \
  --environment https://org5eb0379b.crm4.dynamics.com/
```

Result: blocked on this Linux PAC build because Dataverse Package Deployer requires Windows/.NET Framework.

Fallback managed solution import was used:

```bash
pac solution import \
  --path artifacts/deployments/crdb-20260728/TACATDP_Impact_Tracking_Prototype_0_2_3_0_managed_no_plugin.zip \
  --environment https://org5eb0379b.crm4.dynamics.com/ \
  --publish-changes
```

Result: solution imported successfully and all customizations published.

Power Pages upload was then run:

```bash
pac pages upload \
  --environment https://org5eb0379b.crm4.dynamics.com/ \
  --path powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool \
  --modelVersion Enhanced \
  --forceUploadAll
```

Result: Power Pages website upload succeeded in 49.72 seconds.

## Verification

Commands run:

```bash
pac env who
pac solution list --environment https://org5eb0379b.crm4.dynamics.com/
pac pages list --environment https://org5eb0379b.crm4.dynamics.com/ --verbose
curl -I -L --max-time 20 https://tacatdp.powerappsportals.com/
```

Observed:

- `pac env who` connected as `dmuroba@CRDBBANK.CO.TZ` to `TACATDP-CRDB-Dev`.
- `tacatdp_prototype` is present as managed version `0.2.3.0`.
- `TACATDP Monitoring Tool` is listed in CRDB.
- The public portal responds and redirects to Microsoft sign-in as expected for the protected site.

## Required Manual Post-Deployment Checks

- Purge or restart Power Pages cache before browser review.
- Confirm the portal loads the `production-ux-cleanup-20260728-001` bundle after sign-in.
- Open `User & Access > Add user` and confirm the four-step flow: `User`, `Role`, `Access`, `Review`.
- Queue a test onboarding request and confirm the `OnboardingRequest` row is created.
- Confirm the CRDB server-side processor handles contact, assignment, and invitation delivery.
- Confirm assigned users see only assigned project/form access.

## Boundary

The Dataverse Package Deployer wrapper is still valid for Windows-based CRDB administration, but this Linux workstation cannot run Dataverse Package Deployer. Direct managed solution import plus PAC Power Pages upload is the working Linux deployment path.
