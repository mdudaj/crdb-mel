# User Activation Diagnostics CRDB Deployment - 2026-07-31

## Scope

Deployed the read-only User Activation Diagnostics slice to the CRDB Power Pages environment so Platform Administrators can distinguish contact, invitation, redemption, external identity, web role, and assignment state before issuing the next invite.

## Target

- Dataverse URL: `https://org5eb0379b.crm4.dynamics.com/`
- Power Pages website: `TACATDP Monitoring Tool`
- Website ID: `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`
- PAC identity: `dmuroba@CRDBBANK.CO.TZ`

## Delivered

- Uploaded the latest SPA package with entry bundle `index-DBgUXmD3.mjs` and cache key `activation-diagnostics-20260731-001`.
- Added read-only admin Web API exposure for `adx_invitation`.
- Added read-only admin Web API exposure for `adx_externalidentity`.
- Extended `contact` Web API fields to include Power Pages identity flags.
- Updated both duplicate CRDB `Webapi/contact/fields` site settings to the same extended field list to avoid stale field resolution.

## Verification

Commands passed locally before upload:

```bash
python3 scripts/validate-access-activation-diagnostics.py
python3 scripts/validate-webforms-spa-foundation.py
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-DBgUXmD3.mjs
```

CRDB upload command:

```bash
pac pages upload --environment https://org5eb0379b.crm4.dynamics.com/ --path powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
```

Result:

- First upload succeeded in `102.10 secs`.
- Second upload, used to update the stale duplicate contact field setting, succeeded in `85.71 secs`.

Read-back checks confirmed:

- `Webapi/adx_invitation/enabled = true`
- `Webapi/adx_externalidentity/enabled = true`
- `Webapi/adx_invitation/fields = adx_invitationid,adx_name,adx_expirydate,adx_invitecontact,statecode,statuscode,createdon,modifiedon`
- `Webapi/adx_externalidentity/fields = adx_externalidentityid,adx_username,adx_contactid,createdon`
- Both CRDB `Webapi/contact/fields` records include `adx_identity_username`, `adx_identity_logonenabled`, and `adx_identity_emailaddress1confirmed`.

## Post-Deployment Step

Purge Power Pages cache and restart the CRDB site, then open `User & Access > Activation` as Denis or Hailo. New users must remain pending until the diagnostics view shows that a Power Pages external identity exists.
