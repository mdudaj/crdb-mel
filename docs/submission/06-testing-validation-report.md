# Sustainable Finance MEL Platform Testing and Validation Report

## Purpose

This report defines how the Sustainable Finance MEL Platform prototype should be validated for submission. It focuses on the TACATDP proof-of-concept workflow and the agreed prototype revisions.

## Validation Scope

| Area | Validation target |
|---|---|
| Portal access | Approved users can reach the Power Pages site. |
| Authentication | Users sign in with approved tenant accounts. |
| Form workflow | Users can open and complete the baseline form. |
| Validation | Required and invalid visible fields are handled correctly. |
| Dataverse persistence | Submitted records are stored in the current data layer. |
| Beneficiary linkage | Submissions can be associated with beneficiary records or beneficiary summary identifiers. |
| KPI dashboard | Portal displays agreed key indicators. |
| Documentation | Prototype and future-product claims are separated. |

## Test Cases

| ID | Test | Expected Result | Status |
|---|---|---|---|
| TST-01 | Open portal URL as an approved user | Portal loads successfully after sign-in | To verify |
| TST-02 | Open assigned TACATDP baseline form | Form is visible to the assigned user | To verify |
| TST-03 | Attempt to continue with missing required visible fields | User sees validation errors and cannot continue/submit | To verify |
| TST-04 | Complete required visible fields | User can proceed through the form | To verify |
| TST-05 | Submit a valid baseline record | Submission is stored in Dataverse | To verify |
| TST-06 | Check beneficiary linkage | Submission references a beneficiary identity or beneficiary summary model | To verify |
| TST-07 | Open portal KPI dashboard | KPI cards/charts render without Power BI dependency | To verify |
| TST-08 | Verify dashboard data source | Dashboard values use live records or clearly labelled demo data | To verify |
| TST-09 | Test non-admin user access | User has site visibility, portal role, and active assignment | To verify |
| TST-10 | Review documentation pack | Docs separate prototype capability from future scalable product vision | In progress |

## Evidence Required

For final submission, collect:

- screenshots of portal sign-in or landing page;
- screenshots of the baseline form;
- screenshots of validation behavior;
- screenshots of a successful submission or record confirmation;
- screenshots of the portal KPI dashboard;
- exported or inspected Dataverse records where allowed;
- notes on any failed tests and workarounds.

## Known Validation Constraints

- Power BI integration is not required for prototype acceptance.
- Portal KPI visualisation can be implemented directly on the portal.
- User access depends on tenant, Power Pages visibility, contact, web role, and assignment configuration.
- Production readiness is not claimed until architecture, security, governance, and support checks are complete.

## Result Summary

Current status: documentation validation is in progress. Runtime validation should be completed after the final prototype revision for beneficiary modeling and portal KPI visualisation.
