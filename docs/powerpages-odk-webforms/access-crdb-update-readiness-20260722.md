# CRDB User Management Update Readiness - 2026-07-22

Status: implemented for portal package readiness. Mshirika write activation is available only through the explicit Mshirika test build.

## Purpose

Prepare User & Access management and AssignForm assignment readiness for the next CRDB environment update. Mshirika can run a controlled OnboardingRequests queue test after the queue table, Power Pages Web API settings, table permissions, and Dataverse-triggered processor are registered in the same environment. CRDB production remains disabled until its schema, Web API settings, table permissions, invitation/notification path, and smoke tests are verified.

## UX Scope

- Configuration tab shows `CRDB update package` readiness.
- Configuration tab lists User & Access UI, guarded AssignForm service path, AccessAuditLogs import, portal permissions, and activation smoke tests.
- Create, invite and assign confirmation captures a business reason before activation.
- Create, invite and assign confirmation shows onboarding activation gates from `getUserOnboardingReadiness()`.
- Add User includes the operational `submitAccessWorkflow()` path through `submitUserOnboardingAccess()` when the explicit Mshirika onboarding build flag is set and `OnboardingRequests` create/read permission is available for Platform Administrator.
- The final create action remains disabled and says `Create, invite and assign disabled` while readiness is false.

## Safety Boundary

- Access write build flags default to disabled.
- Mshirika test activation requires explicit `VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED=true`.
- Mshirika test activation requires explicit `VITE_TACATDP_ACCESS_ASSIGN_FORM_WRITE_ENABLED=true`.
- Mshirika test activation requires explicit `VITE_TACATDP_ACCESS_ONBOARDING_AUTOMATION_ENABLED=true`.
- Mshirika test activation requires `mp_onboardingrequest` schema, Web API settings, and administrator table permission.
- Mshirika test activation requires the Dataverse-triggered onboarding processor to update queued requests.
- `VITE_TACATDP_ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED` remains unset/disabled unless one-row audit update is approved.
- UI access is gated by `userOnboardingReadiness.enabled`; while the onboarding gate is off, no operator can trigger the end-to-end create/invite/assign action.
- CRDB permission and site-setting changes remain an explicit environment-update phase.

## Verification

```bash
python3 scripts/validate-access-crdb-update-readiness.py
python3 scripts/validate-access-assignform-disabled-implementation.py
python3 scripts/validate-access-write-preview-ui.py
npm --prefix powerpages/webforms-spa run typecheck
npm --prefix powerpages/webforms-spa run build
python3 scripts/validate-webforms-spa-foundation.py
```
