# Sustainable Finance MEL Platform Documentation Plan

## Purpose

This documentation pack supports delivery and assessment of the Sustainable Finance MEL Platform prototype while also presenting the proposed scalable product vision if the prototype is accepted.

TACATDP monitoring is the proof-of-concept use case. The intended platform is broader: it should support different Sustainable Finance Unit programmes/projects and operational impact initiatives, not only one beneficiary monitoring form.

The pack must clearly separate:

- what the prototype currently does;
- what will be added in the immediate prototype revision;
- what belongs to the future scalable product.

## Audience

- Non-technical reviewers: need to understand the problem, system purpose, user workflows, benefits, limitations, and adoption path.
- Technical reviewers: need to understand architecture, data model, deployment, authentication, testing, risks, and maintainability.
- Project sponsors: need to decide whether the prototype is acceptable and what investment is needed for a production-grade Sustainable Finance MEL Platform.

## Current Prototype Positioning

The current prototype supports baseline data collection from beneficiaries through a deployed Power Platform/Power Pages form derived from the TACATDP impact evaluation workstream.

The prototype should be documented as a proof of concept for digital MEL data collection and monitoring, not as the full Sustainable Finance MEL Platform and not as a fully production-hardened enterprise MEL platform.

## Immediate Prototype Revision

Before final documentation delivery, the prototype scope should be revised to include:

1. A lightweight beneficiary entity model.
2. Portal-level KPI visualisation for key monitoring indicators.

These additions increase assessment value without waiting for full Power BI integration or enterprise master-data governance.

## Future Product Positioning

If accepted, the proposed product should become a scalable Sustainable Finance MEL Platform with:

- configurable programme/project setup;
- central beneficiary registry/master data;
- robust access control and audit;
- governed data model;
- reviewed target application architecture beyond the Power Pages proof-of-concept;
- backend service/API and enterprise DBMS or approved governed data platform where required for scale;
- Power BI or semantic analytics layer;
- operational support, monitoring, backup, and release management;
- integration readiness for approved CRDB systems.

The documentation should show that the same platform concept can support a broader Sustainable Finance Unit operating scope, including configurable programmes, projects, facilities, operational processes, resources, activities, indicators, evidence, and institutional impact initiatives.

## Documentation Set

```text
docs/submission/
  00-documentation-plan.md
  01-executive-overview.md
  02-prototype-scope.md
  03-requirements-specification.md
  04-current-architecture.md
  05-user-manual.md
  06-testing-validation-report.md
  07-deployment-admin-guide.md
  08-known-limitations.md
  09-future-product-vision.md
  10-implementation-roadmap.md
  11-traceability-matrix.md
```

## Writing Rules

- Use `Sustainable Finance MEL Platform` as the current product/system name.
- Use `TACATDP` only for the original programme, source XLSForm, deployed list/schema names, and historical implementation context.
- Describe TACATDP as the proof-of-concept use case, not as the platform boundary.
- Do not claim Power BI integration exists unless it is actually connected and verified.
- Do not claim production readiness. State production readiness requirements under the future-product vision.
- Present Power Pages + Dataverse as the current prototype architecture, not as the final enterprise architecture by default.
- Every major requirement should map to evidence, implementation status, and test/validation status.

## Microsoft Writing Style Guide Rules

Use Microsoft Writing Style Guide principles for all submission-facing documents:

- Lead with the most important point.
- Use short, direct sentences.
- Use familiar words and avoid unnecessary jargon.
- Prefer active voice.
- Use `must` for requirements instead of `shall`.
- Write for scanning first, then reading.
- Keep paragraphs focused and brief.
- Use sentence-style capitalization in headings where practical.
- Use inclusive, accessible language.
- Use clear verbs for actions and procedures.
- Avoid directional-only instructions such as “above” or “below” when a specific reference is clearer.
- Define acronyms before using them where readers may not know them.

## Definition of Done

The documentation pack is ready when:

- prototype and future-product claims are clearly separated;
- beneficiary modeling and portal KPI visualisation are reflected in scope and requirements;
- requirements map to prototype features and tests;
- deployment/authentication notes reflect actual PAC/tenant experience;
- known limitations are explicit;
- next steps toward the scalable product are documented.
