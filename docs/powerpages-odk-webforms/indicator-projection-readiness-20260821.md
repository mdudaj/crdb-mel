# Indicator projection readiness — Step 6

Status: implemented for Mshirika prototype review.

## Scope

Add a read-only Step 6 panel to `#/baseline-import` that calculates the first five governed TACATDP MVP indicators from existing readable data:

- `TAC-BEN-001`
- `TAC-FIN-001`
- `TAC-REG-001`
- `TAC-TEC-001`
- `TAC-TRN-001`

The panel does not create, update, or delete Dataverse rows. It does not write `mp_IndicatorResult`.

## Evidence used

- `schemas/dataverse/indicator-evidence-seed.json` defines the five governed indicator definitions and mappings.
- `powerpages/webforms-spa/src/components/dashboard/tacatdpBaselineProjection.ts` contains the existing baseline-derived dashboard formulas.
- `PowerPagesApiClient.readIndicatorEvidenceSeedBack()` verifies that seeded indicator metadata is readable through Power Pages Web API.
- `PowerPagesApiClient.listBeneficiaries()` reads `mp_BeneficiaryProfile`.
- `PowerPagesApiClient.listDashboardSubmissionReportRows()` reads the bounded `mp_SubmissionReportRow` projection.

## Behaviour

The user opens `#/baseline-import`, then uses Step 6 `Build indicator projection`.

The panel:

- reads seeded indicator definitions and data-source mappings;
- reads beneficiary profiles;
- reads up to 1,000 baseline report rows;
- reuses the existing dashboard baseline projection function;
- shows current value, source row count, verification status, and gap/next check for each MVP indicator.

Verification status is deliberately conservative:

- `baseline imported` for profile and region counts;
- `baseline reported` for financing, technology, and training values sourced from baseline answers;
- `needs ...` where required fields are missing.

## Look and feel

- Material surface card.
- Compact Step 6 header with one primary action.
- Summary count cards for profiles, report rows, calculated rows, and metadata.
- Responsive Material table for indicator readiness rows.
- Status chip text is shown in addition to colour.

## Accessibility checklist

- The action is a semantic button.
- Loading and error messages use `aria-live`.
- The readiness table has a region label and keyboard focus target.
- Table columns use proper header cells.
- Status is communicated as text, not colour only.

## Acceptance criteria

- Step 6 appears after indicator metadata read-back and before diagnostics.
- Clicking `Build indicator projection` reads existing Dataverse data only.
- The result includes five rows, one for each governed MVP indicator.
- Each row shows code, name, current value, source rows, verification status, and gap/next check.
- The UI explicitly states that no `mp_IndicatorResult` rows are written.
- Existing indicator seed/read-back validation still passes.

## Verification

Run:

```bash
npm run build:mshirika-runtime
node scripts/validate-indicator-browser-seed.mjs
node scripts/validate-indicator-evidence-runbook.mjs
python3 scripts/stage-powerpages-spa-build.py
node scripts/verify-powerpages-spa-assets.mjs
python3 scripts/validate-powerpages-package-hygiene.py --repair-manifest
```

Expected result: all commands pass. Vite may still report the known upstream `@getodk/web-forms` `eval` and chunk-size warnings.
