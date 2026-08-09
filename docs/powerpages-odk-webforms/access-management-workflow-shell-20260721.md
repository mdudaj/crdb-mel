# User & Access Workflow Shell

Date: 2026-07-21

## Requirement

Add a safe, business-readable **Add user access** workflow inside the portal
User & Access route. The workflow must improve the UX for CRDB/DAMAX review
without creating or updating Dataverse records until the write permission,
assignment model, and audit path are approved.

## UX Description

The administrator opens User & Access and selects **Add user**. A governed
workflow panel opens with five steps:

1. User email.
2. Contact status.
3. Role.
4. Project and form access.
5. Confirmation preview.

The final step summarizes the intended user, contact state, role, project, and
forms. The final create action is disabled and explicitly states that access
writes are pending approval.

## Acceptance Criteria

- **Add user** is enabled for administrators.
- The workflow collects email, role, project, and form selections.
- Contact status is shown using the current assignment/contact data available
  to the read-only User & Access slice.
- The final step is a preview only and must not call any Dataverse write API.
- The final create button is disabled.
- The workflow uses existing shell spacing, cards, icon buttons, status chips,
  and restrained CRDB styling.
- The validator fails if the disabled write warning or workflow shell is
  removed.

## Accessibility Checklist

- The workflow panel has labelled title and description.
- Step navigation uses buttons and exposes the current step through
  `aria-current="step"`.
- Inputs have visible labels.
- Checkbox rows preserve native checkbox semantics.
- The disabled final action has an explicit accessible label.
- Contact state is shown as text, not color alone.

## Implementation Notes

- Runtime implementation:
  `powerpages/webforms-spa/src/views/AssignedFormsView.vue`.
- Styling:
  `powerpages/webforms-spa/src/styles.css`.
- Guardrail:
  `scripts/validate-webforms-spa-foundation.py`.
- This slice intentionally adds no Power Pages Web API write functions and no
  Dataverse permission changes.

## Verification

Local verification:

```bash
npm run build
python3 scripts/validate-webforms-spa-foundation.py
node --check powerpages/webforms-spa/dist/assets/index-DR9CtNRo.mjs
```

Results:

- `npm run build` passed. Vite still reports the known upstream ODK direct
  `eval` and chunk-size warnings.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check powerpages/webforms-spa/dist/assets/index-DR9CtNRo.mjs` passed.
- `rg "createFormAssignment|createAccess|mp_formassignments.*POST|POST.*mp_formassignments"` found no new assignment-write path in the SPA source.

Deployment verification:

- Uploaded the enhanced-model package to Mshirika
  `PowerPagesDeveloper-070926-125720`.
- `pac pages upload --modelVersion 2 --forceUploadAll` completed with
  `Power Pages website upload succeeded`.
- PAC emitted the known non-fatal `powerpagecomponent` warnings.
- Downloaded the hosted enhanced-model package to
  `/tmp/tacatdp-mshirika-access-workflow-post-upload-20260721-001`.
- Downloaded Home references confirmed:
  - `index-DR9CtNRo.mjs?v=access-workflow-shell-20260721-001`;
  - `index-D1C2E4gN.css?v=access-workflow-shell-20260721-001`.
- Downloaded hosted bundle contains `Add user access`,
  `Create access disabled`, and the preview-only Dataverse warning.
- `node --check` passed on the downloaded hosted `index-DR9CtNRo.mjs` entry.
