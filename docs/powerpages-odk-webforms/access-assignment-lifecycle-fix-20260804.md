# Access Assignment Lifecycle Fix - 2026-08-04

## Context

During CRDB first-delivery verification, Denis Muroba could see TACATDP projects/forms but Hailo Kibiki could not, even though both users had active Power Pages contacts and the same `Platform Administrator` web role.

## Evidence

CRDB `pac env fetch` checks showed:

- Denis and Hailo both had active Contact rows.
- Denis and Hailo were both linked to `Platform Administrator Web Role`.
- Denis' `mp_formassignment` row returned `mp_lifecyclestatus = Active`.
- Hailo's older `mp_formassignment` row did not return an active lifecycle value.
- The SPA assignment query filters by `mp_lifecyclestatus eq 100000000`.

Therefore, Hailo's project visibility failure was not a web-role problem. It was an assignment lifecycle/data-quality problem.

## Root Cause

The portal assignment creation payload did not explicitly set `mp_lifecyclestatus` when creating an `mp_formassignment` row. Newer CRDB UI-created rows mostly had Active values, likely from Dataverse defaults or later manual updates, but the implementation was not deterministic.

The duplicate-assignment path also treated any existing row for the same email/form version as already assigned, even if that row was inactive or missing lifecycle. That allowed stale rows to block usable access.

## Resolution

Updated `powerpages/webforms-spa/src/powerpages-api/client.ts` so that:

- New `AssignForm` rows explicitly set `mp_lifecyclestatus = 100000000`.
- Existing assignment rows with missing/inactive lifecycle are patched back to Active instead of returning a false `already-assigned` result.
- Duplicate detection selects `mp_lifecyclestatus` so it can distinguish active access from stale access.

## Verification

Commands run:

```bash
npm run build:mshirika-runtime
python3 scripts/validate-webforms-spa-foundation.py
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-D6hGH8UB.mjs
```

Results:

- Build passed.
- WebForms SPA runtime foundation validation passed.
- Packaged bundle syntax check passed.
- Home and localized Home fragments reference `assignment-lifecycle-fix-20260804-001`.

## Deployment Notes

After CRDB upload and cache purge/restart, use the User & Access UI to assign Hailo to the TACATDP form again. The UI should reactivate the existing stale assignment row and make the project visible without a manual Dataverse table edit.

## Related Fix: Resend Invitation Role Source

A second CRDB finding on 2026-08-04 showed Hailo's resend invitation request being queued with `Data Collector / Bank Officer` even though Hailo already had the `Platform Administrator` Power Pages web role.

Root cause: the User & Access list inferred `Platform Administrator` only for the currently signed-in session user. Other contacts were displayed as Bank Officer by default, and the resend workflow copied that displayed value into `mp_targetrole`.

Resolution: `listAccessUsers()` now loads each Contact's actual Power Pages web-role links through the Contact-to-web-role navigation property and derives the visible role from those records. The current-session role fallback is used only when the role-link lookup is unavailable and only for the signed-in user. Future resend requests should preserve `Platform Administrator` for Hailo and any other admin Contact.

Verification added for this package:

```bash
npm run typecheck
npm run build:mshirika-runtime
python3 scripts/validate-webforms-spa-foundation.py
node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-BKXPZQih.mjs
```

Deployment marker: `access-role-link-lookup-20260804-004`.
