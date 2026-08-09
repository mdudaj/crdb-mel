# TACATDP Governed Seed Deployment Requirements

Date: 2026-07-16
Status: approved direction after Configuration Migration Tool file-column failure

## Problem

The managed solution installs TACATDP schema and Power Pages components, but the CRDB environment also needs one project, one form, one published form version, one form attachment row, and the approved 16.7 MB XForm in `mp_formattachment.mp_file`. Configuration Migration Tool validates the lookup fields after using `entityreference`, but rejects the Dataverse file column as missing.

## Requirements

1. Deliver one versioned Microsoft Package Deployer artifact, not a hand-edited CMT archive or manual table upload.
2. Preserve managed solution unique name `tacatdp_prototype`, version `0.2.2.0`, and the no-plug-in package boundary.
3. Import or update the managed solution before writing seed records.
4. Upsert Project, Form, FormVersion, FormAssignments, and FormAttachment with stable IDs and dependency-order lookups.
5. Keep the active assignment for confirmed Power Pages contact email `Denis.Muroba@crdbbank.co.tz`.
6. Add active assignments for both supplied Hailo Kibiki identities, `Hailo.Kibiki@crdbbank.co.tz` and `hkibiki@crdbbank.co.tz`, because no Hailo contact exists yet and the portal filters assignments by the contact email populated from Entra `preferred_username`.
7. Validate the approved XForm SHA-256 before any seed mutation.
8. Upload the XForm using Dataverse file block messages and verify the file column is populated.
9. Permit safe retry: rerunning the package must converge on the same records and file.
10. Do not register a plug-in assembly, activate workflows, overwrite unmanaged customizations, or delete target data.
11. Fail the deployment if any seed record or file verification fails.

## Acceptance Criteria

- `pac package show` identifies one managed solution and one deployment extension.
- Package validation confirms no plug-in components and the approved nested solution/XForm hashes.
- `pac package deploy` completes successfully against a test environment with required data privileges.
- The project, form, form version, attachment, and three fixed assignment IDs exist with the expected lookup chain and emails.
- After Hailo's first portal sign-in, the resulting contact email matches one of the two seeded Hailo identities and exactly one TACATDP project is visible.
- `mp_formattachment.mp_file` is non-null and the portal resolves the `dataverse-file:` marker.
- A second deployment completes without duplicate rows.
