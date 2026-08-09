# Onboarding Result UX Polish - 2026-07-30

## Purpose

Make the User & Access create/invite/assign result state clear enough for bank administrators to complete onboarding without opening Dataverse or Power Pages Management.

## Requirements

- After submit, keep the administrator on the Add User review/result surface.
- Show a compact timeline with the stages `Queued`, `Processing`, and `Needs review`.
- Keep `Refresh status` as the main follow-up action while processor work is pending or under review.
- When a manual invitation code exists, show only the operational fields needed for handoff: redeem link, code, and expiry.
- Copy actions must have clear feedback through `aria-live` status text.
- Expired invitation codes must not be copyable as valid activation material.
- Expired invitations must expose a clear `Create new invitation` action.
- Avoid long implementation text in the main result path.

## UX Description

The result panel should behave like an operations checkpoint:

- status first;
- next action second;
- sensitive activation material only when available;
- concise warning about approved internal delivery channel;
- technical ids available but secondary.

## Acceptance Criteria

- The review screen renders an onboarding timeline after request creation.
- Queue status maps visually to queued, processing, review, complete, or failed states.
- Manual invitation fallback panel shows redeem link, invitation code, and expiry.
- Copy buttons are disabled when the invitation is expired.
- Missing invitation result fields show a short pending message and `Refresh status`.
- Validation commands pass.

## Verification Plan

Run:

```bash
python3 scripts/validate-access-create-invite-assign-ux.py
npm --prefix powerpages/webforms-spa run build:mshirika-runtime
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/<new-entry>.mjs
git diff --check
```

After deployment, create a test new-user request on Mshirika and confirm the admin can refresh, see the code/redeem URL/expiry, copy both fields, and identify the manual delivery instruction without reading implementation gates.

## Delivery Evidence

Implemented in:

- `powerpages/webforms-spa/src/views/AssignedFormsView.vue`
- `powerpages/webforms-spa/src/styles.css`
- `scripts/validate-access-create-invite-assign-ux.py`

Packaged bundle:

- `index-CGXE1ls4.mjs?v=onboarding-result-ux-20260730-001`
- `index-thzYBJgQ.css?v=onboarding-result-ux-20260730-001`

Commands run:

```bash
python3 scripts/validate-access-create-invite-assign-ux.py
npm --prefix powerpages/webforms-spa run build:mshirika-runtime
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-CGXE1ls4.mjs
git diff --check
pac pages upload --environment "https://orga3cf4b37.crm4.dynamics.com/" --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool --modelVersion Enhanced --forceUploadAll
```

Result:

- UX validator passed.
- Runtime build passed.
- Packaged browser bundle syntax check passed.
- Diff whitespace check passed.
- Mshirika Power Pages upload succeeded in 99.22 seconds.

Render evidence:

- Static render evidence is the compiled Vue template in `index-CGXE1ls4.mjs` plus Home page references updated to the cache key above.
- Manual browser review remains required after Power Pages cache purge/restart because the hosted site controls server-side cache and authentication state.
