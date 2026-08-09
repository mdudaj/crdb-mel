# ADR 0007: Portal User and Access Management

Status: proposed.
Date: 2026-07-21

## Context

TACATDP is being deployed as a Power Pages and Dataverse platform inside CRDB's Microsoft environment. The prototype currently depends on Power Pages contacts and email-based `FormAssignments` to decide which users can see assigned forms. This worked for Denis and was manually hardened for Hailo Kibiki, but manual Dataverse updates are not an acceptable operational model.

CRDB requires Microsoft-managed authentication. Business users also need a simple way to manage access without using Portal Management, Dataverse tables, PAC commands, or developer scripts.

## Decision

TACATDP will build a portal-based **User & Access** UI for routine user and assignment management.

Authentication will be handled by CRDB Microsoft identity, preferably Microsoft Entra sign-in configured by CRDB IT. TACATDP will not introduce local password management as the default sign-in method.

Authorization will use three layers:

1. Power Pages web roles for site/module access.
2. Power Pages table permissions for Dataverse CRUD through `/_api`.
3. TACATDP business access records for project membership and form assignment.

The first implementation will keep the current email-based `mp_formassignment` path for compatibility, while adding a governed path toward contact-linked project membership and role-based project/form assignment.

Access-management writes will require a dedicated append-only audit table before activation. The proposed review-only schema is `schemas/dataverse/access-audit-schema.json`; its human-readable companion is `schemas/dataverse/access-audit-schema.md`.

The audit table will record actor, affected user, action, scope, business reason, source route, request id, timestamp, result status, and before/after state snapshots. Rollback will be modeled as a new audit event that references the original event rather than modifying or deleting the original record.

The operational write sequence is defined in `access-write-path-contract-20260721.md`. The supporting role, route, table-permission, Web API, and deployment privilege mapping is defined in `access-permission-matrix-20260721.md`.

ADR 0008 extends this decision for onboarding automation. Create/invite/assign will use a Dataverse `OnboardingRequest` queue processed by server-side automation, not direct portal invocation of a Power Pages cloud-flow trigger.

## Consequences

- User access becomes manageable by authorized portal administrators.
- Project/form visibility no longer depends on developer-run seed scripts.
- Power Pages table permissions and site settings remain part of the governed solution package.
- CRDB IT still owns Microsoft identity-provider configuration and any tenant-level Entra decisions.
- The portal must include permission-denied and audit-friendly states because authorization mistakes are operationally sensitive.
- Access writes remain blocked until the audit table, table permissions, Web API settings, and rollback expectations are approved.
- User & Access write implementation must follow the confirmation, reason, request-id, audit-before-mutation, idempotency, and rollback rules in the write-path contract.
- Future multi-project support can build on the same membership and role model.

## Rejected Alternatives

- **Portal Management only**: technically available, but too admin-centric for routine CRDB/DAMAX operation.
- **Manual Dataverse row edits**: workable for emergency fixes, not sustainable or auditable as a product workflow.
- **Open self-registration**: conflicts with controlled CRDB project access and risks unapproved users creating portal contacts.
- **Entra group sync first**: attractive long term, but requires CRDB tenant decisions and possible Graph/Power Automate governance before product value is delivered.
