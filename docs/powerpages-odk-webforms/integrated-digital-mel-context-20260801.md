# Integrated Digital MEL Context - CRDB SFU / TACATDP

Date: 2026-08-01

## Purpose

Record the product context received from CRDB Sustainable Finance Unit (SFU)
for TACATDP so future platform, UX, data-model, and reporting work remains
aligned with the client's MEL operating model without expanding the current
delivery scope beyond the agreed TACATDP field monitoring and impact tracking
release.

This is a context and direction artifact. It is not approval to implement every
future module in the current scope.

## Evidence Reviewed

- `RECAP FOR_MEL INTERACTIVE PLATFORM-SYSTEM TO DAMAX_EXPECTAIONS.docx`
  - 1,152 extracted paragraphs and 177 table rows.
  - Emphasizes an integrated Results-Based Management (RBM) system aligned to
    TACATDP impact logic: inputs -> activities -> outputs -> outcomes.
  - Requires role-based access for M&E Manager, Regional Managers,
    Relationship Officers, and field enumerators.
  - Groups field data into five practical sections:
    Farmer and Farm Profile Information; Crop and Climate Rationale;
    Beneficiary Quantification; GHG and Water Efficiency; Environmental
    Assessment and Risk Management Compliance.
- `TACATDP_DETAILED M&EPLAN_TO BE TRANSLATED ON DIGITAL MELPLATOFOM AND REPORTING UNDER DEVELOPMMENT .xlsx`
  - 27 sheets.
  - Includes green-loan portfolio sheets, ICMA impact-reporting templates,
    project results framework, M&E detailed plans, component matrices,
    GCF/AGF indicators, Component 1 and Component 2 impact reports, dashboard
    metric examples, and web-based M&E reporting references.
- `TACATDP_M&E PLAN (Comp 1&2) end to end_to be intergrated MEL PLATFORM.xlsx`
  - 14 sheets.
  - Includes project description, fund reflow, logical framework, data source
    and data collection/delivery plans, performance monitoring/evaluation
    plans, performance result narratives, challenges, lessons learned, case
    studies, dissemination plan, indicator definitions, and activity targets.
- WhatsApp/PDF-image extracts shared by Hailo.
  - Confirm the expected Digital MEL Tool functional components:
    questionnaires, dashboards/data visualization, savings/performance
    tracking, onboarding/field capture, SROI/mandatory parameters, climate risk
    integration, adaptive impact indicators, geo heatmaps, feedback capture,
    interactive dashboards, and component activity matrix.

## Client Operating Context

The client is CRDB Bank. The primary business owner is the Sustainable Finance
Unit. TACATDP is the first supported project/programme and focuses on climate
resilient food-crop agriculture financing funded through the GCF.

The platform must help CRDB show that sustainable finance products are not only
disbursed, but monitored, verified, and translated into measurable climate
resilience and development results.

## Product Interpretation

TACATDP should be treated as the first configured programme/project in an
Integrated Digital MEL platform for Sustainable Finance, not as the permanent
identity or hard-coded scope of the system.

The immediate product remains:

- TACATDP field monitoring;
- project/form assignment;
- geo-referenced data capture through Power Pages;
- submission review, data view, export, and Power BI readiness;
- user/access management and system activity diagnostics.

The future-ready platform foundation should preserve clear seams for:

- programmes and projects;
- beneficiaries/farmers/groups/AMCOS/SACCOS/enterprises;
- loan/investment/guarantee/insurance records;
- financed activity or climate-smart technology;
- monitoring visit;
- field evidence such as GPS, photos, timestamps, and submitter;
- climate rationale and hazard/risk context;
- beneficiary quantification and disaggregation;
- ESS/risk compliance;
- indicator results and calculated measures;
- reporting templates and dissemination products.

## Recommended Domain Model Direction

Use this conceptual chain when designing future data, UX, and reporting
capabilities:

```text
Programme
  -> Project
  -> Beneficiary / Customer / Farmer Group
  -> Financing Activity / Climate-Smart Investment
  -> Monitoring Visit
  -> Evidence
  -> Indicator Result
  -> Report / Dashboard / Export
```

This chain translates the client documents into a practical software model
without copying workbook sheets directly into route names or tables.

## Current Scope Boundary

For the current TACATDP release, keep the visible shell lean:

- Dashboard
- Projects
- Reporting
- User & Access
- System Activity

Do not implement the full national MEL shell, MIS/CRM integration, TMA early
warning integration, SROI/GHG calculation engine, full beneficiary registry,
or automated GCF reporting templates in the current release unless separately
approved and funded.

For roadmap/future-phase modules, use explicit future-phase language:

> Future phase module. Planned for the Integrated Digital MEL platform and not
> enabled in the current TACATDP field monitoring release.

Avoid wording such as "missing", "not delivered", or "dead end".

## Functional Themes To Preserve

The evidence points to these durable platform themes:

1. **RBM/RMF traceability**
   - Inputs, activities, outputs, outcomes, indicators, baselines, targets,
     means of verification, and reporting products must remain linkable.
2. **Field monitoring and verification**
   - Online/offline capture, GPS/photo evidence, edit/replace/version history,
     and audit trail are not optional for the mature platform.
3. **Sustainable finance portfolio evidence**
   - The system should eventually connect loan/customer/investment records to
     climate-smart practices and observed outcomes.
4. **Beneficiary quantification**
   - Direct/indirect beneficiaries, gender, youth, vulnerable groups, farmer
     groups, training records, and value-chain participant categories require
     calculation and consistency checks.
5. **Climate and ESS accountability**
   - Climate rationale, hazards, water efficiency, GHG/co-benefits, insurance,
     guarantees, and ESS/risk compliance require governed data structures.
6. **Reporting products**
   - Dashboards, Power BI, GCF/URT templates, APR annexes, semi-annual briefs,
     policy briefs, case studies, and public snapshots are reporting outputs,
     not just charts.

## UX Implications

- Do not mirror workbook sheets as app navigation.
- Design for bank workers and SFU managers, not researchers.
- Collect remains contextual to a project or monitoring assignment.
- Admin/SFU manager roles may see future-phase modules for roadmap positioning;
  collectors should see only their actionable work.
- Dashboards should emphasize attention, coverage, data quality, field progress,
  and reporting readiness before decorative analytics.
- Data views should disclose scope and freshness because reporting may combine
  field submissions, imported portfolio data, and derived indicators.

## Implementation Instructions For Future Agents

Before implementing new TACATDP/SFU MEL UX, inspect:

- this file;
- `managed-service-ux-governance.md`;
- `operational-ux-research-and-plan-20260730.md`;
- `docs/app-vision.md`;
- current Dataverse schema artifacts under `schemas/dataverse/`;
- current Power Pages SPA source and validator.

Use professional product judgement to translate the MEL documents into coherent
roles, workflows, data contracts, and reporting surfaces. Do not treat every
spreadsheet sheet, heading, or example table as a route or table requirement.
