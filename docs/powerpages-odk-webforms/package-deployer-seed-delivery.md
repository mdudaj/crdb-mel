# TACATDP Package Deployer Delivery

Date: 2026-07-15

## Governed References

- Microsoft Package Deployer: <https://learn.microsoft.com/power-platform/alm/package-deployer-tool>
- PAC package commands: <https://learn.microsoft.com/power-platform/developer/cli/reference/package>
- Dataverse file block API: <https://learn.microsoft.com/power-apps/developer/data-platform/file-column-data>
- Managed solution release: `docs/powerpages-odk-webforms/managed-solution-update-20260715.md`

## Build

Inspect the managed solution and XForm hashes before building. Then run:

```bash
deployment/Tacatdp.DeploymentPackage/build-package.sh \
  /path/to/TACATDP_Impact_Tracking_Prototype_0_2_3_0_managed_no_plugin.zip \
  artifacts/xforms/tacatdp_impact_evaluation-20260714000200000.xml
```

Validate the generated package:

```bash
python3 scripts/validate-deployment-package.py \
  deployment/Tacatdp.DeploymentPackage/bin/Release/Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip
```

## Deploy

Deployment is an explicit environment write and requires approval. On the CRDB Windows PC:

```powershell
pac auth select --name tacatdp-crdb
pac package show --package "C:\path\Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip"
pac package deploy `
  --package "C:\path\Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip" `
  --environment https://org5eb0379b.crm4.dynamics.com `
  --logConsole `
  --verbose
```

Do not run `pac data import` for this release.

## Verification

1. Confirm `tacatdp_prototype` remains managed at version `0.2.3.0`.
2. Confirm the four reporting tables have Web API enabled/fields site settings and Authenticated Users table permissions. A signed-in GET to `/_api/mp_submissionreportrows?$top=1` must not return `9004010C`.
3. Confirm Project ID `1bb217ce-b07b-f111-ab0e-7c1e523612eb` exists.
4. Confirm Form ID `896d52d5-b07b-f111-ab0e-7c1e523612eb` references that project.
5. Confirm FormVersion ID `0e024e5c-607f-f111-ab0e-7ced8d41fa2d` references that form and version `20260714000200000`.
6. Confirm FormAttachment ID `11024e5c-607f-f111-ab0e-7ced8d41fa2d` has a non-null `mp_file`.
7. Confirm the three FormAssignments are active and reference the published form version: `5f36a0d7-6957-4508-9201-af99f1556d26` for Denis, `fd1f0397-b827-429d-90de-77434df37a49` for `Hailo.Kibiki@crdbbank.co.tz`, and `b0266afc-0677-4992-9509-1e757ab0a759` for `hkibiki@crdbbank.co.tz`.
8. Have Hailo sign in once, confirm the resulting Power Pages contact email matches one seeded identity, restart the site, purge cache, and confirm the project/form loads.
9. Deploy the same package a second time in non-production verification and confirm no duplicate rows.

## Failure Handling

Retain the Package Deployer log. Do not uninstall the managed solution or delete data. Correct the package under the same source lineage, increment the package or solution version as appropriate, validate in a non-production environment, and redeploy.
