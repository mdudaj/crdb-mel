# Indicator browser seed protocol artifact

Trace: `20260821-145723-2625fa`

Task: add Linux-compatible indicator seed delivery through Power Pages browser Web API and prepare Mshirika deployment.

## Task classification

- Protocol category: frontend.
- Risk: high because the change adds admin-only Power Pages Web API write capability and table permissions.
- Delivery constraint: use PAC and Power Pages; do not use Azure CLI; do not rely on Linux Package Deployer for Dataverse package deployment.

## Requirements note

The implementation must let an approved Platform Administrator seed the first TACATDP indicator definitions and data-source mappings from `schemas/dataverse/indicator-evidence-seed.json`.

The implementation must:

- reuse the existing signed-in Power Pages session;
- keep the route behind the existing Platform Administrator web-role gate;
- validate the seed file before writes;
- write only `mp_IndicatorDefinition` and `mp_DataSourceMapping`;
- use idempotent matching to avoid duplicate definitions and mappings;
- document that Package Deployer remains a Windows-only path for this workstation.

## Product requirements

1. Add a visible admin-only step on `#/baseline-import` for indicator metadata seeding.
2. Show a Material-consistent file picker and action button.
3. Validate the seed JSON on file selection using dry-run semantics.
4. Display counts for indicator definitions and data-source mappings.
5. Execute idempotent upsert only after explicit operator action.
6. Ensure enhanced Power Pages upload package includes required Web API site settings and table permissions.
7. Add deterministic validators so future staging cannot omit the enhanced upload package metadata.

## UX description

The admin import page now includes Step 5, `Seed indicator definitions`.

The UI follows the existing baseline-import pattern:

- eyebrow label identifies the step;
- title states the action;
- helper text explains scope and tables not affected;
- file picker accepts `.json`;
- validation result appears as a success banner;
- run action is disabled until validation succeeds;
- result counts are shown in the same compact count-card style used by baseline import results.

## Accessibility checklist

- The new panel uses semantic section and heading structure.
- The file input remains keyboard accessible.
- Success and error banners use `aria-live="polite"`.
- The button has visible text and an icon marked `aria-hidden`.
- Result counts are grouped under an `aria-label`.
- The route remains protected with a visible denied state for users without the admin role.

## Acceptance criteria

- `schemas/dataverse/indicator-evidence-seed.json` validates before execution.
- The client rejects seed files with wrong project code or broader `writes_only` scope.
- Browser writes are limited to:
  - `/_api/mp_indicatordefinitions`
  - `/_api/mp_datasourcemappings`
- The implementation does not write observations, evidence, indicator results, submissions, or beneficiaries.
- The enhanced upload package contains:
  - `Webapi/mp_indicatordefinition/enabled`
  - `Webapi/mp_indicatordefinition/fields`
  - `Webapi/mp_datasourcemapping/enabled`
  - `Webapi/mp_datasourcemapping/fields`
  - Platform Administrator table permissions for both metadata tables.
- Build and validation commands pass.
- If live upload fails, the exact PAC failure and environment state are recorded.

## Verification summary

Passed:

- `node scripts/validate-indicator-evidence-seed.mjs`
- `python3 -B scripts/validate-indicator-seed-package.py`
- `node scripts/validate-indicator-browser-seed.mjs`
- `node scripts/validate-indicator-evidence-runbook.mjs`
- `npm run build:mshirika-runtime`
- `python3 scripts/stage-powerpages-spa-build.py`
- `node scripts/verify-powerpages-spa-assets.mjs`
- `python3 scripts/validate-powerpages-package-hygiene.py --repair-manifest`
- `npm run test:powerpages-assets`
- `npm run test:material`

Build warning noted:

- Vite reports direct `eval` inside `@getodk/web-forms`; this is existing third-party dependency behavior.
- Vite reports chunk-size warnings; existing known bundle-size issue, not caused by this seed flow.

## Deployment evidence

Mshirika profile check passed before upload:

- PAC profile: `tacatdp-mshirika`
- user: `john.mduda@mshirikacorp.onmicrosoft.com`
- environment: `07b77aa3-c0c0-e513-8b8c-407b83639a45`
- environment name: `PowerPagesDeveloper-070926-125720`

Upload attempts failed before completion:

- `pac pages upload --path powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll`
- `pac pages upload --path powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced`
- `pac paportal upload --path powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll`

Observed PAC error:

```text
Sorry, the app encountered a non-recoverable error and will need to terminate.
Exception Type: System.InvalidOperationException
```

The PAC diagnostic log path was:

```text
/home/jmduda/.config/Code/User/globalStorage/microsoft-isvexptools.powerplatform-vscode/pac/.store/microsoft.powerapps.cli.tool/2.11.2/microsoft.powerapps.cli.tool/2.11.2/tools/net10.0/any/logs/pac-log.txt
```

No successful Mshirika upload was confirmed for this task.

Follow-up deployment on 2026-08-21:

- VS Code-bundled PAC 2.11.2 remained the failing path for `pac pages upload`.
- Existing .NET global PAC 2.10.1 at `/home/jmduda/.dotnet/tools/pac` connected to the same named Mshirika profile when run with token-cache filesystem access.
- PAC 2.10.1 completed:

```bash
source scripts/use-powerplatform-env.sh mshirika >/dev/null
/home/jmduda/.dotnet/tools/pac pages upload \
  --path powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool \
  --modelVersion Enhanced \
  --forceUploadAll
```

Result:

```text
Power Pages website upload succeeded in 110.23 secs.
```

Non-fatal warnings:

- PAC reported many stale `powerpagecomponent` delete failures with `Object reference not set to an instance of an object`.
- PAC reported one update failure for missing `powerpagecomponent` id `ca928def-2b04-4948-bc22-1cb12a0c24a0`.
- The command still exited `0` and reported upload success.

Post-upload verification passed:

- `pac pages list` returned website `fccc0cc6-7f5e-4885-aeb8-2272e68130a3`, `TACATDP Monitoring Tool`.
- `powerpagecomponent` read-back found:
  - `Webapi/mp_indicatordefinition/enabled`
  - `Webapi/mp_indicatordefinition/fields`
  - `Webapi/mp_datasourcemapping/enabled`
  - `Webapi/mp_datasourcemapping/fields`
  - `mp_indicatordefinition Admin Import`
  - `mp_datasourcemapping Admin Import`
- HTTP check to `https://tacatdp.powerappsportals.com/` returned a redirect to Microsoft sign-in, which is expected for the authenticated/private site.

## Artifact readiness

Ready:

- browser seed client method;
- admin Step 5 UI;
- source site settings and table permissions;
- enhanced upload package staging sync;
- validators;
- runbook note.

Blocked:

- Browser execution of Step 5 still requires an authenticated Platform Administrator session in the portal.

Next action:

1. Open `#/baseline-import` as a Platform Administrator.
2. Select `schemas/dataverse/indicator-evidence-seed.json`.
3. Run Step 5 indicator seed.
4. Verify the result shows 5 indicator definitions and 5 data-source mappings.
