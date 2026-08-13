# Prototype acceptance scope — 2026-08-12

## Purpose

This artifact defines what must be true before the Sustainable Finance MEL Platform prototype can be treated as ready for stakeholder review using TACATDP as the proof-of-concept programme.

Acceptance here means the prototype is suitable for demonstration, review, and software-development documentation. It does not mean the platform is production-ready, fully generalized, or fully connected to all future Dataverse entities.

## Evidence base

- `docs/powerpages-odk-webforms/requirements.md`
- `docs/powerpages-odk-webforms/acceptance-criteria.md`
- `docs/powerpages-odk-webforms/slice-checklist.md`
- `docs/powerpages-odk-webforms/tacatdp-dashboard-echarts-slice-20260810.md`
- `docs/powerpages-odk-webforms/beneficiary-detail-model-slice-20260811.md`
- `docs/powerpages-odk-webforms/beneficiary-readonly-actions-mshirika-deployment-20260812.md`
- `docs/powerpages-odk-webforms/crdb-microsoft-resources-permissions-20260813.md`
- `docs/powerpages-odk-webforms/managed-service-ux-governance.md`
- `docs/powerpages-odk-webforms/monitoring-tool-ux-design-system.md`
- `schemas/dataverse/odk-central-inspired-mvp-schema.json`
- `schemas/dataverse/beneficiary-entity-extension-schema.json`
- `ubongo/projects/crdb-mel/overview.md`
- `ubongo/projects/crdb-mel/decisions.md`

## Scope boundary

The accepted prototype must demonstrate:

1. A Power Pages-hosted, authenticated Microsoft-managed MEL tool.
2. A CRDB-branded application shell with route separation.
3. A TACATDP dashboard using demonstration data and ECharts visualisation.
4. A beneficiary registry and detail model that previews the future monitored-entity model.
5. A Power Pages-hosted web forms/XForms data-collection path backed by Dataverse.
6. Saved submitted-record review and reporting/export pathways.
7. User/access-management surfaces that explain onboarding and operational access state.
8. Explicit prototype limitations and future-product direction.
9. A clear CRDB Microsoft resource and permission model for the scalable platform path.

The accepted prototype must not imply:

- official CRDB Bank or Green Climate Fund statistics;
- complete production security review;
- complete offline sync;
- complete binary attachment persistence;
- complete beneficiary master-data persistence;
- unrestricted CRDB environment review access;
- Power BI integration being available inside the portal.

## Product requirements

| ID | Requirement | Prototype acceptance rule |
|---|---|---|
| PR-01 | Authenticated Microsoft-managed host | The prototype runs through Power Pages and uses Power Pages authentication; no custom login or client secret is introduced. |
| PR-02 | Route ownership | The shell owns navigation, route title, global actions, and footer. Page content must not duplicate large route headers. |
| PR-03 | Dashboard visualisation | Dashboard is a dedicated TACATDP operational visualisation route, not mixed with form operations. |
| PR-04 | Demonstration-data governance | Every KPI/beneficiary/dashboard value that is not live official data must be identifiable as prototype or demonstration data. |
| PR-05 | Beneficiary model preview | Beneficiaries are modeled as richer monitored entities in the prototype UI, with technical Dataverse mapping behind disclosure. |
| PR-06 | Collection workflow | A signed-in assigned user can reach the form runner, load the current TACATDP XForm-backed form, submit online, and receive visible success or failure status. |
| PR-07 | Saved-record workflow | Submitted records are visible as shared authenticated records where table permissions allow it; Edit must version an existing submission rather than creating a duplicate record. |
| PR-08 | Reporting/export pathway | Data/reporting pages must show a reviewable path to reporting projections, CSV export, and future Power BI connection without claiming Power BI embed is complete. |
| PR-09 | Access-management pathway | User/access routes must show onboarding, role, activation, audit, and configuration concepts without enabling unsafe writes outside approved flows. |
| PR-10 | Deployment/package hygiene | Power Pages package staging must verify Home references, referenced assets, no duplicate partial URLs, and deployed JavaScript syntax. |
| PR-11 | Environment clarity | Mshirika and CRDB environment differences must be stated before stakeholder review. |
| PR-12 | Future-product seam | The prototype must preserve the broader platform direction for multiple programmes/projects and avoid hard-coding TACATDP as the platform schema. |

