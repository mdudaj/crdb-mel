# 8. Known Limitations

## Purpose

This document records known prototype limitations so reviewers can distinguish between current proof-of-concept capability and future production requirements.

## Prototype Limitations

| Limitation | Impact | Future Resolution |
|---|---|---|
| TACATDP is the only implemented proof-of-concept use case | The platform concept is demonstrated through one programme workflow | Add configurable programme/project templates and generic monitored entities |
| Beneficiary model is lightweight | It supports prototype tracking but not full master-data governance | Implement central beneficiary registry, deduplication, lifecycle, audit, and ownership rules |
| Portal KPI dashboard is basic | Immediate monitoring is possible, but analytics depth is limited | Add governed analytics layer and semantic reporting model |
| Power BI is not yet connected | Advanced dashboards are not part of the current prototype | Integrate Power BI or approved BI tool after permission, licensing, and governance approval |
| Power Pages is the prototype shell | It may not satisfy all long-term enterprise UX, integration, or scalability requirements | Review target frontend/application architecture before production |
| Dataverse is the current prototype data store | It must be reviewed against enterprise scale, integration, and governance needs | Decide final DBMS/data platform through architecture review |
| Access setup depends on tenant/environment configuration | User onboarding may fail if site visibility, roles, or assignments are incomplete | Formalize access provisioning and support procedures |
| Offline-first collection is not complete | Field collection may depend on connectivity | Define offline requirements and synchronization model |
| Production operations are not formalized | No full SLA, backup, monitoring, or incident process is claimed | Add production operations plan before rollout |

## Claims Not Made

The current prototype does not claim:

- full production readiness;
- full enterprise scalability;
- complete multi-programme configuration;
- complete Power BI implementation;
- complete offline synchronization;
- integration with internal enterprise systems;
- formal support or SLA coverage.

## Submission Position

The prototype should be evaluated as a proof of concept showing:

- digital baseline collection;
- beneficiary-linked monitoring structure;
- Dataverse-backed prototype data model;
- portal-level KPI visibility;
- clear path toward a scalable Sustainable Finance MEL Platform.
