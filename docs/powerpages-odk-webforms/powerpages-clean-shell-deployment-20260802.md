# Power Pages Clean Shell Deployment Note - 2026-08-02

## Context

The Mshirika review deployment of the SFU/MEL shell initially showed the old Power Pages website header, footer, and floating bot button around the SPA. That chrome is not part of the managed shell and should not appear on the Home SPA route.

## Root Cause

The generated Power Pages upload package had:

- `website.yml`: `adx_defaultbotconsumerid` set to the Power Virtual Agents bot consumer
- visible header/footer web templates rendering CRDB/Impact Monitoring chrome outside the managed Vue shell

The first attempted fix set `adx_usewebsiteheaderandfooter: false`, which removed the visual chrome but also removed the Power Pages anti-forgery token provider used by `window.shell.getTokenDeferred()`. That broke Dataverse Web API calls with `Power Pages anti-forgery token provider is not available.`

## Required Package Settings

Before uploading the Home SPA package to Mshirika or CRDB, keep Power Pages header/footer services enabled so the anti-forgery token provider remains available:

```yaml
# page-templates/Monitoring-Tool-SPA.pagetemplate.yml
adx_usewebsiteheaderandfooter: true
```

Then make the Header/Footer web templates visually silent for the SPA host. The managed Vue shell owns navigation, identity, and footer UI.

Also remove the following line from `website.yml`:

```yaml
adx_defaultbotconsumerid: <guid>
```

Do not disable header/footer globally for other non-SPA pages unless those pages are intentionally moved into the managed shell.

## Mshirika Deployment Result

After correcting the generated package, Mshirika Power Pages upload succeeded:

```bash
pac pages upload --environment https://orga3cf4b37.crm4.dynamics.com/ --path powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
```

Initial visual-chrome removal upload result: `Power Pages website upload succeeded in 125.03 secs.`

Corrected token-preserving upload result: `Power Pages website upload succeeded in 124.76 secs.`

PAC emitted known stale `powerpagecomponent ... Does Not Exist` warnings, but completed successfully.

## CRDB Next Step

When CRDB authentication is available, recreate the Denis PAC auth profile and upload the same corrected package:

```bash
pac auth create --name crdb-20260803 --environment https://org5eb0379b.crm4.dynamics.com/ --deviceCode
pac pages upload --environment https://org5eb0379b.crm4.dynamics.com/ --path powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
```

After upload, purge cache/restart the site and confirm:

- the old website header, footer, and bot are not visible around the SPA;
- the dashboard no longer reports `Power Pages anti-forgery token provider is not available`;
- assignments/projects load through the Dataverse Web API.

## Blank Page Recovery - 2026-08-03

A hard refresh rendered a blank page after the token-preserving shell cleanup. The Home page copy was still a full Vite document (`<!doctype html>`, `<html>`, `<head>`, `<body>`) nested inside the Power Pages page shell. With Power Pages header/footer services enabled, the Home copy must be a fragment only.

Required packaging rule:

- keep only the Power Pages/Liquid session script, asset links/scripts, and `<div id="app"></div>` in the Home page copy;
- do not include `<!doctype html>`, `<html>`, `<head>`, `<title>`, or `<body>` in the Power Pages page copy;
- keep `adx_usewebsiteheaderandfooter: true` so `window.shell.getTokenDeferred()` remains available;
- keep visible Header/Footer templates silent for the SPA host.

Mshirika recovery upload used cache marker `mel-shell-20260803-001` and succeeded:

```text
Power Pages website upload succeeded in 122.26 secs.
```

After purge/restart, verify the page is not blank, the Power Pages visual header/footer/bot are hidden, and Dataverse Web API calls no longer report a missing anti-forgery token.
