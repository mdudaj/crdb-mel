# Indicator and evidence schema deployment to Mshirika — 2026-08-20

Status: deployed to Mshirika development environment and verified from a fresh post-import solution export.

## Scope

Approved scope:

- Generate the actual solution metadata/package for the approved indicator/evidence schema.
- Start with the Mshirika development environment.
- Propose seed indicators.
- Recommend whether Power Pages should read `mp_IndicatorResult` directly now.

This deployment created schema only. It did not import seed records, baseline records, Power Pages site settings, table permissions, portal code, or dashboard changes.

## Target environment

| Item | Value |
|---|---|
| Tenant account | `john.mduda@mshirikacorp.onmicrosoft.com` |
| PAC profile | `tacatdp-mshirika` |
| Environment | `PowerPagesDeveloper-070926-125720` |
| Environment ID | `07b77aa3-c0c0-e513-8b8c-407b83639a45` |
| Organization URL | `https://orga3cf4b37.crm4.dynamics.com/` |
| Solution | `tacatdp_prototype` |
| Import package mode | Unmanaged |
| Solution version | `0.2.6.0` |

Mshirika uses the unmanaged installed solution, so the unmanaged package was imported.

## Package generation

The current Mshirika solution was cloned:

```bash
source scripts/use-powerplatform-env.sh mshirika
pac auth select --name "$PAC_AUTH_NAME"
pac solution clone \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --name tacatdp_prototype \
  --outputDirectory /tmp/mshirika-indicator-evidence-clone \
  --packagetype Both \
  --async \
  --max-async-wait-time 20
```

The indicator/evidence solution source was generated:

```bash
python3 scripts/generate-indicator-evidence-solution-patch.py \
  --source /tmp/mshirika-indicator-evidence-clone/tacatdp_prototype/src \
  --output /tmp/mshirika-indicator-evidence-solution/src \
  --repo-root /home/jmduda/KodeX/crdb-mel \
  --version 0.2.6.0
```

Generated tables:

- `mp_IndicatorDefinition`
- `mp_DataSourceMapping`
- `mp_Observation`
- `mp_Evidence`
- `mp_IndicatorResult`

Generated relationship count: 15.

Generated alternate-key count: 5.

Implementation note: `TwoOptions` fields from the review schema are generated as local two-value choice fields (`No`, `Yes`) in this PAC package path because the existing exported source did not contain a reusable boolean/two-options XML template. The logical schema still documents them as two-options flags; this can be revisited if a tested boolean template is added.

## Package validation

Unpacked source validation:

```bash
python3 scripts/validate-indicator-evidence-solution-package.py \
  /tmp/mshirika-indicator-evidence-solution/src
```

Packed zips:

```bash
pac solution pack \
  --zipfile /tmp/tacatdp_indicator_evidence_unmanaged.zip \
  --folder /tmp/mshirika-indicator-evidence-solution/src \
  --packagetype Unmanaged \
  --log /tmp/tacatdp-indicator-evidence-pack-unmanaged.log \
  --errorlevel Info

pac solution pack \
  --zipfile /tmp/tacatdp_indicator_evidence_managed.zip \
  --folder /tmp/mshirika-indicator-evidence-solution/src \
  --packagetype Managed \
  --useUnmanagedFileForMissingManaged \
  --log /tmp/tacatdp-indicator-evidence-pack-managed.log \
  --errorlevel Info
```

Packed zip validation:

```bash
python3 scripts/validate-indicator-evidence-solution-package.py \
  /tmp/tacatdp_indicator_evidence_unmanaged.zip

python3 scripts/validate-indicator-evidence-solution-package.py \
  /tmp/tacatdp_indicator_evidence_managed.zip
```

All package validations passed.

## Mshirika import

Imported the unmanaged package:

```bash
source scripts/use-powerplatform-env.sh mshirika
pac auth select --name "$PAC_AUTH_NAME"
pac solution import \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --path /tmp/tacatdp_indicator_evidence_unmanaged.zip \
  --publish-changes \
  --async \
  --max-async-wait-time 20
```

Result:

- Solution import completed successfully.
- Publish all customizations completed successfully.
- No Power Pages settings or table permissions were changed.
- No data was imported.

## Post-import verification

The Mshirika solution was cloned again after import:

```bash
source scripts/use-powerplatform-env.sh mshirika
pac auth select --name "$PAC_AUTH_NAME"
pac solution clone \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --name tacatdp_prototype \
  --outputDirectory /tmp/mshirika-indicator-evidence-verify \
  --packagetype Unmanaged \
  --async \
  --max-async-wait-time 20
```

The fresh export included:

- `mp_DataSourceMapping`
- `mp_Evidence`
- `mp_IndicatorDefinition`
- `mp_IndicatorResult`
- `mp_Observation`

Verification command:

```bash
python3 scripts/validate-indicator-evidence-solution-package.py \
  /tmp/mshirika-indicator-evidence-verify/tacatdp_prototype/src
```

Result:

- Post-import package validation passed.
- Entity XML includes the five tables.
- Entity XML includes the five alternate keys.
- Relationship XML includes the 15 generated relationships.

## Proposed seed indicators

Seed only indicator definitions and source mappings first:

| Indicator code | Name | Type | Method | Initial status |
|---|---|---|---|---|
| `TAC-BEN-001` | Beneficiary profiles imported | Output | Imported | Active |
| `TAC-FIN-001` | Reported baseline amount | Financial | Reported | Active |
| `TAC-REG-001` | Regions covered | Output | Imported | Active |
| `TAC-TEC-001` | Technologies financed | Output | Imported | Active |
| `TAC-TRN-001` | Farmers trained | Output | Reported | Active |

Do not seed repayment, NPL, or official tCO₂e result rows yet. Those require approved finance-source integration and approved climate calculation methodology.

## Power Pages read recommendation

Do not switch the dashboard to read `mp_IndicatorResult` immediately.

Recommended sequence:

1. Seed `mp_IndicatorDefinition` and `mp_DataSourceMapping`.
2. Implement a calculation path that writes `mp_IndicatorResult`.
3. Add read-only Power Pages Web API settings for `mp_IndicatorResult`.
4. Add conservative table permissions for read-only dashboard access.
5. Switch one dashboard section to read `mp_IndicatorResult`.
6. Compare it against the current browser projection before migrating the rest.

Reason: the current dashboard projection already updates from imported baseline report rows. Reading `mp_IndicatorResult` before a reliable refresh path exists would introduce stale or empty governed KPI records.

## Follow-up for CRDB

Use the same generated package path when CRDB access is available:

- If CRDB has `tacatdp_prototype` installed unmanaged, import `/tmp/tacatdp_indicator_evidence_unmanaged.zip`.
- If CRDB has it installed managed, import `/tmp/tacatdp_indicator_evidence_managed.zip`.
- Clone and validate the target solution after import before adding Power Pages Web API settings or seed data.
