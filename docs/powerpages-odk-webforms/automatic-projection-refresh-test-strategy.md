# Automatic Projection Refresh Test Strategy

## Local Unit Tests

- Pure C# projection core: root, repeat, nested repeat, namespace, empty/skipped, malformed XML, coercion, key sanitization.
- Cross-language parity against Python fixture output.
- Latest-version ordering and superseded no-op.
- Expected-key versus existing-key reconciliation.
- Retry classification and sanitized tracing.
- Stateless implementation/source checks; no `Task.Run`, parallel loops, `ExecuteMultipleRequest`, `ExecuteTransactionRequest`, or bulk request messages.

## Adapter Tests

- Mock `IOrganizationService` calls and verify selected columns/query bounds.
- Verify answer deletes precede repeat deletes.
- Verify root Ready is last successful state mutation.
- Verify deterministic parse failure does not throw retry.
- Verify transient fault requests bounded retry and never changes canonical rows.

## Dev Integration Tests

- New submit, edit, duplicate retry/idempotency, removed field, removed repeat, malformed synthetic payload, least-privilege execution, solution component inventory, System Job/trace evidence.
- Measure created-version to Ready-projection latency; acceptance target is within two minutes for normal dev load.
- Compare one-instance plug-in output with Python repair output.

## Regression Gates

- Existing Python projection validator remains passing.
- SPA foundation validator remains passing.
- Plug-in package build and unit tests pass without live credentials.
- Solution export contains assembly, type, step, image, tables, keys, and required relationships.
- No test fixture contains real customer/participant data.
