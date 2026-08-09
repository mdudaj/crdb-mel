# TACATDP Linux Power Platform Environment Setup

Use isolated tool state for each Power Platform tenant/environment. This prevents
PAC CLI token-cache collisions when switching between the Mshirika trial
environment and the CRDB environment.

## Targets

| Target | Environment | Dataverse URL |
| --- | --- | --- |
| `mshirika` | `PowerPagesDeveloper-070926-125720` | `https://orga3cf4b37.crm4.dynamics.com/` |
| `crdb` | `TACATDP-CRDB-Dev` | `https://org5eb0379b.crm4.dynamics.com/` |

## Start a Mshirika Session

From the TACATDP repository root:

```bash
source scripts/use-powerplatform-env.sh mshirika
```

First-time login:

```bash
az login --tenant "$TACATDP_POWERPLATFORM_TENANT_ID" --allow-no-subscriptions
pac auth create \
  --name "$PAC_AUTH_NAME" \
  --tenant "$TACATDP_POWERPLATFORM_TENANT_ID" \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --deviceCode
```

Normal verification:

```bash
az account show
pac auth who
pac pages list
```

## Start a CRDB Session

Use a fresh terminal or source the helper again:

```bash
source scripts/use-powerplatform-env.sh crdb
```

First-time login:

```bash
az login --tenant "$TACATDP_POWERPLATFORM_TENANT_ID" --allow-no-subscriptions
pac auth create \
  --name "$PAC_AUTH_NAME" \
  --tenant "$TACATDP_POWERPLATFORM_TENANT_ID" \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --deviceCode
```

Normal verification:

```bash
az account show
pac auth who
pac pages list
```

## Dataverse Web API Token Check

Do not print access tokens. To verify the active Azure CLI login can call
Dataverse, run:

```bash
TOKEN=$(az account get-access-token \
  --tenant "$TACATDP_POWERPLATFORM_TENANT_ID" \
  --resource "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --query accessToken -o tsv)

curl -sS \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" \
  "${POWER_PLATFORM_ENVIRONMENT_URL%/}/api/data/v9.2/WhoAmI"
```

Expected result: JSON containing user and organization IDs.

## Assign a Portal Web Role

After a user has an active Power Pages `Contact` row, assign a portal web role
through the reviewed helper:

```bash
python3 scripts/powerpages-assign-webrole.py \
  --env-file .env \
  --email john.mduda@mshirikacorp.onmicrosoft.com \
  --role Administrators \
  --execute
```

The helper is idempotent. Run it without `--execute` first for a dry-run.

## Switching Rules

- Source `scripts/use-powerplatform-env.sh` before every PAC/Azure session.
- Do not reuse one terminal for CRDB and Mshirika unless you re-source the helper.
- Do not copy token-cache directories between targets.
- Do not commit files under `.tacatdp-powerplatform`, `.azure`, or generated auth/cache paths.
- Keep `.env` secrets out of the repository; this helper does not require secrets.
- After Power Pages uploads or role changes, restart the site or purge cache in
  Power Pages Studio/Admin Center when browser behavior still reflects stale
  content. This PAC build does not expose restart or purge-cache commands.

## Why This Exists

PAC on Linux can fail when application and user tokens share a flat token cache.
The helper isolates `HOME`, `AZURE_CONFIG_DIR`, and XDG config/data/cache paths
per target so each tenant/environment gets a separate PAC and Azure CLI state.
