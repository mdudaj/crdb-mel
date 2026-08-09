# User & Access Write-Path Readiness - 2026-07-21

## Purpose

Make the preview-only access management state explicit before any user, role, assignment, suspension, or reactivation write path is enabled.

## Requirements

- Add a `Configuration` tab under User & Access.
- Show readiness criteria for contact permission, assignment write permission, web role strategy, audit design, approver/reason requirement, and rollback policy.
- Mark sensitive actions as `Write actions disabled`.
- Show permission-model notes in add-user and change-confirmation flows.
- Do not add Dataverse create, update, delete, or audit-log write calls.

## UX Notes

- The readiness panel gives administrators a clear activation checklist.
- Badges beside Add user, Change role, Suspend, Reactivate, and Create access avoid ambiguity.
- Permission notes explain why confirmation flows are present but final writes remain disabled.

## Verification

- `npm run build` passed for `powerpages/webforms-spa`; build emitted only known ODK direct `eval` and chunk-size warnings.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files/index-Y4sh2uAq.mjs` passed.
- Uploaded to Mshirika Power Pages environment `https://orga3cf4b37.crm4.dynamics.com/`; PAC reported `Power Pages website upload succeeded in 143.38 secs.`
- PAC emitted known non-fatal `powerpagecomponent` update/content-size warnings during upload; post-upload download verified the deployed web files and Home references.
- Post-upload download path: `/tmp/tacatdp-mshirika-access-readiness-post-upload-20260721-001`.
- Downloaded Home references point to `/assets/index-Y4sh2uAq.mjs?v=access-readiness-20260721-001` and `/assets/index-BrtJazMT.css?v=access-readiness-20260721-001`.
- Downloaded bundle contains `Write-path readiness`, `Write actions disabled`, `Permission model required`, `access-readiness-panel`, and `access-readiness-row`.
- `node --check` passed against the downloaded `index-Y4sh2uAq.mjs`.
