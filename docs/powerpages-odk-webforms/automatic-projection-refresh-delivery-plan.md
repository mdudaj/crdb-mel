# Automatic Projection Refresh Delivery Plan

Local implementation status: phases 1-3 complete on 2026-07-14. Phase 4 environment registration and phase 5 hosted verification remain approval-gated.

## Evidence to Inspect First

- All `automatic-projection-refresh-*` artifacts and ADR 0004.
- `scripts/build-reporting-projections.py` and its validator.
- Reporting schema JSON/notes and current environment deployment record.
- Current `mp_submissionversion` schema/logical columns and alternate-key active state.
- Official Microsoft plug-in/event/async/tracing/solution documentation linked from the research note.
- Installed `pac plugin init/push` help, PAC auth target, .NET SDK, and generated target framework before package restore.

## Phase 1: Scaffold and Contract

1. Create a non-protected task branch.
2. Scaffold `dataverse/Tacatdp.ReportingProjection.Plugin/` with `pac plugin init --skip-signing` after package-install approval.
3. Record generated target framework and reviewed NuGet dependencies; pin versions.
4. Add shared JSON fixtures under `tests/fixtures/reporting-projection/` covering root answers, repeats, nested repeats, empty/skipped values, numeric/date/boolean/JSON coercion, removed children, malformed XML, retries, and out-of-order versions.
5. Generate expected output using the existing Python core and commit only non-sensitive synthetic fixtures.

## Phase 2: Pure Projection Core

1. Implement stateless pure functions for metadata parsing, XML namespace stripping, path/key normalization, value coercion, repeat detection, and output construction.
2. Keep Dataverse SDK calls outside the pure core.
3. Add unit tests proving parity with shared fixture outputs.
4. Add guard tests for no XML/answer data in trace messages.

## Phase 3: Dataverse Adapter

1. Validate the Create/PostOperation context and instance-id-only post image; retrieve the latest canonical payload server-side.
2. Retrieve the parent submission and latest version using only required columns.
3. Return immediately for a superseded trigger.
4. Resolve current report row by alternate key; set Stale.
5. Upsert expected root/repeat/answer rows sequentially using alternate keys.
6. Query existing child keys for the root; delete obsolete answers, then obsolete repeats.
7. Set Ready with source version and projected timestamp only after reconciliation.
8. For deterministic parse errors, persist Failed and sanitized error. For transient faults, trace and request bounded retry. Let exhausted failures remain diagnosable in System Jobs.

## Phase 4: Registration and Solution Packaging

Requires explicit approval for package restore, plug-in push/registration, role/user changes, solution component changes, and publish/import.

1. Confirm PAC identity, environment URL, and `tacatdp_prototype` solution.
2. Create/select a dedicated execution user with a reviewed least-privilege role.
3. Build the package and run local tests/format/static checks.
4. Push/register the assembly in dev.
5. Register one `Create` / `mp_submissionversion` / PostOperation / asynchronous step with the named post image and fixed execution user.
6. Add assembly, type, step, and image to the unmanaged solution; verify dependencies.
7. Export/unpack the solution for source review and run solution checker where available.

## Phase 5: Hosted Verification

1. Create one new submission and wait for the async System Job.
2. Verify root/answer counts, source version, status, projected timestamp, and portal visibility.
3. Edit the same instance; remove at least one answer and one repeat row.
4. Verify same root, version N+1, stale-child removal, and no duplicate roots.
5. Force duplicate processing and out-of-order fixture tests locally; do not manipulate production jobs.
6. Test malformed XML only with a synthetic dev record after explicit approval.
7. Run Python one-instance rebuild and verify idempotent parity.
8. Capture System Job, trace, row-count, and portal evidence without payload values.

## Rollback

1. Disable the plug-in step; do not delete canonical or reporting tables.
2. Confirm new submissions still persist canonically.
3. Run `python3 scripts/build-reporting-projections.py --instance-id <id> --execute` for affected records after diagnosis, or full rebuild when approved.
4. Revert the plug-in solution version through normal managed/unmanaged solution ALM; do not unregister components ad hoc in production.
5. Re-enable only after parity, stale-child, and async failure tests pass.

## Known Failure Signatures

- Missing post image/column: registration contract failure; disable step and correct image.
- Privilege error on projection write/delete: execution-user role incomplete; do not grant ordinary portal users write access.
- Duplicate key/conflict: verify active alternate keys and SDK key-attribute payload handling.
- Old version overwrites latest: latest-version guard failure; disable step immediately and rebuild.
- Stale child rows: reconciliation failure; disable step and use repair rebuild after fix.
- System Job timeout/resource failure: reduce selected data/operations; reconsider external queue architecture if the bounded plug-in cannot meet limits.
