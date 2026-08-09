# Automatic Reporting Projection Refresh Research

Date: 2026-07-14
Status: complete for architecture selection

## Question

How should TACATDP refresh derived reporting rows automatically after Power Pages creates a new `SubmissionVersion` for a new submission or edit, without making the browser responsible for reporting consistency?

## Repository Evidence

- `powerpages/webforms-spa/src/powerpages-api/client.ts` creates one immutable `mp_submissionversion` for every submit/edit and links it to the canonical `mp_submission`.
- `scripts/build-reporting-projections.py` already proves deterministic XML parsing, root/repeat/answer projection, stable alternate keys, and rebuild from canonical rows.
- `scripts/validate-reporting-projection-builder.py` proves root and repeat behavior without network access.
- `schemas/dataverse/reporting-projection-schema.json` provides alternate keys and source-version lookups for idempotent writes.
- No plug-in project, registered plug-in source, or solution-packaged cloud flow exists in the repository.
- The installed toolchain has PAC CLI 2.8.1 with `pac plugin init/push` and .NET SDK 10.0.109. Implementation still requires checking the generated plug-in target framework and restoring reviewed Microsoft SDK packages.

## Official Microsoft Evidence

- The [Dataverse event framework](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/event-framework) runs extensions in response to server-side data events. Asynchronous PostOperation steps run after the core row operation completes.
- [Register a plug-in](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/register-plug-in) documents Create/PostOperation/asynchronous registration, post images, impersonation, and adding both assemblies and steps to an unmanaged solution.
- The [Dataverse asynchronous service](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/asynchronous-service) queues asynchronous plug-ins as System Jobs independently of the original operation.
- [Plug-in exception handling](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/handle-exceptions) confirms asynchronous failures do not cancel the original transaction and can be retried up to four times for retry-classified failures.
- [Plug-in tracing](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/logging-tracing) provides `ITracingService`, Plugin Trace Logs, and System Job details for asynchronous failures.
- Microsoft recommends [stateless `IPlugin` implementations](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/best-practices/business-logic/develop-iplugin-implementations-stateless) because Dataverse caches instances and may invoke them concurrently.
- Microsoft recommends considering asynchronous execution for longer work and documents the Dataverse message time limit in [plug-in performance guidance](https://learn.microsoft.com/en-sg/power-apps/developer/data-platform/analyze-performance).
- Microsoft says [not to use batch request types inside plug-ins](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/best-practices/business-logic/avoid-batch-requests-plugin).
- [Dataverse Upsert](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-upsert-insert-update-record) supports alternate-key idempotency.
- The Power Automate [Dataverse row trigger](https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger) can trigger when a row is added, modified, or deleted, but flow concurrency and request limits still apply.
- Microsoft documents [flow concurrency limits](https://learn.microsoft.com/en-us/power-automate/limits-and-config) and recommends limiting trigger/action data through filters and selected columns in [flow data guidance](https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/work-with-relevant-data).
- [Plug-in solution packaging](https://learn.microsoft.com/en-us/power-platform/alm/plugin-component) and [Power Platform ALM](https://learn.microsoft.com/en-us/power-platform/alm/) support moving the assembly and registered steps through solutions.

## Options

| Option | Strengths | Weaknesses | Decision |
| --- | --- | --- | --- |
| Asynchronous Dataverse plug-in on `SubmissionVersion` Create | Server-side event, isolated from submit transaction, deterministic C# XML support, testable, solution-packageable, System Job observability | Requires .NET implementation, registration, least-privilege execution user, and careful performance design | Selected |
| Solution-aware Power Automate cloud flow | Low-code trigger, visible run history, solution-aware | Complex arbitrary XForm/repeat parsing and stale-child reconciliation; concurrency and action-volume risk; hard to maintain parity with rebuild code | Rejected for projection core |
| Browser calls a custom API after submit | Immediate user feedback | Makes derived consistency dependent on browser/network; Power Pages Web API does not provide a dependable custom action path for this design; duplicates orchestration in the client | Rejected |
| Azure Function/webhook/service bus | Strong scale and language flexibility | Adds infrastructure, identity, monitoring, deployment, and synchronization boundaries not justified for the prototype | Deferred |
| Scheduled rebuild only | Simple and already available | Stale reporting window and no event-level completion/failure signal | Retain only as repair/backfill path |

## Selected Registration Shape

- Primary table: `mp_submissionversion`.
- Message: `Create` only. Edits already create a new immutable version, so an Update trigger is unnecessary.
- Stage/mode: PostOperation, asynchronous.
- Post image: instance id only. The implementation retrieves the latest canonical version server-side, so copying XML into the image would duplicate a potentially large payload without improving correctness.
- Execution context: a dedicated least-privilege Dataverse system user selected in the step's **Run in User's Context**, not the Power Pages caller.
- Solution: existing unmanaged `tacatdp_prototype`; include assembly, plug-in type, step, and image.

## Correctness Findings

1. Asynchronous events can complete out of order. The plug-in must retrieve the latest canonical version for the instance and no-op when the triggering version is no longer latest.
2. Stable upserts alone are insufficient. An edit may remove an answer or repeat row, so the projector must delete obsolete child rows after expected rows have been upserted.
3. Projection failure must never roll back the canonical field submission. Asynchronous execution provides this isolation.
4. The browser creates the version before updating the submission header during edit. Projection `UpdatedAt` should use the immutable version creation timestamp, not depend on the later header update.
5. Malformed XML is deterministic: record a Failed root projection with a sanitized message and preserve existing canonical data.
6. Transient platform failures should be traced and retried; unexpected failures remain visible as failed System Jobs.
7. The plug-in must remain stateless, avoid parallelism and batch request messages, and limit selected columns/queries.
8. The Python rebuild script remains the authoritative repair/backfill tool. Shared fixtures must prove C# runtime parity with Python behavior.
9. Repeated sibling names cannot identify a repeat containing only one row. New submissions must persist normalized XForm repeat paths in `SubmissionJson`; sibling-count inference remains a compatibility fallback for older submissions.

## Recommendation

Implement a stateless asynchronous C# Dataverse plug-in with a pure projection core and shared cross-language fixtures. Register it only on `mp_submissionversion` Create. Keep the existing Python builder for dry-run, bulk rebuild, recovery, and parity verification.
