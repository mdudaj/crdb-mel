# 11. Traceability Matrix

## Purpose

This matrix links Sustainable Finance MEL Platform objectives to requirements, prototype features, evidence, validation, and future-product gaps.

## Traceability

| Objective | Requirement | Prototype Feature | Evidence / Validation | Future Product Gap |
|---|---|---|---|---|
| Digitize beneficiary baseline data collection | Users must submit structured baseline data through a digital form | Power Platform/Power Pages baseline form derived from TACATDP XLSForm | Portal deployment check, form walkthrough, screenshots, test submissions | Offline collection, stronger data quality workflow |
| Prove the reusable SFU platform concept | TACATDP must be documented as the proof-of-concept use case, not the whole platform | Submission docs separate TACATDP prototype from Sustainable Finance MEL Platform vision | Documentation review | Configurable programme/project setup for multiple use cases |
| Structure data for monitoring and reporting | Submitted data must map to stable lists/entities | Generated schema and section-based data model | `schemas/sharepoint-lists-schema.json`, import templates, schema docs | Governed production data model and migration plan |
| Track beneficiaries beyond one-off submissions | Beneficiaries should be identifiable and linkable to submissions | Lightweight beneficiary entity model linked to baseline submissions | Beneficiary scope artifact and data model review | Central beneficiary registry, deduplication, master-data governance |
| Provide immediate monitoring visibility | Reviewers should see key indicators without waiting for Power BI | Portal-level KPI cards/charts | Portal dashboard screenshots and manual validation | Power BI semantic model and governed reporting workspace |
| Support technical handover | Admins/developers need deployment and maintenance guidance | Deployment/admin guide and project `AGENTS.md` | Documentation review, PAC command notes | Formal support model and release management |
| Communicate limitations honestly | Reviewers must understand what is prototype vs future product | Known limitations and future-product vision docs | Documentation review | Production readiness plan and budget |
| Support future Sustainable Finance Unit use cases | Platform should support different programmes/projects and operational impact domains | Future-product vision lists configurable monitored entities and example use cases | Architecture/roadmap review | Generic data model, project templates, indicator catalogue, dashboards |
| Avoid locking production to prototype technology | Future product must evaluate a robust enterprise architecture beyond Power Pages where needed | Current architecture distinguishes Power Pages + Dataverse prototype from future app/API/DBMS direction | Architecture document review | Target stack decision, hosting model, DBMS selection, integration architecture |

## Status Legend

| Status | Meaning |
|---|---|
| Complete | Implemented and validated in the prototype |
| In progress | Partially implemented or being revised |
| Planned | Agreed for prototype revision but not yet implemented |
| Future | Belongs to scalable product vision |

## Current Open Validation Items

- Confirm final deployed portal version after latest changes.
- Capture screenshots for baseline form workflow.
- Capture screenshots for portal KPI dashboard once added.
- Verify beneficiary-linked data behavior after the lightweight model is implemented.
- Record Power BI as future-product scope unless tenant permissions are granted and integration is verified.
