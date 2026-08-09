# Platform Branding Generalization

Date: 2026-07-21

## Requirement

The portal is now a general-purpose projects monitoring tool. TACATDP is the
first project implemented on the platform, but it must not be presented as the
platform identity.

## UX Rule

- Global shell, sign-in copy, side navigation, top bar, and hidden Power Pages
  header metadata use `Impact Monitoring`.
- TACATDP appears only when the TACATDP project/form is being shown in project
  context, for example `TACATDP Impact Evaluation` in project cards, project
  workspace title, form runner title, exports, and reporting rows.
- Project-specific configuration remains data-driven where possible; future
  projects should appear as additional project rows without changing the shell
  product name.

## Acceptance Criteria

- The sign-in panel invites users into Impact Monitoring, not directly into
  TACATDP.
- The left navigation brand shows `Impact Monitoring` without a secondary
  subtitle.
- The top app bar eyebrow shows `Impact Monitoring`.
- User & Access copy refers to project/form access generally.
- The TACATDP project still appears as `TACATDP Impact Evaluation` when the
  user views assigned projects or opens that project.
- The validator fails if TACATDP-specific copy returns to the global shell.

## Implementation Notes

- Runtime SPA changes live in
  `powerpages/webforms-spa/src/views/AssignedFormsView.vue`.
- Local HTML title lives in `powerpages/webforms-spa/index.html`.
- Hidden Power Pages header/snippet labels were updated in both source and
  upload packages so fallback/default chrome also uses the generic platform
  identity.
- `scripts/validate-webforms-spa-foundation.py` now requires the generic
  platform constants and rejects TACATDP shell-level copy.

## Verification

Local verification:

```bash
npm run build
python3 scripts/validate-webforms-spa-foundation.py
node --check powerpages/webforms-spa/dist/assets/index-IH70g70V.mjs
```

Results:

- `npm run build` passed. Vite still reports the known upstream ODK direct
  `eval` and chunk-size warnings.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check powerpages/webforms-spa/dist/assets/index-IH70g70V.mjs` passed.

Deployment verification:

- Uploaded the enhanced-model package to Mshirika
  `PowerPagesDeveloper-070926-125720`.
- `pac pages upload --modelVersion 2 --forceUploadAll` completed with
  `Power Pages website upload succeeded`.
- PAC emitted the known non-fatal `powerpagecomponent` warnings for missing
  component rows and oversized generated component content.
- Downloaded the hosted enhanced-model package to
  `/tmp/tacatdp-mshirika-branding-general-post-upload-20260721-001`.
- Downloaded Home references confirmed:
  - `index-IH70g70V.mjs?v=branding-general-20260721-001`;
  - `index-BVFW9552.css?v=branding-general-20260721-001`.
- Downloaded header/snippet labels confirmed `Projects Monitoring Tool` for
  that deployment.

## Naming Revision

On 2026-07-21, the generic product label was shortened from
`Projects Monitoring Tool` to `Impact Monitoring`. The same shell/project rule
still applies: TACATDP appears only when the TACATDP project is being viewed.
The side-navigation subtitle was removed after visual review to keep the brand
block compact.

Verification for the naming revision:

- `npm run build` passed. Vite still reports the known upstream ODK direct
  `eval` and chunk-size warnings.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check powerpages/webforms-spa/dist/assets/index-DLmZEiq9.mjs` passed.
- Uploaded the enhanced-model package to Mshirika
  `PowerPagesDeveloper-070926-125720`.
- `pac pages upload --modelVersion 2 --forceUploadAll` completed with
  `Power Pages website upload succeeded`.
- PAC emitted the known non-fatal `powerpagecomponent` warnings.
- Downloaded the hosted enhanced-model package to
  `/tmp/tacatdp-mshirika-impact-monitoring-post-upload-20260721-001`.
- Downloaded Home references confirmed:
  - `index-DLmZEiq9.mjs?v=impact-monitoring-20260721-001`;
  - `index-BVFW9552.css?v=impact-monitoring-20260721-001`.
- Downloaded header/snippet labels confirmed `Impact Monitoring`.
- `node --check` passed on the downloaded hosted `index-DLmZEiq9.mjs` entry.

No-subtitle revision:

- Removed the side-navigation secondary `Monitoring workspace` text from the
  runtime shell.
- `scripts/validate-webforms-spa-foundation.py` now rejects
  `Monitoring workspace` in the shell bundle.
- `npm run build` passed. Vite still reports the known upstream ODK direct
  `eval` and chunk-size warnings.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check powerpages/webforms-spa/dist/assets/index-DslXnEDW.mjs` passed.
- Uploaded the enhanced-model package to Mshirika
  `PowerPagesDeveloper-070926-125720`.
- `pac pages upload --modelVersion 2 --forceUploadAll` completed with
  `Power Pages website upload succeeded`.
- PAC emitted the known non-fatal `powerpagecomponent` warnings.
- Downloaded the hosted enhanced-model package to
  `/tmp/tacatdp-mshirika-impact-nosubtitle-post-upload-20260721-001`.
- Downloaded Home references confirmed:
  - `index-DslXnEDW.mjs?v=impact-monitoring-nosubtitle-20260721-001`;
  - `index-BVFW9552.css?v=impact-monitoring-nosubtitle-20260721-001`.
- `rg "Monitoring workspace|platformTagline"` found no matches in the
  downloaded hosted entry bundle or Home copies.
- `node --check` passed on the downloaded hosted `index-DslXnEDW.mjs` entry.

Logo-only side-navigation revision:

- Removed the side-navigation brand text container so the side nav shows only
  the CRDB logo.
- `scripts/validate-webforms-spa-foundation.py` now rejects
  `managed-side-nav__brand-text` in the runtime shell.
- `npm run build` passed. Vite still reports the known upstream ODK direct
  `eval` and chunk-size warnings.
- `python3 scripts/validate-webforms-spa-foundation.py` passed.
- `node --check powerpages/webforms-spa/dist/assets/index-DVzMB7jq.mjs` passed.
- Uploaded the enhanced-model package to Mshirika
  `PowerPagesDeveloper-070926-125720`.
- `pac pages upload --modelVersion 2 --forceUploadAll` completed with
  `Power Pages website upload succeeded`.
- PAC emitted the known non-fatal `powerpagecomponent` warnings.
- Downloaded the hosted enhanced-model package to
  `/tmp/tacatdp-mshirika-impact-logo-only-post-upload-20260721-001`.
- Downloaded Home references confirmed:
  - `index-DVzMB7jq.mjs?v=impact-monitoring-logo-only-20260721-001`;
  - `index-BVFW9552.css?v=impact-monitoring-logo-only-20260721-001`.
- `rg "managed-side-nav__brand-text|Monitoring workspace"` found no matches
  in the downloaded hosted entry bundle or Home copies.
- `node --check` passed on the downloaded hosted `index-DVzMB7jq.mjs` entry.
- `node --check` passed on the downloaded hosted `index-IH70g70V.mjs` entry.
