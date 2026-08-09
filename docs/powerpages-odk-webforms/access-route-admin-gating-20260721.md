# User & Access Route Admin Gating - 2026-07-21

## Purpose

Harden the User & Access administration surface before enabling any access-management writes.

## Evidence

- Current SPA routing is state-based in `powerpages/webforms-spa/src/views/AssignedFormsView.vue`; there is no router package.
- Power Pages bootstraps the signed-in user's roles into `window.__TACATDP_POWERPAGES__.roles` from Liquid `user.roles` in the Home page fragment.
- Existing User & Access work is intentionally preview-only and still blocks Dataverse create, update, delete, and audit-log writes.

## Requirements

- Hide the User & Access side-navigation entry unless the signed-in user has an approved administrator role.
- Block direct route intent for the access route when the signed-in user is not authorised.
- Show a clear not-authorised state instead of rendering the access-management workspace for unauthorised users.
- Show the authorisation source, required role, detected roles, and matched role to administrators and denied users.
- Keep all User & Access write actions disabled.
- Do not add Dataverse write calls, table-permission changes, site-setting changes, or authentication-provider changes.

## Authorisation Decision

- Temporary source of truth: Power Pages web roles exposed by the authenticated Power Pages session.
- Required roles for this slice: `Administrators` or `Platform Administrator`.
- Local development remains enabled through the existing local fixture path.
- Future CRDB hardening should replace or supplement this with a solution-managed role model once the agreed Dataverse permission and audit design is approved.

## UX

- Authorised administrators see the User & Access navigation item and an `Admin route enabled` source card in the access overview.
- Unauthorised users do not see the User & Access navigation item.
- If an unauthorised user reaches `#access` directly, the app shows a denial page with the decision source and role details.
- The Configuration tab includes a Route guard panel so administrators can verify the current access decision source.

## Acceptance Criteria

- Non-admin sessions cannot render the `access-workspace`.
- Non-admin direct route intent to `#access` shows the denied state.
- Admin sessions can open the route and load the read-only user list.
- The side-nav User & Access item remains hidden for non-admin sessions.
- Sensitive access actions remain marked as disabled.
- The validator fails if the route-guard strings or authorisation-source UI are removed.

## Verification

- `npm run build` passed for `powerpages/webforms-spa`; build emitted only known ODK direct `eval` and chunk-size warnings.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-CYGW669e.mjs` passed.
- Uploaded to Mshirika Power Pages environment `https://orga3cf4b37.crm4.dynamics.com/`; PAC reported `Power Pages website upload succeeded in 145.82 secs.`
- PAC emitted known non-fatal `powerpagecomponent` update/content-size warnings during upload.
- Post-upload download path: `/tmp/tacatdp-mshirika-access-route-gating-post-upload-20260721-001`.
- Downloaded Home references point to `/assets/index-CYGW669e.mjs?v=access-route-gating-20260721-001` and `/assets/index-DALgcSQx.css?v=access-route-gating-20260721-001`.
- Downloaded bundle contains `Admin route enabled`, `A direct request for this administration route was blocked`, `Access route authorisation`, `Required role`, `Detected roles`, `Matched admin role`, `access-authorization-card`, `access-authorization-list`, and `access-authorization-panel`.
- `node --check` passed against the downloaded `index-CYGW669e.mjs`.
