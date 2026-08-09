# XLSForm Self-Service Requirements

Date: 2026-07-15
Status: proposed

## Users and Permissions

- A Collector can collect and view permitted data but cannot manage form definitions.
- A Form Manager can upload, validate, replace, abandon, download, and preview a draft revision for an assigned project.
- A Publisher can publish, retire, or restore an eligible version.
- The first release may assign Form Manager and Publisher to the same people, but authorization must remain separable.
- Every action must be constrained to the current project and enforced server-side through web roles and table permissions.

## User Experience

- Form management remains inside an opened project; it is not a top-level form selector.
- The project header continues to show the project title and right-aligned Collect action.
- Add a restrained **Manage form** action for authorized users, leading to a project-scoped form management view.
- The first viewport shows the **Current form** status, published version, publication date, and an **Upload revision** action.
- The revision workflow uses four clear stages: Upload, Check, Review, Publish.
- Visible terminology must use bank-operational language such as Current form, Revision, Check results, Preview, and Publish. Terms such as pyxform, XForm, XML schema, and entity set remain in diagnostics available to technical support only.
- Validation results show blocking errors before warnings. Each issue identifies the workbook sheet, row, field where available, plain-language impact, and corrective action.
- The review stage summarizes added, removed, renamed, and type-changed fields plus repeat-group changes and reporting impact.
- Preview renders the draft form without changing the active collection form or writing production submissions.
- Publish requires confirmation and a release note and states that the revision affects future collections only.
- Version history provides status, version, uploader, upload time, publisher, publish time, release note, and actions appropriate to state.
- Processing states must survive refresh and show queued, checking, ready, failed, abandoned, and published outcomes without blocking the page.

## Import and Validation

- Accept one `.xlsx` workbook per import, initially capped at 10 MB pending hosted limit verification.
- Reject macro-enabled, encrypted, malformed, unsupported, or deceptively named files.
- Verify required XLSForm sheets and settings, including a stable `form_id` matching the current form.
- Generate a unique immutable published version when a supplied version is empty or conflicts.
- Compile with a pinned pyxform version in an isolated server-side process.
- Preserve the source workbook, compiled XForm, compiler version, content hash, diagnostics, and compatibility result.
- Store the compiled XForm in Dataverse-managed file storage when it exceeds the memo-column limit.
- A failed import must not alter the current published form or assignment.
- Re-upload may replace an unpublished draft but must not overwrite a published version.
- Duplicate source hashes should warn the user and avoid redundant compilation unless explicitly retried by support.

## Version and Publication Semantics

- `Forms` remains the stable identity and `FormVersions` remains immutable after publication.
- An upload creates an import job and, after successful validation, a Draft form version.
- Only one ready draft per form is supported in the first release.
- Publish atomically marks the draft Published and updates future active assignments to it.
- Existing submissions and edits remain associated with the form version on which they were created unless an explicit migration feature is approved later.
- Retiring a version prevents new collection from that version but never deletes its submissions or stored definition.
- Restore creates a new publication decision pointing future assignments to an earlier valid definition; it does not rewrite history.

## Reliability, Security, and Audit

- Browser requests use the Power Pages authenticated session, CSRF protection, and a flow restricted to the correct web role.
- The compiler endpoint is not directly callable from browser code and uses an approved service identity.
- Import processing is idempotent by job identifier and records retry count and terminal failure details.
- Workbook parsing has decompressed-size, row, cell, duration, and memory limits.
- User-facing diagnostics never include secrets, connection details, stack traces, or arbitrary workbook formulas rendered as HTML.
- All upload, validation, abandon, publish, retire, restore, and download events are auditable.
- The current published version remains available if compilation infrastructure is unavailable.

## Acceptance Criteria

- An authorized Form Manager can upload the current 2.4 MB TACATDP workbook and receive a job identifier without a full-page wait.
- A Collector cannot see or invoke upload or publish operations.
- Invalid workbooks produce actionable diagnostics and do not change the current form.
- A valid revision reaches Ready state, can be previewed, and remains invisible to Collect until publication.
- Publishing changes the Collect action to the new version for future sessions while historical records retain their old version.
- Refreshing or reopening the project shows the correct import status and version history.
- The managed solution can be imported into a clean target with required connection references/environment variables and the cloud flow can be registered with the site.
