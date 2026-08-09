# CRDB Admin Role Permission Fix - 2026-07-28

## Purpose

Enable the implemented User & Access administrator path in CRDB after deployment.

## Finding

CRDB has active Power Pages contacts for:

- `Denis.Muroba@crdbbank.co.tz`
- `Hailo.Kibiki@crdbbank.co.tz`

CRDB initially exposed Power Pages web roles:

- `Administrators`
- `Authenticated Users`
- `Anonymous Users`

The SPA accepts both `Administrators` and `Platform Administrator` as access-admin roles, but the Power Pages package previously carried only `Administrators`. The add-user workflow also requires Power Pages Web API settings and table permissions for the onboarding queue.

## Package Changes

Updated both source and upload Power Pages packages to include:

- `Platform Administrator` web role alias.
- `Platform Administrator` linked to site administrative access and page change rule.
- `Platform Administrator` linked to admin contact read table permission.
- Admin create/read table permission for `mp_onboardingrequest`.
- Admin create/read table permission for `mp_accessauditlog`.
- `Webapi/mp_onboardingrequest/enabled=true`.
- `Webapi/mp_onboardingrequest/fields` for the queue payload.
- `Webapi/mp_accessauditlog/enabled=true`.
- `Webapi/mp_accessauditlog/fields` for access audit payloads.

## Verification

Local checks passed:

```bash
python3 scripts/validate-webforms-spa-foundation.py
python3 scripts/validate-access-mshirika-activation.py
git diff --check
```

## Deployment Status

Uploaded to CRDB with PAC profile `tacatdp-crdb-adminfix2` after Denis Muroba completed device-code authentication.

Upload command:

```bash
pac pages upload \
  --environment "https://org5eb0379b.crm4.dynamics.com/" \
  --path "/home/jmduda/KodeX.2026/tacatdp/powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool" \
  --modelVersion Enhanced \
  --forceUploadAll
```

PAC reported:

```text
Power Pages website upload succeeded
```

CRDB verification confirmed:

- `Administrators` web role exists.
- `Platform Administrator` web role exists.
- `mp_onboardingrequest` table permission exists, is active, and grants create/read to `Administrators` and `Platform Administrator`.
- `mp_accessauditlog` table permission exists, is active, and grants create/read to `Administrators` and `Platform Administrator`.
- `contact` admin read table permission grants read to `Administrators` and `Platform Administrator`.
- `Webapi/mp_onboardingrequest/enabled=true`.
- `Webapi/mp_onboardingrequest/fields` contains the onboarding queue payload fields.
- `Webapi/mp_accessauditlog/enabled=true`.
- `Webapi/mp_accessauditlog/fields` contains the access audit payload fields.
- Denis Muroba and Hailo Kibiki Power Pages contacts exist and are active in CRDB.

The enhanced Power Pages component content is the source of truth for these role references. The raw `powerpagecomponent_powerpagecomponent` intersect table still only exposed older authenticated-user relationships in PAC fetch output, but the uploaded component content includes the administrator-role arrays for the new permissions.

## Manual CRDB Verification

After upload:

1. Purge/restart the Power Pages site cache.
2. Ask Denis/Hailo to sign out and sign in again.
3. In the browser console, confirm:

```javascript
window.__TACATDP_POWERPAGES__
```

Expected:

- `isAuthenticated` is `true`.
- `roles` includes `Administrators` or `Platform Administrator`.

Then retest User & Access Management:

- Add User should be visible to the administrator.
- Submit should queue an `mp_onboardingrequest` record instead of returning `403`.
- The success state should show the queued request id.

## Portal Role Assignment Finding

If Denis/Hailo can sign in but **User & Access** remains hidden, the issue is
not the Dataverse security role or the Power Pages table permission record. The
SPA reads Power Pages web roles from:

```javascript
window.__TACATDP_POWERPAGES__.roles
```

That value is populated by Power Pages Liquid from the signed-in Contact's site
web role memberships. CRDB PAC verification found active Contacts for Denis and
Hailo, but no readable contact-to-web-role relationship rows for them.

Azure CLI token-based Dataverse writes are not available for the current CRDB
operators, so the approved non-code path is:

1. Open the CRDB site in Power Pages/Power Apps maker tools.
2. Open the **Power Pages Management** app for the site.
3. Go to **Security > Web Roles**.
4. Open **Platform Administrator**.
5. Add existing Contacts:
   - `Denis.Muroba@crdbbank.co.tz`
   - `Hailo.Kibiki@crdbbank.co.tz`
6. Save.
7. Purge/restart the site cache.
8. Ask both users to sign out and sign in again.

Expected browser verification:

```javascript
window.__TACATDP_POWERPAGES__.roles
```

includes `Platform Administrator`.

## Shared Mailbox Requirement

The User & Access UI can be made visible through Power Pages web role membership,
but email delivery for invitations and assignment notifications requires an
approved Dataverse mailbox in the CRDB environment.

An attempt to approve Denis Muroba's personal mailbox returned:

```text
This email address can only be approved by a user with the Global Administrator
or Exchange Administrator role in Office 365 or the Delegated Mailbox Approver
role in Dynamics 365.
```

CRDB should create or nominate a shared sender mailbox, for example:

```text
noreply@crdbbank.co.tz
```

Required mailbox setup:

- The mailbox exists in CRDB Microsoft 365 / Exchange Online.
- The mailbox is available in the CRDB Dataverse environment.
- Server profile is **Microsoft Exchange Online**.
- Outgoing email uses **Server-Side Synchronization**.
- Email is approved by a Global Administrator, Exchange Administrator, or
  Delegated Mailbox Approver.
- **Test & Enable Mailbox** succeeds.
- Outgoing email status shows `Success`.

Do not use Denis or Hailo personal mailboxes as the production sender.
