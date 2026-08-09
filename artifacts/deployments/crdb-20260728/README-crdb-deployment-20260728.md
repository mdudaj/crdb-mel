# CRDB Deployment Package - 2026-07-28

## Classification

High-risk deployment packaging for a banking production environment. This package prepares a CRDB update from the Mshirika-validated TACATDP / Impact Monitoring build.

## Package Contents

Release folder:

`artifacts/deployments/crdb-20260728/`

Files:

- `Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip`
- `TACATDP_Impact_Tracking_Prototype_0_2_3_0_managed_no_plugin.zip`
- `tacatdp-monitoring-tool-powerpages-20260728.zip`

Checksums:

```text
f52c9e8ddb7909efbfd3399a487a9882e1ca532ae483852c4d2e067c29132667  Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip
99e5e030d7c7257d8415aa90d93c4068e44019c198bcc19bdc472523580e4a04  TACATDP_Impact_Tracking_Prototype_0_2_3_0_managed_no_plugin.zip
ad8429242492b2ef43066cbfe0e6bb649f9a2114702c9ab0f53c91b4cf162523  tacatdp-monitoring-tool-powerpages-20260728.zip
```

## Deployment Order

1. Import or deploy the Dataverse solution package first.
2. Upload the Power Pages site package second.
3. Publish customizations.
4. Clear Power Pages server-side cache or restart the site.
5. Open the portal and complete smoke testing.

## Dataverse Package

Preferred command:

```powershell
pac package deploy `
  --package "C:\path\Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip" `
  --environment "https://org5eb0379b.crm4.dynamics.com/"
```

Fallback managed solution import:

```powershell
pac solution import `
  --path "C:\path\TACATDP_Impact_Tracking_Prototype_0_2_3_0_managed_no_plugin.zip" `
  --environment "https://org5eb0379b.crm4.dynamics.com/" `
  --publish-changes
```

The solution unique name is `tacatdp_prototype`, version `0.2.3.0`, managed, and intentionally excludes plug-in assemblies.

## Power Pages Package

Unzip `tacatdp-monitoring-tool-powerpages-20260728.zip`; it contains the upload folder `tacatdp-monitoring-tool`.

Upload command:

```powershell
pac pages upload `
  --environment "https://org5eb0379b.crm4.dynamics.com/" `
  --path "C:\path\tacatdp-monitoring-tool" `
  --modelVersion Enhanced `
  --forceUploadAll
```

This package carries the reviewed User & Access UX cleanup. The Home fragments reference:

- `index-0EKo1gv8.mjs`
- `index-CfUxfRBd.css`
- cache key `production-ux-cleanup-20260728-001`

## Verification

Local package verification passed:

```bash
npm --prefix powerpages/webforms-spa run typecheck
npm --prefix powerpages/webforms-spa run build:mshirika-access
python3 scripts/validate-access-create-invite-assign-ux.py
python3 scripts/validate-access-mshirika-activation.py
python3 scripts/validate-webforms-spa-foundation.py
python3 scripts/validate-deployment-package.py deployment/Tacatdp.DeploymentPackage/bin/Release/Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip
node --check powerpages/webforms-spa/dist/assets/index-0EKo1gv8.mjs
git diff --check
```

Hosted Mshirika review passed before CRDB packaging. PAC upload to Mshirika completed successfully, and the protected portal responded with Microsoft sign-in as expected.

## CRDB Smoke Tests

- Confirm `tacatdp_prototype` is version `0.2.3.0`.
- Confirm Power Pages Home loads the `production-ux-cleanup-20260728-001` asset references after cache purge.
- Sign in as a CRDB administrator and open `User & Access`.
- Confirm the Add User flow has four steps: `User`, `Role`, `Access`, `Review`.
- Queue a new user onboarding request and confirm a Dataverse `OnboardingRequest` row is created.
- Confirm the CRDB onboarding processor creates or reuses the contact, writes assignments, and sends the invitation email through the configured CRDB mailbox path.
- Sign in as an assigned user and confirm only assigned project/form access is visible.

## Known Boundary

The managed solution export does not carry the newest Power Pages asset filenames from the PAC site upload. CRDB deployment therefore requires both the Dataverse package and the separate Power Pages upload package.
