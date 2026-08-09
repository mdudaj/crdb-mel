# ADR 0005: Staged XLSForm Self-Service Import

Status: proposed
Date: 2026-07-15

## Context

TACATDP currently compiles and publishes revised XLSForms through developer-run Python and Dataverse scripts. Bank operations users need to upload a revised workbook from the project portal without exposing implementation internals or risking an immediate change to active data collection.

Power Pages supports invoking solution-aware cloud flows with a file parameter and web-role authorization. The existing compiler is Python/pyxform based, the generated TACATDP XForm is too large for the current memo column, and the Dataverse schema already separates stable forms, versions, attachments, and assignments.

## Decision

Use a staged, asynchronous import workflow:

- Power Pages sends the workbook to a role-secured, solution-aware cloud flow.
- The flow creates a Dataverse import job, persists the source workbook, and dispatches compilation to an approved Python service running pinned pyxform.
- Successful compilation creates a Draft `FormVersion` and file-backed compiled XForm with diagnostics and compatibility metadata.
- Preview and Publish are separate operations. Publish is explicitly authorized and updates future form assignments atomically.
- Published versions are immutable; historical submissions retain their original form version.

The portal will present this workflow inside the selected project through a **Manage form** surface, using operational language appropriate to bank staff.

## Consequences

- New Dataverse import-job metadata and permission rules are required.
- A solution-aware cloud flow, connection references, environment variables, production Power Automate licensing, and an approved Python hosting boundary are required.
- The hosted compiler needs isolated execution, resource limits, telemetry, and deterministic dependency pinning.
- The current seed script must be refactored into reusable compile, stage, and publish operations rather than being the portal backend directly.
- The solution deployment runbook must include cloud-flow registration in each Power Pages target.

## Rejected Alternatives

- Direct publish immediately after upload: validation errors or accidental revisions would affect collection without review.
- Browser-side XLSForm compilation: creates performance, dependency, and security risks and duplicates server validation.
- Direct binary upload through the Power Pages portals Web API as the baseline: current official Web API documentation does not establish this as the supported file-upload path.
- Power Automate-only XLSForm parsing: would reimplement a mature grammar and diverge from pyxform behavior.
- Dataverse plug-in compilation: Python pyxform is not a natural Dataverse sandbox workload and would increase permission and packaging complexity.
