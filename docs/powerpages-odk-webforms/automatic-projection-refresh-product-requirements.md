# Automatic Projection Refresh Product Requirements

## Problem

Reporting rows currently refresh only when a trusted developer runs the rebuild script. Bank staff can submit or edit a record successfully while Data, CSV, and Power BI continue to show the previous projection.

## Users

- Monitoring user: expects submitted/edited data to appear without developer intervention.
- Reporting analyst: needs current, non-duplicated reporting rows.
- Platform administrator: needs observable failures, bounded retries, repair commands, and solution-managed deployment.
- Security owner: needs server-side least-privilege execution and no browser credentials.

## Requirements

| ID | Priority | Requirement |
| --- | --- | --- |
| APR-RQ-01 | P0 | Creating a canonical `SubmissionVersion` must enqueue projection refresh automatically. |
| APR-RQ-02 | P0 | Projection execution must be asynchronous and must not roll back or reject the canonical submit/edit transaction. |
| APR-RQ-03 | P0 | The latest canonical version must produce exactly one current root projection identified by the existing `ReportKey` alternate key. |
| APR-RQ-04 | P0 | Root, repeat, and answer output must match the Python projection contract for the same fixture; submission metadata must carry XForm repeat paths so singleton and nested repeats are not inferred only from sibling counts. |
| APR-RQ-05 | P0 | A superseded/out-of-order event must perform no projection writes. |
| APR-RQ-06 | P0 | Reprocessing the same version must be idempotent and must not duplicate rows. |
| APR-RQ-07 | P0 | Answers/repeats removed by an edit must not remain in the current projection. |
| APR-RQ-08 | P0 | Malformed XML must preserve canonical rows and produce an observable Failed projection state with a sanitized error. |
| APR-RQ-09 | P0 | Runtime code must contain no secrets and must execute as a dedicated least-privilege Dataverse user. |
| APR-RQ-10 | P0 | Assembly, type, asynchronous step, and post image must be included in `tacatdp_prototype` for solution export/import. |
| APR-RQ-11 | P1 | Operational traces must include correlation id, submission/version ids, instance id, version number, counts, outcome, and elapsed time without answer values or XML. |
| APR-RQ-12 | P1 | Transient failures must use bounded Dataverse async retry behavior; deterministic data failures must not retry indefinitely. |
| APR-RQ-13 | P1 | The Python rebuild remains available for dry-run, one-instance repair, and full backfill. |
| APR-RQ-14 | P1 | Shared fixtures must detect behavioral drift between the Python repair path and C# runtime path. |
| APR-RQ-15 | P1 | Successful projection should normally become visible within two minutes in the development environment; exact service timing is eventually consistent, not transactional. |
| APR-RQ-16 | P1 | The plug-in must be stateless, select only required columns, avoid parallel execution, and avoid batch request messages. |

## Data Rules

- Canonical `Submissions` and `SubmissionVersions` remain source of truth.
- Runtime trigger identity is the created `SubmissionVersion` id.
- Latest-version selection orders by version number, then created timestamp/id as a deterministic tie-breaker.
- Projection `UpdatedAt` uses the immutable version creation timestamp for edit consistency.
- Expected child keys are calculated before obsolete child reconciliation.
- Obsolete answers are removed before obsolete repeat rows.
- A root reaches Ready only after all expected child writes and cleanup succeed.

## Operational States

- `Ready`: current version projected and child reconciliation completed.
- `Stale`: refresh started or a newer canonical version exists.
- `Failed`: deterministic payload/projector failure; canonical data remains intact.
- Failed asynchronous System Job: unexpected/transient platform failure exhausted retries; repair with the one-instance rebuild after diagnosis.

## Security and Privacy

- Do not trace submitted XML, answer values, email beyond the existing support identifiers, tokens, or credentials.
- The execution user receives only read on canonical/form metadata and create/read/write/delete/append/append-to needed on reporting projections.
- Power Pages users retain read-only reporting-table access; they do not gain plug-in deployment or repair privileges.
