# System Activity Logging and Admin UX

Date: 2026-07-31

## Purpose

Define the logging and administrator operations surface for TACATDP before the
next CRDB onboarding and production-hardening slice. The admin navigation label
is **System Activity**.

## Evidence

- CRDB non-admin activation failed even after contact, invitation, and
  assignment records existed. The useful proof state was distributed across
  contact, invitation, redemption, external identity, web role, and assignment
  records.
- Power Pages sign-in still exposes local username/password and forgot-password
  controls even though the target CRDB authentication model is Microsoft Entra
  sign-in.
- The native Power Pages redeem screen accepts invitation codes and then routes
  users through a supported authentication method. It does not mean activation
  has completed until redemption and external identity state exist in Dataverse.
- TACATDP already has related operational data points:
  - `mp_onboardingrequest` request status, result message, error category, and
    sanitized error JSON.
  - `mp_accessauditlog` for governed access mutations.
  - User Activation Diagnostics for contact, invitation, redemption, external
    identity, web role, and assignment checks.
  - Notification delivery settings for manual-code versus email delivery mode.

Microsoft references:

- Power Pages local/external authentication settings:
  https://learn.microsoft.com/en-us/power-pages/security/authentication/set-authentication-identity
- Power Pages invitation redemption behavior:
  https://learn.microsoft.com/en-us/power-pages/security/invite-contacts
- Power Pages authentication setup and default provider behavior:
  https://learn.microsoft.com/is-is/power-pages/security/authentication/configure-site
- Power Pages diagnostic logs:
  https://learn.microsoft.com/fil-ph/power-pages/admin/view-portal-error-log
- Dataverse and model-driven telemetry with Application Insights:
  https://learn.microsoft.com/en-us/power-platform/admin/analyze-telemetry
- Dataverse telemetry events:
  https://learn.microsoft.com/en-us/power-platform/admin/telemetry-events-dataverse
- Power Platform audit logs in Microsoft Purview:
  https://learn.microsoft.com/en-au/power-platform/admin/activity-logging-auditing/activity-logs-overview
- Dataverse auditing:
  https://learn.microsoft.com/mt-mt/power-platform/admin/manage-dataverse-auditing

## Requirements

### Functional

- Add an administrator route named **System Activity**.
- Place **System Activity** in the bottom administration group of the side nav,
  near User & Access, Configuration, and other platform administration items.
- Show a concise health summary for authentication, Web API permissions,
  onboarding queue, invitation delivery, submissions, reporting projection,
  exports, Power BI configuration, and cache/platform readiness.
- Show recent operational events with severity, component, action, actor,
  affected user/project/form, status, timestamp, correlation/request id, and
  next action.
- Provide detail drawers for each event with a sanitized technical explanation,
  timeline, linked records, and clear admin action.
- Support filtering by severity, component, status, actor, affected user,
  project, form, and date range.
- Use the same correlation/request id across portal request, queue row, audit
  row, processor result, and user-facing result panel where possible.
- Mark onboarding users as **Ready** only when activation diagnostics prove
  external identity binding. Invitation creation alone is **Pending**.
- Record and surface expected failure modes:
  - missing Power Pages Web API setting;
  - missing table permission;
  - stale duplicate site setting;
  - Power Pages cache not purged;
  - mailbox not tested/enabled;
  - invitation created but not redeemed;
  - invitation expired;
  - no external identity;
  - assignment exists without activation;
  - submission save failed;
  - attachment metadata persisted but binary upload failed;
  - projection failed or stale;
  - export/Power BI configuration missing.

### UX

- The route must feel like a bank operations console, not a developer log dump.
- Use tabs:
  - `Health`
  - `Events`
  - `Onboarding`
  - `Submissions`
  - `Integrations`
- Use semantic chips:
  - green: healthy/succeeded;
  - amber: pending/degraded;
  - red: failed/blocked;
  - neutral: not configured/not applicable.
- Default view should show only actionable warnings and recent failures. Routine
  successful events are available through filters but should not dominate the
  first screen.
- Every error state must have a business-readable explanation and next action.
- Avoid exposing raw stack traces, bearer tokens, invitation codes in list rows,
  secrets, connector credentials, or mailbox internals.
- Use detail drawers for technical evidence rather than large inline panels.

### Security and Compliance

