#!/usr/bin/env python3
"""Validate the scoped TACATDP indicator Package Deployer project."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "deployment/Tacatdp.IndicatorSeedPackage"


def require(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"Missing required package file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    seed = json.loads(require(ROOT / "schemas/dataverse/indicator-evidence-seed.json"))
    packaged_seed = json.loads(require(PACKAGE / "PkgAssets/Content/indicator-evidence-seed.json"))
    if seed != packaged_seed:
        raise SystemExit("Packaged indicator seed JSON does not match schemas/dataverse/indicator-evidence-seed.json")

    csproj = require(PACKAGE / "Tacatdp.IndicatorSeedPackage.csproj")
    extension = require(PACKAGE / "PackageImportExtension.cs")
    deployer = require(PACKAGE / "IndicatorSeedDeployer.cs")
    import_config = require(PACKAGE / "PkgAssets/ImportConfig.xml")

    for fragment in [
        "<TargetFramework>net472</TargetFramework>",
        "Microsoft.PowerApps.MSBuild.PDPackage",
        "Tacatdp.IndicatorSeedPackage",
    ]:
        if fragment not in csproj:
            raise SystemExit(f"Package project missing expected fragment: {fragment}")

    for fragment in [
        "IndicatorSeedDeployer.SeedFileName",
        "new IndicatorSeedDeployer(CrmSvc).Deploy(seedPath)",
        "Idempotently seeds TACATDP indicator definitions and data-source mappings only",
    ]:
        if fragment not in extension:
            raise SystemExit(f"Package extension missing expected fragment: {fragment}")

    for fragment in [
        'new Entity("mp_indicatordefinition")',
        'new Entity("mp_datasourcemapping")',
        'new EntityReference("mp_project", projectId)',
        'new EntityReference("mp_indicatordefinition", definitionId)',
        'new ConditionExpression("mp_project", ConditionOperator.Equal, projectId)',
        'new ConditionExpression("mp_code", ConditionOperator.Equal, code)',
        'new ConditionExpression("mp_mappingkey", ConditionOperator.Equal, mappingKey)',
    ]:
        if fragment not in deployer:
            raise SystemExit(f"Seed deployer missing expected fragment: {fragment}")

    for forbidden in [
        'new Entity("mp_observation")',
        'new Entity("mp_evidence")',
        'new Entity("mp_indicatorresult")',
        'new Entity("mp_form"',
        'new Entity("mp_submission"',
        "UploadBlockRequest",
        "ImportSolution",
        "<PdSolution",
    ]:
        if forbidden in deployer or forbidden in csproj or forbidden in import_config:
            raise SystemExit(f"Scoped indicator seed package contains forbidden fragment: {forbidden}")

    print("Indicator seed package validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
