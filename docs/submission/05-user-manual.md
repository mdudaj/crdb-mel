# 5. User Manual

## Purpose

This manual explains how users interact with the Sustainable Finance MEL Platform prototype. The current prototype uses TACATDP monitoring as the proof-of-concept use case.

## User Groups

| User | Main actions |
|---|---|
| Beneficiary/respondent | Provide baseline information where self-service access is enabled. |
| Enumerator/data collector | Capture beneficiary baseline data through the portal form. |
| MEL reviewer | Review submitted records and monitor basic KPI indicators. |
| Administrator | Manage access, deployment configuration, and troubleshooting. |

## Accessing the Prototype

1. Open the deployed Power Pages portal URL provided by the administrator.
2. Sign in using the approved work/school account.
3. If access is denied, contact the administrator. Access may require both site visibility permission and application-level role/assignment configuration.

## Baseline Data Collection Workflow

1. Sign in to the portal.
2. Open the assigned TACATDP baseline monitoring form.
3. Complete each visible section.
4. Review validation messages before continuing.
5. Save or submit the form according to the available action.
6. Confirm that the submission is recorded.

## Beneficiary Information

The prototype should support beneficiary-linked records. This means a submitted baseline assessment should be associated with a beneficiary identity or beneficiary summary record instead of existing only as a one-off form response.

This supports later follow-up, monitoring, and comparison across reporting periods.

## Portal KPI Dashboard

The prototype should expose basic monitoring indicators directly in the portal. These may include:

- total baseline submissions;
- total beneficiaries captured;
- beneficiary coverage by location;
- beneficiary coverage by value chain;
- social inclusion indicators where data exists;
- submission status or completion counts.

If live data is not yet available, any demo or sample dashboard data must be clearly labelled.

## Common Access Issues

| Issue | Likely cause | Action |
|---|---|---|
| Sign-in succeeds but portal access is denied | User lacks Power Pages site visibility or app role/assignment | Ask administrator to verify site visibility, contact, web role, and active assignment. |
| User sees no assigned form/project | Assignment is missing or inactive | Ask administrator to verify active assignment records in Dataverse. |
| Form does not submit | Required/visible fields are missing or invalid | Review validation messages and complete required fields. |
| Dashboard looks empty | No submitted records or data permissions issue | Confirm submissions exist and reviewer permissions are configured. |

## User Responsibilities

- Enter accurate data.
- Do not share account credentials.
- Report validation, access, or data issues to the administrator.
- Do not treat the prototype as production-ready unless formally approved.

## Prototype Limitation Notice

The current system is a proof-of-concept prototype. It demonstrates the MEL workflow, data structure, and portal-level visibility, but full production readiness requires additional security, governance, analytics, support, and architecture review.
