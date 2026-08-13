# Beneficiary bridge deployment to Mshirika — 2026-08-14

Status: deployed to Mshirika development environment.

## Scope

Approved scope was limited to the minimal beneficiary bridge schema:

- `mp_TrackedEntity`
- `mp_EntityIdentifier`
- `mp_BeneficiaryProfile`
- `mp_BeneficiarySubmissionLink`

No baseline beneficiary data was imported in this step.

CRDB deployment remains deferred until Dennis/Hailo access is available.

## Target environment

| Item | Value |
|---|---|
| Tenant account | `john.mduda@mshirikacorp.onmicrosoft.com` |
| PAC profile | `tacatdp-mshirika` |
| Environment | `PowerPagesDeveloper-070926-125720` |
| Environment ID | `07b77aa3-c0c0-e513-8b8c-407b83639a45` |
| Organization URL | `https://orga3cf4b37.crm4.dynamics.com/` |

## Package generation

The solution source was generated from the current Mshirika `tacatdp_prototype`
solution clone using:

```bash
python3 scripts/generate-beneficiary-bridge-solution-patch.py \
  --source /tmp/mshirika-tacatdp-solution-clone/tacatdp_prototype/src \
  --output /tmp/mshirika-beneficiary-bridge-solution/src \
  --repo-root /home/jmduda/KodeX/crdb-mel \
  --version 0.2.4.0
```

The generator adds the four approved tables, required relationships, alternate
keys, and solution root components. It intentionally generates only custom
columns plus the primary key for the new entities; Dataverse creates system
metadata. This avoids localized-label conflicts caused by copying system
attribute labels from another exported table.

Text columns used by alternate keys are constrained to shorter lengths so the
Dataverse alternate-key index stays below the 1700-byte limit.

## Package validation

Both packages were packed successfully:

```bash
pac solution pack \
  --zipfile /tmp/tacatdp_beneficiary_bridge_unmanaged.zip \
  --folder /tmp/mshirika-beneficiary-bridge-solution/src \
  --packagetype Unmanaged \
  --log /tmp/tacatdp-beneficiary-bridge-pack-unmanaged.log \
  --errorlevel Info

pac solution pack \
  --zipfile /tmp/tacatdp_beneficiary_bridge_managed.zip \
  --folder /tmp/mshirika-beneficiary-bridge-solution/src \
  --packagetype Managed \
  --useUnmanagedFileForMissingManaged \
  --log /tmp/tacatdp-beneficiary-bridge-pack-managed.log \
  --errorlevel Info
```

The generated unmanaged package was inspected and confirmed to contain the new
relationship definitions, including:

- `mp_Project_TrackedEntity_Project`
- `mp_TrackedEntity_EntityIdentifier_TrackedEntity`
- `mp_TrackedEntity_BeneficiaryProfile_TrackedEntity`
- `mp_Project_BeneficiaryProfile_Project`
- `mp_TrackedEntity_BeneficiarySubmissionLink_TrackedEntity`
- `mp_Submission_BeneficiarySubmissionLink_Submission`

## Import result

Mshirika has `tacatdp_prototype` installed as unmanaged, so the mode-matching
unmanaged package was imported:

```bash
source scripts/use-powerplatform-env.sh mshirika
pac auth select --name "$PAC_AUTH_NAME"
pac solution import \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --path /tmp/tacatdp_beneficiary_bridge_unmanaged.zip \
  --publish-changes \
  --async \
  --max-async-wait-time 20
```

Result:

- Solution import completed successfully.
- Publish all customizations completed successfully.

## Verification

Read-only FetchXML count checks were run after publish.

| Table | Fetch result |
|---|---:|
| `mp_trackedentity` | 0 |
| `mp_entityidentifier` | 0 |
| `mp_beneficiaryprofile` | 0 |
| `mp_beneficiarysubmissionlink` | 0 |

Count `0` is expected because this deployment created schema only. The baseline
data import is a separate later step.

## Failure signatures resolved

| Failure | Resolution |
|---|---|
| Managed import failed because Mshirika has an unmanaged installed solution. | Use unmanaged package for Mshirika; reserve managed package for environments installed as managed. |
| Missing relationship definitions for generated lookup columns. | Add relationship detail XML and register names in `Other/Relationships.xml`. |
| `UQ_LocalizedLabelCheck` duplicate localized label during entity creation. | Do not copy system attributes/labels from exported source table into generated new tables. |
| Alternate-key index exceeded 1700 bytes. | Reduce text column lengths used in alternate keys. |

## Next step

When Dennis/Hailo access is available, repeat the same package-generation path
against the CRDB environment mode:

- if CRDB has `tacatdp_prototype` as managed, import the managed zip;
- if CRDB has it as unmanaged, import the unmanaged zip;
- verify the four tables with FetchXML before importing baseline data.
