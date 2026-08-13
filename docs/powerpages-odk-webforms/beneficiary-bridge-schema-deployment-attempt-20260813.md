# Beneficiary bridge schema deployment attempt — 2026-08-13

Status: blocked before Dataverse write.

## Approved scope

The user approved delivery after the preflight. The intended execution scope was limited to additive Dataverse schema deployment in CRDB development:

- `mp_TrackedEntity`
- `mp_EntityIdentifier`
- `mp_BeneficiaryProfile`
- `mp_BeneficiarySubmissionLink`
- required lookup relationships
- required alternate keys

The approval did not include:

- baseline data import;
- Power Pages table permission changes;
- Power Pages Web API site setting changes;
- portal deployment;
- destructive repair.

## Target

| Item | Value |
|---|---|
| Environment | `TACATDP-CRDB-Dev` |
| Environment ID | `42a3b1e6-8eea-e74a-ae11-3edc41e62d57` |
| PAC profile | `tacatdp-crdb` |
| PAC user | `dmuroba@CRDBBANK.CO.TZ` |

## Pre-write checks completed

- Repository working tree was clean at task start.
- `scripts/dataverse-schema-deploy.py` was inspected as the existing Dataverse metadata writer.
- The CRDB PAC profile was verified with `pac auth who`.
- The existing schema preflight remained the governing schema contract:
  - `docs/powerpages-odk-webforms/beneficiary-bridge-schema-deployment-preflight-20260813.md`

## Blocker

The existing metadata writer requires a Dataverse Web API access token.

The CRDB PAC profile can query Dataverse with `pac org fetch`, but PAC CLI `2.9.3` does not expose an access-token command.

Azure CLI was checked through the CRDB profile wrapper and returned:

```text
ERROR: Please run 'az login' to setup account.
```

An Azure CLI device-code login was started for the CRDB profile:

```bash
source scripts/use-powerplatform-env.sh crdb
az login --use-device-code --tenant "$POWER_PLATFORM_TENANT_ID" --allow-no-subscriptions
```

The device-code session did not complete after repeated polling, so it was interrupted. No schema write was attempted.

## Result

No Dataverse write occurred.

No table was created, modified, deleted, imported, or published.

## Required next action

Complete one of the following before retrying schema deployment:

1. Log in Azure CLI under the CRDB profile using the approved CRDB development user:

   ```bash
   cd /home/jmduda/KodeX/crdb-mel
   source scripts/use-powerplatform-env.sh crdb
   az login --use-device-code --tenant "$POWER_PLATFORM_TENANT_ID" --allow-no-subscriptions
   az account get-access-token --resource "$POWER_PLATFORM_ENVIRONMENT_URL"
   ```

2. Provide an approved service principal/application user for the CRDB development environment and update the deployment env-file path accordingly.

After token access is confirmed, rerun:

```bash
python3 scripts/plan-beneficiary-bridge-schema-deployment.py \
  --repo-root /home/jmduda/KodeX/crdb-mel \
  --output-json /tmp/tacatdp-beneficiary-bridge-schema-deployment-plan.json
```

Then execute only the approved four-table schema slice.
