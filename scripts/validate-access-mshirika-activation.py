#!/usr/bin/env python3
"""Validate Mshirika-only User Management activation artifacts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"
VITE_ENV = ROOT / "powerpages/webforms-spa/src/vite-env.d.ts"
PACKAGE = ROOT / "powerpages/webforms-spa/package.json"
CONFIGURE = ROOT / "scripts/powerpages-configure-webapi.py"
QUEUE_SCHEMA = ROOT / "schemas/dataverse/onboarding-request-schema.json"
DOC = ROOT / "docs/powerpages-odk-webforms/access-mshirika-activation-test-20260722.md"
UPLOAD_HOME = ROOT / "powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-pages/home/Home.webpage.copy.html"
UPLOAD_HOME_CONTENT = ROOT / "powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-pages/home/content-pages/Home.en-US.webpage.copy.html"
UPLOAD_WEB_FILES = ROOT / "powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required artifact: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require(path: Path, terms: tuple[str, ...]) -> str:
    text = read(path)
    for term in terms:
        if term not in text:
            fail(f"{path.relative_to(ROOT)} missing required text: {term}")
    return text


def main() -> int:
    require(CLIENT, (
        "VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED === 'true'",
        "VITE_TACATDP_ACCESS_ASSIGN_FORM_WRITE_ENABLED === 'true'",
        "VITE_TACATDP_ACCESS_ONBOARDING_AUTOMATION_ENABLED === 'true'",
        "VITE_TACATDP_ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED === 'true'",
        "ACCESS_ONBOARDING_QUEUE_WEB_API_PATH",
        "'/_api/mp_onboardingrequests'",
        "createOnboardingRequest",
        "queued-for-assignment-notification",
    ))
    require(VITE_ENV, (
        "VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED",
        "VITE_TACATDP_ACCESS_ASSIGN_FORM_WRITE_ENABLED",
        "VITE_TACATDP_ACCESS_ONBOARDING_AUTOMATION_ENABLED",
        "VITE_TACATDP_ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED",
    ))
    require(PACKAGE, (
        "build:mshirika-access",
        "VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED=true",
        "VITE_TACATDP_ACCESS_ASSIGN_FORM_WRITE_ENABLED=true",
        "VITE_TACATDP_ACCESS_ONBOARDING_AUTOMATION_ENABLED=true",
        "VITE_TACATDP_ODK_RUNTIME_ENABLED=false",
    ))
    configure = require(CONFIGURE, (
        "ACCESS_WRITE_TABLES",
        "--include-access-writes",
        "--access-role-name",
        "mp_onboardingrequest",
        "TACATDP OnboardingRequests Admin Queue",
        "mp_accessauditlog",
        '"logical": "contact"',
        "mp_formassignment",
        "mp_formversion",
        "permission_role_exists",
        'payload={"mspp_value": value}',
        'preserving existing wildcard fields',
    ))
    if 'ACCESS_WRITE_TABLES' in configure and 'find_authenticated_role' not in configure:
        fail("configure script must keep authenticated runtime role discovery")
    if 'ACCESS_WRITE_TABLES' in configure and 'find_role_by_name' not in configure:
        fail("configure script must discover administrator role by name for access writes")
    require(QUEUE_SCHEMA, (
        "OnboardingRequests",
        "RequestKey",
        "Status",
        "RequestType",
        "FormScopeJson",
        "direct_power_pages_cloud_flow_invocation_disallowed",
    ))
    require(DOC, (
        "prepared for Mshirika development testing only",
        "npm --prefix powerpages/webforms-spa run build:mshirika-access",
        "VITE_TACATDP_ACCESS_ONBOARDING_AUTOMATION_ENABLED=true",
        "VITE_TACATDP_ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED",
        "VITE_TACATDP_ODK_RUNTIME_ENABLED=false",
        "OnboardingRequests",
        "Dataverse-triggered",
        "queued",
        "Do not reuse the activated Mshirika bundle for CRDB",
    ))
    bundle_candidates = sorted(UPLOAD_WEB_FILES.glob("index-*.mjs"), key=lambda path: path.stat().st_mtime, reverse=True)
    if bundle_candidates:
        queue_bundles = [path for path in bundle_candidates if "/_api/mp_onboardingrequests" in read(path)]
        if queue_bundles:
            bundle = read(queue_bundles[0])
            for term in ("Write actions enabled", "AssignForm enabled", "/_api/mp_onboardingrequests"):
                if term not in bundle:
                    fail(f"Mshirika bundle missing queue activation term: {term}")
            if "/_api/cloudflow/v1.0/trigger/" in bundle:
                fail("Mshirika bundle must not call the direct Power Pages cloud-flow trigger for onboarding")
    for asset in list(UPLOAD_WEB_FILES.glob("*.mjs")) + list(UPLOAD_WEB_FILES.glob("*.css")):
        if asset.stat().st_size > 1_048_576:
            fail(f"Mshirika access asset exceeds Power Pages content limit: {asset.name}")
    index_css = sorted(UPLOAD_WEB_FILES.glob("index-*.css"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not index_css:
        fail("Mshirika access upload package missing index stylesheet")
    require(index_css[0], (".",))

    print("TACATDP Mshirika access activation validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
