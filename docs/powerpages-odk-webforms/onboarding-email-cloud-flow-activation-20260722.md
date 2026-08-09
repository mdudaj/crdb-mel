# Onboarding Email Cloud Flow Activation

Status: native Power Pages invitation workflow and native Dataverse existing-user assignment notification wired in Mshirika.

## Purpose

Activate the final User & Access action by registering a Power Pages-triggered cloud flow and storing its trigger GUID in `TACATDP/OnboardingFlowTriggerId`.

## Evidence

- Microsoft documents Power Pages cloud-flow integration as a three-step process: create a solution-aware flow, add it to the site, then invoke it from `/_api/cloudflow/v1.0/trigger/<guid>`.
- Microsoft documents that only solution-aware flows can be attached to a Power Pages site.
- Microsoft documents that adding a flow to a site generates a unique URL.
- Microsoft's current Power Pages cloud-flow documentation shows browser calls using `shell.ajaxSafePost` with `data: { eventData: JSON.stringify(...) }` and says cloud flows moved across environments must be registered in the target site before invocation.
- Initial Mshirika Dataverse query found no active modern TACATDP cloud flow and no `TACATDP/OnboardingFlowTriggerId` site setting.
- On 2026-07-22, Mshirika `TACATDP/OnboardingFlowTriggerId` was configured with the generated Power Pages trigger GUID, then removed again because the flow had no real email/invitation action.
- On 2026-07-22, an approved Dataverse connector connection named `tacatdp-dataverse-service-principal` was created for the Mshirika environment.
- The generated flow was patched to contain the Power Pages trigger, `Parse JSON`, Dataverse `CreateRecord` for `adx_invitations`, Dataverse `PerformBoundAction` for native `ExecuteWorkflow`, and a Power Pages response.
- John could not be assigned/tested with an Outlook mailbox from this Linux environment because tenant login returned no access to the Mshirika resource. Office 365 Outlook remains a future provider option for CRDB if the mailbox/licensing path is approved.
- Approval was given to use the native Portal Management invitation workflow for new users and Dataverse-native email for existing-user assignment notifications in Mshirika.
- PAC 2.9.3 in this Linux environment exposes `pages download/upload` but no command for creating/registering Power Pages cloud flows.

## Required Flow

Create a solution-aware instant cloud flow named:

`TACATDP - Onboarding Email Delivery`

Trigger:

- Connector: Power Pages
- Trigger: When Power Pages calls a flow
- Input: `eventData`
- Input type: Text

The browser call must use Power Pages `shell.ajaxSafePost` and post the documented Power Pages cloud-flow envelope:

```json
{
  "eventData": "<serialized business payload>"
}
```

In browser code this is passed as the `ajaxSafePost` data object, not as a manually stringified request body. The flow must parse `@triggerBody()?['eventData']` as JSON.

The parsed business payload has this shape:

```json
{
  "requestId": "email:...",
  "deliveryType": "EnsureContact | PowerPagesInvitation | AssignmentNotification",
  "contactId": "00000000-0000-0000-0000-000000000000",
  "email": "user@example.com",
  "fullName": "User Name",
  "role": "Data Collector",
  "projectName": "Project name",
  "reason": "Business reason",
  "actorEmail": "admin@example.com",
  "assignmentResults": [],
  "sourceRoute": "/access",
  "occurredAt": "2026-07-22T00:00:00.000Z"
}
```

## Flow Behavior

For `deliveryType = EnsureContact`:

1. Parse `@triggerBody()?['eventData']`.
2. Create the Dataverse `contact` row with `fullname` and `emailaddress1`.
3. Return `contactId` to the portal.
4. Do not send an invitation in this branch; the portal must create audited assignments first.

For `deliveryType = PowerPagesInvitation`:

1. Parse `@triggerBody()?['eventData']`.
2. Use `contactId` to create or prepare the Power Pages invitation through the approved Portal Management invitation process.
3. Send the invitation email through the native `Send Invitation` workflow or an approved equivalent that produces a valid invitation redemption link.
4. Return a short status response such as `Invitation requested for user@example.com`.

