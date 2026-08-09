# Solution Update and XLSForm Self-Service Research

Date: 2026-07-15
Status: complete for planning

## Question 1: Updating the CRDB Environment

### Evidence

- The development environment contains the unmanaged source solution `tacatdp_prototype`, friendly name `TACATDP Impact Tracking Prototype`, version `0.1.0.0`.
- The previous CRDB import log identifies the delivered package as **managed**, version `0.1.0.0`, publisher `tacatdp`.
- Microsoft requires an update to keep the same solution lineage and use a version higher than the installed `major.minor.build.revision` value.
- Microsoft distinguishes three managed-solution actions:
  - **Update** replaces included components but leaves components omitted from the newer package in the target.
  - **Upgrade** also removes components that belonged to the older solution but are absent from the newer package.
  - **Stage for Upgrade** keeps old and new versions temporarily and is intended for migration before applying the upgrade.
- Power Pages site components created after the site was first added are not automatically added to its solution. Each new site component and each required Dataverse table must be included deliberately.
- Editing managed Power Pages configuration in CRDB creates an unmanaged layer that can mask later managed updates.

### Options

| Option | Use | Assessment |
| --- | --- | --- |
| Managed **Update** | Catch CRDB up without deleting omitted old components | Recommended for the next package because the current package inventory has not yet been proven as an authoritative deletion baseline |
| Managed **Upgrade** | Make CRDB exactly match the new package, including removals | Use after component inventory and deletion intent are verified |
| **Stage for Upgrade** | Run old and new side by side during data migration | Unnecessary unless a schema/data migration requires coexistence |
| Unmanaged import | Development-time customization in the target | Reject for CRDB; it weakens rollback and layering discipline |
| Patch/clone solution | Small patch chain | Reject for routine delivery; normal versioned updates are simpler and current Microsoft guidance favors them |

### Recommended Update Path

1. In CRDB, confirm `tacatdp_prototype` is installed as managed at `0.1.0.0` and inspect active solution layers for the site and key tables.
2. In development, retain the existing unique name and publisher; change the version to `0.2.0.0`.
3. Inventory and add every current component, including new Power Pages site components, web files, Dataverse tables/columns/keys, web roles/table permissions, site settings, environment-variable definitions, flows, and connection references.
4. Run dependency checks and export a managed package.
5. Import into CRDB using **Update**, without **Overwrite unmanaged customizations**.
6. Supply target environment-variable and connection values. Register any Power Pages cloud flows in CRDB.
7. Bind the imported website record if needed, restart the site, and run authenticated runtime smoke tests.
8. Move operational records such as forms, assignments, and seed data through a separate controlled data migration; ordinary solutions transport configuration, not the current business data set.

## Question 2: Portal Upload of Revised XLSForms

### Platform Findings

- Power Pages file columns support upload on basic and multistep forms, but Microsoft states that a file cannot be uploaded through a file column while the form is in Insert mode. A create-then-update interaction would therefore be required for that route.
- Power Pages can securely invoke a solution-aware Power Automate cloud flow associated with the site and restricted by web role. The trigger supports a `File` parameter and portal requests use the authenticated application session plus a CSRF token.
- Power Pages portal Web API supports only a subset of Dataverse operations and does not support actions/functions. Direct custom binary file-column upload through the portal API is not documented as a supported primary path.
- The current workbook is about 2.4 MB, while its compiled XForm is much larger and already requires Dataverse file storage. Compilation and validation must occur on the server, not in the browser.
- The repository already has a pinned pyxform-based compiler and immutable `Forms` / `FormVersions` / `FormAttachments` model. The current developer seed path publishes immediately and must be split into draft and publish operations for self-service.
- ODK Central provides a useful precedent: upload creates or replaces a privileged draft, validation occurs before release, and publishing is a separate action. Published data remains associated with the form version that collected it.

### Architecture Options

| Option | Advantages | Limitations | Decision |
| --- | --- | --- | --- |
| Power Pages cloud flow receives the workbook; asynchronous Python compiler validates it | Official portal file parameter, web-role security, solution-aware flow, clean UX | Requires Power Automate production licensing and an approved Python hosting service | **Recommended** |
| Basic form creates an import record, then update form uploads its file | Mostly native controls and Dataverse file storage | Two-step UX caused by the Insert-mode restriction; still needs a compiler | Viable fallback |
| Custom SPA writes binary directly to a Dataverse file column | Maximum UX control | Not sufficiently documented or proven through Power Pages in this project | Spike only, not baseline |
| Portal upload with administrator running the current script | Smallest initial change | Not self-service and retains operational dependency on a developer | Interim slice only |
| Upload precompiled XForm XML | Avoids hosted pyxform | Exposes technical internals and is unsuitable for bank operations staff | Reject |
| Reimplement XLSForm conversion in Power Automate or a Dataverse plug-in | Keeps processing inside Power Platform | High complexity, parser risk, and poor parity with pyxform | Reject |

### Recommended Processing Boundary

1. The portal invokes a role-secured, solution-aware flow with the `.xlsx` file and target form identifier.
2. The flow creates an import job, stores the source workbook under a generated file identity, and returns the job identifier quickly.
3. The flow dispatches compilation to an approved Python Azure Function or equivalent managed service running the repository's pinned pyxform version.
4. The compiler validates workbook structure, size, file signature, `form_id`, version rules, field compatibility, and generated XML.
5. Results are written back as a Draft `FormVersion`, compiled XForm attachment, hash, diagnostics, and compatibility summary.
6. The portal polls the job and presents errors, warnings, changes, preview, and version history.
7. Publishing is a separate authorized command. It changes the draft to Published and switches future collection assignments atomically; existing submissions remain bound to their original version.

## Security and Operations

- Allow only `.xlsx`; reject macros and legacy `.xls` in the first release.
- Validate extension, MIME hint, ZIP/XLSX signature, workbook structure, decompressed size, row/cell limits, and pyxform output.
- Generate storage names; retain the original name only as metadata.
- Restrict upload/preview and publish through distinct web roles and Dataverse table permissions.
- Apply request, file-size, execution-time, and concurrency limits; prevent duplicate imports using the workbook hash.
- Do not expose compiler credentials or function keys to browser code.
- Record uploader, timestamps, diagnostics, publisher, release note, source hash, and previous/current version links.
- Decide with CRDB security whether malware scanning is required before processing Office Open XML files.

## Primary References

- Microsoft, Upgrade or update a solution: https://learn.microsoft.com/en-us/power-apps/maker/data-platform/update-solutions
- Microsoft, Import solutions: https://learn.microsoft.com/en-us/power-apps/maker/data-platform/import-update-export-solutions
- Microsoft, Use solutions with Power Pages: https://learn.microsoft.com/en-us/power-pages/configure/power-pages-solutions
- Microsoft, Solution layers: https://learn.microsoft.com/en-us/power-apps/maker/data-platform/solution-layers
- Microsoft, Configure a file column on Power Pages: https://learn.microsoft.com/en-us/power-pages/configure/file-column
- Microsoft, Configure Power Automate cloud flows in Power Pages: https://learn.microsoft.com/en-us/power-pages/configure/cloud-flow-integration
- Microsoft, Power Pages portals Web API: https://learn.microsoft.com/en-us/power-pages/configure/web-api-overview
- Microsoft, Azure Functions Python reference: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python
- ODK, Managing Forms in Central: https://docs.getodk.org/central-forms/
- OWASP, File Upload Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
