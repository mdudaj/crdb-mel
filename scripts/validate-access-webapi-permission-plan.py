#!/usr/bin/env python3
"""Validate User & Access Web API and table-permission planning artifacts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/powerpages-odk-webforms/access-webapi-permission-package-plan-20260721.md"
MATRIX = ROOT / "docs/powerpages-odk-webforms/access-permission-matrix-20260721.md"
RUNBOOK = ROOT / "docs/powerpages-odk-webforms/access-audit-import-update-runbook-20260721.md"
CLIENT = ROOT / "powerpages/webforms-spa/src/powerpages-api/client.ts"

PLAN_TERMS = (
    "No environment write",
    "ACCESS_WRITE_ACTIONS_ENABLED",
    "Webapi/mp_accessauditlog/enabled",
    "Webapi/mp_accessauditlog/fields",
    "Webapi/mp_formassignment/enabled",
    "Webapi/mp_formassignment/fields",
    "Webapi/contact/enabled",
    "Platform Administrator",
    "Project Manager",
    "Data Collector / Bank Officer",
    "Parent/relationship scoped",
    "EntityPermissionReadIsMissing",
    "Smoke Tests",
)
MATRIX_TERMS = (
    "access-webapi-permission-package-plan-20260721.md",
    "Platform Administrator only",
    "Do not grant audit read access to Data Collector",
)
RUNBOOK_TERMS = (
    "access-webapi-permission-package-plan-20260721.md",
    "Webapi/mp_accessauditlog/enabled",
    "Power Pages Security workspace",
)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required artifact: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require_terms(path: Path, terms: tuple[str, ...]) -> str:
    text = read(path)
    for term in terms:
        if term not in text:
            fail(f"{path.relative_to(ROOT)} missing required text: {term}")
    return text


def main() -> int:
    require_terms(PLAN, PLAN_TERMS)
    require_terms(MATRIX, MATRIX_TERMS)
    require_terms(RUNBOOK, RUNBOOK_TERMS)

    client = read(CLIENT)
    if "VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED === 'true'" not in client:
        fail("access writes must default to disabled while permission package is planning-only")
    for forbidden in (
        "Webapi/mp_accessauditlog/enabled",
    ):
        if forbidden in client:
            fail(f"runtime permission or audit endpoint must not be wired in client yet: {forbidden}")
    if "/_api/mp_accessauditlogs" in client:
        require_terms(
            ROOT / "docs/powerpages-odk-webforms/access-assignform-disabled-implementation-20260721.md",
            ("Audit and assignment Web API helpers exist only behind the disabled public submit guard",),
        )

    print("TACATDP access Web API permission plan validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
