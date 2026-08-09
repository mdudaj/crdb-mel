# ADR-0006: Package Deployer for TACATDP Seed Data and XForm

Date: 2026-07-15
Status: accepted

## Context

Dataverse solutions transport schema and solution-aware components, not arbitrary custom-table rows and file-column values. CMT successfully validated the TACATDP lookup schema only when lookups were encoded as `entityreference`, then failed on `mp_formattachment.mp_file`. Continuing to patch CMT archives would produce an unsupported and fragile delivery path.

## Decision

Use Microsoft Package Deployer as the release unit. Bundle the existing managed no-plug-in solution, the approved XForm, and a package extension that runs after solution import. The extension upserts the four seed records and uploads the XForm with Dataverse's block file API.

The package extension is client-side deployment code. It is not imported or registered as a Dataverse plug-in assembly, so it does not require `prvCreatePluginAssembly`.

## Consequences

- CRDB receives one reproducible `.pdpkg.zip` artifact and one `pac package deploy` command.
- The deployment user still needs solution import privileges plus create/update/append/append-to rights for the four seed tables and file upload rights on FormAttachments.
- The package can be retried without generating duplicate rows.
- Automatic reporting projection remains excluded until plug-in permission is approved.
- Rollback is corrective deployment with a higher version; the package never deletes the managed solution or seed data.

## Rejected Alternatives

- Hand-editing CMT archives: rejected after repeated schema/file validation failures.
- Manual row and file upload: rejected because it is not repeatable ALM.
- Embedding the 16.7 MB XForm in a Dataverse text column: rejected because the column limit is insufficient.
- Registering a server plug-in to seed data: rejected because CRDB has not granted `prvCreatePluginAssembly` and deployment does not require runtime automation.
