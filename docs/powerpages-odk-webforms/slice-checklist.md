# Power Pages ODK Web Forms Slice Checklist

## Completed

- [x] ODK Central-inspired Dataverse schema deployed to the Power Pages environment.
- [x] Rich XForm-backed MVP form seeded.
- [x] Power Pages Web API settings configured for 8 `mp_*` tables.
- [x] Authenticated Users table permissions linked.
- [x] Invalid nameless site settings cleaned.
- [x] `/api-smoke` page uploaded.
- [x] Automated hosted-state smoke verifier added and passing.
- [x] Browser `/api-smoke` runtime test passed after Power Pages Security workspace table-permission role saves.
- [x] `EntityPermissionReadIsMissing` troubleshooting documented.
- [x] File-handling research documented for built-in Power Pages controls, file columns, and the hosted browser failure.
- [x] Monitoring Tool UX/design-system direction documented.

## Completed Slice: SPA Foundation

- [x] User stories captured.
- [x] SPA package skeleton created under `powerpages/webforms-spa/`.
- [x] Mobile-first shell created without ODK dependency installation.
- [x] Power Pages `/_api` client module added.
- [x] Local draft adapter stub added.
- [x] Source validator added for no-secret and `/_api` guardrails.
- [x] Package/version/license review accepted before package installation.

## Current Slice: ODK Runtime Proof

- [x] Review `vue`, `vite`, `@vitejs/plugin-vue`, `typescript`, `vue-tsc`, ODK Web Forms, and XForms engine package versions/licenses.
- [x] Install dependencies from the pinned package set.
- [x] Build the SPA locally.
- [x] Load one XForm XML payload through the API client.
- [x] Render through ODK Web Forms/XForms engine.
- [x] Removed browser-local runtime marker creation after form load because it produced false, non-restorable drafts.
- [x] Keep automated hosted-state smoke verifier as a required gate.

## Current Slice: Dataverse Submission Mapping

- [x] Map ODK Web Forms submit payload to `mp_submissions`.
- [x] Map canonical instance XML and compact submit metadata to `mp_submissionversions`.
- [x] Use Power Pages `/_api`, CSRF token handling, and deployed lookup navigation properties.
- [x] Update the source validator to guard the submit mapping path.
- [x] Add browser-visible submit diagnostics for build marker, ODK runtime click, ODK submit event, and Dataverse write attempt.
- [x] Confirm hosted browser shows build `submit-no-formversion-bind-20260711-001`.
- [x] Diagnose first submit authorization failure: ODK emitted ready payload, Power Pages blocked `mp_FormVersion@odata.bind` with `90040106` because `mp_formversion` lacked `Append To`.
- [x] Confirm a valid ODK Send emits the ODK submit event and creates `mp_submissions` plus `mp_submissionversions` rows.
- [x] Verify the submitted `SubmissionVersions` JSON preserves `assignmentKey`, `formVersionId`, and `xmlFormId` while browser submit skips the failing `Submissions.FormVersion` lookup bind.
- [x] Add attachment metadata handling after the base submit path works.
- [x] Verify hosted browser shows build `renderer-spacing-submit-label-20260711-001`.
- [x] Verify a submit with one photo/file creates an `mp_submissionattachment` row.
- [x] Verify whether Power Pages accepts or rejects the guarded file-column binary upload probe.
- [ ] Add browser-level submit verification against the Power Pages developer environment.

## Current Slice: Attachment Persistence Probe

- [x] Preserve the working `mp_submissions` and `mp_submissionversions` write path.
- [x] Extract non-`xml_submission_file` `File` values from the ODK submit payload.
- [x] Create `mp_submissionattachments` rows linked to the created submission version.
- [x] Attempt single-request `PATCH /_api/mp_submissionattachments(<id>)/mp_file` with `x-ms-file-name`.
- [x] Report attachment row count, binary upload count, and warning details in the hosted UI.
- [x] Browser-confirm binary upload behavior on the hosted Power Pages origin: metadata persists, direct file-column binary upload fails with `400` / `0x80048d19`, and `mp_file_name` remains null.

