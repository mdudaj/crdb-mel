# CRDB duplicate webfile ownership classification

Date: 2026-08-11

## Scope

This is a read-only ownership classification of duplicate Power Pages web-file records in the CRDB environment.

No Dataverse records were deleted. No Power Pages upload was run.

## Target

- PAC target: `crdb`
- Environment: `TACATDP-CRDB-Dev`
- Environment URL: `https://org5eb0379b.crm4.dynamics.com/`
- PAC identity: `dmuroba@CRDBBANK.CO.TZ`

## Evidence path

The earlier inventory showed that the fresh CRDB PAC download contains duplicate browser-facing `adx_partialurl` records. This classification checks ownership through the enhanced Power Pages table that PAC itself reported during upload:

- Table queried: `powerpagecomponent`
- Read method: `pac org fetch`
- Key fields:
  - `powerpagecomponentid`
  - `name`
  - `ismanaged`

The downloaded web-file metadata `adx_webfileid` values match `powerpagecomponentid` for these enhanced Power Pages web-file records.

## Tooling added

Added:

- `scripts/classify-crdb-duplicate-webfiles.py`

The script:

- requires `TACATDP_POWERPLATFORM_TARGET=crdb`;
- uses the current PAC profile;
- runs read-only FetchXML;
- does not use `.env`;
- does not print tokens;
- does not delete or update Dataverse records.

## Commands run

```bash
PYTHONPYCACHEPREFIX=/tmp/crdb-mel-pycache python3 -m py_compile scripts/classify-crdb-duplicate-webfiles.py

source scripts/use-powerplatform-env.sh crdb
python3 scripts/classify-crdb-duplicate-webfiles.py --only-current-dist
python3 scripts/classify-crdb-duplicate-webfiles.py
```

## Classification summary

| Scope | Records classified | Managed-blocked | Unmanaged current delete candidates | Unmanaged stale delete candidates |
| --- | ---: | ---: | ---: | ---: |
| Current Vite dist duplicates only | 24 | 15 | 9 | 0 |
| Full duplicate inventory | 57 | 39 | 9 | 9 |

## Current-build duplicate groups

These groups overlap the current Vite `dist/assets` output and are therefore relevant to the deployed dashboard bundle.

| Partial URL | Records | Managed-blocked | Unmanaged current delete candidates | Stale managed records |
| --- | ---: | ---: | ---: | ---: |
| `strings_es-C8xkQaZj-KYNBMnTd.mjs` | 8 | 5 | 3 | 1 |
| `strings_fr-C0vLmCzP-Bi34LuTN.mjs` | 8 | 5 | 3 | 1 |
| `strings_id-BE0G3I_d-B0dO9nQF.mjs` | 8 | 5 | 3 | 1 |

Each group has a mix of managed and unmanaged records. Because managed records remain in every current duplicate group, deleting only unmanaged rows will not eliminate the duplicate partial URL condition.

## Cleanup interpretation

The duplicate condition is not safely cleanable through a simple Dataverse delete batch.

Reasons:

1. Most duplicate records are managed Power Pages components.
2. PAC already attempted to delete stale managed components during upload and CRDB rejected those deletes with managed-property evaluation errors.
3. Each current duplicated locale chunk still has managed records even after separating unmanaged candidates.
4. A partial cleanup that deletes only unmanaged records would not remove all duplicate partial URLs and could remove one of the records currently serving the expected binary.

## Recommendation

Do not perform ad hoc record deletion in CRDB.

Safe options:

1. Leave the duplicates documented if the active home page and asset verifier continue to pass.
2. If cleanup is required, handle managed records through solution lifecycle or Power Pages component management, not direct delete.
3. Before any approved cleanup:
   - identify which managed solution owns each managed `powerpagecomponent`;
   - confirm whether CRDB can remove or upgrade that solution safely;
   - back up the site with `pac pages download`;
   - prepare an explicit rollback package;
   - run cleanup first in a non-production/safe environment if available.

## Operational rule

For CRDB deployments, treat duplicate partial URLs as two separate checks:

1. Current asset safety:
   - `node scripts/verify-powerpages-spa-assets.mjs`
   - Must pass before accepting a deployment.
2. Server hygiene:
   - `source scripts/use-powerplatform-env.sh crdb`
   - `python3 scripts/classify-crdb-duplicate-webfiles.py --only-current-dist`
   - Use this to decide whether duplicates are unmanaged cleanup candidates or managed-blocked residue.

For the current state, deployment safety passed, but server hygiene remains managed-blocked.

## Revalidation on 2026-08-20

The CRDB site was downloaded again from `TACATDP-CRDB-Dev` using the enhanced-model Power Pages download path and verified against the current SPA build.

Fresh download evidence:

| Check | Result |
| --- | ---: |
| Downloaded web-file metadata records | 315 |
| Duplicate partial URLs | 17 |
| Current SPA duplicate partial URLs | 3 |
| Current SPA asset count | 32 |
| Missing current SPA assets | 0 |
| Mismatched current SPA assets | 0 |

Current duplicate partial URLs remain:

- `strings_es-C8xkQaZj-KYNBMnTd.mjs` — 8 records
- `strings_fr-C0vLmCzP-Bi34LuTN.mjs` — 8 records
- `strings_id-BE0G3I_d-B0dO9nQF.mjs` — 8 records

The live ownership classifier again returned the same current-build pattern:

| Scope | Records classified | Managed-blocked | Unmanaged current delete candidates | Unmanaged stale delete candidates |
| --- | ---: | ---: | ---: | ---: |
| Current Vite dist duplicates only | 24 | 15 | 9 | 0 |

Decision: no delete was performed. The 9 unmanaged records all match the current SPA binary and are therefore not proven unused. The stale current-build records are managed. Deleting only unmanaged records would still leave duplicate partial URLs and could remove valid current binary copies. Cleanup must remain a CRDB solution-lifecycle or Power Pages component-management action with the owning administrator.
