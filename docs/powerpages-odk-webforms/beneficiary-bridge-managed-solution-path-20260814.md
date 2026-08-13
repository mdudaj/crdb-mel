# Beneficiary bridge managed-solution path — 2026-08-14

Status: packaging-path investigation. No Dataverse schema write was performed.

## Why this exists

Azure CLI permissions are not ready in the CRDB tenant. Historically, CRDB writes were completed through PAC device-code authentication and managed solution import, not Azure CLI.

For the beneficiary bridge schema, the direct metadata writer still needs a Dataverse Web API token. Therefore, the non-Azure path is to package the four bridge tables into a Dataverse solution and import it with PAC.

## Read-only Mshirika evidence

Mshirika environment:

| Item | Value |
|---|---|
| Environment | `PowerPagesDeveloper-070926-125720` |
| PAC profile | `tacatdp-mshirika` |
| PAC user | `john.mduda@mshirikacorp.onmicrosoft.com` |

Read-only inventory:

| Table | State |
|---|---|
| `mp_project` | Exists; count 1. |
| `mp_submission` | Exists; count 5. |
| `mp_trackedentity` | Missing. |
| `mp_entityidentifier` | Missing. |
| `mp_beneficiaryprofile` | Missing. |
| `mp_beneficiarysubmissionlink` | Missing. |

## Solution clone evidence

The current Mshirika solution was cloned read-only:

```bash
source scripts/use-powerplatform-env.sh mshirika
pac auth select --name "$PAC_AUTH_NAME"
pac solution clone \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --name tacatdp_prototype \
  --outputDirectory /tmp/mshirika-tacatdp-solution-clone \
  --packagetype Both \
  --async \
  --max-async-wait-time 20
```

The clone exported and unpacked both unmanaged and managed solution sources.

Exported entities included:

- `mp_Project`
- `mp_Form`
- `mp_FormVersion`
- `mp_FormAssignment`
- `mp_FormAttachment`
- `mp_Submission`
- `mp_SubmissionVersion`
- `mp_SubmissionAttachment`
- reporting projection tables
- access/onboarding tables

The four beneficiary bridge tables were not present.

## Pack validation

The cloned unmanaged solution was repacked successfully:

```bash
pac solution pack \
  --zipfile /tmp/tacatdp_prototype_repacked_unmanaged.zip \
  --folder /tmp/mshirika-tacatdp-solution-clone/tacatdp_prototype/src \
  --packagetype Unmanaged \
  --log /tmp/tacatdp-solution-pack.log \
  --errorlevel Info
```

This proves the local PAC solution packaging path works.

## Safe delivery path

Do not manually hand-author Dataverse entity XML for the bridge tables without a generator and validator.

Safe options:

1. Use Maker/Dataverse solution UI in Mshirika to create the four tables in `tacatdp_prototype`, export managed, then import to CRDB with PAC.
2. Build a repository generator that emits valid SolutionPackager entity XML for:
   - `mp_TrackedEntity`
   - `mp_EntityIdentifier`
   - `mp_BeneficiaryProfile`
   - `mp_BeneficiarySubmissionLink`
   - required relationships
   - required alternate keys
3. Use an approved Web API token/service principal and the existing metadata writer.

Until one of those is ready, the schema should not be imported.

## Correct rule for future runs

Do not default to Azure CLI for CRDB/Mshirika writes. First check:

1. PAC profile state.
2. Existing managed-solution import/export path.
3. Whether the required change is already available in a solution package.
4. Only then consider direct Dataverse Web API token paths.
