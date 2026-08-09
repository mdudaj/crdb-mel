# Onboarding Flow Failure Diagnostics Delivery - 2026-07-23

Status: deployed to Mshirika development environment. Not yet proven by recipient email delivery.

## Task Classification

Bug fix and workflow hardening for the Power Pages User & Access onboarding path. The observed portal result changed from trigger-schema `400 IncorrectPayload` failures to `500 : error`, which indicates the cloud-flow trigger was reachable but an internal flow action failed without returning a useful result to the portal.

## Requirements

- The portal must not silently redirect or report success after a mutating onboarding workflow unless it receives a confirmed contact, assignment, invitation, or notification result.
- The Power Pages cloud flow must return short non-secret failure statuses for internal flow failures.
- The portal must treat returned failure statuses as failed onboarding outcomes even if the cloud-flow response is HTTP 200.
- The next administrator retry must produce either a successful result or a named failing action that can be checked in Power Automate run history.

## UX Description

The existing route-level onboarding result panel remains the user-facing feedback surface. For this slice, the result panel must show the affected email, timestamp, failure status, and actionable message. No new visual layout was introduced; the change improves the content shown in the existing error feedback state.

## Accessibility Checklist

- Existing page-level result panel remains visible text, not console-only output.
- Failure state remains reachable after submit and is not hidden behind hover-only UI.
- Error details are plain text and do not depend on color alone.

## Artifact Readiness

- Governed by `docs/powerpages-odk-webforms/access-create-invite-assign-ux-20260722.md`.
- Governed by `docs/powerpages-odk-webforms/onboarding-email-cloud-flow-activation-20260722.md`.
- Runtime evidence: user-reported `500 : error` after prior trigger-schema fixes.
- Official reference: Microsoft Power Pages cloud-flow integration documentation for solution-aware flow registration, role assignment, `/_api/cloudflow/v1.0/trigger/<guid>`, and `shell.ajaxSafePost` with `eventData`.

## Change Summary

- Added explicit failure responses to the onboarding flow configurator for Parse JSON, contact create, invitation create/workflow, assignment email create, and assignment email send.
- Made parse-failure response avoid reading `body('Parse_JSON')`.
- Made the portal client reject returned flow statuses containing failure/error/timeout language.
- Rebuilt and uploaded the Mshirika access bundle with cache marker `mshirika-flow-failure-diagnostics-20260723-001`.

## Verification Summary

- `npm --prefix powerpages/webforms-spa run typecheck` passed.
- `npm --prefix powerpages/webforms-spa run build:mshirika-access` passed.
- `python3 scripts/validate-access-create-invite-assign-ux.py` passed.
- `python3 scripts/validate-access-mshirika-activation.py` passed.
- `python3 scripts/validate-access-crdb-update-readiness.py` passed.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check` passed for the tracked and upload-package `index-00W4I3DT.mjs`.
- Live flow verification confirmed `Parse_JSON.inputs.content = triggerBody()`, required trigger fields `requestId`, `deliveryType`, and `email`, and no missing failure response actions.
- `pac pages upload` to Mshirika succeeded.
- Post-upload `pac pages download` verified the hosted Home page references the new cache marker.
- `python3 scripts/verify-powerpages-api-smoke-hosted.py --env-file .env` passed.

## Remaining Risk

The recipient invitation email is still not confirmed. If the next retry still shows generic `500 : error`, the administrator must inspect the Power Automate run history in the maker portal because the service-principal route could not retrieve useful run-history details from Linux.
