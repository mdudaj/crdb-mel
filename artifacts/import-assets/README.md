# TACATDP import assets

This folder records generated import references for the cleaned TACATDP baseline dataset.

## Tracked reference

- `reference/tacatdp-cleaned-dta-dry-run.json`

The reference file is a sanitized dry-run summary. It contains counts, linkage checks, duplicate-review counts, and the recommended import mode. It does not contain raw beneficiary rows.

## Local-only import payloads

Raw browser import payloads are copied to:

- `artifacts/import-assets/local/tacatdp-cleaned-dta-dry-run.json`
- `artifacts/import-assets/local/tacatdp-cleaned-dta-import-asset-smoke.json`
- `artifacts/import-assets/local/tacatdp-cleaned-dta-import-asset.json`

`artifacts/import-assets/local/` is intentionally ignored by Git because the smoke and full import assets contain raw beneficiary payloads.

Use the full local asset for the Mshirika portal import:

```text
artifacts/import-assets/local/tacatdp-cleaned-dta-import-asset.json
```

Recommended portal import mode:

```text
replace
```

## 2026-08-26 Mshirika import checkpoint

While the Mshirika cleaned-baseline import is running, CRDB login can be checked
separately with the named PAC profile `tacatdp-crdb`.

Observed state:

- `pac auth who` may still show the CRDB profile, but Dataverse operations can
  fail if CRDB conditional access has expired the refresh token.
- Failure signature:

  ```text
  AADSTS70043: The refresh token has expired or is invalid due to sign-in frequency checks by conditional access.
  ```

Restart CRDB login only when the CRDB user is available to complete the device
code prompt:

```bash
pac auth create \
  --name tacatdp-crdb \
  --tenant 4fc60296-e19d-4bd4-8ea8-96cbf963ed25 \
  --environment https://org5eb0379b.crm4.dynamics.com/ \
  --deviceCode
```

## 2026-08-26 CRDB login refreshed

The named CRDB PAC profile was refreshed successfully after device-code login.

Verified:

- `pac auth who` connects as `dmuroba@CRDBBANK.CO.TZ`.
- `pac pages list` connects to `TACATDP-CRDB-Dev`.
- The CRDB environment lists the `TACATDP Monitoring Tool` Power Pages website.

## 2026-08-26 CRDB baseline-import permission check

Observed CRDB state:

- Web API site settings exist for:
  - `mp_trackedentity`
  - `mp_entityidentifier`
  - `mp_beneficiaryprofile`
  - `mp_beneficiarysubmissionlink`
- Table-permission rows were missing for the same four baseline registry
  tables.
- A pruned `pac pages upload` package containing only those table permissions
  did not create the missing rows. PAC reported `Expected non-empty Guid` for
  the four `adx_entitypermission` records.
- The server-side Package Deployer route is still the correct no-browser-write
  path for importing cleaned baseline data, but on this Linux machine:

  ```text
  pac package deploy --package-type dataverse requires .NET Framework and is not available on this build.
  ```

Immediate non-Azure recovery:

1. Open Power Pages maker/security workspace for `TACATDP Monitoring Tool`.
2. Go to **Security > Table permissions**.
3. Create or open these four permissions:
   - `mp_trackedentity Admin Import`
   - `mp_entityidentifier Admin Import`
   - `mp_beneficiaryprofile Admin Import`
   - `mp_beneficiarysubmissionlink Admin Import`
4. For each permission:
   - Table: matching table above.
   - Access type: `Global`.
   - Privileges: `Read`, `Create`, `Write`, `Append`, `Append To`.
   - Do not enable `Delete`.
   - Web roles: `Administrators` and `Platform Administrator`.
5. Save each permission from the Security workspace.
6. Restart or clear cache for the site.
7. Retry baseline import.
