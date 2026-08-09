# Power Pages Role Membership Investigation - 2026-07-28

## Purpose

Explain why **User & Access** is visible in the Mshirika trial environment but
hidden for Denis/Hailo in CRDB, and define the correction required in CRDB.

## Authoritative Model

Power Pages uses Dataverse Contact records to represent signed-in site users.
Signed-in contacts automatically receive the site's default **Authenticated
Users** web role. Custom/admin authorization requires an additional web role
membership linked to the Contact. Table permissions grant Dataverse access to
web roles, but they do not by themselves assign those roles to contacts.

The TACATDP portal exposes the signed-in user's Power Pages roles through:

```javascript
window.__TACATDP_POWERPAGES__.roles
```

That value is populated from Liquid `user.roles` in:

```text
powerpages/tacatdp-monitoring-tool/.powerpages-site/web-pages/home/Home.webpage.copy.html
```

The SPA shows **User & Access** only when the role list includes:

- `Administrators`
- `Platform Administrator`

Implemented in:

```text
powerpages/webforms-spa/src/powerpages-api/client.ts
```

## Mshirika Findings

Environment:

```text
https://orga3cf4b37.crm4.dynamics.com/
PowerPagesDeveloper-070926-125720
```

Power Pages web roles:

| Role | Role ID | Default role flag |
| --- | --- | --- |
| Authenticated Users | `1bb3051d-e53f-44e0-b226-d6c7050632b0` | `authenticatedusersrole=true` |
| Administrators | `eee16194-79d2-4e30-9fb9-ea55b3b25e3e` | false |
| Anonymous Users | `eb9999dc-9f56-416f-a7e7-375afbf93908` | `anonymoususersrole=true` |

Contacts queried:

| Contact | Contact ID | State |
| --- | --- | --- |
| `john.mduda@mshirikacorp.onmicrosoft.com` | `f1e65863-d37b-f111-ab0e-7c1e523612eb` | Active |
| `j.mduda@hotmail.com` | `f103749b-6c87-f111-ab0e-70a8a57d9610` | Active |

Contact-role relationships:

| Contact | Web role |
| --- | --- |
| `john.mduda@mshirikacorp.onmicrosoft.com` | `Authenticated Users` |
| `john.mduda@mshirikacorp.onmicrosoft.com` | `Administrators` |

No relationship row was returned for the Hotmail contact in the query. The
working Mshirika administrator path is therefore not caused by environment-level
Power Platform permissions alone. It works because John's Power Pages Contact is
explicitly linked to the **Administrators** web role.

Mshirika admin table permissions also reference the administrator role. Example:

- `contact` read permission includes `Administrators`.
- `mp_onboardingrequest` create/read/write permission includes `Administrators`.
- Web API settings for `mp_onboardingrequest` and `mp_accessauditlog` are enabled.

## CRDB Findings

Environment:

```text
https://org5eb0379b.crm4.dynamics.com/
TACATDP-CRDB-Dev
```

Confirmed earlier in CRDB:

| Contact | Contact ID | State |
| --- | --- | --- |
| `Denis.Muroba@crdbbank.co.tz` | `ad95bc35-6580-f111-ab0e-e4fb1ef8c9e5` | Active |
| `Hailo.Kibiki@crdbbank.co.tz` | `fed93471-3081-f111-ab0e-e4fb1ef8c9e5` | Active |

Confirmed earlier in CRDB after upload:

- `Administrators` web role exists.
- `Platform Administrator` web role exists.
- `mp_onboardingrequest` permission grants create/read to both admin roles.
- `mp_accessauditlog` permission grants create/read to both admin roles.
- Web API settings for both tables are enabled.

Current browser evidence for Denis/Hailo:

```javascript
window.__TACATDP_POWERPAGES__.roles
// ['Authenticated Users']
```

This means CRDB authentication is working and the Contact is recognized, but the
Contact is only receiving the automatic default role. The Contact is not linked
to `Administrators` or `Platform Administrator`, so the SPA correctly hides
**User & Access**.

## Required CRDB Correction

Assign both CRDB Contacts to a site administrator web role:

Preferred:

- `Platform Administrator`

Acceptable because the SPA currently also supports it:

- `Administrators`

Contacts:

- `Denis.Muroba@crdbbank.co.tz`
- `Hailo.Kibiki@crdbbank.co.tz`

## UI Correction Path

Use this path when Azure CLI/Dataverse Web API writes are not available:

1. Open CRDB environment in `make.powerapps.com`.
2. Open **Power Pages Management** for the TACATDP site.
3. Go to **Security > Web Roles**.
4. Open **Platform Administrator**.
5. Add existing Contacts:
   - `Denis.Muroba@crdbbank.co.tz`
   - `Hailo.Kibiki@crdbbank.co.tz`
6. Save.
7. Purge/restart the site cache.
8. Ask Denis/Hailo to sign out and sign in again.

Expected browser result:

```javascript
window.__TACATDP_POWERPAGES__.roles
// ['Authenticated Users', 'Platform Administrator']
```

After that, **User & Access** should render.

## Mailbox Requirement for Invitations and Notifications

After the role membership fix, **User & Access** can render, but invitation and
assignment email delivery still depends on a CRDB-approved Dataverse mailbox.

Attempting to approve Denis Muroba's personal mailbox returned the platform
error:

```text
This email address can only be approved by a user with the Global Administrator
or Exchange Administrator role in Office 365 or the Delegated Mailbox Approver
role in Dynamics 365.
```

This confirms that portal/platform administrator access is not sufficient for
mailbox approval.

CRDB should provide and approve a shared sender mailbox for TACATDP, for example:

```text
noreply@crdbbank.co.tz
```

The mailbox must be configured in the CRDB Dataverse environment with:

- Microsoft Exchange Online server profile.
- Outgoing email set to server-side synchronization.
- Email address approved by a Global Administrator, Exchange Administrator, or
  Delegated Mailbox Approver.
- **Test & Enable Mailbox** completed successfully.
- Outgoing email status showing `Success`.

Do not rely on Denis or Hailo personal mailboxes for production email delivery.
The shared mailbox is required for governed Power Pages invitations and existing
user assignment notifications.

## Programmatic Correction Path

When a permitted Dataverse Web API token is available, use the reviewed helper:

```bash
python3 scripts/powerpages-assign-webrole.py \
  --env-file <crdb-env-file> \
  --email Denis.Muroba@crdbbank.co.tz \
  --role "Platform Administrator" \
  --execute

python3 scripts/powerpages-assign-webrole.py \
  --env-file <crdb-env-file> \
  --email Hailo.Kibiki@crdbbank.co.tz \
  --role "Platform Administrator" \
  --execute
```

This helper creates the enhanced-model relationship:

```text
powerpagecomponents(<role-id>)/powerpagecomponent_mspp_webrole_contact/$ref
```

Do not use this path with the Mshirika `.env`; that file currently targets:

```text
https://orga3cf4b37.crm4.dynamics.com/
```

## PAC State Note

PAC can query Mshirika and CRDB after the correct profile is selected, but this
Linux environment intermittently hits the known ExternalTokenManagement token
cache issue after switching between service-principal and user profiles. If PAC
returns:

```text
ExternalTokenManagement Authentication Requested but not configured correctly
```

reauthenticate the affected profile before relying on further live queries.
