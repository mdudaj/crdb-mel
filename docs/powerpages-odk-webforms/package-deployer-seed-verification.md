# TACATDP Package Deployer Verification

Date: 2026-07-16
Status: package 1.0.2 built and locally verified; CRDB Windows deployment pending

## Completed

- `dotnet publish -c Release` compiled the net472 Package Deployer extension.
- Package contains exactly one nested managed solution reference.
- Nested solution is `tacatdp_prototype` version `0.2.2.0` and contains no plug-in assembly or component types 90-93.
- `publishworkflowsandactivateplugins` is false.
- `overwriteunmanagedcustomizations` is false.
- Embedded XForm SHA-256 is `12b955fcf42330dbfb8051cbd6d5130a6c0128d78825d7e7b899c901a17f4c28`.
- Package validator passed.
- Built package SHA-256 is `958e6304f5f4758156576d2071a0b5dfb16b179e7dc899fbe7fce9b200faf9db`.
- Local `pac package show` was unavailable because the installed Linux PAC build does not expose that .NET Full Framework-only command; run it on the CRDB Windows PAC installation before deployment.

## CRDB 1.0.0 Result

- Project, Form, FormVersion, FormAttachment, and the XForm file were verified in `TACATDP-CRDB-Dev`.
- No FormAssignment existed, and the portal derives its project list from assignments rather than directly from Projects.
- The Power Pages contact email was verified as `Denis.Muroba@crdbbank.co.tz`.

## CRDB 1.0.1 Result

- Package 1.0.1 deployed successfully.
- The managed solution, project, form, form version, attachment file, Denis assignment, Web API settings, table permission, and Authenticated Users role association were verified.

## Package 1.0.1

- Adds the active FormAssignment for `Denis.Muroba@crdbbank.co.tz`.
- Package validator and ZIP integrity checks passed.
- Built package SHA-256 is `c40ba7207001e96dcc21859143a11559fbe356b63b90fc04e89326051b64f6c4`.
- The authenticated Linux PAC deployment attempt was correctly rejected because Dataverse Package Deployer requires the Windows .NET Framework PAC build. No CRDB write occurred during that attempt.

## Package 1.0.2

- Retains Denis's assignment and adds stable assignments for `Hailo.Kibiki@crdbbank.co.tz` and `hkibiki@crdbbank.co.tz`.
- CRDB contact lookup on 2026-07-16 found no contact for either supplied Hailo identity or name, so both aliases are seeded until first sign-in establishes the contact email derived from Entra `preferred_username`.
- `dotnet publish -c Release` compiled the package; the only warning is the existing PDPackage SDK compatibility advisory for .NET SDK `10.0.109`.
- Package validator and ZIP integrity checks passed.
- Built package SHA-256 is `510659fcbf8458514b6ed0f48eb1fa637e7e52c043fdb6ae080688b96f0d431b`.
- Remaining gates: deploy package 1.0.2 from Windows after explicit approval, verify both new assignment rows, then complete Hailo's authenticated browser smoke test.
