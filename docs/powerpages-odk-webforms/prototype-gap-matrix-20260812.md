# Prototype gap matrix — 2026-08-12

## Purpose

This matrix turns the prototype acceptance scope into the remaining work queue. It separates acceptance blockers from deferred product work so the team does not keep polishing UI while core prototype proof remains unverified.

## Priority definitions

- P0: Blocks prototype acceptance.
- P1: Should be completed before client/stakeholder submission if access and time allow.
- P2: Useful polish or documentation, but not a blocker.
- Deferred: Future product scope, not prototype acceptance.

## Gap matrix

| Priority | Area | Gap | Evidence | Required action | Acceptance output |
|---|---|---|---|---|---|
| P0 | Current deployed state | Stakeholder review of the latest Mshirika deployment is not yet recorded in an acceptance artifact. | Latest Mshirika deployment marker is `beneficiary-readonly-actions-20260812-029`. | Review Mshirika in browser and record pass/fail notes for dashboard, beneficiaries, shell, users/access, and data routes. | Review note with screenshots or explicit observations. |
| P0 | Collection workflow | Current signed-in browser proof of full form load and submit is still required. | `slice-checklist.md` keeps browser-level submit/full-form verification unchecked. | In Mshirika or CRDB, sign in as an assigned user, open TACATDP form, submit a safe test record, and confirm result banner. | Evidence note with form load, submit result, submission id/version, and any attachment warning. |
| P0 | Saved records | Need current browser proof that a submitted record returns to Saved and does not create misleading duplicates. | Requirements require successful submit to return to Saved and edit submit to version existing records. | After the submit proof, confirm Saved list refreshes, shows the record, and displays owner/version metadata. | Evidence note with Saved list observation. |
| P0 | Reporting/Data reads | Authenticated reporting reads and CSV download need current browser confirmation or explicit exclusion. | `slice-checklist.md` leaves reporting read/CSV browser checks unchecked. | Test Data/Reporting route after cache refresh. If blocked, document the exact browser/API failure and classify as demo-only. | Pass note or blocked note with error signature. |
| P0 | CRDB/Mshirika status | CRDB latest deployment cannot be assumed from Mshirika latest marker. | Latest documented deployment was Mshirika-only for read-only beneficiary actions. | State current review target in the submission pack: Mshirika preview is current; CRDB update requires separate approval/access. | Environment-status note in the submission pack. |
| P1 | Tablet/phone | Responsive browser review is pending. | Dashboard and shell are desktop-first; acceptance docs keep phone-width verification unchecked. | Test target widths or explicitly declare desktop-first prototype review scope. | Responsive review note or accepted desktop-only boundary. |
| P1 | User/access confidence | CRDB private-site visibility and invitation activation remain operational risks. | Project memory documents separate site visibility, invitation, external identity, web role, and assignment gates. | If CRDB review is required, verify those gates as a bundled checklist. | CRDB access diagnostic note or documented blocker. |
| P1 | Documentation pack | Software-development documentation needs one cross-reference to prototype acceptance scope and future product vision. | User requested prototype documentation and future scalable/robust product vision. | Update submission docs to reference acceptance scope, gap matrix, known limitations, and future-product vision. | Clean shareable doc pack references these artifacts. |
| P1 | CRDB Microsoft ecosystem readiness | Scalable MEL platform infrastructure, Microsoft resources, and permissions need CRDB review before pilot/handover planning. | `crdb-microsoft-resources-permissions-20260813.md` defines required CRDB Microsoft ecosystem layers, resources, and permission gates. | Review the CRDB Microsoft ecosystem checklist with CRDB IT, SFU, reporting, risk, compliance, and enterprise architecture owners. | Confirmed owner/permission matrix or documented gaps. |
| P1 | Demo script | No single demo walkthrough is recorded. | Existing slice docs are implementation-focused. | Create a short demo script: dashboard, drill-through, beneficiary detail, form collect, saved records, reporting, access state, limitations. | `prototype-demo-script-YYYYMMDD.md`. |
| P2 | Dashboard visual evidence | Current visual state is acceptable by recent review, but screenshots are not recorded in the latest acceptance artifact. | User said "looking good" before CRDB update and next-slice cycle. | Capture current Mshirika screenshots if needed for client pack. | Screenshot references or review note. |
| P2 | Beneficiary persistence decision | Central beneficiary/monitored-entity tables are designed but not deployed. | `beneficiary-detail-model-slice-20260811.md` and schema artifacts define future direction. | Keep as review-only unless client requires persistent beneficiary master data in prototype. | Explicit decision note: defer or approve schema write. |
| P2 | Power BI | Power BI connection is guided but not verified as live. | `slice-checklist.md` leaves Power BI Desktop connection unchecked. | Treat as optional unless stakeholder insists. | Either connection evidence or limitation note. |
| Deferred | Offline | Editable local drafts and offline sync are not implemented. | `requirements.md` and `slice-checklist.md` defer offline work. | Future product slice after online path is stable. | Future roadmap item. |
| Deferred | Attachments | Binary file persistence is not production-grade through Power Pages browser route. | Attachment probe documented Power Pages rejection for direct binary file-column upload. | Future managed Microsoft mediator or proven supported route. | Future architecture decision. |
| Deferred | Multi-project platform | TACATDP is the proof-of-concept; reusable multi-project runtime is not fully implemented. | Project overview preserves seams but bounds near-term prototype. | Keep in future product vision; do not block TACATDP prototype. | Future product roadmap. |
| Deferred | Self-service form publishing | Self-service form-definition import/publish UI is not part of current prototype acceptance. | Existing requirements/ADR keep publish as future governed operation. | Future admin module. | Future roadmap item. |

## Recommended next slice

P0 end-to-end browser verification should be next:

1. Confirm current review target and signed-in user.
2. Open Mshirika with cache disabled or after Power Pages cache refresh.
3. Verify dashboard and Beneficiaries still render after the latest deployment.
4. Open Workspace/Project, load the TACATDP form, submit one safe test record, and record the result.
5. Confirm Saved records show the submitted record and that Data/Reporting reads behave as expected.
6. Record exact evidence and blockers.

If browser access blocks the P0 workflow, do not switch to UI polish. Record the access blocker and move to documentation pack updates that clearly identify the verification gap.

## Verification commands for documentation-only changes

Run from the repository root:

```bash
git diff --check
rg -n "prototype-acceptance-scope-20260812|prototype-gap-matrix-20260812" docs/powerpages-odk-webforms
```

No Power Pages upload, Dataverse schema write, or permission change is required for this documentation slice.
