# Baseline browser import route — Mshirika — 2026-08-14

Status: deployed to Mshirika Power Pages.

## Why this route was added

Linux PAC cannot execute Dataverse Package Deployer packages because Microsoft requires Windows .NET Framework for `pac package deploy --package-type dataverse`.

The working alternative already proven by the prototype is Power Pages Web API writes through the authenticated browser session. This route keeps the import inside the Microsoft tenant boundary and does not require Azure CLI, service-principal credentials, or raw Dataverse OAuth tokens.

## Delivered

- Added an administrator-only `Baseline Import` workspace in the portal shell.
- Added a local XForm seed step for form version `2608130924`.
- Added a local baseline JSON import step for the generated bridge asset.
- Added browser-side idempotent upsert behavior:
  - `mp_Submission`
  - `mp_SubmissionVersion`
  - `mp_TrackedEntity`
  - `mp_EntityIdentifier`
  - `mp_BeneficiaryProfile`
  - `mp_BeneficiarySubmissionLink`
- Added Power Pages Web API site settings for the four bridge tables.
- Added administrator-scoped table permissions for:
  - `mp_form`
  - `mp_formversion`
  - `mp_trackedentity`
  - `mp_entityidentifier`
  - `mp_beneficiaryprofile`
  - `mp_beneficiarysubmissionlink`

The baseline JSON is not deployed as a web file. The administrator selects it locally from the browser.

## Mshirika deployment result

Command:

```bash
source scripts/use-powerplatform-env.sh mshirika
pac auth select --name "$PAC_AUTH_NAME"
pac pages upload \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool \
  --modelVersion Enhanced \
  --forceUploadAll
```

Result:

```text
Power Pages website upload succeeded in 264.63 secs.
```

## Operator steps

Open the Mshirika portal as a Platform Administrator.

1. Open `#/baseline-import`.
2. Select the compiled XForm XML:
   - `artifacts/xforms/tacatdp_impact_evaluation-2608130924.xml`
3. Confirm the page reports that form version `2608130924` is ready.
4. Select the generated baseline bridge JSON:
   - `deployment/Tacatdp.DeploymentPackage/PkgAssets/Content/tacatdp-baseline-bridge-import.json`
5. Run `Run 5-row smoke`.
6. If the smoke succeeds, run `Run full import`.

Expected full import counts:

| Item | Expected count |
|---|---:|
| Baseline rows | 965 |
| Entity identifiers | 2,886 |
| Duplicate review groups | 10 |

Duplicate groups are review-only. The importer does not merge duplicate Customer ID or phone candidates.

## Validation

Completed:

- `npm --prefix powerpages/webforms-spa run build:mshirika-runtime`
- `python3 scripts/stage-powerpages-spa-build.py`
- `node scripts/verify-powerpages-spa-assets.mjs`
- `python3 scripts/validate-powerpages-package-hygiene.py --repair-manifest`
- latest staged bundle syntax check with `node --check`
- Mshirika `pac pages upload` succeeded.

## Notes

- Do not commit the generated baseline JSON or package zip.
- The import route is temporary and administrator-only.
- After CRDB approves the requested service principal/application user, prefer the server-side importer for repeatable bulk imports.
