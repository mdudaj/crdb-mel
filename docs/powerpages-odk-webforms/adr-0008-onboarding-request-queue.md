# ADR 0008: Onboarding Request Queue

Status: proposed.
Date: 2026-07-24

## Context

The User & Access workflow must create or reuse a Power Pages contact, send the correct onboarding email, assign project/form access, and return a clear result to the administrator.

The first implementation attempted to call a Power Pages cloud flow directly from the portal through `/_api/cloudflow/v1.0/trigger/<guid>`. Mshirika testing repeatedly returned generic `500 : error` responses. The latest flow detail evidence showed no run history and no connections, which means the request can fail before any auditable workflow step is reached.

Microsoft Power Pages documentation requires cloud flows to be solution-aware, added to the site, assigned web roles, and called with the Power Pages cloud-flow API contract. Microsoft ALM documentation also states that cloud flows moved with Power Pages components must be registered in the target environment. This makes the direct trigger path sensitive to hidden site registration state and target-environment setup.

For a banking environment, onboarding cannot depend on a browser call that fails opaquely and leaves no durable request row.

## Decision

TACATDP will replace direct portal cloud-flow invocation for onboarding with a Dataverse-backed `OnboardingRequest` queue.

The portal will create an onboarding request row through the normal Power Pages Web API. A Dataverse-triggered cloud flow will process that row server-side using approved connection references. The flow will create or reuse the contact, create/send the Power Pages invitation for new users, send assignment notification for existing users, write project/form assignments, and update the request status.

The portal must not call `/_api/cloudflow/v1.0/trigger/<guid>` for create/invite/assign onboarding.

## Consequences

- Onboarding becomes observable through Dataverse rows and Power Automate run history.
- The administrator gets a durable request id, status, and failure message instead of a silent redirect or generic browser error.
- CRDB deployment no longer depends on editing portal JavaScript with a flow trigger GUID.
- The solution must include the queue table, choice values, table permissions, Web API settings, Dataverse-triggered flow, connection references, and environment-specific configuration.
- The UX becomes slightly asynchronous: submission creates a request immediately, while processing may complete shortly after.
- Retry, cancellation, and manual resolution can be modeled as audited status changes.
- The flow must be idempotent so retries do not create duplicate contacts or assignments.

## Rejected Alternatives

- **Keep direct Power Pages cloud-flow invocation**: rejected because repeated tests produced opaque `500 : error` responses and no useful run history.
- **Browser creates contact/invitation/assignment rows directly**: rejected because it expands portal table permissions on sensitive tables and still leaves email delivery fragmented.
- **Manual Portal Management process**: rejected for routine operation because it is not a managed product workflow for CRDB/DAMAX administrators.
- **Custom API or plugin first**: deferred because the CRDB import path currently lacks plugin assembly privileges and the first production-safe slice should avoid requiring `prvCreatePluginAssembly`.
- **External backend service**: rejected for now because CRDB asked for a Microsoft 365/Power Platform implementation and the queue pattern stays within Dataverse and Power Automate.

## Verification

- Confirm the portal creates an `OnboardingRequest` row through `/_api`.
- Confirm a Dataverse-triggered flow run starts after the row is created.
- Confirm completed requests create/reuse a contact and create assignment rows.
- Confirm failed requests update status and sanitized error fields.
- Confirm browser code no longer contains onboarding calls to `/_api/cloudflow/v1.0/trigger/`.
