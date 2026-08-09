# Access Onboarding Queue Traceability - 2026-07-24

Status: proposed.

## User Story

As a platform administrator, I want to submit a governed onboarding request for a new or existing user so that the system can create or reuse the Power Pages contact, send the appropriate activation or notification email, assign project/form access, and show me a reliable status without requiring developer scripts or manual Dataverse edits.

## Requirement Mapping

| Requirement | Artifact | Implementation Surface | Verification |
| --- | --- | --- | --- |
| Portal creates request before mutation | Requirements, data contract | Add User review submit service | New request row appears with `Pending` status. |
| Portal stops direct cloud-flow trigger calls | ADR 0008 | Portal onboarding service | Browser bundle contains no onboarding call to `/_api/cloudflow/v1.0/trigger/`. |
| Server-side automation processes request | ADR 0008, delivery plan | Dataverse-triggered cloud flow | Flow run appears for created request row. |
| Contact create/reuse is centralized | Requirements, runbook | Cloud flow contact step | Contact exists or is reused by email. |
| Invitation/notification is centralized | Requirements, runbook | Cloud flow email step | New user receives invitation or existing user receives notification. |
| Assignments are idempotent | Requirements, data contract | Cloud flow assignment step | Retry does not create duplicate assignment rows. |
| Status is business-readable | Requirements, data contract | Portal result panel and request row | Portal shows `Pending`, `Processing`, `Completed`, `Failed`, `Cancelled`, or `Needs Review`. |
| Audit is preserved | Requirements, runbook | AccessAuditLogs and request row | Audit key/status written before assignment mutation. |
| CRDB import avoids plugin privilege | Delivery plan | Solution package | Package excludes C# plugin assembly until approval. |

## Acceptance Criteria Mapping

| Acceptance criterion | Evidence required |
| --- | --- |
| Creating a request creates exactly one queue row | Dataverse row screenshot or API response with request id. |
| Status starts as `Pending` | Request row details and portal result panel. |
| Flow run appears | Power Automate run history for request id. |
| Success creates contact and assignments | Contact row, assignment row, completed request status. |
| Failure is visible and non-duplicating | Failed request row with sanitized message and no duplicate assignments. |
| Direct cloud-flow endpoint removed | Static search over portal source/build artifacts. |
| Mshirika smoke passes before CRDB | Verification summary and deployment notes. |

## Artifact Readiness

- Requirements: ready for implementation planning.
- ADR: ready for review.
- Data contract: ready for schema implementation with final Dataverse logical-name validation.
- Delivery plan: ready for next slice.
- Runbook: ready for Mshirika operator testing.
- Validator: required before implementation and before CRDB packaging.

## Definition of Done

- Queue schema is packaged in the managed solution.
- Portal Add User flow creates queue rows and keeps the administrator on a result/status page.
- Dataverse-triggered automation updates status and writes assignments.
- New-user and existing-user Mshirika smoke tests pass.
- Non-admin user cannot access request rows or User & Access management surfaces.
- CRDB package includes schema, permissions, connection references, cloud flow, portal code, and runbook.
- Protocol check passes with requirements, ADR, delivery, and verification artifacts attached.

## Verification Summary

Planned verification commands:

```bash
python3 scripts/validate-access-onboarding-queue-artifacts.py
PYTHONPYCACHEPREFIX=/tmp/tacatdp-pycache python3 -m py_compile scripts/validate-access-onboarding-queue-artifacts.py
git diff --check
```

Runtime verification remains pending until the schema and queue submission implementation slices are delivered in Mshirika.
