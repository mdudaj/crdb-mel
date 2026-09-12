# User manual

Date: 2026-08-27

## 1. Purpose

This manual explains how users operate the TACATDP Integrated M&E System and Monitoring Tool prototype.

The prototype supports authenticated access, form version setup, baseline data import, dashboard review, beneficiary review, and reporting/export review.

## 2. User roles

| Role | Main tasks |
|---|---|
| Platform Administrator | Prepare the form version, import baseline data, manage access, and support users. |
| M&E Manager | Review dashboard outputs, reports, system status, and SOP compliance. |
| MEL Officer | Review monitoring dashboard, beneficiary records, submissions, and reporting projections. |
| Data Collector / Field Officer | Open assigned forms and submit data. |
| Reviewer / Approver | Review submitted records and confirm data readiness. |
| ICT / System Administrator | Manage environment access, deployment, permissions, and support. |

## 3. Sign in

1. Open the portal link.
2. Select the Microsoft sign-in option.
3. Sign in with the approved account.
4. Confirm that the application shell loads.

If access is denied, contact the Platform Administrator or ICT administrator. A successful Microsoft sign-in does not automatically grant application access. The user also needs site visibility, web role, table permissions, and form assignment where applicable.

## 4. View the dashboard

1. Open the portal.
2. Select `Overview` or `Dashboards`.
3. Wait for live baseline data to load.
4. Review the KPI cards, map, financed practices, training, climate outcomes, and submission status.

If a card shows a pending state, the required source data may not be available yet. Do not treat pending values as zero.

## 5. Seed the latest form version

This task is for Platform Administrators only.

1. Open `#/baseline-import`.
2. In Step 1, select the compiled XForm XML file:

   ```text
   artifacts/xforms/tacatdp_impact_evaluation-2608130924.xml
   ```

3. Confirm that the page reports form version `2608130924` as ready.

This step prepares the form version that baseline submissions and future data updates reference.

## 6. Import baseline data

This task is for Platform Administrators only.

1. Open `#/baseline-import`.
2. Confirm that Step 1 has already seeded form version `2608130924`.
3. In Step 2, select the generated baseline bridge JSON file.
4. Select the import mode:
   - Use `Append` to preserve history.
   - Use `Replace` to update matching baseline rows in place.
5. Run the smoke test first.
6. If the smoke test succeeds, run the full import.
7. Wait until the import reaches the final row count.
8. Open the dashboard and reports to confirm that baseline projections refresh.

Do not upload the original Kobo workbook directly into the browser import control. The browser import expects the generated JSON bridge asset.

## 7. Review beneficiaries

1. Open `Beneficiaries`.
2. Use search or filters to find a region, beneficiary, technology/practice, or status.
3. Open a beneficiary detail view.
4. Review profile, finance, technology/practice, training, outcomes, location, and data-lineage sections.

The prototype beneficiary view is a registry projection from imported submissions. Production registry governance must be finalized during the next architecture phase.

## 8. Review submitted records and reports

1. Open `Data Submissions` or `Reports`.
2. Search or filter the available records.
3. Confirm projection status and update dates.
4. Export CSV where the route provides an export action.

If reporting reads fail, the user may be missing table permissions for the relevant Dataverse table.

## 9. Interpret pending states

| Pending state | Meaning |
|---|---|
| Awaiting live data | The app has not received readable live rows yet. |
| Awaiting loan financing data | The required loan fields are not available in the current projection. |
| Awaiting dated loan records | Monthly trend cannot render until dated loan records are available. |
| Pending loan performance feed | Repayment and portfolio quality require CRDB operational loan-performance data. |
| Data unavailable | The current user may lack permission, or the source table may not be configured for Web API access. |

## 10. Support notes

When reporting an issue, include:

- portal URL;
- signed-in user email;
- route name;
- action attempted;
- exact error message;
- screenshot;
- date and time.