### Submit Diagnosis Workflow

If clicking ODK Send appears to reload the page or returns to the top with answers still filled, do not patch the submit path from assumption. Use this sequence:

1. Confirm the hosted page shows build `submit-diagnostics-20260711-001`.
2. If the build marker is absent, clear Power Pages server-side cache through `/_services/about` or Power Pages preview, then retest.
3. Click Send once and inspect the visible diagnostics.
4. If `Last runtime click` changes but `Last ODK submit event` does not, treat it as an ODK validation/runtime issue and inspect visible validation errors before Dataverse code.
5. If `Last ODK submit event` changes but `Last Dataverse write` fails, use the displayed error and Power Pages `/_api`/table-permission docs. For `90040106` on `mp_formversion` to `mp_submission`, grant `Append To` on the `mp_formversion` table permission while keeping create/write/delete disabled.
6. If Dataverse write completes, verify new rows in `mp_submissions` and `mp_submissionversions`.

## Deferred

- [ ] Offline sync queue.
- [ ] Production-grade attachment binary persistence through a verified Power Pages file-column route or a managed Microsoft server-side mediator.
- [ ] Submission history.
- [ ] Production-scoped table permissions.
- [ ] Admin publishing UI.

## Next Slice: Reporting, Export, and Power BI

- [x] Research ODK Central, KoboToolbox, Microsoft Dataverse/Power BI, and OnaData availability.
- [x] Draft reporting/export requirements.
- [x] Draft reporting/export ADR.
- [x] Draft delivery plan and implementation instructions.
- [x] Draft acceptance criteria, user stories, traceability, artifact readiness, definition of done, and verification summary.
- [x] Draft additive Dataverse reporting schema artifacts.
- [x] Deploy the additive reporting schema after approval: 4 tables, 58 columns, 13 relationships, and 4 alternate keys.
- [x] Select browser-generated CSV from reporting projections for the first bounded export slice; keep XLSX mechanism deferred until hosted repeat data exists.
- [x] Implement and execute projection rebuild from latest current submission versions.
- [x] Configure authenticated Power Pages Web API settings and table permissions for reporting and export settings tables.
- [x] Build Monitoring Tool Data area against reporting projections with server-side pagination/filtering and normalized answer detail.
- [x] Build named root CSV export UX with reusable settings stored in `mp_exportsettings`.
- [x] Build actionable Power BI guidance panel with environment URL, reporting tables, relationship guidance, and permission boundary.
- [x] Upload reporting portal build `reporting-data-export-powerbi-20260715-001` to the explicit development website ID.
- [x] Replace unsupported reporting `$skip` with FetchXML `count`/`page` in build `reporting-fetchxml-exportname-20260715-001`.
- [x] Prove Power Pages `9004010A` is caused by combining FetchXML `returntotalrecordcount` with OData `$count`, package corrected build `reporting-count-fix-20260715-002`, and add a regression validator.
- [x] Upload `reporting-count-fix-20260715-002`; verify both hosted Home markers, the enhanced web-file hash, and the complete hosted configuration state.
- [ ] Verify the authenticated Data tab returns rows and total count without `9004010A` after server-side cache refresh.
- [x] Generate new CSV export names as `<Form_Name>_YYYYMMDD_HHMMSS` with spaces replaced by underscores.
- [ ] Browser-verify authenticated `/_api` reporting reads and CSV download after Power Pages cache refresh.
- [ ] Verify Power BI Desktop connection to Dataverse reporting tables.

### Reporting Backend Verification: 2026-07-14

- [x] Projected 5 canonical submissions into 5 root report rows and 145 answer rows with 0 failures.
- [x] Hosted verifier passed with 12 table permissions and 24 Web API settings.
- [ ] Capture a hosted repeat-group submission; current live repeat row count is 0 and repeat behavior is fixture-validated only.
- [ ] Add automatic projection refresh after submit/edit; activation was explicitly deferred on 2026-07-15 and the current trusted rebuild path remains `scripts/build-reporting-projections.py --execute`.

