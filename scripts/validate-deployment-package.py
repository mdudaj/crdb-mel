#!/usr/bin/env python3
import hashlib
import io
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree


EXPECTED_XFORM_HASH = "1fa53c3517f63dac748c777616c322a9be4da8b70b89e5e3a21a61d6619d8b51"
XFORM_ENTRY = "PkgAssets/Content/tacatdp_impact_evaluation-2608130924.xml"
BASELINE_ENTRY = "PkgAssets/Content/tacatdp-baseline-bridge-import.json"
SOLUTION_ENTRY = "PkgAssets/TACATDP_Impact_Tracking_Prototype_0_2_3_0_managed_no_plugin.zip"
EXPECTED_ASSIGNMENT_EMAILS = (
    "Denis.Muroba@crdbbank.co.tz",
    "Hailo.Kibiki@crdbbank.co.tz",
    "hkibiki@crdbbank.co.tz",
)
AUTHENTICATED_USERS_ROLE_ID = "1bb3051d-e53f-44e0-b226-d6c7050632b0"
REPORTING_POWER_PAGE_COMPONENT_IDS = (
    "ed261eee-a77f-f111-ab0e-7ced8d41fa2d",
    "f3261eee-a77f-f111-ab0e-7ced8d41fa2d",
    "f9261eee-a77f-f111-ab0e-7ced8d41fa2d",
    "04271eee-a77f-f111-ab0e-7ced8d41fa2d",
    "79d527f4-a77f-f111-ab0e-7ced8d41fa2d",
    "7dd527f4-a77f-f111-ab0e-7ced8d41fa2d",
    "87d527f4-a77f-f111-ab0e-7ced8d41fa2d",
    "8bd527f4-a77f-f111-ab0e-7ced8d41fa2d",
    "8fd527f4-a77f-f111-ab0e-7ced8d41fa2d",
    "a5d527f4-a77f-f111-ab0e-7ced8d41fa2d",
    "a77433fa-a77f-f111-ab0e-7ced8d41fa2d",
    "c77433fa-a77f-f111-ab0e-7ced8d41fa2d",
)
REPORTING_PERMISSION_COMPONENT_IDS = (
    "f9261eee-a77f-f111-ab0e-7ced8d41fa2d",
    "7dd527f4-a77f-f111-ab0e-7ced8d41fa2d",
    "8fd527f4-a77f-f111-ab0e-7ced8d41fa2d",
    "c77433fa-a77f-f111-ab0e-7ced8d41fa2d",
)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: validate-deployment-package.py <package.pdpkg.zip>")

    package_path = Path(sys.argv[1])
    if not package_path.is_file():
        fail(f"package not found: {package_path}")

    has_baseline_asset = False
    with zipfile.ZipFile(package_path) as package:
        names = set(package.namelist())
        has_baseline_asset = BASELINE_ENTRY in names
        required = {
            "Tacatdp.DeploymentPackage.dll",
            "PkgAssets/ImportConfig.xml",
            XFORM_ENTRY,
            SOLUTION_ENTRY,
        }
        missing = sorted(required - names)
        if missing:
            fail(f"missing package entries: {', '.join(missing)}")

        xform_hash = hashlib.sha256(package.read(XFORM_ENTRY)).hexdigest()
        if xform_hash != EXPECTED_XFORM_HASH:
            fail(f"XForm hash mismatch: {xform_hash}")
        if has_baseline_asset and len(package.read(BASELINE_ENTRY)) < 100:
            fail("baseline bridge asset is unexpectedly small")

        deployment_assembly = package.read("Tacatdp.DeploymentPackage.dll")
        for email in EXPECTED_ASSIGNMENT_EMAILS:
            if email.encode("utf-16-le") not in deployment_assembly:
                fail(f"deployment assembly does not contain assignment identity: {email}")

        import_config = ElementTree.fromstring(package.read("PkgAssets/ImportConfig.xml"))
        solutions = import_config.findall("./solutions/configsolutionfile")
        if len(solutions) != 1:
            fail("ImportConfig.xml must contain exactly one managed solution")
        solution = solutions[0]
        if solution.get("solutionpackagefilename") != Path(SOLUTION_ENTRY).name:
            fail("ImportConfig.xml references the wrong solution")
        if solution.get("publishworkflowsandactivateplugins") != "false":
            fail("package must not activate plug-ins or workflows")
        if solution.get("overwriteunmanagedcustomizations") != "false":
            fail("package must not overwrite unmanaged customizations")

        with zipfile.ZipFile(io.BytesIO(package.read(SOLUTION_ENTRY))) as managed_solution:
            solution_names = managed_solution.namelist()
            if any(name.startswith("PluginAssemblies/") for name in solution_names):
                fail("nested managed solution contains a plug-in assembly")
            solution_xml = managed_solution.read("solution.xml")
            for component_type in (b'type="90"', b'type="91"', b'type="92"', b'type="93"'):
                if component_type in solution_xml:
                    fail(f"nested managed solution contains component {component_type.decode()}")

            solution_root = ElementTree.fromstring(solution_xml)
            if solution_root.findtext("./SolutionManifest/UniqueName") != "tacatdp_prototype":
                fail("nested managed solution has the wrong unique name")
            if solution_root.findtext("./SolutionManifest/Version") != "0.2.3.0":
                fail("nested managed solution has the wrong version")
            if solution_root.findtext("./SolutionManifest/Managed") != "1":
                fail("nested solution is not managed")

            solution_names_lower = {name.lower() for name in solution_names}
            for component_id in REPORTING_POWER_PAGE_COMPONENT_IDS:
                expected = f"powerpagecomponents/{component_id}/powerpagecomponent.xml"
                if expected not in solution_names_lower:
                    fail(f"nested solution lacks reporting component: {component_id}")

            for component_id in REPORTING_PERMISSION_COMPONENT_IDS:
                entry = f"powerpagecomponents/{component_id}/powerpagecomponent.xml"
                permission_xml = managed_solution.read(entry).decode(
                    "utf-8-sig", errors="strict"
                )
                if AUTHENTICATED_USERS_ROLE_ID not in permission_xml.lower():
                    fail(
                        "reporting table permission lacks Authenticated Users role: "
                        f"{component_id}"
                    )

    baseline_status = "with baseline bridge asset" if has_baseline_asset else "without baseline bridge asset"
    print(f"PASS: {package_path} ({baseline_status})")


if __name__ == "__main__":
    main()
