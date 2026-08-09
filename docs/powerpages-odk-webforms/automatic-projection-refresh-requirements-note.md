# Automatic Projection Refresh Requirements Note

## Bounded Outcome

Automatically refresh TACATDP reporting projections whenever a new canonical `SubmissionVersion` is created by submit or edit, while preserving canonical submission success and retaining the trusted rebuild path.

## Scope

- Create a solution-packaged asynchronous Dataverse plug-in.
- Port the existing projection algorithm to a pure, testable C# core.
- Trigger on `mp_submissionversion` Create/PostOperation/asynchronous.
- Upsert the current root, repeat, and answer projections by alternate key.
- Reconcile removed child rows.
- Ignore superseded/out-of-order version events.
- Record deterministic projection failures and operational trace evidence.
- Keep the Python rebuild command for backfill and recovery.

## Non-Goals

- No Power Pages UI changes in this slice.
- No synchronous projection that can block or roll back submission.
- No XLSX generation, Power BI embedding, warehouse, Azure Function, or public endpoint.
- No schema deletion or canonical payload mutation.
- No environment registration/import/publish without explicit approval.

## Governing References

- `automatic-projection-refresh-research.md`
- `adr-0004-automatic-projection-refresh.md`
- `scripts/build-reporting-projections.py`
- `scripts/validate-reporting-projection-builder.py`
- `schemas/dataverse/reporting-projection-schema.json`
- Microsoft Dataverse event framework, plug-in registration, async service, exception handling, tracing, ALM, and plug-in best-practice documentation linked from the research note.
