# App Vision and MVP Strategy

## Current decision

The long-term vision is a reusable Integrated Digital MEL platform for CRDB Sustainable Finance programmes, powered by Dataverse, Microsoft Entra, Power Pages, Power BI, and Power Platform ALM.

TACATDP is the first supported project. It should prove field monitoring, impact tracking, and reporting readiness while preserving seams for a broader sustainable-finance MEL system.

The form runtime should still mirror the useful architecture of ODK Central and ODK Collect for assigned forms, versioned submissions, offline-aware field capture, and evidence handling. That runtime is now one capability inside the larger MEL platform, not the whole product vision.

The near-term deliverable is the July 7, 2026 MVP described in `docs/mvp-july-7.md`:

> One published form assigned to one user, rendered dynamically in Canvas from Dataverse metadata, with draft/save/submit/history and one attachment field.

## Product shape

- **Integrated MEL platform**: programmes, projects, beneficiaries, financing activities, field monitoring, evidence, indicator results, dashboards, reports, roles, audit, and configuration.
- **ODK Central equivalent**: Dataverse plus future admin surfaces for forms, versions, assignments, submissions, exports, monitoring, and publishing.
- **ODK Collect equivalent**: a Power Pages / ODK Web Forms runtime that authenticates through CRDB Microsoft identity, shows assigned forms, renders form definitions, saves drafts where supported, submits data, and shows history.
- **Compiler/import path**: seed one form manually or from a small JSON/YAML artifact for MVP; build XLSForm-to-Dataverse metadata compilation after the runtime path is proven.

## Why a metadata renderer now

Generating one Power App per form is not the platform architecture. It would create duplicated screens, formulas, permissions, and ALM work for every instrument.

The app should instead render metadata:

- `Forms`;
- `FormVersions`;
- `Sections`;
- `Questions`;
- `Choices`;
- `ValidationRules`;
- `FormAssignments`.

Runtime data should be generic:

- `Submissions`;
- `SubmissionAnswers`;
- `SubmissionFiles`.

## MVP boundary

The July 7 MVP is intentionally narrow:

1. Use Power Apps / Entra authentication; no custom login.
2. Show assigned published forms for the current user.
3. Render text, integer, decimal, date, select one, select many, file/photo attachment, and GPS if quick enough.
4. Save drafts and submit using `Draft`, `Submitted`, and `Locked` statuses.
5. Allow edits until locked.
6. Show the user's own submission history for a selected form.
7. Seed one form; do not build the full XLSForm compiler yet.

## Deferred platform capabilities

After the first working vertical slice, add:

- sustainable-finance programme shell and roadmap modules;
- beneficiary/customer registry;
- loan, investment, guarantee, and insurance integration surfaces;
- climate rationale and hazard/risk modules;
- ESS/risk compliance tracking;
- indicator result model for baselines, targets, means of verification, and disaggregation;
- GCF/URT reporting templates and dissemination products;
- XLSForm parser/compiler;
- repeat groups and nested repeats;
- richer XPath expression support;
- offline-first sync and conflict handling;
- barcode;
- admin publishing UI;
- version migration;
- dashboards and export projections;
- richer locking/review workflows.

## Relationship to older artifacts

Older TACATDP generated screen artifacts and section-specific plans remain useful as source material and reference, but they are not the default implementation path for the platform. The active implementation path is the metadata-driven MVP documented in `docs/mvp-july-7.md` and the updated `docs/tacatdp-prototype-slice-1/` artifacts.