- **System Activity** is visible only to Platform Administrators.
- Data Collectors must not read system activity, access audit rows, invitation
  codes, external identity diagnostics, or other users' operational logs.
- Logs must be sanitized before writing to Dataverse.
- Raw platform diagnostic logs remain outside the portal in CRDB-controlled
  services such as Azure Blob diagnostics, Application Insights, Purview, or
  Power Automate run history.
- Portal logs should store references and categories, not secrets.

## ADR

Decision: implement **System Activity** as a TACATDP administrator experience
that summarizes app-level operational state from Dataverse, while relying on
Microsoft platform logging for low-level platform traces.

Rationale:

- Power Pages and Dataverse failures are distributed across multiple Microsoft
  services. A single admin UX should explain the operational state without
  requiring routine users to open Portal Management, Power Automate run history,
  Azure logs, and Dataverse tables separately.
- Microsoft-provided logging remains the source for platform-level server
  traces, request telemetry, and tenant audit history.
- TACATDP-owned operational events provide business context, correlation ids,
  sanitized failure categories, and next actions.

Rejected alternatives:

- Use only browser console logs: insufficient for CRDB administrators and lost
  after page reload.
- Use only Power Automate run history: useful for processor failures, but does
  not cover portal UX, Web API permissions, submissions, reporting, or user
  activation state.
- Expose raw Microsoft diagnostics directly inside the portal: too noisy and
  risks leaking technical or sensitive details.

## Login and Redeem Direction

Target CRDB login experience:

- Disable local username/password sign-in.
- Disable forgot-password for local accounts.
- Keep Microsoft Entra sign-in as the single functional sign-in action.
- Keep invitation redemption available for invited users.
- Remove or disable stale custom identity provider entries such as obsolete
  OpenID providers.
- Prefer a default provider/direct Microsoft Entra path after the identity
  provider configuration is confirmed in CRDB.

Redeem behavior:

- The manual invitation link/code must use the native Power Pages redeem route.
- Redeem routes the invited user through a supported authentication method.
- Activation is complete only when Dataverse shows redemption/external identity
  state. The portal must not treat the user as active merely because the link
  was opened or Microsoft sign-in appeared.

## Delivery Plan

### Slice 1: Requirements and UX Contract

- Create this artifact.
- Update future UX navigation language to **System Activity**.
- Confirm the first screen and tabs before implementation.

### Slice 2: App-Level Event Model

- Add a governed Dataverse schema artifact for `OperationEvents` or equivalent.
- Include correlation id, component, severity, status, message, next action,
  actor, affected user/project/form, source route, and sanitized details.
- Add validator checks that secrets and invitation codes are not logged.

### Slice 3: Admin System Activity UI

- Add the side-nav item in the admin bottom group.
- Implement tabs, filters, event list, health summary, and detail drawer.
- Start with read-only events from existing tables:
  - onboarding requests;
  - access audit logs;
  - activation diagnostics;
  - notification settings;
  - submission/reporting failure fields.

### Slice 4: Event Writers

- Add explicit, sanitized event creation around onboarding, access mutations,
  submission save/edit, projection refresh, export, and configuration changes.
- Reuse request ids and audit keys.
- Keep direct write capability gated to Platform Administrators or trusted
  server-side processors.

### Slice 5: Platform Logging Integration

- Document CRDB setup for Power Pages diagnostic logs to Azure Blob.
- Document Dataverse auditing and Purview audit-log prerequisites.
- Document Application Insights option and licensing boundary.
- Add links or reference IDs in **System Activity** where platform logs must be
  checked outside the portal.

## Acceptance Criteria

- Admin sees **System Activity** in the bottom administration navigation group.
- Admin can tell whether user activation is blocked by contact, invitation,
  redemption, external identity, role, or assignment state.
- Admin can identify failed onboarding requests and the next action without
  opening Power Automate first.
- Admin can see stale configuration signatures, such as duplicate Web API site
  settings or cache-required state, as operational checks.
- Collector users cannot see **System Activity**.
- No list view exposes raw invitation codes, tokens, secrets, or stack traces.
- Each failure state has a next action.

## Verification Gates

- Requirements/design artifact reviewed.
- Validator requires `System Activity` naming if/when route is implemented.
- Role-gating test confirms Data Collector cannot see the route.
- Hosted smoke confirms Platform Administrator can open the route.
- At least one seeded failed event and one healthy event render correctly.
- Browser console stays free of unhandled errors on route load.
