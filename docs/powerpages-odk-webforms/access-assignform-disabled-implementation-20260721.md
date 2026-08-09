# AssignForm Disabled Implementation - 2026-07-21

Status: implemented behind disabled feature flags. No live write activation.

## Scope

Add AssignForm-specific client methods so the first access write path is implementation-ready while still blocked by feature flags.

## Implemented

- `VITE_TACATDP_ACCESS_ASSIGN_FORM_WRITE_ENABLED` build flag defaults to disabled.
- `areAssignFormWritesEnabled()`.
- `getAssignFormAccessReadiness()`.
- `buildAssignFormAccessCommand()`.
- `buildAssignFormAccessPreview()`.
- guarded `submitAssignFormAccess()`.
- duplicate lookup helper `findFormAssignmentByEmailAndVersion()`.
- shared `buildFormAssignmentKey()` helper.
- internal `createAccessAuditRequested()` helper.
- internal `createAssignFormAssignment()` helper.
- internal `updateAccessAuditResult()` helper gated by `VITE_TACATDP_ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED`.
- audit payload mapper `toAccessAuditWebApiPayload()`.

## Safety Boundary

- Access write build flags default to disabled unless explicitly enabled for a target environment test build.
- `submitAssignFormAccess()` throws before duplicate lookup or mutation while flags are off.
- UI access is gated by `assignFormReadiness.enabled`; while flags are off, the Create access action remains disabled.
- Audit and assignment Web API helpers exist only behind the disabled public submit guard.
- Audit result update is skipped unless one-row audit lifecycle is explicitly approved by flag.

## Verification

```bash
python3 scripts/validate-access-assignform-disabled-implementation.py
python3 scripts/validate-access-assignform-activation-design.py
npm --prefix powerpages/webforms-spa run typecheck
npm --prefix powerpages/webforms-spa run build
python3 scripts/validate-webforms-spa-foundation.py
```
