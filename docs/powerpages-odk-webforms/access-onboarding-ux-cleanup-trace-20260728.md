# Access Onboarding UX Cleanup Trace - 2026-07-28

## Task

Clean the User & Access onboarding experience before the CRDB production update, removing operator-facing clutter while preserving the governed Dataverse onboarding queue architecture.

## Evidence Reviewed

- Material Design stepper guidance for dependent multi-step tasks.
- GOV.UK task list and step-by-step guidance for short task labels and sequential journeys.
- Power Pages invitation guidance for native invitation delivery.
- Existing TACATDP onboarding queue requirements, ADR, and processor runbook.
- Current Power Pages SPA source, styles, validators, build scripts, and upload package fragments.

## Decisions

- Keep the Dataverse `OnboardingRequests` queue as the production architecture.
- Reduce the visible Add User workflow from five steps to four: User, Role, Access, Review.
- Move onboarding path detail into a compact status card inside the User step.
- Keep detailed readiness and environment gates on the Status tab instead of the primary task path.
- Use one short submit action: `Create access`.
- Update Power Pages hosted asset references to the rebuilt bundle names and a 2026-07-28 cache key.

## Changed Areas

- `powerpages/webforms-spa/src/views/AssignedFormsView.vue`
- `powerpages/webforms-spa/src/styles.css`
- `powerpages/tacatdp-monitoring-tool/.powerpages-site`
- `powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool`
- `scripts/validate-access-create-invite-assign-ux.py`
- `scripts/validate-access-mshirika-activation.py`
- `scripts/validate-webforms-spa-foundation.py`

## Verification

- `npm --prefix powerpages/webforms-spa run typecheck`
- `npm --prefix powerpages/webforms-spa run build:mshirika-access`
- `python3 scripts/validate-access-create-invite-assign-ux.py`
- `python3 scripts/validate-access-mshirika-activation.py`
- `python3 scripts/validate-webforms-spa-foundation.py`
- `node --check powerpages/webforms-spa/dist/assets/index-0EKo1gv8.mjs`
- `git diff --check`

All commands passed locally.

## Open Environment Boundary

Mshirika still cannot prove invitation email delivery because the tenant has no working Exchange/mailbox license. CRDB validation must include a sender mailbox test and a full new-user invitation redemption smoke test after deployment.
