# Solution Update and XLSForm Self-Service Delivery Plan

Date: 2026-07-15
Status: proposed

## Track A: CRDB Catch-Up Package

### A1. Target Audit

- In CRDB, record the installed `tacatdp_prototype` version and managed state.
- Inspect solution history, dependencies, active layers, Power Pages website binding, and any CRDB-only configuration.
- Export or record current environment-variable values, connection ownership, web roles, and site registration without copying secrets into the repository.

### A2. Source Package Inventory

- Keep unique name `tacatdp_prototype`, publisher `tacatdp`, and set version `0.2.0.0`.
- Compare the current development site and schema with solution contents.
- Add all missing Power Pages site components and Dataverse components explicitly.
- Include solution-aware flows, connection references, and environment-variable definitions only after their implementation is complete.
- Validate dependencies and produce a component manifest for review.

### A3. Import and Verification

- Export a managed package and preserve its manifest/hash as a release artifact.
- Import into CRDB using **Update** and leave **Overwrite unmanaged customizations** disabled.
- Map approved connections and environment values; register site cloud flows; bind/restart the site if required.
- Seed/migrate current operational form records separately.
- Smoke-test project selection, Collect, submit/edit, Data pagination, export naming/download, Power BI guidance, and permissions.
- Adopt **Upgrade** in a later release only after a deletion-aware package diff is reviewed.

## Track B: XLSForm Upload Foundation

### B1. Hosted Feasibility Spike

- Prove a Power Pages cloud-flow trigger can receive the current 2.4 MB workbook in the development site and return a job identifier.
- Prove the selected Python host can compile it with the pinned pyxform version within agreed time and memory limits.
- Measure base64/request overhead, generated XForm size, execution duration, and Dataverse file-write behavior.
- Confirm CRDB licensing, DLP policy, Azure hosting approval, service identity, network path, malware-scanning requirement, and operational owner.
- Stop before product implementation if any of these gates is unresolved; retain the admin-assisted upload fallback.

### B2. Data Contract

- Add a `FormImportJob` table with project/form lookup, status, original display filename, generated storage name, source file, source hash, compiler version, diagnostics, compatibility summary, timestamps, requester, and resulting draft lookup.
- Add publication metadata needed for release notes, publisher, prior version, and restore audit.
- Define alternate keys/idempotency rules and Draft/Published/Retired transitions.
- Define web roles, table permissions, and column exposure before enabling portal APIs.

### B3. Compiler Service

- Extract the current compile behavior into a deterministic library used by both CLI and hosted entrypoints.
- Pin dependencies and add malicious/malformed workbook limits.
- Produce structured diagnostics and a machine-readable field compatibility diff.
- Persist source and compiled artifacts using generated identifiers.
- Add unit fixtures for valid, warning, invalid, oversized, encrypted, duplicate, form-id mismatch, field-removal, and type-change cases.

### B4. Orchestration

- Create a solution-aware Power Pages-triggered flow with a File parameter.
- Create the job and return promptly; dispatch compilation asynchronously.
- Write terminal results idempotently and keep technical failures separate from user-safe diagnostics.
- Add retry and dead-letter/support handling without automatic publication.

### B5. Portal UX

- Add project-scoped **Manage form** access for authorized users.
- Build Current form, Upload revision, Check results, Review changes, Preview, and Publish states.
- Add persistent status polling and version history.
- Use the existing design tokens and compact Material-style interaction patterns; do not introduce nested cards or researcher-oriented terminology.
- Verify keyboard operation, focus management, responsive layout, long filenames, progress states, and error summaries.

### B6. Publication and Rollback

- Implement a server-side Publish command with concurrency checks and release-note requirement.
- Update future assignments in one controlled operation and retain old version bindings.
- Implement abandon, retire, and restore semantics with audit records.
- Prevent publish when validation is stale, incomplete, failed, or based on a changed source hash.

### B7. ALM and Rollout

- Add all schema, site components, flow, connection references, environment variables, roles, and permissions to the same solution lineage.
- Deploy first to development, then a CRDB test/UAT environment if available, then production through an approved managed update.
- Register the cloud flow with each target site after import.
- Provide support runbooks for stuck jobs, compiler outage, failed publish, and restoring the prior version.

## Verification Gates

- Local compiler regression and security fixtures pass.
- SPA build and foundation validators pass.
- Hosted upload/compile completes with the current TACATDP workbook.
- Unauthorized role tests fail closed for list, upload, download, preview, and publish.
- Draft does not alter Collect; publish changes only future collection; historical submissions retain their version.
- Solution checker, dependency check, managed import into a clean target, flow registration, and authenticated browser smoke pass.
- No secrets, environment-specific URLs, connection IDs, or function keys are embedded in source or web assets.

## Approval Gates

- CRDB target audit and managed solution import.
- Power Automate production licensing and DLP review.
- Python/Azure hosting, service identity, and network/security approval.
- Dataverse schema and permission changes.
- Power Pages site upload and publish.
- Production publication of the first user-uploaded form revision.
