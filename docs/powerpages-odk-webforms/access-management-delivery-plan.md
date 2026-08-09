# User and Access Management Delivery Plan

Date: 2026-07-21

## Evidence to Inspect First

- `docs/powerpages-odk-webforms/access-management-research.md`
- `docs/powerpages-odk-webforms/access-management-requirements.md`
- `docs/powerpages-odk-webforms/adr-0007-portal-user-access-management.md`
- `docs/powerpages-odk-webforms/power-pages-auth-permission-troubleshooting.md`
- `schemas/dataverse/odk-central-inspired-mvp-schema.json`
- `powerpages/webforms-spa/src/views/AssignedFormsView.vue`
- Microsoft Power Pages authentication, web role, invitation, and table permission docs.

## Slice 1: Access Model and UI Shell

1. Add a User & Access navigation entry visible only to Platform Administrator.
2. Add role constants/labels in the portal app.
3. Add read-only Users list backed by Power Pages contacts and TACATDP assignments.
4. Show exact contact email and whether a TACATDP assignment exists.
5. Add empty, loading, permission-denied, and error states.
6. Verify ordinary users cannot see or call the admin data endpoints through the portal.

## Slice 2: Assignment Management

1. Add project membership and form assignment UI.
2. Start with additive writes to existing `mp_formassignment`.
3. Use exact contact email as the assignment key for the prototype.
4. Add suspend/reactivate behavior through status/lifecycle fields where available.
5. Preserve historical submissions when access is suspended.
6. Verify assigned user sees project/form after sign-out/sign-in and Power Pages cache refresh where needed.

## Slice 3: Schema Hardening

1. Add or confirm `ProjectMembership` style schema:
   - contact lookup;
   - project lookup;
   - role;
   - status;
   - start/end dates;
   - assignment source;
   - audit metadata.
2. Link form assignments to membership where possible.
3. Keep email fallback for compatibility.
4. Package schema changes in the governed solution.
5. Avoid destructive migration of existing assignment rows.

## Slice 4: Invitation/Onboarding Support

1. Show whether a matching contact exists.
2. Provide administrator guidance when a user must log in once before assignment.
3. If CRDB approves, add invitation creation or invitation instructions.
4. Do not enable open self-registration without CRDB approval.
5. Confirm identity-provider settings with CRDB IT before changing authentication configuration.

## Slice 5: Audit and Production Readiness

1. Add access-change log or use Dataverse audit where enabled.
2. Add admin documentation.
3. Add support runbook for email mismatch, missing contact, missing web role, missing table permission, and Power Pages cache issues.
4. Add acceptance tests/smoke scripts.

## Slice 6: Governed Write-Path Activation

1. Review and approve `access-write-path-contract-20260721.md`.
2. Review and approve `access-permission-matrix-20260721.md`.
3. Decide whether `AccessAuditLogs` uses a one-row requested/succeeded lifecycle or strict physically append-only result events.
4. Deploy the approved audit schema and minimum table permissions.
5. Implement feature-flagged portal write services.
6. Enable one write action at a time, starting with idempotent form assignment create.
7. Smoke test Platform Administrator, delegated Project Manager, and Data Collector accounts before deploying to CRDB.

## Slice 7: AssignForm First Live Write

1. Review and approve `access-assignform-activation-design-20260721.md`.
2. Keep first activation limited to `AssignForm` and Platform Administrator.
3. Implement audit-before-mutation, duplicate assignment detection, no-op success, and failed audit/mutation states.
4. Keep role changes, suspension, reactivation, removal, invitation, project assignment, and rollback disabled until later slices.
5. Run `python3 scripts/validate-access-assignform-activation-design.py` before implementation and before activation.

## Verification Gates

- `pac env who` confirms the CRDB target environment.
- Portal authenticated smoke test confirms administrator can see User & Access.
- Non-admin authenticated smoke test confirms User & Access is hidden and protected.
- Contact lookup returns Hailo/Denis using the exact email shown in portal.
- Assignment create creates one active assignment row and does not duplicate existing rows.
- Assigned user sees project/form after sign-in.
- Suspended user no longer sees project/form but historical submissions remain.
- Browser code uses `/_api` and does not include secrets or bearer tokens.
- Power Pages table permissions and web roles are packaged or documented before deployment.
- `python3 scripts/validate-access-write-path-contract.py` passes before any User & Access write implementation is enabled.

## Required Approval Before Implementation

- Any CRDB authentication/identity-provider setting change.
- Any Dataverse schema write.
- Any Power Pages table permission or web-role change.
- Any Power Pages upload or managed solution import.
- Any invitation automation that sends email to CRDB users.
