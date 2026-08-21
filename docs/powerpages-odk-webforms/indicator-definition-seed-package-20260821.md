# Indicator definition seed package

Date: 2026-08-21

Status: packaged and validated; live Mshirika execution blocked by Linux PAC Package Deployer limitation.

## Scope

This package is intentionally narrow. It seeds only:

- `mp_IndicatorDefinition`
- `mp_DataSourceMapping`

It does not seed:

- `mp_Observation`
- `mp_Evidence`
- `mp_IndicatorResult`
- baseline beneficiary rows
- form rows
- Power Pages site settings
- Power Pages table permissions

## Seeded indicators

The seed file is `schemas/dataverse/indicator-evidence-seed.json`.

First-pass TACATDP indicators:

- `TAC-BEN-001` — Beneficiary profiles imported
- `TAC-FIN-001` — Reported baseline loan amount
- `TAC-REG-001` — Regions represented in baseline
- `TAC-TEC-001` — Climate-smart technologies reported
- `TAC-TRN-001` — Training participation reported

Each indicator includes at least one `mp_DataSourceMapping` row so formulas are reviewable metadata rather than hidden dashboard code.

## Package artifact

Project:

```bash
deployment/Tacatdp.IndicatorSeedPackage/
```

Built package:

```bash
deployment/Tacatdp.IndicatorSeedPackage/bin/Release/Tacatdp.IndicatorSeedPackage.1.0.0.pdpkg.zip
```

## Verification run

Passed:

```bash
node scripts/validate-indicator-evidence-seed.mjs
python3 -B scripts/validate-indicator-seed-package.py
dotnet publish deployment/Tacatdp.IndicatorSeedPackage/Tacatdp.IndicatorSeedPackage.csproj -c Release
```

Build warning:

```text
No solutions are specified for this package.
```

This package intentionally contains no solution import because the approved task is data seed only.

## Live deployment attempt

Target:

- PAC profile: `tacatdp-mshirika`
- User: `john.mduda@mshirikacorp.onmicrosoft.com`
- Environment: `PowerPagesDeveloper-070926-125720`
- URL: `https://orga3cf4b37.crm4.dynamics.com/`

Command attempted:

```bash
source scripts/use-powerplatform-env.sh mshirika
pac auth select --name tacatdp-mshirika
pac package deploy \
  --package deployment/Tacatdp.IndicatorSeedPackage/bin/Release/Tacatdp.IndicatorSeedPackage.1.0.0.pdpkg.zip \
  --environment https://orga3cf4b37.crm4.dynamics.com/ \
  --logConsole \
  --verbose
```

Result:

```text
'pac package deploy --package-type dataverse' requires .NET Framework and is not available on this build.
Use the Windows version of pac.exe, or pass '--package-type erp' to deploy a Finance and Operations package.
```

No live Dataverse seed writes were performed by this package deployment attempt.

## Correct non-Azure execution path

Run the same package from Windows `pac.exe`, using the named Mshirika profile:

```powershell
pac auth select --name tacatdp-mshirika
pac package deploy `
  --package "C:\path\Tacatdp.IndicatorSeedPackage.1.0.0.pdpkg.zip" `
  --environment https://orga3cf4b37.crm4.dynamics.com/ `
  --logConsole `
  --verbose
```

This uses PAC authentication, not Azure CLI.

## Alternative execution path

`scripts/seed-indicator-evidence.py` can execute the same seed through Dataverse Web API, but it requires a Dataverse bearer token path:

- `POWER_PLATFORM_ACCESS_TOKEN_COMMAND`, or
- approved client credentials/service principal, or
- Azure CLI login.

This path was not used because the current decision is PAC-only.

## Next action

Use Windows `pac.exe package deploy` for the scoped seed package, then verify read-back counts for:

- five `mp_IndicatorDefinition` rows under project `TACATDP`;
- five `mp_DataSourceMapping` rows linked to those definitions.

Do not switch the dashboard to `mp_IndicatorResult` until a calculation job writes governed result rows.
