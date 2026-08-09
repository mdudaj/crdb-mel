# Access Onboarding Queue Delivery Plan - 2026-07-24

Status: proposed.

## Objective

Make User & Access onboarding reliable in Mshirika before the next CRDB update by replacing direct portal cloud-flow invocation with a Dataverse request queue and server-side processing.

## References

- `docs/powerpages-odk-webforms/access-onboarding-queue-requirements-20260724.md`
- `docs/powerpages-odk-webforms/adr-0008-onboarding-request-queue.md`
- `docs/powerpages-odk-webforms/access-onboarding-queue-data-contract-20260724.md`
- `docs/powerpages-odk-webforms/access-write-path-contract-20260721.md`
- `docs/powerpages-odk-webforms/access-permission-matrix-20260721.md`
- Microsoft Learn: Configure Power Automate cloud flows in Power Pages
- Microsoft Learn: Integrate Power Automate cloud flow with a Power Pages site

## Slice 1: Artifacts and Guardrails

1. Create requirements, ADR, data contract, delivery plan, runbook, and traceability artifacts.
2. Add an executable artifact validator.
3. Mark the direct cloud-flow invocation path as superseded for onboarding.
4. Keep the existing flow artifacts as diagnostics only, not as the next implementation basis.

## Slice 2: Dataverse Schema Package

1. Add `mp_onboardingrequest` schema to the governed Dataverse schema package.
2. Add status and request-type choices.
3. Add alternate key on `mp_requestkey`.
4. Add Web API site settings for the narrow field list.
5. Add Power Pages table permissions for administrator create/read and automation update.
6. Package without C# plugin dependencies so CRDB can import without `prvCreatePluginAssembly`.

## Slice 3: Portal Queue Submission

1. Update Add User review step to create an `OnboardingRequest` row through Power Pages `/_api`.
2. Remove onboarding dependency on `/_api/cloudflow/v1.0/trigger/<guid>`.
3. Show request id, initial `Pending` status, and clear next action after submit.
4. Keep the administrator on the result surface.
5. Add status refresh and failure panel.
6. Prevent duplicate submit while the same request is in flight.

## Slice 4: Dataverse-Triggered Automation

1. Create a solution-aware cloud flow triggered when an `OnboardingRequest` row is created or moved to retry state.
2. Set status to `Processing`.
3. Resolve or create contact by normalized email.
4. Create access audit row before assignment mutation.
5. For new users, create/send the native Power Pages invitation.
6. For existing users, send Dataverse-native assignment notification.
7. Create form assignments idempotently.
8. Update request to `Completed` or `Failed`.

## Slice 5: Retry, Cancel, and Detail UX

1. Add request detail drawer.
2. Add explicit retry for failed requests.
3. Add cancel for pending requests.
4. Show processing attempts and last attempt time.
5. Show sanitized failure category and message.

## Slice 6: Mshirika Verification

1. Deploy schema and portal changes to Mshirika.
2. Purge cache and restart portal.
3. Submit new-user onboarding request for a test email.
4. Confirm request row is created.
5. Confirm flow run appears.
6. Confirm contact exists and assignment exists on success.
7. Confirm portal displays completed result.
8. Run non-admin smoke test to confirm no access to onboarding queue rows.

## Slice 7: CRDB Update Package

1. Build managed solution from the verified state.
2. Include queue table, choices, permissions, cloud flow, connection references, and portal code.
3. Document required import privileges and post-import connection-reference steps.
4. Confirm CRDB administrator connection owner can create/update contacts, invitations, assignments, and access audit rows.
5. Import and smoke test before enabling wider use.

## Verification Commands

```bash
python3 scripts/validate-access-onboarding-queue-artifacts.py
PYTHONPYCACHEPREFIX=/tmp/tacatdp-pycache python3 -m py_compile scripts/validate-access-onboarding-queue-artifacts.py
git diff --check
```

## Not in This Slice

- Microsoft Graph people picker.
- Entra group synchronization.
- Bulk onboarding upload.
- Custom API/plugin implementation.
- General Office 365 Outlook dependency as the default Mshirika email path.
