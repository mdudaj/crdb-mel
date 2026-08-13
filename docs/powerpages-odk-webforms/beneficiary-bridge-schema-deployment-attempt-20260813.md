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

This does not mean all CRDB/Mshirika writes require Azure CLI. Previous CRDB writes used PAC device-code authentication with managed solution import and Power Pages upload. That path remains valid when the schema change is packaged as a Dataverse solution.

## Result

No Dataverse write occurred.

No table was created, modified, deleted, imported, or published.

## Required next action

Complete one of the following before retrying schema deployment:

1. Use the documented PAC managed-solution path:

   - create the four bridge tables in a solution source/package;
   - pack/export a managed solution;
   - import with `pac solution import --publish-changes`;
   - verify the four tables with read-only FetchXML.

   This is the preferred path while CRDB Azure CLI permissions are not ready.

2. Or log in Azure CLI under the CRDB profile using the approved CRDB development user:

   ```bash
   cd /home/jmduda/KodeX/crdb-mel
   source scripts/use-powerplatform-env.sh crdb
   az login --use-device-code --tenant "$POWER_PLATFORM_TENANT_ID" --allow-no-subscriptions
   az account get-access-token --resource "$POWER_PLATFORM_ENVIRONMENT_URL"
   ```

3. Or provide an approved service principal/application user for the CRDB development environment and update the deployment env-file path accordingly.

After token access is confirmed, rerun:

```bash
python3 scripts/plan-beneficiary-bridge-schema-deployment.py \
  --repo-root /home/jmduda/KodeX/crdb-mel \
  --output-json /tmp/tacatdp-beneficiary-bridge-schema-deployment-plan.json
```

Then execute only the approved four-table schema slice.

## Mshirika fallback check — 2026-08-14

Mshirika was checked as the fallback environment. Read-only aggregate inventory showed:

| Table | Mshirika state |
|---|---|
| `mp_project` | Exists; count 1. |
| `mp_submission` | Exists; count 5. |
| `mp_trackedentity` | Not found in metadata. |
| `mp_entityidentifier` | Not found in metadata. |
| `mp_beneficiaryprofile` | Not found in metadata. |
| `mp_beneficiarysubmissionlink` | Not found in metadata. |

The current Mshirika solution was cloned read-only with PAC. The clone confirmed the current solution contains runtime, reporting, access, and onboarding tables but not the four bridge tables. Repacking the cloned unmanaged solution succeeded, proving the PAC solution-packaging path is available.

Do not hand-author Dataverse entity XML for the bridge tables without a generator/validator. The safe non-Azure path is a reviewed managed-solution package.
