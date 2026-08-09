# CRDB First Delivery Update - 2026-08-04

## Scope

Prepare the first CRDB environment update before the Friday MEL-platform expansion work.

This delivery keeps the visible product lean and operational:

- Dashboard
- Projects
- Reporting
- User & Access
- System Activity
- Configuration for invitation delivery settings

Future MEL modules remain navigable as scoped roadmap surfaces only. TACATDP remains the active project supported by this first delivery.

## Package

Power Pages enhanced-model package:

```bash
powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool
```

Active Home cache marker:

```text
crdb-first-delivery-20260804-015
```

Active stable app assets:

- `web-files/index-BQ9y-_bQ.mjs`
- `web-files/index-CUcM3xYd.mjs`
- `web-files/index-CpD24Gld.css`
- `web-files/index-BoV_sUI5.css`

## Pre-Update Checks

1. Confirm latest managed Dataverse solution is already imported in CRDB.
2. Confirm CRDB target environment URL:

```text
https://org5eb0379b.crm4.dynamics.com/
```

3. Confirm the site is the CRDB Power Pages site:

```text
https://tacatdp-crdb.powerappsportals.com/
```

4. Confirm Denis Muroba or another approved CRDB admin is signed in to PAC.
5. Confirm non-admin testers are granted private-site visibility before invitation redemption.

## Upload Command

Use one line in PowerShell or Bash:

```bash
pac pages upload --environment "https://org5eb0379b.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
```

If PAC prints `--modelVersion: command not found`, the command was split across lines incorrectly. Re-run the one-line command above.

## Post-Update Steps

1. Purge Power Pages cache.
2. Restart the site.
3. Hard refresh the browser.
4. Confirm Home references `crdb-first-delivery-20260804-015`.
5. Sign in as Denis or Hailo and confirm:
   - Dashboard loads without blank page.
   - Side navigation shows the current lean shell.
   - Dashboard has no large empty bottom gap.
   - Projects opens TACATDP project/form.
   - Collect opens the form runtime.
   - Reporting/Data opens without `$skip` or `$count` errors.
   - User & Access is visible for Platform Administrator users.
   - User & Access configuration no longer shows delivery/update gate wording.
6. For a non-admin test user:
   - Grant private-site visibility in Power Pages Studio.
   - Create/recreate the invitation from User & Access.
   - Copy the manual redeem link/code if mailbox delivery is not configured.
   - After redemption, verify Contact, external identity, web role, and form assignment before marking activation complete.

## Known Gates

- Mailbox email delivery is optional for first delivery. Manual invitation code fallback is the supported path until CRDB provides and enables a shared sender mailbox.
- Private Power Pages sites require site visibility access before a non-admin invitee can redeem and sign in.
- Delivery/update gates must remain in documentation and System Activity/Configuration diagnostics only; they must not appear as normal operational page content.
- The ODK Web Forms runtime still emits upstream build warnings for direct `eval` and large chunks. These warnings are known and not introduced by this delivery.

## Verification Run Locally

```bash
cd powerpages/webforms-spa
npm run typecheck
npm run build:mshirika-runtime
cd ../..
python3 scripts/validate-webforms-spa-foundation.py
python3 scripts/validate-access-crdb-update-readiness.py
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-BQ9y-_bQ.mjs
```

## Rollback

Before upload, download the current CRDB site package to a timestamped folder:

```bash
pac pages download --environment "https://org5eb0379b.crm4.dynamics.com/" --webSiteId <crdb-website-id> --path /tmp/tacatdp-crdb-backup-YYYYMMDD-HHMM --overwrite --modelVersion Enhanced
```

If the update fails after upload, re-upload the backup package, purge cache, restart the site, and retest login.
