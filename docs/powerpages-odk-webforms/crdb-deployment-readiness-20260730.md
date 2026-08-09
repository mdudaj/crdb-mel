# TACATDP / Impact Monitoring CRDB Deployment Package - 2026-07-30

## Classification

High-risk production update package for CRDB Power Pages and Dataverse. This package is prepared from the Mshirika-tested build and must be applied by an account with the required CRDB Power Platform permissions.

## Package Contents

- `Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip` - Package Deployer package with the managed no-plugin Dataverse solution and seed content from the earlier CRDB baseline.
- `TACATDP_Impact_Tracking_Prototype_0_2_3_0_managed_no_plugin.zip` - fallback managed solution import package. It intentionally excludes C# plug-in assemblies.
- `tacatdp-monitoring-tool/` - latest Power Pages upload source. Home references `notification-settings-20260730-001` assets.
- `schemas/dataverse/onboarding-request-schema.json` - onboarding request queue schema.
- `schemas/dataverse/notification-delivery-settings-schema.json` - notification/mailbox configuration schema.
- `scripts/` - deployment/configuration/validation scripts for schema, Power Pages Web API permissions, and onboarding processor configuration.
- `docs/` - delivery notes for notification settings, manual invitation fallback, onboarding result UX, and export role scope.

## Required Privileges

The CRDB deployment user needs permission to import managed solutions and create/update Dataverse metadata. At minimum, this includes table/entity creation privileges such as `prvCreateEntity`, plus privileges needed to create/update columns, choices, alternate keys, web roles/table permissions/site settings, and cloud-flow definitions/connections.

If the C# plug-in assembly privilege `prvCreatePluginAssembly` is not available, use the no-plugin solution package included here and keep automatic plug-in projection refresh deferred.

## Deployment Order

1. Import `Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip` with Package Deployer, or import `TACATDP_Impact_Tracking_Prototype_0_2_3_0_managed_no_plugin.zip` as a fallback.
2. Deploy or verify the onboarding queue schema.
3. Deploy or verify the notification delivery settings schema.
4. Configure Power Pages Web API site settings and table permissions, including access-write permissions.
5. Configure the onboarding queue processor cloud flow to read `mp_notificationdeliverysettings`.
6. Upload the latest Power Pages site folder.
7. Publish customizations, purge Power Pages cache, and restart the site.
8. Run the post-deploy smoke checklist below.

## Commands

Set CRDB environment URL:

```powershell
$EnvUrl = "https://org5eb0379b.crm4.dynamics.com/"
```

Preferred baseline package deploy:

```powershell
pac package deploy `
  --package "C:\path\Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip" `
  --environment $EnvUrl
```

Fallback managed solution import:

```powershell
pac solution import `
  --path "C:\path\TACATDP_Impact_Tracking_Prototype_0_2_3_0_managed_no_plugin.zip" `
  --environment $EnvUrl `
  --publish-changes
```

Schema updates:

```powershell
python scripts/dataverse-schema-deploy.py --schema-file schemas/dataverse/onboarding-request-schema.json --execute
python scripts/dataverse-schema-deploy.py --schema-file schemas/dataverse/notification-delivery-settings-schema.json --execute
```

Power Pages Web API/table permissions:

```powershell
python scripts/powerpages-configure-webapi.py --include-access-writes --execute
```

Onboarding processor update:

```powershell
python scripts/powerautomate-configure-onboarding-queue-processor.py --invitation-delivery-mode manual-code --execute
```

Power Pages upload:

```powershell
pac pages upload `
  --environment $EnvUrl `
  --path "C:\path\tacatdp-monitoring-tool" `
  --modelVersion Enhanced `
  --forceUploadAll
```

## Mailbox Readiness

The portal now has `User & Access > Configuration > Onboarding delivery`.

Default CRDB-safe state:

- Delivery mode: `Manual invitation code`.
- Mailbox readiness: `Not configured` or `Pending admin setup`.

Switch to mailbox email delivery only after CRDB has:

- created or identified a shared/service mailbox,
- licensed/enabled it for Exchange Online where required,
- approved the mailbox in Dataverse,
- completed Dataverse mailbox `Test & Enable`,
- configured the native Power Pages Send Invitation workflow/connection.

The portal must not approve, test, license, or create Exchange/Dataverse mailboxes. It only records readiness and lets the server-side processor decide whether email delivery is safe.

## Manual Invitation Fallback

If no mailbox is ready, admins can still create/reuse the contact and queue onboarding. The processor creates a native Power Pages invitation and writes the invitation code/redeem URL/expiry back to the request. The admin can then provide the code/link verbally or through an approved CRDB communication channel.

If the invitation expires, the admin should create a new onboarding request so the processor generates a fresh single-use invitation.

## Post-Deploy Smoke Checklist

- Confirm Power Pages Home references `notification-settings-20260730-001` assets after cache purge.
- Sign in as Denis and Hailo and confirm `window.__TACATDP_POWERPAGES__.roles` includes the expected administrator web role, not only `Authenticated Users`.
- Confirm `User & Access` is visible to platform administrators.
- Open `User & Access > Configuration` and confirm the notification delivery settings card loads from Dataverse or shows the default manual-code configuration.
- Confirm the TACATDP/Impact Monitoring project and assigned form are visible.
- Open Collect, confirm the form renders, submit a controlled test, then edit it.
- Confirm the Data tab loads without `$skip`, `$count`, or singular/plural Web API errors.
- Confirm collectors only see/export their own records while platform administrators can export all records.
- Queue a new-user onboarding request and confirm an `mp_onboardingrequest` row is created.
- Confirm the processor creates/reuses the contact, creates a native invitation, writes assignment rows after audit succeeds, and records either manual-code or email result details.

## Local Verification Completed

- `python3 scripts/validate-notification-delivery-settings.py`
- `python3 scripts/validate-access-create-invite-assign-ux.py`
- `python3 scripts/validate-onboarding-queue-processor-plan.py`
- `node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-DM97LP7i.mjs`
- `git diff --check`

Mshirika live deployment evidence: Power Pages upload succeeded and the notification-settings smoke request `ONB-NOTIFY-SMOKE-20260730040952` completed with manual-code fallback and invitation details present.

## Known Boundary

The included managed solution remains the no-plugin `0.2.3.0` baseline. Newer schema/configuration changes are included as explicit scripts and schemas in this package until a fresh CRDB-exported managed solution is produced after the required privileges are available.
