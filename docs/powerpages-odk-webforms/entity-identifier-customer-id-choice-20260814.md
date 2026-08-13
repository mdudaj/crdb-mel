# Entity identifier Customer ID choice — 2026-08-14

Status: deployed to Mshirika and verified from exported solution metadata.

## Purpose

The baseline importer needs to store approved Customer ID values in
`mp_EntityIdentifier` using a dedicated identifier type, not the generic `Other`
choice.

## Schema change

Table:

- `mp_EntityIdentifier`

Column:

- `mp_identifiertype`

Choice added:

| Label | Value |
|---|---:|
| `Customer ID` | `100000006` |

The value was appended after existing choices to avoid shifting existing option
values:

| Existing label | Existing value |
|---|---:|
| `Source record` | `100000000` |
| `Customer name` | `100000001` |
| `Phone` | `100000002` |
| `National ID` | `100000003` |
| `Loan reference` | `100000004` |
| `Other` | `100000005` |

## Mshirika deployment

Generated package:

```bash
python3 scripts/generate-beneficiary-bridge-solution-patch.py \
  --source /tmp/mshirika-tacatdp-solution-clone/tacatdp_prototype/src \
  --output /tmp/mshirika-beneficiary-bridge-solution-customer-id/src \
  --repo-root /home/jmduda/KodeX/crdb-mel \
  --version 0.2.5.0
```

Packed packages:

- `/tmp/tacatdp_beneficiary_bridge_customer_id_unmanaged.zip`
- `/tmp/tacatdp_beneficiary_bridge_customer_id_managed.zip`

Mshirika import used the unmanaged package because the installed Mshirika
solution is unmanaged:

```bash
source scripts/use-powerplatform-env.sh mshirika
pac auth select --name "$PAC_AUTH_NAME"
pac solution import \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --path /tmp/tacatdp_beneficiary_bridge_customer_id_unmanaged.zip \
  --publish-changes \
  --async \
  --max-async-wait-time 20
```

Result:

- solution import succeeded;
- publish all customizations succeeded.

## Verification

The Mshirika solution was cloned after import:

```bash
pac solution clone \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --name tacatdp_prototype \
  --outputDirectory /tmp/mshirika-tacatdp-solution-clone-customer-id-verify \
  --packagetype Unmanaged \
  --async \
  --max-async-wait-time 20
```

Exported metadata verified `mp_EntityIdentifier.mp_identifiertype` contains:

```json
{
  "value": "100000006",
  "label": "Customer ID"
}
```

The baseline payload dry-run was rerun and now reports no remaining schema
follow-ups.

## CRDB note

CRDB deployment is deferred until Dennis/Hailo access is available. Use the same
versioned package path, matching the installed solution mode in CRDB.
