# User & Access Write Service Shell - 2026-07-21

Status: implemented as a frontend service shell disabled by default. No Dataverse writes are enabled unless an explicit environment build flag is set.

## Scope

This slice adds typed client-side write-path preparation for User & Access actions without activating mutation calls. It bridges the approved write-path contract to implementation while preserving the current `Write actions disabled` UX.

## Implemented

- Added access write command, snapshot, readiness, audit preview, and mutation preview types.
- Added a build-time `VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED` gate that defaults to disabled.
- Added `getAccessWriteReadiness()` for UI/readiness display.
- Added `buildAccessWritePreview()` to construct:
  - request id;
  - audit key;
  - actor email and detected roles;
  - affected user email;
  - action, scope, reason, source route, timestamp;
  - before/after snapshot JSON;
  - future mutation preview payload.
- Added `submitAccessWrite()` as the future execution entrypoint, but it throws `AccessWriteDisabledError` while the feature flag is off.
- Added a validator to prevent accidental live write endpoint wiring before approval.

## Deliberately Not Implemented

- No audit-row create call.
- No assignment create/update call.
- No contact create/update call.
- No table permission or site setting changes.
- No deployment.

## Activation Requirements

Before setting the feature flag for a target environment, complete the gates in `access-write-path-contract-20260721.md`:

- audit schema deployed;
- table permissions approved;
- Web API site settings enabled for the exact tables/fields;
- smoke tests for administrator, delegated manager, and data collector accounts;
- explicit deployment approval.

## Verification

```bash
python3 scripts/validate-access-write-service-shell.py
npm --prefix powerpages/webforms-spa run typecheck
python3 scripts/validate-webforms-spa-foundation.py
git diff --check
```
