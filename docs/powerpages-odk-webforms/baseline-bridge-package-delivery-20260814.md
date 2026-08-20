# Baseline bridge package delivery — 2026-08-14

Status: package built and validated; local deploy blocked by Linux PAC Package Deployer limitation.

## Scope

This delivery prepares the approved TACATDP baseline import for the Mshirika development environment without using Azure CLI.

The package-deployer seed extension now supports:

- latest TACATDP XForm version `2608130924`;
- canonical `mp_Project`, `mp_Form`, `mp_FormVersion`, `mp_FormAttachment`, and assignment seed refresh;
- baseline `mp_Submission` and `mp_SubmissionVersion` import;
- `mp_TrackedEntity` beneficiary rows;
- `mp_EntityIdentifier` rows for source UUID, approved Customer ID, and approved phone identifiers;
- `mp_BeneficiaryProfile` rows;
- `mp_BeneficiarySubmissionLink` rows;
- review-only duplicate handling with no automatic merge.

## Generated local artifacts

These artifacts are intentionally ignored by git because they contain generated deployment content and, for the baseline JSON, approved beneficiary data:

| Artifact | Purpose | Commit status |
|---|---|---|
| `artifacts/xforms/tacatdp_impact_evaluation-2608130924.xml` | Latest compiled XForm. | Ignored. |
| `deployment/Tacatdp.DeploymentPackage/PkgAssets/Content/tacatdp-baseline-bridge-import.json` | Package seed input generated from the Kobo baseline export. | Ignored; contains raw approved import data. |
| `deployment/Tacatdp.DeploymentPackage/bin/Release/Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip` | Dataverse Package Deployer package. | Ignored; sensitive delivery artifact. |

## Package asset counts

The generated baseline bridge package asset contains:

| Item | Count |
|---|---:|
| Baseline rows | 965 |
| Entity identifiers | 2,886 |
| Duplicate-review groups | 10 |

Duplicate groups remain review-only. The package does not merge duplicate Customer ID or phone candidates.

## Verification completed

Commands run:

```bash
.venv/bin/python scripts/xlsform-compile.py \
  --workbook /home/jmduda/Downloads/TACATDP/TACATDP_Tool.xlsx \
  --version 2608130924 \
  --skip-pyxform-validate

.venv/bin/python scripts/import-baseline-bridge.py \
  --mode package-asset \
  --xlsform /home/jmduda/Downloads/TACATDP/TACATDP_Tool.xlsx \
  --workbook /home/jmduda/Downloads/TACATDP/TACATDP_Impact_Data_Tracking_for_Financed_Beneficiaries_-_all_versions_-_English_en_-_2026-08-13-06-12-18.xlsx \
  --repo-root /home/jmduda/KodeX/crdb-mel \
  --output-json deployment/Tacatdp.DeploymentPackage/PkgAssets/Content/tacatdp-baseline-bridge-import.json \
  --summary-json /tmp/tacatdp-baseline-bridge-package-asset-summary-20260814.json

deployment/Tacatdp.DeploymentPackage/build-package.sh \
  artifacts/deployments/crdb-20260728/TACATDP_Impact_Tracking_Prototype_0_2_3_0_managed_no_plugin.zip \
  artifacts/xforms/tacatdp_impact_evaluation-2608130924.xml \
  deployment/Tacatdp.DeploymentPackage/PkgAssets/Content/tacatdp-baseline-bridge-import.json
```

Validation result:

```text
PASS: deployment/Tacatdp.DeploymentPackage/bin/Release/Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip (with baseline bridge asset)
```

## Local deployment result

Deployment command attempted:

```bash
source scripts/use-powerplatform-env.sh mshirika
pac auth select --name "$PAC_AUTH_NAME"
pac package deploy \
  --environment "$POWER_PLATFORM_ENVIRONMENT_URL" \
  --package deployment/Tacatdp.DeploymentPackage/bin/Release/Tacatdp.DeploymentPackage.1.0.3.pdpkg.zip \
  --logConsole
```

Result:

```text
Error: 'pac package deploy --package-type dataverse' requires .NET Framework and is not available on this build.
Use the Windows version of pac.exe, or pass '--package-type erp' to deploy a Finance and Operations package.
```

This confirms the previous project lesson: Linux PAC can authenticate, fetch, upload Power Pages, and import solutions, but Dataverse Package Deployer packages require Windows PAC/.NET Framework support.

## Required execution path

Use one of these approved non-Azure options:

1. Run the generated `.pdpkg.zip` from a Windows machine with PAC and the Mshirika profile selected.
2. Ask the environment administrator to run the same `pac package deploy` command from Windows.
3. Provide an approved Dataverse application user/service principal so the repository Web API importer can run without Azure CLI.

Do not commit the generated baseline JSON or package zip because they contain approved but sensitive beneficiary import data.
