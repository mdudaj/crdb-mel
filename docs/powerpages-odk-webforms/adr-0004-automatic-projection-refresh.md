# ADR 0004: Asynchronous Dataverse Plug-in for Projection Refresh

Status: accepted
Date: 2026-07-14
Accepted: 2026-07-14

## Context

TACATDP stores canonical immutable submission versions and derives reporting rows for portal Data, CSV, and Power BI. The trusted Python builder proves the projection contract but requires manual execution. Automatic refresh must tolerate edits, retries, out-of-order events, removed repeat/answer rows, and projection failures without making field submission fail.

## Decision

Implement a stateless C# Dataverse plug-in registered on `Create` of `mp_submissionversion` as an asynchronous PostOperation step.

The plug-in will:

1. Read the trigger post image and required canonical parent data.
2. Retrieve the latest version for the instance and no-op if the trigger is superseded.
3. Mark/upsert the root projection as Stale.
4. Build expected root, repeat, and answer rows using a pure C# projection core.
5. Upsert expected rows through existing alternate keys.
6. Delete obsolete answer rows, then obsolete repeat rows, for the same root projection.
7. Mark the root Ready only after reconciliation succeeds.
8. Persist a Failed root for deterministic XML/data errors; trace and use bounded async retry for transient platform failures.

The C# core and Python rebuild path will share fixtures and expected projection outputs. The Python script remains the repair/backfill path.

## Registration Contract

- Table: `mp_submissionversion`
- Message: `Create`
- Stage: PostOperation
- Mode: Asynchronous
- Deployment: Server, Sandbox/Database defaults
- Execution user: dedicated least-privilege Dataverse system user
- Post image alias: `SubmissionVersionImage`
- Post image columns: instance id only. The plug-in retrieves the latest canonical version and required columns server-side, avoiding duplicate XML in the asynchronous context.
- Solution: `tacatdp_prototype`, including assembly, type, step, and image

## Consequences

- Projection visibility is eventually consistent and normally follows submission within the async service window.
- Canonical submit/edit succeeds even when projection fails.
- The repository gains a C# plug-in project and cross-language fixture contract.
- Deployment requires package restore/build, plug-in registration, least-privilege user/role configuration, solution inclusion, and environment verification.
- Administrators must monitor failed System Jobs and use the Python rebuild for repair.

## Rejected Alternatives

- **Power Automate projection flow**: suitable trigger but poor fit for arbitrary XML/repeat traversal, stale-child cleanup, high action counts, concurrency guards, and code-level parity tests.
- **Synchronous plug-in**: would increase submit latency and could roll back canonical field data.
- **Browser-triggered custom API**: makes consistency depend on browser/network completion and duplicates orchestration in Power Pages.
- **Azure Function/webhook**: adds infrastructure and identity boundaries not justified for this prototype.
- **Scheduled rebuild only**: retained for repair, but does not satisfy automatic refresh.

## Revisit When

- projection work approaches Dataverse plug-in execution/resource limits;
- submission volume requires queue partitioning or external compute;
- a governed Fabric/Synapse/warehouse path becomes the primary analytics architecture;
- CRDB mandates a no-custom-code policy.
