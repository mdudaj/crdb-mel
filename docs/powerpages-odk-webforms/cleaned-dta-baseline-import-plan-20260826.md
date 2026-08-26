# Cleaned DTA Baseline Import Plan: 2026-08-26

## Scope

Prepare the cleaned TACATDP DAP dataset for the existing Power Pages browser baseline import flow.

Input folder:

`/home/jmduda/Downloads/TACATDP/DAP AND DATASET_share`

## Source files

| File | Role | Import decision |
| --- | --- | --- |
| `TACATDP_Impact_Data_Tracking_for_Financed_Beneficiarie_Dataset.dta` | Root beneficiary baseline submissions | Import first |
| `Loan and value chains invested in.dta` | Loan/value-chain repeat-style rows | Preserve under each root submission JSON through `_submission__uuid -> _uuid` |
| `Stages of Value Chain Cost Quantification Dataset.dta` | Value-chain cost rows | Defer linked import until `PID` mapping is verified |
| `DAP_TACADPT_share.xlsx` | Results/summary tables | Reference only; not direct row-level import source |

## Import identity

- Use `_uuid` as the canonical submission identity.
- Preserve the existing browser-import tracked-entity key format
  `TACATDP:kobo:<_uuid>` because the cleaned DTA file is a cleaned export of
  the same Kobo baseline collection. This lets replace imports update the
  existing beneficiary registry instead of creating a second registry namespace.
- Use `Customer_ID` and `Farmer_Phone` as approved beneficiary identifiers.
- Do not use `Customer_ID` or `Farmer_Phone` as the sole submission key because duplicates exist.

## Current cleaned-data profile

- Root rows: 1,246
- Root columns: 1,317
- Loan/value-chain child rows: 1,484
- Value-chain cost rows: 7,585
- `_uuid`: 1,246 unique values
- `Customer_ID`: 1,216 unique values across 1,246 rows
- `Farmer_Phone`: 1,242 unique values across 1,246 rows
- GPS coordinates: present for all 1,246 root rows
- Regions: 29
- Districts: 130
- Wards: 415

## Import approach

1. Generate a dry-run summary:

   ```bash
   .venv/bin/python scripts/normalize-cleaned-dta-import.py \
     --dta-folder "/home/jmduda/Downloads/TACATDP/DAP AND DATASET_share" \
     --output-json /tmp/tacatdp-cleaned-dta-dry-run.json
   ```

2. Review the sanitized summary counts.

3. Generate a browser import asset only after the summary is accepted:

   ```bash
   .venv/bin/python scripts/normalize-cleaned-dta-import.py \
     --dta-folder "/home/jmduda/Downloads/TACATDP/DAP AND DATASET_share" \
     --mode package-asset \
     --output-json /tmp/tacatdp-cleaned-dta-import-asset.json
   ```

4. In the portal, use `replace` mode for this cleaned dataset.

5. Run a small browser import smoke test first with `--limit 5`, then run the full file only after counts and table permissions are verified.

## Safety

- Dry-run output omits raw rows and PII.
- Package assets contain raw beneficiary payloads and must stay under `/tmp`.
- No live Dataverse import, deployment, table permission change, or site-setting change is performed by the normalizer.

## Follow-up

- Confirm whether `PID` in the value-chain cost file maps to root `_id`, row number, participant number, or another cleaned-analysis key.
- If confirmed, add value-chain cost rows either as preserved submission JSON repeats or as a later normalized reporting projection.