### Next Slice: Automatic Projection Refresh Artifacts

- [x] Research Dataverse asynchronous plug-ins, Power Automate triggers, async failure/retry, tracing, performance, upsert, and solution ALM.
- [x] Draft requirements note and product requirements.
- [x] Draft ADR 0004 selecting an asynchronous PostOperation plug-in on `SubmissionVersion` Create.
- [x] Draft user stories, acceptance criteria, traceability, delivery/rollback plan, test strategy, readiness, definition of done, and verification summary.
- [x] Approve ADR 0004 before implementation.
- [x] Scaffold the `net462` plug-in project with exact package versions and a dependency lock.
- [x] Implement the stateless C# projection core and Dataverse adapter.
- [x] Persist XForm repeat paths in new submission metadata for singleton/nested repeat projection.
- [x] Validate normalized Python/C# output against the shared synthetic fixture.
- [x] Build and inspect the local Release plug-in package without uploading it.
- [x] Register the signed assembly and plug-in type in the development `tacatdp_prototype` solution after environment-write approval.
- [ ] Create the dedicated least-privilege execution identity/role and register the step/post image; explicitly deferred on 2026-07-15.

## Next Slice: Monitoring Tool UX Foundation

- [x] Rename user-facing shell text to **Monitoring Tool**.
- [x] Add CRDB-branded design tokens from `assets/images/CRDB_Bank_PLC.svg` and verify contrast-oriented darker shell primary.
- [x] Add reusable shell sections: app shell, top action bar, loading panel, project card, form card, status banner, debug panel, ODK runtime boundary.
- [x] Route unauthenticated users to Power Pages / Microsoft Entra sign-in when the Power Pages token provider is unavailable.
- [x] Present a work queue first: project/form cards, draft count, session indicator, and signed-in user in the top shell.
- [x] Move prototype diagnostics behind a collapsed debug panel.
- [x] Keep attachment binary warnings visible but not as a full submission failure when metadata persisted.
- [x] Verify host CSS does not broadly restyle ODK controls with the source validator.
- [x] Upload build `monitoring-tool-ux-foundation-20260711-001` to the explicit Power Pages website ID.
- [x] Post-upload PAC download verifies Home references `index-CLUTd6fC.mjs` and `index-CLlTa1IS.css`.
- [ ] Verify phone-width layout in a signed-in browser session.
- [ ] Verify the signed-in browser can start the form, submit, and see the collapsed diagnostics only when expanded.

## Current Slice: CRUD Workspace Revision

- [x] Replace assigned-form-first shell with project cards as the first screen.
- [x] Add project-detail workspace with icon+text Back and Add new actions.
- [x] Add Saved and Drafts tabs for project data cards.
- [x] Page data cards at 10 records per page.
- [x] Use Open for existing saved/draft cards and avoid Start in the shell.
- [x] Preserve online/offline status in the project workspace and runner top bar.
- [x] Keep ODK Web Forms isolated inside `OdkRuntimeBoundary`.
- [x] Replace text glyph action markers (`<`, `>`, `R`, `S`, `D`, `+`) with maintained Lucide Vue icons.
- [x] Filter non-restorable runtime-load markers out of the Drafts list.
- [x] Update source validator so form load cannot reintroduce automatic draft marker creation.
- [ ] Verify the signed-in browser shows only one CRDB header, project cards first, and the project detail data-card tabs.

## Current Slice: Shared Submitted Records Search/Edit

