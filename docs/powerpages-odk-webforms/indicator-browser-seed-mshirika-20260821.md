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

- indicator definitions are matched by `mp_code`;
- data-source mappings are matched by `mp_mappingkey`;
- repeated execution updates matching records instead of creating duplicates.

Runtime association fallback:

- The browser seed first validates that project `TACATDP` exists.
- If Power Pages rejects `mp_Project@odata.bind` with `90040106` / `EntityPermissionAppendToIsMissingDuringAssociationChange`, the seed retries without the `mp_project` lookup bind.
- This fallback is intentional for the prototype browser path because `mp_project Admin Import` already has `Append To`, but the hosted runtime can still reject the association.
- The durable service-owned path should restore project association through an approved Dataverse service principal, application user, Power Automate owner, or Windows Package Deployer path.

Mapping summary constraint:

- `mp_indicatordefinition.mp_datasourcemappingjson` is a short review field and is configured with a 200-character maximum in the current Dataverse table.
- Do not write the full `definition.mappings` JSON into this column from the browser seed.
- Store the full mapping details in `mp_DataSourceMapping` rows, and write only a compact mapping-key summary into `mp_datasourcemappingjson`.

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
- OData lookup for `mp_indicatordefinition` by stable `mp_code`
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

## Mshirika upload command

Use the existing .NET global PAC 2.10.1 executable for this upload path:

```bash
source scripts/use-powerplatform-env.sh mshirika >/dev/null
/home/jmduda/.dotnet/tools/pac pages upload \
  --path powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool \
  --modelVersion Enhanced \
  --forceUploadAll
```

Reason:

- VS Code-bundled PAC 2.11.2 repeatedly crashed on this package with `System.InvalidOperationException`.
- The already-installed .NET global PAC 2.10.1 completed the same upload successfully.
- When run from the managed Codex sandbox, PAC may fail to access the named profile token lockfile under `/home/jmduda/.tacatdp-powerplatform/...`; run the PAC command outside the sandbox or with approved escalation.

Post-upload verification:

```bash
source scripts/use-powerplatform-env.sh mshirika >/dev/null
/home/jmduda/.dotnet/tools/pac pages list
/home/jmduda/.dotnet/tools/pac org fetch --xml "<fetch count='10'><entity name='powerpagecomponent'><attribute name='powerpagecomponentid'/><attribute name='name'/><attribute name='powerpagecomponenttype'/><filter><condition attribute='name' operator='like' value='Webapi/mp_indicatordefinition%'/></filter></entity></fetch>"
/home/jmduda/.dotnet/tools/pac org fetch --xml "<fetch count='10'><entity name='powerpagecomponent'><attribute name='powerpagecomponentid'/><attribute name='name'/><attribute name='powerpagecomponenttype'/><filter><condition attribute='name' operator='like' value='Webapi/mp_datasourcemapping%'/></filter></entity></fetch>"
/home/jmduda/.dotnet/tools/pac org fetch --xml "<fetch count='20'><entity name='powerpagecomponent'><attribute name='powerpagecomponentid'/><attribute name='name'/><attribute name='powerpagecomponenttype'/><filter type='or'><condition attribute='name' operator='eq' value='mp_indicatordefinition Admin Import'/><condition attribute='name' operator='eq' value='mp_datasourcemapping Admin Import'/></filter></entity></fetch>"
```

Expected deployed components:

- `Webapi/mp_indicatordefinition/enabled`
- `Webapi/mp_indicatordefinition/fields`
- `Webapi/mp_datasourcemapping/enabled`
- `Webapi/mp_datasourcemapping/fields`
- `mp_indicatordefinition Admin Import`
- `mp_datasourcemapping Admin Import`

## Risk notes

- Do not use Azure CLI for this path.
- Do not retry the Linux Package Deployer failure; it is a platform limitation, not a missing package in this repository.
- Do not use the VS Code-bundled PAC 2.11.2 for this Mshirika upload until its `System.InvalidOperationException` crash is resolved.
- Do not broaden Web API permissions to `mp_Observation`, `mp_Evidence`, or `mp_IndicatorResult` until the service-owned calculation path is approved.
- If lookup bind errors occur, inspect the Power Pages Web API site setting field list and table permission append/append-to flags before changing entity names.
- If `mp_project` association still returns `90040106` after verified `Append To`, use the implemented no-bind browser fallback instead of repeatedly editing the same table permission.