## User stories

| ID | User story | Acceptance |
|---|---|---|
| US-01 | As a MEL Officer, I can open the dashboard and understand TACATDP financing, reach, regional implementation, loan performance, and climate outcomes within a few seconds. | KPI row, analytics grid, Tanzania mainland regional map, technology financing, loan performance, training, submissions, and impact goal are visible and labelled as demonstration data. |
| US-02 | As a MEL Officer, I can move from dashboard insight to beneficiary records. | Dashboard drill-through opens Beneficiaries with filters preserved in the route hash. |
| US-03 | As a MEL Officer, I can inspect a beneficiary as an operational entity, not only as one form row. | Detail drawer shows profile, finance, technology, training, outcomes, data lineage, record matching, group/member links, location history, and collapsed technical mapping. |
| US-04 | As a field or bank officer, I can open an assigned TACATDP form and submit online. | The form loads from Dataverse-backed XForm data and submit writes through Power Pages `/_api`, preserving canonical submission payload. |
| US-05 | As a reviewer, I can inspect submitted records and understand whether the system supports shared review. | Saved records show shared submitted records readable by table permissions, with search, pagination, owner/version metadata, and Edit action. |
| US-06 | As an administrator, I can understand user onboarding state and access-management controls. | User/access pages show activation, roles, onboarding queue, audit/activity, and configuration state with safe write boundaries. |
| US-07 | As a stakeholder, I can understand what is prototype-only and what moves into the future product. | Review package includes limitations, future-product vision, data-model path, and explicit non-goals. |

## Acceptance checklist

### A. Application shell and navigation

- [x] CRDB-branded shell is present.
- [x] Left navigation separates Dashboard, Programme, Monitoring & Evaluation, Insights, and Administration.
- [x] Dashboard route is dedicated to visualisation.
- [x] Operational form/workbench content is moved outside the dashboard.
- [x] Route title/subtitle live in the shell header.
- [x] Footer contains last updated, data synced, and CRDB/Sustainable Finance Unit context.
- [ ] Stakeholder browser review confirms no route appears visually broken after latest Mshirika deployment.

### B. Dashboard visualisation

- [x] Dashboard uses Apache ECharts through `vue-echarts`.
- [x] Dashboard uses local Tanzania ADM1 GeoJSON rather than external map tiles.
- [x] Zanzibar regions are masked for mainland Tanzania view.
- [x] Dashboard includes KPI cards, loan portfolio, disbursement trend, regional map, technologies financed, loan performance, climate outcomes, training, recent submissions, and impact goal.
- [x] Chart spacing regressions are guarded by `npm run test:material`.
- [x] Demonstration data is documented.
- [ ] Stakeholder browser review confirms dashboard layout remains visually acceptable at target desktop width.
- [ ] Tablet/phone review remains pending unless explicitly excluded from prototype acceptance.

### C. Beneficiary registry and detail model

- [x] Beneficiaries route exists with metric cards, filters, search, desktop table/list, and mobile card fallback.
- [x] Beneficiary records are richer prototype entities with finance, training, technology, outcome, submission, identity, group, and location context.
- [x] Detail drawer presents business sections before technical mapping.
- [x] Technical Dataverse mapping is collapsed behind disclosure.
- [x] Footer actions are read-only prototype interactions.
- [x] `Export detail` shows a planned notice and generates no file.
- [x] Validator guards the detail-drawer rules.
- [ ] Stakeholder browser review confirms the drawer interaction is acceptable after latest Mshirika deployment.
- [ ] Production Dataverse beneficiary master table creation remains unapproved and out of prototype acceptance unless the client requires persistence.

### D. Collection and submission workflow

