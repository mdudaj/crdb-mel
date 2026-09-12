# Draft SOPs

Date: 2026-08-27

## 1. Purpose

These draft standard operating procedures define how different user levels operate the TACATDP Integrated M&E System and Monitoring Tool prototype.

The SOPs should be finalized after CRDB confirms the final system configuration, deployment strategy, user roles, and permission model.

## 2. SOP ownership

| Area | Responsible role |
|---|---|
| System access and permissions | ICT / Platform Administrator |
| Form version control | Platform Administrator and M&E Manager |
| Baseline import | Platform Administrator |
| Data collection | Data Collector / Field Officer |
| Submission review | MEL Officer and Reviewer / Approver |
| Dashboard review | M&E Manager and MEL Officer |
| Reporting | M&E Manager and MEL Officer |
| Production support | ICT / System Administrator |

## 3. Access management SOP

1. ICT confirms that the user has an approved Microsoft account.
2. The Platform Administrator confirms the required application role.
3. ICT or the Platform Administrator grants portal access where the site is private.
4. The Platform Administrator assigns the user to the required form or project.
5. The user signs in and confirms that the expected routes are visible.
6. The administrator records the access change for audit purposes.

## 4. Form version management SOP

1. The M&E Manager approves the form version to be used.
2. The Platform Administrator confirms the compiled XForm XML version.
3. The Platform Administrator opens `#/baseline-import`.
4. The Platform Administrator uploads the approved XML in Step 1.
5. The Platform Administrator confirms that the portal reports the form version as ready.
6. The M&E Manager confirms that data collectors should use the updated form.

Current approved prototype form version:

```text
2608130924
```

## 5. Baseline import SOP

1. The data owner confirms that the cleaned dataset is approved for import.
2. The technical team generates the baseline bridge JSON from the cleaned dataset.
3. The Platform Administrator opens `#/baseline-import`.
4. The Platform Administrator selects the generated JSON file.
5. The Platform Administrator runs the smoke test first.
6. If the smoke test succeeds, the Platform Administrator runs the full import.
7. The Platform Administrator waits for the final row count.
8. The MEL Officer checks dashboard and reporting projections.
9. The M&E Manager confirms that the imported baseline is acceptable for prototype reporting.

## 6. Data collection SOP

1. The Data Collector signs in to the portal.
2. The Data Collector opens the assigned form.
3. The Data Collector completes required fields.
4. The Data Collector reviews the form before submission.
5. The Data Collector submits the form.
6. The system stores the submission and versioned payload.
7. The Data Collector reports any validation or submission issue to the MEL Officer.

## 7. Submission review SOP

1. The MEL Officer opens submitted records or reports.
2. The MEL Officer checks completeness, region, beneficiary profile, finance, training, and outcome fields.
3. The Reviewer / Approver checks records that require validation.
4. Corrections are requested where data is incomplete or inconsistent.
5. Approved records are used for dashboard and reporting projections.

## 8. Dashboard review SOP

1. The MEL Officer opens the dashboard.
2. The MEL Officer waits for live data to load.
3. The MEL Officer reviews beneficiary, reporting, financing, regional, training, and outcome cards.
4. The MEL Officer records pending metrics and missing source feeds.
5. The M&E Manager reviews dashboard screenshots and interpretation notes before external sharing.

Do not interpret missing data as zero. Pending states must be reported as pending.

## 9. Reporting SOP

1. The MEL Officer opens the reporting route.
2. The MEL Officer selects the relevant records or reporting period.
3. The MEL Officer exports available data where required.
4. The M&E Manager reviews the report for consistency.
5. The final report includes notes on data source, limitations, and pending operational feeds.

## 10. Change management SOP

1. Any change in hosting, architecture, role model, form structure, or source data must be documented.
2. The client reviews and signs off requirements and design changes before implementation.
3. The technical team implements approved changes in a test environment first.
4. The M&E Manager validates the output.
5. ICT approves deployment to the target CRDB environment.

## 11. Current SOP limitations

These SOPs are draft because the final CRDB deployment strategy is changing. They should be revised after CRDB confirms:

- final hosting model;
- database platform;
- authentication model;
- workflow engine;
- reporting stack;
- user roles;
- support owner;
- production deployment path.
