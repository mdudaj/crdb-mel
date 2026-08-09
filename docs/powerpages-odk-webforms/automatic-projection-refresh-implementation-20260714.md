# Automatic Projection Refresh Local Implementation

Date: 2026-07-15
Environment write: signed assembly and plug-in type registered in development; event step not registered

## Delivered

- PAC-generated `net462` plug-in project under `dataverse/Tacatdp.ReportingProjection.Plugin/`.
- Stateless pure projection core plus Dataverse adapter for latest-version guarding, sequential upsert, answer-before-repeat reconciliation, Ready/Stale/Failed states, convergence, sanitized tracing, and bounded async retry.
- Exact Microsoft package versions and `packages.lock.json`.
- Non-executing registration contract for `tacatdp_prototype` with Create/PostOperation/asynchronous and an instance-id-only post image.
- Shared synthetic fixture and package-free .NET validator.
- Full normalized Python/C# parity validator.
- Python repair-path stale-child reconciliation.
- Portal submission metadata now includes normalized XForm repeat paths, which makes singleton and nested repeat detection deterministic.
- Strong-name signing required by the target Dataverse environment.
- Dry-run-first `scripts/dataverse-register-projection-plugin.py` with development-target, solution, execution-user, deployment-principal, and required-role guards.
- Signed assembly and plug-in type registered in the current development `tacatdp_prototype` solution.

## Package

Local generated package:

`dataverse/Tacatdp.ReportingProjection.Plugin/bin/Release/Tacatdp.ReportingProjection.Plugin.1.0.0.nupkg`

The generated `bin/` output is ignored and is not a source artifact. Rebuild it from the locked project before registration.

## Verification

```bash
dotnet restore dataverse/Tacatdp.ReportingProjection.Plugin/Tacatdp.ReportingProjection.Plugin.csproj --locked-mode
dotnet build dataverse/Tacatdp.ReportingProjection.Plugin/Tacatdp.ReportingProjection.Plugin.csproj --configuration Release --no-restore
dotnet build tests/Tacatdp.ReportingProjection.Plugin.Tests/Tacatdp.ReportingProjection.Plugin.Tests.csproj --configuration Release
dotnet tests/Tacatdp.ReportingProjection.Plugin.Tests/bin/Release/net10.0/Tacatdp.ReportingProjection.Plugin.Tests.dll tests/fixtures/reporting-projection/root-nested-repeat.json
python3 scripts/validate-reporting-projection-parity.py
python3 scripts/validate-reporting-projection-builder.py
python3 scripts/validate-reporting-projection-plugin.py
python3 scripts/validate-webforms-spa-foundation.py
cd powerpages/webforms-spa && npm run build
```

## Remaining Gates

- Provision a dedicated application user and reviewed `TACATDP Projection Processor` role; do not reuse the System Administrator deployment principal or Microsoft-managed portal identities.
- Register the documented step and image with the dedicated user's Dataverse system-user ID, verify solution inclusion, then export/unpack for review.
- Run submit/edit, duplicate/out-of-order, stale-child, malformed synthetic payload, retry/System Job, latency, and portal visibility checks.
- Disable the step and use the Python one-instance rebuild if hosted verification fails.