For `deliveryType = AssignmentNotification`:

1. Parse `@triggerBody()?['eventData']`.
2. Create a native Dataverse `email` activity from the configured sender system user to the existing user's contact.
3. Run the Dataverse `SendEmail` action on that email.
4. Return `dataverse-assignment-notification-sent` to the portal.
5. Keep Office 365 Outlook as a configurable CRDB option if its connector, mailbox, and DLP path are approved.

Do not return tokens, connection names, secrets, invitation codes, or authorization headers to the portal.

Every branch must include explicit failure responses for the portal. Use HTTP 200 with a failure status in the response body when the trigger reached the flow but an internal action failed, because the portal needs a business-readable result panel instead of a generic `500 : error`. The required failure statuses are:

- `onboarding-payload-parse-failed`
- `dataverse-contact-create-failed`
- `native-invitation-create-failed`
- `native-invitation-workflow-failed`
- `dataverse-assignment-email-create-failed`
- `dataverse-assignment-email-send-failed`

Failure responses must not include invitation codes, access tokens, connection identifiers, or raw authorization data.

## Power Pages Registration

In Power Pages Studio:

1. Select the Mshirika environment.
2. Open `TACATDP Monitoring Tool`.
3. Select **Edit**.
4. Go to **Set up**.
5. Open **Cloud flows** under **Integrations**.
6. Select **Add cloud flow**.
7. Choose `TACATDP - Onboarding Email Delivery`.
8. Add the `Administrators` web role.
9. Save.
10. Copy the generated trigger URL or GUID.

After registration, verify the enhanced site component role link. The site should contain a Power Pages component with `powerpagecomponenttype = 33` for `TACATDP - Onboarding Email Delivery`, and that component must be associated to the `Administrators` web role through `powerpagecomponent_powerpagecomponent`. A site setting alone is not sufficient.

Also verify the component content has non-empty flow trigger metadata. A broken registration can leave `flowapiurl` populated but `flowtriggerurl` and `metadata` empty. In that state Power Pages can expose `/_api/cloudflow/v1.0/trigger/<guid>` but still return a generic `500 : error` without creating a Power Automate run. The supported repair is to re-register the cloud flow in Power Pages Studio for the target site so Microsoft regenerates the environment-specific trigger URL and metadata.

## Configure Portal Site Setting

After the trigger URL or GUID is available, run:

```bash
python3 scripts/powerpages-configure-webapi.py \
  --env-file .env \
  --include-access-writes \
  --access-role-name Administrators \
  --onboarding-flow-trigger-id <cloud-flow-trigger-guid> \
  --execute
```

Then clear Power Pages config cache or restart the site.

## Mshirika Configuration Evidence

Completed on 2026-07-22:

- Created Dataverse connection: `tacatdp-dataverse-service-principal`.
- Patched flow `TACATDP - Onboarding Email Delivery`.
- Verified saved actions:
  - `Parse_JSON`
  - `Route_delivery_type`
  - `Create_native_Power_Pages_invitation`
  - `Run_native_Send_Invitation_workflow`
  - `Create_Dataverse_assignment_email`
  - `Send_Dataverse_assignment_email`
  - Power Pages response actions for both branches
- Re-created site setting `TACATDP/OnboardingFlowTriggerId` with the generated trigger GUID.
- Rebuilt and uploaded the Mshirika access bundle with cache buster `mshirika-native-invitation-20260722-001`.
- Post-upload site download verified hosted Home references `/assets/index-ojTKmmzR.mjs?v=mshirika-native-invitation-20260722-001` and includes `onboardingFlowTriggerId`.
- Patched the flow again for Dataverse-native existing-user assignment notifications, with Office 365 Outlook retained only as a future configurable provider option.
- Rebuilt the Mshirika access bundle as `/assets/index-DBwQ_r5R.mjs?v=mshirika-dataverse-notification-20260722-001`.

Contact-create boundary update completed after browser test:

