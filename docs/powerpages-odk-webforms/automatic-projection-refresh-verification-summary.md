# Automatic Projection Refresh Verification Summary

Date: 2026-07-15

## Verified

- Current submit/edit path creates immutable `SubmissionVersion` rows, making Create the sufficient trigger for both workflows.
- Existing Python code and fixtures prove the projection contract and repair path.
- Reporting tables and alternate keys required by idempotent writes already exist in the dev environment.
- No existing plug-in project or cloud-flow source conflicts with the selected design.
- Official Microsoft documentation supports asynchronous PostOperation plug-ins, System Job isolation, bounded retry, tracing, stateless design, alternate-key upsert, and solution packaging.
- Local PAC CLI 2.8.1 exposes `pac plugin init/push`; .NET SDK 10.0.109 is installed.
- The artifact set covers behavior, security, concurrency, stale-child cleanup, observability, ALM, testing, rollback, and repair.
- `python3 scripts/validate-reporting-projection-builder.py` passes against the existing Python projection contract.
- Artifact presence, full requirement/acceptance identifier coverage, and scoped `git diff --check` pass.
- PAC-generated plug-in targets `net462`; exact package versions are locked.
- Release package contains the plug-in DLL and README with no external runtime DLLs or credentials.
- C# validation covers root values, coercion, malformed XML, current/superseded decisions, obsolete keys, metadata parsing, nested repeats, and singleton repeats.
- Normalized Python/C# parity passes for report, repeat, answer, parent, typed-value, and JSON-map output.
- The Python repair path now marks Stale, reconciles obsolete answers before repeats, and marks Ready last.
- The SPA build and foundation validator pass with normalized XForm repeat paths persisted in `SubmissionJson`.
- Dataverse rejected the initial unsigned upload before component creation, proving that this environment requires a public key token.
- The project now uses a repository-local strong-name key; the signed Release build and package complete without warnings.
- Assembly `6cfe4209-c97f-f111-ab0e-7ced8d41fa2d` and plug-in type `6ffe4209-c97f-f111-ab0e-7ced8d41fa2d` are registered in the development environment.
- The assembly is verified as component type 91 in `tacatdp_prototype`.
- The environment contains neither a dedicated TACATDP execution user nor the required `TACATDP Projection Processor` role.
- No step or image exists, so the deployed plug-in cannot currently execute or affect submission data.

## Not Verified or Executed

- Execution user/role privileges.
- Dedicated execution user and reviewed role privileges.
- Asynchronous step, post image, and their solution inclusion.
- Dev runtime latency, retries, System Jobs, traces, or hosted portal refresh.

## Recommendation

Create a dedicated application user and assign only the reviewed `TACATDP Projection Processor` role. Then run the repository registration command with that Dataverse user ID, verify the step/image solution components, and complete hosted submit/edit checks before solution export.