- [x] Power Pages-hosted web forms/XForms path exists.
- [x] Full revised TACATDP form definition was compiled and seeded through Dataverse file-backed XForm storage.
- [x] Submission header/version write path is implemented through Power Pages `/_api`.
- [x] Attachment metadata row persistence is implemented.
- [x] Direct browser binary upload failure is documented and does not block metadata submission.
- [x] Runtime-load markers are not treated as real drafts.
- [ ] Browser-level submit verification against the current hosted environment is still required as final acceptance evidence.
- [ ] Browser verification that the full compiled form loads in the signed-in site remains required.
- [ ] Editable local draft resume remains deferred.
- [ ] Offline sync queue remains deferred.

### E. Saved records, reporting, and export

- [x] Saved records are designed as shared authenticated submitted records, not current-user-only records.
- [x] Saved records support search and pagination in the prototype UI.
- [x] Edit uses latest submission XML and writes a new version for the selected submission.
- [x] Reporting projections and CSV export path exist.
- [x] Power BI guidance panel exists as a future integration path.
- [ ] Browser verification that authenticated reporting reads return rows without `9004010A` remains required.
- [ ] Browser verification that CSV download works after cache refresh remains required.
- [ ] Power BI Desktop connection to Dataverse reporting tables remains optional for prototype acceptance unless explicitly required by the client.

### F. User and access management

- [x] User & Access route exists.
- [x] Users, add/onboarding, roles, activity, and configuration concepts are represented.
- [x] Access-management UX uses Material-style list/surface patterns.
- [x] Invitation/access activation lessons are documented.
- [x] Mshirika private-site access gate is documented.
- [ ] CRDB user review access remains environment-dependent and should not block Mshirika prototype acceptance.
- [ ] If CRDB review is required, verify site visibility, invitation redemption, external identity, web role, and assignment together.

### G. Deployment and environment readiness

- [x] Mshirika has the latest reviewed deployment marker `beneficiary-readonly-actions-20260812-029`.
- [x] Latest Mshirika upload was verified by post-upload download, asset existence checks, and `node --check`.
- [x] Package hygiene validators exist for duplicate partial URLs and referenced assets.
- [x] CRDB full-package/duplicate-webfile issue is documented.
- [ ] CRDB may lag behind the latest Mshirika preview until an explicit CRDB deployment is approved and verified.
- [ ] Before any CRDB update, verify all required assets in the upload package to avoid a blank-page recurrence.

## Definition of done for prototype acceptance

The prototype scope is acceptable when:

1. Mshirika review confirms the current visual state is acceptable.
2. The collection workflow has one current signed-in browser proof: form load, submit, saved-record return, and visible status.
3. Saved/reporting browser reads are verified or explicitly marked as demo-only for the submission package.
4. Known deferred items are listed in the review package, not hidden.
5. CRDB deployment status is stated separately from Mshirika preview status.
6. The software-development documentation pack references this scope and gap matrix.

## Explicitly deferred from prototype acceptance

- Multi-project runtime generalization.
- Production-grade beneficiary master-data persistence.
- Offline sync queue.
- Editable local draft restore.
- Production-grade binary attachment storage.
- Power BI embedded dashboards.
- Production role/security hardening.
- Self-service form-definition authoring/publishing UI.
- Production data warehouse or Fabric/Synapse architecture.

## Scalable platform governance link

Before continuing beyond prototype validation, use `docs/powerpages-odk-webforms/crdb-microsoft-resources-permissions-20260813.md` to explain which CRDB Microsoft resources and permissions are required for pilot, handover, and production-scale operation.

This matters because Power Pages private-site visibility, invitation redemption, Dataverse security roles, Power Pages web roles, table permissions, Web API site settings, Power Automate ownership, Power BI workspace access, DLP policies, and ALM solution ownership are separate control gates. A working prototype in one environment does not automatically prove that CRDB has the resource ownership and permissions needed to operate the scalable MEL platform.

## Next implementation gate

Use `docs/powerpages-odk-webforms/prototype-gap-matrix-20260812.md` as the remaining execution queue. Do not start another UI polish slice unless it closes a listed acceptance gap or the user explicitly reprioritizes.