- Browser-side `POST /_api/contacts` returned `90040103` even after cache purge and restart.
- The flow was extended with `EnsureContact`.
- The portal now delegates missing contact creation to the role-secured Dataverse cloud flow and receives `contactId` before assignment writes.

Cloud-flow trigger input correction completed after browser test:

- Browser-side `POST /_api/cloudflow/v1.0/trigger/<guid>` returned a generic Power Pages 500 page before any contact, invitation, or assignment rows were created.
- Live Mshirika retries showed that a trigger requiring `text` rejects the Power Pages request with `Required properties are missing from object: text`, a trigger requiring `eventData` rejects with `Required properties are missing from object: eventData`, and posting raw top-level `text` returns `Invalid type. Expected Object but got String`.
- Microsoft's Power Pages cloud-flow sample uses the outer `eventData` envelope. The portal now posts `eventData` containing the serialized business payload.
- The portal passes `data: { eventData: "<serialized business payload>" }` to `shell.ajaxSafePost`; it does not set `contentType: application/json` or pass `data: JSON.stringify(...)`.
- Microsoft's detailed how-to calls cloud flows through `shell.ajaxSafePost`, not the generic JSON `fetch` helper used for Dataverse `/_api` CRUD. The portal now uses a dedicated `shell.ajaxSafePost` path for cloud-flow calls.
- The flow configurator now forces the trigger schema to require `eventData` and `Parse_JSON.inputs.content` to `@triggerBody()?['eventData']`.

Cloud-flow failure response correction completed after browser test:

- After the trigger accepted the business payload, the portal returned `500 : error` and Dataverse inspection still found no contact, assignment, audit, invitation, or Dataverse email rows for the test user.
- The Linux service-principal route could patch the flow but could not retrieve useful Power Automate run history, so the flow itself now returns named failure responses from each internal failure point.
- The portal now rejects returned flow statuses that contain failure/error/timeout language, preventing a false positive if Power Pages delivers the response as HTTP 200.

Cloud-flow site role repair completed after browser test:

- The registered flow component existed on the Mshirika site, but no web role was linked to it.
- `scripts/powerpages-configure-webapi.py` now ensures the registered onboarding flow component is associated to the configured access role.
- `scripts/verify-powerpages-api-smoke-hosted.py` now verifies the `TACATDP/OnboardingFlowTriggerId` site setting, registered cloud-flow component, and `Administrators` role link.
- Mshirika verification passed after the `Administrators` role link was created.

Cloud-flow registration metadata failure found after browser test:

- A retry after the role-link repair still returned generic `500 : error`.
- Dataverse inspection still found no contact, assignment, or access-audit rows for the test user.
- Power Automate run-history API returned zero runs for the service-principal-readable flow endpoint, consistent with Power Pages failing before the flow run is created.
- The registered Power Pages component content has `flowapiurl`, but `flowtriggerurl` and `metadata` are empty.
- `scripts/verify-powerpages-api-smoke-hosted.py` now fails on empty cloud-flow trigger URL and metadata.
- Resolution: open Power Pages Studio, remove/re-add or register `TACATDP - Onboarding Email Delivery` under the site Cloud flows list, assign `Administrators`, save, purge/restart the site, then rerun `python3 scripts/verify-powerpages-api-smoke-hosted.py --env-file .env`.

## Verification

1. Open the portal as an administrator.
2. Go to User & Access.
3. Confirm **Create, invite and assign** is enabled.
4. Create a test user with a controlled email address.
5. Confirm the result shows:
   - `Email delivery`: `invitation-sent` for a new user.
   - `Email delivery`: `assignment-notification-sent` for an existing user.
   - `Email request`: a generated request id.
   - `Flow status`: the flow response.
6. Confirm the recipient receives the Power Pages invitation.
7. Confirm the existing user receives the Dataverse assignment notification.
8. Confirm the invited user can redeem the invitation and see only assigned project/form access.

Do not treat the flow as production-ready until steps 5-7 pass. A flow with only `Parse JSON` can accept the portal request but will not send an invitation.
