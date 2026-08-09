#!/usr/bin/env python3
"""Validate User & Access write preview UI wiring."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEW = ROOT / "powerpages/webforms-spa/src/views/AssignedFormsView.vue"
CSS = ROOT / "powerpages/webforms-spa/src/styles.css"
DOC = ROOT / "docs/powerpages-odk-webforms/access-write-preview-ui-20260721.md"

VIEW_TERMS = (
    "AccessWritePreview",
    "selectedAccessWritePreview",
    "accessWorkflowWritePreviews",
    "buildSelectedAccessWriteCommand",
    "buildSafeAccessWritePreview",
    "formatAccessPreviewJson",
    "api.buildAccessWritePreview",
    "Generated preview",
    "Audit payload",
    "Future mutation payload",
)
CSS_TERMS = (
    ".access-preview-payload",
    ".access-preview-record",
    ".access-preview-list--compact",
    ".access-preview-payload pre",
)
DOC_TERMS = (
    "implemented without enabling Dataverse writes",
    "one `AssignForm` preview per selected form version",
    "The final action buttons remain disabled",
)
FORBIDDEN_VIEW_TERMS = (
    "api.submitAccessWrite(",
    "@click=\"submitAccessWrite",
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
    view = require_terms(VIEW, VIEW_TERMS)
    require_terms(CSS, CSS_TERMS)
    require_terms(DOC, DOC_TERMS)

    for term in FORBIDDEN_VIEW_TERMS:
        if term in view:
            fail(f"write submit path must not be wired in preview-only slice: {term}")
    if "Create, invite and assign disabled" not in view:
        fail("create, invite and assign action must remain disabled")
    if "Apply change disabled" not in view:
        fail("apply change action must remain disabled")

    print("TACATDP access write preview UI validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
