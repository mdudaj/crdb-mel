# Assignment Startup and Collect Runtime Delivery Note

Date: 2026-07-29

## Task Classification

Frontend performance and runtime-readiness slice. No Dataverse schema, permission, or authentication changes are included.

## User Finding

After the Mshirika loading-performance upload, browser timing showed:

```text
[TACATDP perf] api:listAssignedForms: 10642.1ms
[TACATDP perf] view:loadWorkspace: 10642.2ms
```

The user also reported that opening a project and clicking Collect left the data collection form loading.

## Requirements Note

- Initial assignment startup must not load large XForm XML.
- Project and form cards should render from assignment/form metadata only.
- Collect/Edit should fetch the XForm XML only when the form runtime is opened.
- ODK runtime must mount only after XForm XML is available.
- Do not upload a runtime-enabled build that exceeds Power Pages web-file/package constraints.

## UX Description

The project workspace remains unchanged visually. Startup should feel faster because the shell and project metadata load before any form XML. When Collect is opened, the existing runner loading panel remains visible while the platform fetches the XForm XML. If hydration fails, the runner shows an explicit error instead of an indefinite loading state.

## Accessibility Checklist

- Existing Collect button semantics are unchanged.
- Existing runner loading panel remains `aria-live`.
- ODK runtime host now renders only when required form XML exists.
- Failure state uses the existing status banner instead of a silent spinner.

## Acceptance Criteria

- `api:listAssignedForms` no longer calls XForm resolution.
- `toSummary()` does not read `mp_xformxml` or call `resolveFormVersionXForm`.
- `api:hydrateAssignmentRuntime` loads XForm XML at Collect/Edit time.
- ODK component mounts only when `selectedAssignment.xformXml` exists.
- Access build remains uploadable under the current Power Pages constraints.
- Runtime-enabled build blocker is documented before any further Collect deployment.

## Change Summary

- Made `FormAssignmentSummary.xformXml` optional.
- Added cached metadata/runtime form-version paths in `PowerPagesApiClient`.
- Added `hydrateAssignmentRuntime()` for timed Collect/Edit XForm loading.
- Updated `openRunner()` to hydrate XForm XML before mounting ODK.
- Updated the ODK host guard to require hydrated XML.
- Added a `build:mshirika-runtime` build command for runtime investigation.
- Added validator checks preventing startup XForm hydration regressions.
- Packaged the uploadable access bundle `index-DJMa_UT7.mjs` with cache marker `assignment-startup-20260729-001`.

## Runtime Packaging Finding

The runtime-enabled build succeeds locally but emits ODK chunks that exceed the previously observed Power Pages web-file/content limit:

```text
dist/assets/dist-pLvMFTNt.mjs                        1,795,998 bytes
dist/assets/index-Cg9qvMI9-CaiUDr-N.mjs              2,239,952 bytes
```

The access build remains uploadable:

```text
dist/assets/index-DJMa_UT7.mjs                       128,150 bytes
dist/assets/vendor-datepicker-C8ItObQq.mjs           285,284 bytes
dist/assets/vendor-icons-CVcq-M7M.mjs                  6,825 bytes
```

Therefore, Collect cannot be restored by simply deploying the runtime-enabled build through the same Power Pages web-file package. A separate ODK runtime packaging decision is required.

## Options for Collect Runtime

1. Split or rebuild ODK runtime chunks below the Power Pages web-file limit.
2. Host ODK runtime chunks from an approved Microsoft static hosting endpoint and keep Power Pages as the authenticated shell.
3. Keep the current access/reporting shell uploadable and defer Collect until CRDB approves the runtime hosting path.

## Verification Summary

Commands run:

```bash
npm --prefix powerpages/webforms-spa run build:mshirika-access
npm --prefix powerpages/webforms-spa run build:mshirika-runtime
python3 scripts/validate-webforms-spa-foundation.py
python3 scripts/validate-access-mshirika-activation.py
git diff --check
```

Results:

- `build:mshirika-access`: passed.
- `build:mshirika-runtime`: passed locally but is not uploadable as-is because two runtime chunks exceed 1MB.
- `validate-webforms-spa-foundation.py`: passed.
- `validate-access-mshirika-activation.py`: passed.
- `git diff --check`: passed.

## Mshirika Upload

Uploaded the access/startup package to Mshirika with:

```bash
pac pages upload \
  --environment "https://orga3cf4b37.crm4.dynamics.com/" \
  --path ./powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool \
  --modelVersion Enhanced \
  --forceUploadAll
```

Result:

- Upload succeeded in 56.91 seconds.
- PAC again printed non-terminal `powerpagecomponent ... Does Not Exist` sync warnings, then completed with `Power Pages website upload succeeded`.

## Render Evidence

No hosted screenshot was captured in this slice. The uploadable package is prepared for startup timing review. Collect runtime review remains blocked by ODK chunk packaging, not by the runner UI path.

## Artifact Readiness

Assignment-startup access bundle uploaded to Mshirika for timing review. Not ready to upload the runtime-enabled Collect build until one runtime packaging option is selected and validated.