- [x] Change Saved records from current-user-only to all submitted records readable by authenticated Power Pages table permissions.
- [x] Keep Add new scoped to the signed-in user's `FormAssignments`.
- [x] Add search-as-you-type at the end of the Saved/Drafts toolbar.
- [x] Search loaded records by instance id, owner, form metadata, status, version, and timestamp.
- [x] Show owner email, latest version number, submitted status, and updated timestamp on saved cards.
- [x] Change saved card action to Edit.
- [x] Use ODK Web Forms `editInstance` with latest `SubmissionVersions.XFormSubmissionXml`.
- [x] Submit from edit mode writes a new `SubmissionVersions` row for the same ODK `instanceID` and updates the submission header timestamp.
- [x] Update validator to block reintroducing signed-in-user filtering on saved submitted records.
- [x] Add CRDB-branded submit progress overlay and return successful submits to the Saved data-card list with the Dataverse result banner.
- [x] Fix edit submit source path so the selected Dataverse submission row is the canonical edit target even if ODK Web Forms emits a new edit-session `instanceID`.
- [x] Add source metadata path for saved card display names from XLSForm `instance_name`, with fallback to canonical instance id.
- [ ] Browser-verify that John and test user both see the same submitted-record list after Power Pages cache refresh.
- [ ] Browser-verify that Edit opens a submitted record with previous answers populated and submit creates version `n+1`.
- [ ] Browser-verify that Edit does not increase the Saved card count.
- [ ] Browser-verify that revised-form saved cards display `Customer_ID:Customer_Name` after the full XLSForm seed is deployed.
- [ ] Browser-verify hosted build `submit-progress-return-list-20260712-001`: submit shows the CRDB loading dots, returns to Saved, and preserves attachment warnings in the banner.

## Next Slice: Editable Local Draft Resume

- [ ] Store local draft instance XML/state, not just metadata.
- [ ] Restore local draft instance XML/state into ODK Web Forms without creating a submitted Dataverse version.
- [ ] Add lifecycle/review locking rules so submitted records become read-only when locked.
- [ ] Add automated checks that opening records does not create a new record or draft unless the user explicitly chooses Add new or Save draft.

## UX Scope Discipline

- [ ] Before future UX-impacting work, capture behavior and data scope first: who sees which records, what is loaded client-side versus paged from Dataverse, which fields are searchable, what each action mutates, and what happens in empty/error/loading states.

## Next Slice: Full XLSForm Import

- [x] Inspect `docs/Revised_TACATDP impact evaluation_20260712.xlsx` without committing the temporary `.~lock` file.
- [x] Document pyxform research, package review, requirements, and implementation plan.
- [x] Install `pyxform==4.5.0` in a project-local tool environment after approval.
- [x] Compile `docs/Revised_TACATDP impact evaluation_20260712.xlsx` to XForm XML.
- [x] Validate generated XForm XML parse, body refs, form id, version, and instance-name expression.
- [x] Add seed-script support for compiled XML and dry-run Dataverse update.
- [x] Dry-run Dataverse seed update before live write.
- [x] Implement Dataverse file-column/FormAttachments storage for full compiled XForms larger than `FormVersions.XFormXml`.
- [x] Update the SPA to load large XForm XML from the Dataverse-managed file source, then render ODK Web Forms.
- [x] Execute Dataverse seed for version `20260712174458448`, storing `FormVersions.XFormXml` as `dataverse-file:tacatdp_impact_evaluation-20260712174458448.xml`.
- [x] Upload compiled XML to `FormAttachments.File` and repoint John/test assignments to the compiled version.
- [x] Upload Power Pages build `xform-file-source-20260712-001`.
- [x] Verify hosted Dataverse state after upload: file-backed XML downloads, parses, and has 428 unique absolute body refs.
- [x] Diagnose browser render regression where the pyxform output loaded but showed only heading/submit because it was serialized with `html:`/`ns1:` prefixes instead of the renderer-compatible `h:html` plus default XForms namespace shape.
- [x] Normalize compiled XForm namespace serialization in `scripts/xlsform-compile.py`.
- [x] Compile and seed normalized version `20260712182300000`; hosted verifier downloads `16,673,209` bytes and confirms 428 unique body refs.
- [ ] Browser-verify the signed-in site loads the full compiled TACATDP Impact Evaluation form from Dataverse file storage.
