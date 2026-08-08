# 2. Prototype Scope

## Prototype Summary

The current Sustainable Finance MEL Platform prototype uses TACATDP monitoring as a proof-of-concept use case for digital Monitoring, Evaluation, and Learning. The current implementation is based on the TACATDP impact evaluation form and Power Platform deployment work.

The prototype demonstrates how programme/project data can be collected digitally, structured for monitoring, and surfaced through simple portal-level indicators. TACATDP is the first demonstration case; it is not the full boundary of the intended platform.

## In Scope

The prototype scope includes:

- baseline data collection from beneficiaries through a deployed portal form;
- structured form sections derived from the TACATDP XLSForm;
- reference data for locations, CRDB branches, and coded choices;
- beneficiary-linked submission records;
- lightweight beneficiary entity modeling;
- basic portal KPI visualisation for immediate monitoring;
- documentation for users, administrators, reviewers, and future developers.

The prototype should also document how the same platform pattern can later support other Sustainable Finance Unit use cases, even if they are not implemented in the current prototype.

## Beneficiary Entity Model

The prototype should model beneficiaries as identifiable records linked to baseline submissions.

At prototype level, the beneficiary model should remain lightweight:

| Entity | Purpose |
|---|---|
| Beneficiary | Identifies the person, household, group, or enterprise being monitored. |
| Submission / Baseline Assessment | Stores one baseline form submission linked to a beneficiary. |
| Reference Data | Supports location, branch, value-chain, and coded-choice filtering. |

Minimum beneficiary fields should include:

- beneficiary identifier;
- beneficiary name or display label where allowed;
- beneficiary type or grouping where applicable;
- sex, age category, youth/women/social inclusion attributes where collected;
- region, district, ward, and village;
- value chain or intervention category;
- source submission metadata.

This supports deduplication, follow-up monitoring, and future baseline-to-endline comparisons.

## Portal KPI Visualisation

Because Power BI access and permissions may take time, the prototype should include basic portal-level visualisation for key indicators.

Recommended prototype KPIs:

- total baseline submissions;
- total beneficiaries captured;
- beneficiaries by region/district;
- beneficiaries by value chain;
- gender/youth/social inclusion summary where data exists;
- form completion or submission status;
- baseline production, yield, income, water, or GHG indicators where enough data exists.

The dashboard should be documented as direct portal visualisation. Power BI should be documented as a future analytics enhancement, not as a dependency for prototype acceptance.

## Out of Scope for Prototype

The prototype does not yet claim:

- full enterprise beneficiary master-data governance;
- full Power BI semantic model and dashboard deployment;
- production-grade integration with CRDB core systems;
- automated data quality workflow and approval pipeline;
- complete offline-first mobile field collection;
- full production support, backup, disaster recovery, and monitoring.

These belong to the scalable product vision.

The prototype also does not yet implement broader non-TACATDP operating use cases. Those should be documented as future configurable programme/project, facility, process, resource, indicator, and evidence capabilities rather than as specific named initiatives.

## Acceptance Position

The prototype is acceptable if it demonstrates:

- working baseline data collection;
- clear beneficiary-linked data structure;
- visible monitoring indicators on the portal;
- documented deployment and administration process;
- known limitations and realistic roadmap toward production scale.
