# Indicator definition browser seed — Mshirika development

Status: implemented for Linux-compatible delivery and Mshirika preview.

## Purpose

Seed the first governed TACATDP indicator metadata through the existing Power Pages administrator route instead of using Package Deployer.

This path exists because the current delivery workstation is Linux-based. PAC authentication and Power Pages upload work here, but `pac package deploy --package-type dataverse` requires the Windows Package Deployer runtime. The browser seed path uses the signed-in Power Pages session and Dataverse Web API permissions already used by the baseline import route.

## Scope

Writes allowed:

- `mp_IndicatorDefinition`
- `mp_DataSourceMapping`

Writes not allowed:

- `mp_Observation`
- `mp_Evidence`
- `mp_IndicatorResult`
- baseline submission tables
- beneficiary tables
- Power Pages access/request tables

Seed file:

- `schemas/dataverse/indicator-evidence-seed.json`

Seed contents:

- `TAC-BEN-001`
- `TAC-FIN-001`
- `TAC-REG-001`
- `TAC-TEC-001`
- `TAC-TRN-001`

## Operator steps

1. Deploy the updated Power Pages source package to Mshirika.
2. Sign in to the portal with a user that has the Platform Administrator web role.
3. Open the admin import route: `#/baseline-import`.
4. Go to Step 5, `Seed indicator definitions`.
5. Select `schemas/dataverse/indicator-evidence-seed.json`.
6. Confirm validation shows 5 indicator definitions and 5 data-source mappings.
7. Click `Run indicator seed`.
8. Confirm the result shows:
   - `mp_IndicatorDefinition: 5`
   - `mp_DataSourceMapping: 5`

The operation is idempotent:

- indicator definitions are matched by TACATDP project and `mp_code`;
- data-source mappings are matched by `mp_mappingkey`;
- repeated execution updates matching records instead of creating duplicates.

## Power Pages enablement

The site source package includes:

- `Webapi/mp_indicatordefinition/enabled`
- `Webapi/mp_indicatordefinition/fields`
- `Webapi/mp_datasourcemapping/enabled`
- `Webapi/mp_datasourcemapping/fields`
- global Platform Administrator table permission for `mp_indicatordefinition`
- global Platform Administrator table permission for `mp_datasourcemapping`

The browser implementation uses:

- `/_api/mp_indicatordefinitions`
- `/_api/mp_datasourcemappings`
- FetchXML lookup for `mp_indicatordefinition` by `mp_project` and `mp_code`
- OData lookup bind names `mp_Project@odata.bind` and `mp_IndicatorDefinition@odata.bind`

## Verification

Run before deployment:

```bash
node scripts/validate-indicator-evidence-seed.mjs
python3 -B scripts/validate-indicator-seed-package.py
node scripts/validate-indicator-browser-seed.mjs
node scripts/validate-indicator-evidence-runbook.mjs
npm run build:mshirika-runtime
python3 scripts/stage-powerpages-spa-build.py
node scripts/verify-powerpages-spa-assets.mjs
python3 scripts/validate-powerpages-package-hygiene.py --repair-manifest
```

Runtime smoke:

1. Open `#/baseline-import`.
2. Confirm Step 5 is visible only for an administrator session.
3. Select the seed JSON.
4. Confirm validation succeeds before the run button is used.
5. Run the seed.
6. Confirm the result counts and no writes to non-seed tables.

## Risk notes

- Do not use Azure CLI for this path.
- Do not retry the Linux Package Deployer failure; it is a platform limitation, not a missing package in this repository.
- Do not broaden Web API permissions to `mp_Observation`, `mp_Evidence`, or `mp_IndicatorResult` until the service-owned calculation path is approved.
- If lookup bind errors occur, inspect the Power Pages Web API site setting field list and table permission append/append-to flags before changing entity names.
